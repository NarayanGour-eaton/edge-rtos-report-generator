"""
GitHub API Client for downloading artifacts and run information.

This module provides functionality to interact with GitHub's REST API to:
- Fetch GitHub Actions run information
- List artifacts for a specific run
- Download artifact contents
"""

import requests
import logging
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import zipfile
import io

logger = logging.getLogger(__name__)


class GitHubAPIClient:
    """Client for interacting with GitHub API to fetch run data and artifacts."""
    
    def __init__(self, config):
        """Initialize GitHub API client with configuration."""
        self.config = config
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        # Set up authentication if provided
        if hasattr(config, 'github_token') and config.github_token:
            self.session.headers.update({
                'Authorization': f'token {config.github_token}'
            })
        
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Actions-Report-Generator'
        })
        
        # Rate limiting
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = 0
    
    def _check_rate_limit(self):
        """Check and handle GitHub API rate limiting."""
        if self.rate_limit_remaining < 10:
            current_time = int(time.time())
            if current_time < self.rate_limit_reset:
                sleep_time = self.rate_limit_reset - current_time + 1
                logger.warning(f"Rate limit low. Sleeping for {sleep_time} seconds...")
                time.sleep(sleep_time)
    
    def _make_request(self, url: str, **kwargs) -> requests.Response:
        """Make a request to GitHub API with rate limiting and error handling."""
        self._check_rate_limit()
        
        try:
            response = self.session.get(url, **kwargs)
            
            # Update rate limit info
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 5000))
            self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            raise
    
    def get_run_info(self, run_id: str) -> Dict[str, Any]:
        """
        Get information about a specific GitHub Actions run.
        
        Args:
            run_id: The GitHub Actions run ID
            
        Returns:
            Dictionary containing run information
        """
        url = f"{self.base_url}/repos/{self.config.repo_owner}/{self.config.repo_name}/actions/runs/{run_id}"
        
        logger.info(f"Fetching run info from: {url}")
        response = self._make_request(url)
        
        run_data = response.json()
        
        logger.info(f"Run: {run_data.get('name', 'Unknown')} - Status: {run_data.get('status', 'Unknown')}")
        logger.info(f"Created: {run_data.get('created_at', 'Unknown')}")
        logger.info(f"Branch: {run_data.get('head_branch', 'Unknown')}")
        
        return run_data
    
    def get_run_artifacts(self, run_id: str) -> List[Dict[str, Any]]:
        """
        Get list of artifacts for a specific GitHub Actions run.
        Handles pagination to fetch all artifacts (not just first 30).
        
        Args:
            run_id: The GitHub Actions run ID
            
        Returns:
            List of artifact dictionaries
        """
        base_url = f"{self.base_url}/repos/{self.config.repo_owner}/{self.config.repo_name}/actions/runs/{run_id}/artifacts"
        
        all_artifacts = []
        page = 1
        per_page = 100  # GitHub API max per page
        
        logger.info(f"Fetching artifacts from run {run_id} with pagination...")
        
        while True:
            url = f"{base_url}?page={page}&per_page={per_page}"
            logger.debug(f"Requesting page {page}: {url}")
            
            response = self._make_request(url)
            artifacts_data = response.json()
            
            artifacts = artifacts_data.get('artifacts', [])
            total_count = artifacts_data.get('total_count', 0)
            
            if not artifacts:
                # No more artifacts
                break
            
            all_artifacts.extend(artifacts)
            logger.info(f"Page {page}: Found {len(artifacts)} artifacts (Total so far: {len(all_artifacts)}/{total_count})")
            
            # Check if we have all artifacts
            if len(all_artifacts) >= total_count or len(artifacts) < per_page:
                break
            
            page += 1
        
        logger.info(f"Found {len(all_artifacts)} total artifacts across {page} pages")
        
        # Filter out build artifacts if configured
        filtered_artifacts = []
        for artifact in all_artifacts:
            name = artifact['name'].lower()
            
            # Skip build artifacts unless they contain test results
            if 'build' in name and not any(test_keyword in name for test_keyword in ['test', 'report', 'result']):
                logger.debug(f"Filtering out build artifact: {artifact['name']}")
                continue
                
            filtered_artifacts.append(artifact)
            logger.debug(f"  - {artifact['name']} ({artifact['size_in_bytes']} bytes)")
        
        logger.info(f"After filtering: {len(filtered_artifacts)} test-related artifacts")
        return filtered_artifacts
    
    def download_artifact(self, artifact_id: int) -> bytes:
        """
        Download artifact contents by artifact ID.
        
        Args:
            artifact_id: The artifact ID to download
            
        Returns:
            Raw artifact data as bytes
        """
        url = f"{self.base_url}/repos/{self.config.repo_owner}/{self.config.repo_name}/actions/artifacts/{artifact_id}/zip"
        
        logger.info(f"Downloading artifact {artifact_id}...")
        response = self._make_request(url)
        
        logger.info(f"Downloaded {len(response.content)} bytes")
        return response.content
    
    def get_workflow_runs(self, workflow_name: Optional[str] = None, branch: Optional[str] = None, 
                         limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent workflow runs, optionally filtered by workflow name or branch.
        
        Args:
            workflow_name: Optional workflow name to filter by
            branch: Optional branch name to filter by
            limit: Maximum number of runs to return
            
        Returns:
            List of workflow run dictionaries
        """
        url = f"{self.base_url}/repos/{self.config.repo_owner}/{self.config.repo_name}/actions/runs"
        params = {'per_page': min(limit, 100)}
        
        if branch:
            params['branch'] = branch
            
        response = self._make_request(url, params=params)
        runs_data = response.json()
        
        runs = runs_data.get('workflow_runs', [])
        
        if workflow_name:
            runs = [run for run in runs if workflow_name.lower() in run.get('name', '').lower()]
        
        return runs[:limit]
    
    def search_recent_runs_by_pattern(self, pattern: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for recent runs that match a specific pattern in the workflow name.
        
        Args:
            pattern: Pattern to search for in workflow names (case insensitive)
            limit: Maximum number of runs to return
            
        Returns:
            List of matching workflow runs
        """
        runs = self.get_workflow_runs(limit=limit * 2)  # Get more to account for filtering
        
        matching_runs = []
        for run in runs:
            workflow_name = run.get('name', '').lower()
            if pattern.lower() in workflow_name:
                matching_runs.append(run)
                if len(matching_runs) >= limit:
                    break
        
        return matching_runs
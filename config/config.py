"""
Configuration management for GitHub Actions Report Generator.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the report generator."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize configuration from file or environment variables."""
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment variables."""
        # Default configuration
        self.repo_owner = "etn-ccis"
        self.repo_name = "edge-rtos-github-builds"
        self.github_token = None
        
        # Artifact processing settings
        self.skip_build_artifacts = True
        self.supported_test_formats = ['.xml', '.json', '.html', '.txt', '.log']
        
        # Output settings
        self.output_format = "both"  # 'text', 'json', 'both'
        self.include_passed_tests = False
        self.max_failure_message_length = 500
        
        # Load from config file if it exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    
                self._update_from_dict(file_config)
                logger.info(f"Loaded configuration from {self.config_file}")
                
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load config file {self.config_file}: {e}")
        
        # Override with environment variables
        self._load_from_environment()
        
        # Validate required settings
        if not self.repo_owner or not self.repo_name:
            raise ValueError("Repository owner and name must be configured")
    
    def _update_from_dict(self, config_dict: dict):
        """Update configuration from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'GITHUB_TOKEN': 'github_token',
            'REPO_OWNER': 'repo_owner',
            'REPO_NAME': 'repo_name',
            'OUTPUT_FORMAT': 'output_format',
        }
        
        for env_var, attr_name in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                setattr(self, attr_name, env_value)
                logger.debug(f"Set {attr_name} from environment variable {env_var}")
    
    def save_config(self, config_file: Optional[str] = None):
        """Save current configuration to file."""
        if config_file is None:
            config_file = self.config_file
        
        config_dict = {
            'repo_owner': self.repo_owner,
            'repo_name': self.repo_name,
            'skip_build_artifacts': self.skip_build_artifacts,
            'supported_test_formats': self.supported_test_formats,
            'output_format': self.output_format,
            'include_passed_tests': self.include_passed_tests,
            'max_failure_message_length': self.max_failure_message_length,
        }
        
        # Don't save sensitive information like tokens
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2)
            logger.info(f"Configuration saved to {config_file}")
        except IOError as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def validate(self):
        """Validate configuration settings."""
        if not self.github_token:
            logger.warning("GitHub token not configured. API rate limits will be lower.")
        
        if not self.repo_owner or not self.repo_name:
            raise ValueError("Repository owner and name are required")
        
        valid_formats = ['text', 'json', 'both']
        if self.output_format not in valid_formats:
            raise ValueError(f"Invalid output format: {self.output_format}. Must be one of {valid_formats}")
    
    def __str__(self):
        """String representation of configuration."""
        return f"Config(repo={self.repo_owner}/{self.repo_name}, format={self.output_format})"
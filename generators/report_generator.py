"""
Report Generator for creating formatted test reports.

This module generates:
- Human-readable text reports with summary and detailed failure information
- JSON reports for programmatic access
- HTML reports (optional)
"""

import sys
from pathlib import Path

# Add core module path
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

import logging
from typing import Dict, List, Any
from datetime import datetime
from artifact_processor import TestSuiteResult, TestResult

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates formatted test reports from processed test results."""
    
    def __init__(self, config):
        """Initialize report generator with configuration."""
        self.config = config
    
    def generate_detailed_report(self, run_info: Dict[str, Any], 
                                test_results: Dict[str, Dict[str, TestSuiteResult]], 
                                run_id: str) -> str:
        """
        Generate detailed text report.
        
        Args:
            run_info: GitHub Actions run information
            test_results: Test results organized by artifact and suite
            run_id: The run ID
            
        Returns:
            Formatted text report
        """
        report_lines = []
        
        # Header
        report_lines.append(f"GitHub Actions Test Report")
        report_lines.append(f"Run ID: {run_id}")
        report_lines.append(f"Workflow: {run_info.get('name', 'Unknown')}")
        report_lines.append(f"Status: {run_info.get('status', 'Unknown')}")
        report_lines.append(f"Branch: {run_info.get('head_branch', 'Unknown')}")
        report_lines.append(f"Commit: {run_info.get('head_sha', 'Unknown')[:8]}")
        report_lines.append(f"Created: {run_info.get('created_at', 'Unknown')}")
        report_lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Overall summary
        overall_stats = self._calculate_overall_stats(test_results)
        report_lines.append("OVERALL SUMMARY:")
        report_lines.append(f"  Total Tests: {overall_stats['total']}")
        report_lines.append(f"  Passed: {overall_stats['passed']}")
        report_lines.append(f"  Failed: {overall_stats['failed']}")
        report_lines.append(f"  Skipped: {overall_stats['skipped']}")
        report_lines.append(f"  Errors: {overall_stats['errors']}")
        
        if overall_stats['total'] > 0:
            pass_rate = (overall_stats['passed'] / overall_stats['total']) * 100
            report_lines.append(f"  Pass Rate: {pass_rate:.1f}%")
        
        report_lines.append("")
        
        # Test suite breakdown
        report_lines.append("TEST SUITE BREAKDOWN:")
        report_lines.append("")
        
        for artifact_name, suites in test_results.items():
            if not suites:
                continue
                
            report_lines.append(f"Artifact: {artifact_name}")
            report_lines.append("-" * (len(artifact_name) + 10))
            
            for suite_name, suite_result in suites.items():
                report_lines.append(f"  {suite_name}:")
                report_lines.append(f"    Total: {suite_result.total}")
                report_lines.append(f"    Passed: {suite_result.passed}")
                report_lines.append(f"    Failed: {suite_result.failed}")
                report_lines.append(f"    Skipped: {suite_result.skipped}")
                report_lines.append(f"    Errors: {suite_result.errors}")
                
                if suite_result.duration > 0:
                    report_lines.append(f"    Duration: {suite_result.duration:.2f}s")
                
                # List failed tests
                failed_tests = [t for t in suite_result.tests if t.status in ['failed', 'error']]
                if failed_tests:
                    report_lines.append(f"    Failed Tests ({len(failed_tests)}):")
                    for i, test in enumerate(failed_tests, 1):
                        report_lines.append(f"      {i}. {test.name}")
                        if test.failure_message:
                            # Truncate long failure messages
                            msg = test.failure_message.strip()
                            if len(msg) > 100:
                                msg = msg[:100] + "..."
                            report_lines.append(f"         Error: {msg}")
                
                report_lines.append("")
            
            report_lines.append("")
        
        # Detailed failure analysis
        all_failures = self._get_all_failures(test_results)
        if all_failures:
            report_lines.append("DETAILED FAILURE ANALYSIS:")
            report_lines.append("=" * 40)
            
            for suite_name, failures in all_failures.items():
                if not failures:
                    continue
                    
                report_lines.append(f"\n{suite_name}: {len(failures)} failed")
                report_lines.append("-" * (len(suite_name) + 20))
                
                for i, test in enumerate(failures, 1):
                    report_lines.append(f"{i}. {test.name}")
                    if test.failure_message:
                        report_lines.append(f"   Error: {test.failure_message}")
                    if test.error_message:
                        report_lines.append(f"   Error: {test.error_message}")
                    report_lines.append("")
        
        return "\n".join(report_lines)
    
    def generate_json_report(self, run_info: Dict[str, Any], 
                           test_results: Dict[str, Dict[str, TestSuiteResult]], 
                           run_id: str) -> Dict[str, Any]:
        """
        Generate JSON report for programmatic access.
        
        Args:
            run_info: GitHub Actions run information
            test_results: Test results organized by artifact and suite
            run_id: The run ID
            
        Returns:
            JSON-serializable dictionary
        """
        overall_stats = self._calculate_overall_stats(test_results)
        
        json_report = {
            "run_info": {
                "run_id": run_id,
                "workflow_name": run_info.get('name', 'Unknown'),
                "status": run_info.get('status', 'Unknown'),
                "branch": run_info.get('head_branch', 'Unknown'),
                "commit_sha": run_info.get('head_sha', 'Unknown'),
                "created_at": run_info.get('created_at', 'Unknown'),
                "report_generated_at": datetime.now().isoformat()
            },
            "summary": overall_stats,
            "test_suites": {},
            "failures": {}
        }
        
        # Process each artifact and suite
        for artifact_name, suites in test_results.items():
            json_report["test_suites"][artifact_name] = {}
            
            for suite_name, suite_result in suites.items():
                suite_data = {
                    "name": suite_result.name,
                    "total": suite_result.total,
                    "passed": suite_result.passed,
                    "failed": suite_result.failed,
                    "skipped": suite_result.skipped,
                    "errors": suite_result.errors,
                    "duration": suite_result.duration,
                    "tests": []
                }
                
                # Add individual test results
                for test in suite_result.tests:
                    test_data = {
                        "name": test.name,
                        "status": test.status,
                        "duration": test.duration
                    }
                    
                    if test.failure_message:
                        test_data["failure_message"] = test.failure_message
                    if test.error_message:
                        test_data["error_message"] = test.error_message
                    
                    suite_data["tests"].append(test_data)
                
                json_report["test_suites"][artifact_name][suite_name] = suite_data
        
        # Add failures summary
        all_failures = self._get_all_failures(test_results)
        for suite_name, failures in all_failures.items():
            json_report["failures"][suite_name] = [
                {
                    "name": test.name,
                    "failure_message": test.failure_message,
                    "error_message": test.error_message
                }
                for test in failures
            ]
        
        return json_report
    
    def generate_summary_report(self, test_results: Dict[str, Dict[str, TestSuiteResult]]) -> str:
        """
        Generate a concise summary report suitable for notifications or quick overview.
        
        Args:
            test_results: Test results organized by artifact and suite
            
        Returns:
            Brief summary text
        """
        overall_stats = self._calculate_overall_stats(test_results)
        
        if overall_stats['total'] == 0:
            return "No test results found."
        
        summary_lines = []
        
        # Overall status
        if overall_stats['failed'] == 0 and overall_stats['errors'] == 0:
            summary_lines.append("✅ All tests passed!")
        else:
            summary_lines.append("❌ Some tests failed")
        
        # Stats
        summary_lines.append(f"Tests: {overall_stats['passed']}/{overall_stats['total']} passed")
        
        if overall_stats['failed'] > 0:
            summary_lines.append(f"Failed: {overall_stats['failed']}")
        if overall_stats['errors'] > 0:
            summary_lines.append(f"Errors: {overall_stats['errors']}")
        if overall_stats['skipped'] > 0:
            summary_lines.append(f"Skipped: {overall_stats['skipped']}")
        
        # Pass rate
        if overall_stats['total'] > 0:
            pass_rate = (overall_stats['passed'] / overall_stats['total']) * 100
            summary_lines.append(f"Pass rate: {pass_rate:.1f}%")
        
        return " | ".join(summary_lines)
    
    def _calculate_overall_stats(self, test_results: Dict[str, Dict[str, TestSuiteResult]]) -> Dict[str, int]:
        """Calculate overall statistics across all test suites."""
        stats = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'errors': 0}
        
        for artifact_name, suites in test_results.items():
            for suite_name, suite_result in suites.items():
                stats['total'] += suite_result.total
                stats['passed'] += suite_result.passed
                stats['failed'] += suite_result.failed
                stats['skipped'] += suite_result.skipped
                stats['errors'] += suite_result.errors
        
        return stats
    
    def _get_all_failures(self, test_results: Dict[str, Dict[str, TestSuiteResult]]) -> Dict[str, List[TestResult]]:
        """Extract all failed tests organized by suite."""
        all_failures = {}
        
        for artifact_name, suites in test_results.items():
            for suite_name, suite_result in suites.items():
                failures = [t for t in suite_result.tests if t.status in ['failed', 'error']]
                if failures:
                    # Use a compound key to handle multiple artifacts with same suite names
                    key = f"{artifact_name}::{suite_name}" if len(test_results) > 1 else suite_name
                    all_failures[key] = failures
        
        return all_failures
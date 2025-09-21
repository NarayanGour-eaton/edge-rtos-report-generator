"""
Regression Report Generator - Matches ETN Team Format

This module generates reports in the exact format used by the ETN team
for nightly regression status reporting, combining automated data extraction
with the established reporting structure.
"""

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from artifact_processor import TestSuiteResult, TestResult

logger = logging.getLogger(__name__)


class RegressionReportGenerator:
    """Generates regression reports matching ETN team format."""
    
    def __init__(self, config):
        """Initialize regression report generator."""
        self.config = config
        
        # Workflow name mappings (customize these based on your actual workflow names)
        self.workflow_mappings = {
            'h743': 'BFT_h743zi_dev (Functional + Module + Build only)',
            'u575': 'BFT_U575zi_q_dev (Functional + Module)',
            'build': 'Build-All-In-Container',
            'blackduck': 'Blackduck',
            'twister': 'Build-All-Twister-In-Container',
            'coverity': 'Coverity-Build-In-Container',
            'tbt': 'TBT-h743zi (Twister build test)',
            'ui_h743': 'BFT_h743zi_dev (UI Test)',
            'ui_u575': 'BFT_U575zi_q_dev (UI test)'
        }
    
    def generate_regression_status_report(self, run_info: Dict[str, Any], 
                                        test_results: Dict[str, Dict[str, TestSuiteResult]], 
                                        run_id: str,
                                        include_historical: bool = False,
                                        branch_name: str = None) -> str:
        """
        Generate regression status report in ETN team format.
        
        Args:
            run_info: GitHub Actions run information
            test_results: Test results organized by artifact and suite
            run_id: The run ID
            include_historical: Whether to include historical success/failure data
            branch_name: Branch name for the regression runs (extracted from run_info if None)
            
        Returns:
            Formatted regression status report
        """
        # Extract branch name from run_info if not provided
        if not branch_name:
            branch_name = run_info.get('head_branch', 'Dev')  # Default to 'Dev' if not found
        report_lines = []
        
        # Header
        report_lines.extend([
            f"Please find latest regression status below.",
            "",
            f"Nightly Regression runs: {branch_name} Branch (Build Repository)",
            f"Date: {datetime.now().strftime('%Y-%m-%d')}",
            f"Run ID: {run_id}",
            "",
            ""
        ])
        
        # Main test results table
        main_workflows = self._process_main_workflows(run_info, test_results)
        if main_workflows:
            report_lines.extend([
                "Workflow Name\tPlan result\tTotal*\tPass\tFail\tSkipped\tActions"
            ])
            
            for workflow_data in main_workflows:
                actions_text = self._format_actions(workflow_data['failures'])
                report_lines.append(
                    f"{workflow_data['name']}\n"
                    f"{workflow_data['status']}\t{workflow_data['total']}\t"
                    f"{workflow_data['pass']}\t{workflow_data['fail']}\t{workflow_data['skipped']}\t"
                    f"{actions_text}"
                )
            
            report_lines.append("")
        
        # UI Test Results (if applicable)
        ui_workflows = self._process_ui_workflows(run_info, test_results)
        if ui_workflows:
            report_lines.extend([
                "Workflow Name\tPlan result\tTotal*\tPass\tFail\tSkipped\t\tComment"
            ])
            
            for workflow_data in ui_workflows:
                comment_text = self._format_ui_comments(workflow_data['failures'])
                report_lines.append(
                    f"{workflow_data['name']}\n"
                    f"{workflow_data['status']}\t{workflow_data['total']}\t"
                    f"{workflow_data['pass']}\t{workflow_data['fail']}\t{workflow_data['skipped']}\t\t"
                    f"{comment_text}"
                )
            
            report_lines.append("")
        
        # Historical Success/Failure Data (if requested)
        if include_historical:
            historical_data = self._generate_historical_summary()
            report_lines.extend([
                "",
                "\tTime Period\tSuccess Days\tFailed Days\t% Success days\t\t",
                f"\tYear to Date\t{historical_data['ytd_success']}\t"
                f"{historical_data['ytd_failed']}\t{historical_data['ytd_percent']}\t\t",
                f"\tLast 30 Days\t{historical_data['last30_success']}\t"
                f"{historical_data['last30_failed']}\t{historical_data['last30_percent']}\t\t",
                ""
            ])
        
        # Quick Links Section
        report_lines.extend([
            "",
            "Quick links:",
            "PXGreen Bugs- Regression Failed:",
            "https://eaton-corp.atlassian.net/wiki/spaces/LTK/pages/19376705/PXGreen+Bugs+-+Regression_Failed",
            "",
            "Nightly_regression_test_status_spreadsheet:",
            "https://eaton.sharepoint.com/:x:/s/PlatformsandAnalyticsART/EeAJ-vxC2IdPiSyykB9L6ZQBb90daXGwYuDr6CmylosQvg?e=eCR5qB&clickparams=eyAiWC1BcHBOYW1lIiA6ICJNaWNyb3NvZnQgT3V0bG9vayIsICJYLUFwcFZlcnNpb24iIDogIjE2LjAuMTg5MjUuMjAyMTYiLCAiT1MiIDogIldpbmRvd3MiIH0%3D&CID=AD9152B2-4D87-4C34-AB6E-DCB3AC369764&wdLOR=c756D7BF0-42FA-43B9-ABD3-10D465D24C89",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def generate_detailed_failure_summary(self, run_info: Dict[str, Any], 
                                         test_results: Dict[str, Dict[str, TestSuiteResult]], 
                                         run_id: str) -> str:
        """
        Generate detailed failure summary for bug creation and analysis.
        """
        report_lines = []
        
        # Header
        report_lines.extend([
            f"DETAILED FAILURE ANALYSIS - Run {run_id}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Workflow: {run_info.get('name', 'Unknown')}",
            f"Branch: {run_info.get('head_branch', 'dev')}",
            "=" * 80,
            ""
        ])
        
        # Overall statistics
        overall_stats = self._calculate_overall_stats(test_results)
        report_lines.extend([
            f"OVERALL SUMMARY:",
            f"  Total Tests: {overall_stats['total']}",
            f"  Passed: {overall_stats['passed']} ({(overall_stats['passed']/max(overall_stats['total'], 1)*100):.1f}%)",
            f"  Failed: {overall_stats['failed']}",
            f"  Skipped: {overall_stats['skipped']}",
            f"  Status: {'FAILED' if overall_stats['failed'] > 0 else 'PASSED'}",
            "",
            "FAILURES BY MODULE:",
            "-" * 40
        ])
        
        # Detailed failure breakdown
        for artifact_name, suites in test_results.items():
            artifact_failures = []
            
            for suite_name, suite_result in suites.items():
                failed_tests = [t for t in suite_result.tests if t.status in ['failed', 'error']]
                if failed_tests:
                    artifact_failures.extend(failed_tests)
            
            if artifact_failures:
                clean_artifact_name = self._clean_artifact_name(artifact_name)
                report_lines.extend([
                    f"",
                    f"📦 {clean_artifact_name.upper()}: {len(artifact_failures)} failed",
                    "-" * (len(clean_artifact_name) + 20)
                ])
                
                for i, test in enumerate(artifact_failures, 1):
                    clean_test_name = self._clean_test_name_for_jira(test.name)
                    report_lines.append(f"  {i:2d}. {clean_test_name}")
                    
                    # Add error details if available
                    if test.failure_message:
                        error_summary = self._extract_error_summary(test.failure_message)
                        report_lines.append(f"      Error: {error_summary}")
                    
                    # Suggest JIRA ticket format
                    jira_summary = self._suggest_jira_title(test.name, test.failure_message)
                    report_lines.append(f"      Suggested JIRA: {jira_summary}")
                    report_lines.append("")
        
        # Bug creation guidelines
        report_lines.extend([
            "=" * 80,
            "BUG CREATION GUIDELINES:",
            "",
            "1. Check existing JIRA tickets for similar failures",
            "2. Create new tickets for genuine new failures",
            "3. Update existing tickets if this is a regression",
            "4. Use suggested JIRA titles above as starting points",
            "5. Include run ID and error details in ticket description",
            "",
            f"Run Details for JIRA:",
            f"  - Run ID: {run_id}",
            f"  - Date: {datetime.now().strftime('%Y-%m-%d')}",
            f"  - Branch: {run_info.get('head_branch', 'dev')}",
            f"  - Commit: {run_info.get('head_sha', 'Unknown')[:8]}",
        ])
        
        return "\n".join(report_lines)
    
    def generate_email_summary(self, run_info: Dict[str, Any], 
                              test_results: Dict[str, Dict[str, TestSuiteResult]], 
                              run_id: str, branch_name: str = None) -> str:
        """
        Generate email-ready summary in ETN format.
        
        Args:
            run_info: GitHub Actions run information
            test_results: Test results organized by artifact and suite  
            run_id: The run ID
            branch_name: Branch name for the regression runs (extracted from run_info if None)
        """
        # Extract branch name from run_info if not provided
        if not branch_name:
            branch_name = run_info.get('head_branch', 'Dev')  # Default to 'Dev' if not found
        overall_stats = self._calculate_overall_stats(test_results)
        
        # Determine overall status
        if overall_stats['failed'] == 0:
            status_emoji = "✅"
            status_text = "PASSED"
        else:
            status_emoji = "❌"
            status_text = "FAILED"
        
        # Calculate pass rate
        pass_rate = (overall_stats['passed'] / max(overall_stats['total'], 1)) * 100
        
        email_lines = [
            f"Subject: Nightly Regression Status - {datetime.now().strftime('%Y-%m-%d')} - {status_text}",
            "",
            f"Please find latest regression status below.",
            "",
            f"Nightly Regression runs: {branch_name} Branch (Build Repository)",
            "",
            f"{status_emoji} NIGHTLY REGRESSION SUMMARY - {datetime.now().strftime('%Y-%m-%d')}",
            "=" * 60,
            "",
            f"Overall Status: {status_text}",
            f"Pass Rate: {pass_rate:.1f}% ({overall_stats['passed']}/{overall_stats['total']})",
            f"Branch: {run_info.get('head_branch', 'dev')}",
            f"Run ID: {run_id}",
            ""
        ]
        
        # Quick stats by workflow
        workflow_summary = self._generate_workflow_summary(test_results)
        if workflow_summary:
            email_lines.extend([
                "WORKFLOW RESULTS:",
                "-" * 20
            ])
            for workflow, stats in workflow_summary.items():
                status_icon = "✅" if stats['failed'] == 0 else "❌"
                email_lines.append(
                    f"{status_icon} {workflow}: {stats['passed']}/{stats['total']} passed"
                )
            email_lines.append("")
        
        # Failed tests summary (if any)
        if overall_stats['failed'] > 0:
            email_lines.extend([
                f"🚨 FAILED TESTS ({overall_stats['failed']}):",
                "-" * 30
            ])
            
            failure_count = 0
            for artifact_name, suites in test_results.items():
                for suite_name, suite_result in suites.items():
                    failed_tests = [t for t in suite_result.tests if t.status in ['failed', 'error']]
                    for test in failed_tests:
                        if failure_count < 10:  # Limit to first 10 for email
                            clean_name = self._clean_test_name_for_email(test.name)
                            email_lines.append(f"  • {clean_name}")
                        failure_count += 1
            
            if failure_count > 10:
                email_lines.append(f"  ... and {failure_count - 10} more failures")
            
            email_lines.extend([
                "",
                "📋 ACTION REQUIRED:",
                "  • Review detailed failure analysis (attached/linked)",
                "  • Create/update JIRA tickets for genuine failures",
                "  • Check for regressions from recent changes",
            ])
        else:
            email_lines.extend([
                "🎉 ALL TESTS PASSED!",
                "No action required - all systems are green.",
            ])
        
        email_lines.extend([
            "",
            "Quick links:",
            "• PXGreen Bugs - Regression Failed:",
            "  https://eaton-corp.atlassian.net/wiki/spaces/LTK/pages/19376705/PXGreen+Bugs+-+Regression_Failed",
            "• Nightly Regression Test Status Spreadsheet:",
            "  https://eaton.sharepoint.com/:x:/s/PlatformsandAnalyticsART/EeAJ-vxC2IdPiSyykB9L6ZQBb90daXGwYuDr6CmylosQvg?e=eCR5qB&clickparams=eyAiWC1BcHBOYW1lIiA6ICJNaWNyb3NvZnQgT3V0bG9vayIsICJYLUFwcFZlcnNpb24iIDogIjE2LjAuMTg5MjUuMjAyMTYiLCAiT1MiIDogIldpbmRvd3MiIH0%3D&CID=AD9152B2-4D87-4C34-AB6E-DCB3AC369764&wdLOR=c756D7BF0-42FA-43B9-ABD3-10D465D24C89",
            "",
            f"Detailed reports available in: Run {run_id} artifacts"
        ])
        
        return "\n".join(email_lines)
    
    # Helper methods
    def _process_main_workflows(self, run_info: Dict[str, Any], 
                               test_results: Dict[str, Dict[str, TestSuiteResult]]) -> List[Dict]:
        """Process main workflow results."""
        workflows = []
        
        for artifact_name, suites in test_results.items():
            # Map artifact to workflow name
            workflow_name = self._map_artifact_to_workflow(artifact_name)
            
            # Calculate totals
            total = sum(suite.total for suite in suites.values())
            passed = sum(suite.passed for suite in suites.values())
            failed = sum(suite.failed + suite.errors for suite in suites.values())
            skipped = sum(suite.skipped for suite in suites.values())
            
            # Determine status
            status = "Successful" if failed == 0 else "Failed"
            
            # Extract failures for actions
            failures = []
            for suite_name, suite_result in suites.items():
                failed_tests = [t for t in suite_result.tests if t.status in ['failed', 'error']]
                failures.extend(failed_tests)
            
            workflows.append({
                'name': workflow_name,
                'status': status,
                'total': total,
                'pass': passed,
                'fail': failed,
                'skipped': skipped,
                'failures': failures
            })
        
        return workflows
    
    def _process_ui_workflows(self, run_info: Dict[str, Any], 
                             test_results: Dict[str, Dict[str, TestSuiteResult]]) -> List[Dict]:
        """Process UI workflow results separately."""
        # This would be customized based on how UI tests are identified
        # For now, return empty as UI tests might be in separate artifacts
        return []
    
    def _format_actions(self, failures: List[TestResult]) -> str:
        """Format actions/JIRA links for failures."""
        if not failures:
            return ""
        
        # Group similar failures and suggest JIRA titles
        actions = []
        for failure in failures[:3]:  # Limit to first 3 for space
            jira_title = self._suggest_jira_title(failure.name, failure.failure_message)
            actions.append(f"[LTK-XXXXX] {jira_title}")
        
        if len(failures) > 3:
            actions.append(f"... and {len(failures) - 3} more failures")
        
        return "\n".join(actions)
    
    def _format_ui_comments(self, failures: List[TestResult]) -> str:
        """Format comments for UI test failures."""
        if not failures:
            return "UI tests completed successfully"
        
        return f"UI tests failed - {len(failures)} failures detected"
    
    def _generate_historical_summary(self) -> Dict[str, Any]:
        """Generate historical success/failure data."""
        # This would connect to your historical data source
        # For now, return placeholder data
        return {
            'ytd_success': 63,
            'ytd_failed': 117,
            'ytd_percent': '35.7',
            'last30_success': 9,
            'last30_failed': 21,
            'last30_percent': '29.03'
        }
    
    def _generate_workflow_summary(self, test_results: Dict[str, Dict[str, TestSuiteResult]]) -> Dict[str, Dict]:
        """Generate summary by workflow."""
        workflow_stats = {}
        
        for artifact_name, suites in test_results.items():
            workflow_name = self._clean_artifact_name(artifact_name)
            
            total = sum(suite.total for suite in suites.values())
            passed = sum(suite.passed for suite in suites.values())
            failed = sum(suite.failed + suite.errors for suite in suites.values())
            
            workflow_stats[workflow_name] = {
                'total': total,
                'passed': passed,
                'failed': failed
            }
        
        return workflow_stats
    
    def _map_artifact_to_workflow(self, artifact_name: str) -> str:
        """Map artifact name to workflow name."""
        artifact_lower = artifact_name.lower()
        
        for key, workflow_name in self.workflow_mappings.items():
            if key in artifact_lower:
                return workflow_name
        
        # Default mapping
        return artifact_name.replace('-', ' ').title()
    
    def _suggest_jira_title(self, test_name: str, failure_message: str) -> str:
        """Suggest JIRA ticket title based on test failure."""
        # Extract meaningful parts from test name
        clean_test = self._clean_test_name_for_jira(test_name)
        
        # Extract error type from failure message
        error_type = self._extract_error_type(failure_message)
        
        # Determine device/platform
        platform = self._extract_platform_from_test(test_name)
        
        return f"{error_type}: {clean_test} - {platform}"
    
    def _clean_test_name_for_jira(self, test_name: str) -> str:
        """Clean test name for JIRA ticket titles."""
        # Remove file paths and keep relevant parts
        if '::' in test_name:
            parts = test_name.split('::')
            return parts[-1].replace('test_', '').replace('_', ' ').title()
        
        return test_name.replace('test_', '').replace('_', ' ').title()
    
    def _clean_test_name_for_email(self, test_name: str) -> str:
        """Clean test name for email display."""
        if '::' in test_name:
            parts = test_name.split('::')
            module = parts[0].split('/')[-1] if '/' in parts[0] else parts[0]
            test = parts[-1].replace('test_', '')
            return f"{module}: {test.replace('_', ' ')}"
        
        return test_name.replace('test_', '').replace('_', ' ')
    
    def _extract_error_type(self, failure_message: str) -> str:
        """Extract error type from failure message."""
        if not failure_message:
            return "Test Failure"
        
        message_lower = failure_message.lower()
        
        if 'timeout' in message_lower:
            return "Timeout Error"
        elif 'connection' in message_lower:
            return "Connection Issue"
        elif 'assertion' in message_lower or 'expected' in message_lower:
            return "Assertion Failure"
        elif 'permission' in message_lower or 'unauthorized' in message_lower:
            return "Permission Issue"
        elif 'not found' in message_lower:
            return "Resource Not Found"
        else:
            return "Test Failure"
    
    def _extract_platform_from_test(self, test_name: str) -> str:
        """Extract platform information from test name."""
        name_lower = test_name.lower()
        
        if 'h743' in name_lower:
            return "H743"
        elif 'u575' in name_lower:
            return "U575"
        else:
            return "Generic"
    
    def _extract_error_summary(self, failure_message: str) -> str:
        """Extract concise error summary."""
        if not failure_message:
            return "No error details available"
        
        # Take first meaningful line
        lines = failure_message.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('=') and not line.startswith('-'):
                if len(line) > 100:
                    return line[:97] + "..."
                return line
        
        return "Error details available in full report"
    
    def _clean_artifact_name(self, name: str) -> str:
        """Clean artifact name for display."""
        clean = name.replace('-test-results', '').replace('_results', '')
        clean = clean.replace('artifact_', '').replace('pytest_', '')
        return clean.replace('-', ' ').replace('_', ' ').title()
    
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
"""
Email Report Templates for GitHub Actions Test Results.

This module provides email-friendly report formats commonly used for
nightly test reporting and team communication.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
from artifact_processor import TestSuiteResult, TestResult

logger = logging.getLogger(__name__)


class EmailReportGenerator:
    """Generates email-friendly test reports for team communication."""
    
    def __init__(self, config):
        """Initialize email report generator."""
        self.config = config
    
    def generate_executive_summary(self, run_info: Dict[str, Any], 
                                 test_results: Dict[str, Dict[str, TestSuiteResult]], 
                                 run_id: str) -> str:
        """
        Generate executive summary report suitable for management emails.
        
        Format: Concise, high-level overview with key metrics
        """
        overall_stats = self._calculate_overall_stats(test_results)
        
        # Determine overall status
        if overall_stats['failed'] == 0 and overall_stats['errors'] == 0:
            status_icon = "✅ PASSED"
            status_color = "GREEN"
        else:
            status_icon = "❌ FAILED" 
            status_color = "RED"
        
        # Calculate pass rate
        pass_rate = 0
        if overall_stats['total'] > 0:
            pass_rate = (overall_stats['passed'] / overall_stats['total']) * 100
        
        report_lines = [
            f"=== NIGHTLY TEST REPORT - {datetime.now().strftime('%Y-%m-%d')} ===",
            "",
            f"🎯 OVERALL STATUS: {status_icon}",
            f"📊 PASS RATE: {pass_rate:.1f}% ({overall_stats['passed']}/{overall_stats['total']})",
            f"⚡ WORKFLOW: {run_info.get('name', 'Unknown')}",
            f"🌿 BRANCH: {run_info.get('head_branch', 'main')}",
            f"🔗 RUN ID: {run_id}",
            "",
            "📈 QUICK STATS:",
            f"   • Total Tests: {overall_stats['total']}",
            f"   • Passed: {overall_stats['passed']} ✅",
            f"   • Failed: {overall_stats['failed']} ❌" if overall_stats['failed'] > 0 else "",
            f"   • Skipped: {overall_stats['skipped']} ⏭️" if overall_stats['skipped'] > 0 else "",
            f"   • Errors: {overall_stats['errors']} ⚠️" if overall_stats['errors'] > 0 else "",
        ]
        
        # Filter out empty lines
        report_lines = [line for line in report_lines if line != ""]
        
        if overall_stats['failed'] > 0 or overall_stats['errors'] > 0:
            report_lines.extend([
                "",
                "🚨 ACTION REQUIRED:",
                "   Please review failed tests and create appropriate bug reports.",
                f"   Detailed failure analysis attached below."
            ])
        
        return "\n".join(report_lines)
    
    def generate_team_summary(self, run_info: Dict[str, Any], 
                            test_results: Dict[str, Dict[str, TestSuiteResult]], 
                            run_id: str) -> str:
        """
        Generate team-oriented summary with module breakdown.
        
        Format: Module-by-module breakdown for team leads
        """
        overall_stats = self._calculate_overall_stats(test_results)
        
        report_lines = [
            f"📧 TEAM TEST SUMMARY - {datetime.now().strftime('%B %d, %Y')}",
            "=" * 60,
            "",
            f"Workflow: {run_info.get('name', 'Unknown')}",
            f"Run ID: {run_id}",
            f"Branch: {run_info.get('head_branch', 'main')}",
            f"Commit: {run_info.get('head_sha', 'Unknown')[:8]}",
            f"Date: {run_info.get('created_at', 'Unknown')}",
            "",
            "MODULE BREAKDOWN:",
            "-" * 20
        ]
        
        # Group by test module/suite
        for artifact_name, suites in test_results.items():
            if not suites:
                continue
            
            # Clean up artifact name for display
            clean_name = self._clean_artifact_name(artifact_name)
            report_lines.append(f"\n📦 {clean_name.upper()}:")
            
            for suite_name, suite_result in suites.items():
                status_icon = "✅" if suite_result.failed == 0 and suite_result.errors == 0 else "❌"
                
                report_lines.append(f"  {status_icon} {suite_name}:")
                report_lines.append(f"     Total: {suite_result.total} | "
                                  f"Passed: {suite_result.passed} | "
                                  f"Failed: {suite_result.failed}")
                
                if suite_result.failed > 0:
                    failed_tests = [t for t in suite_result.tests if t.status in ['failed', 'error']]
                    report_lines.append(f"     ⚠️  FAILURES ({len(failed_tests)}):")
                    for i, test in enumerate(failed_tests[:5], 1):  # Limit to first 5
                        clean_test_name = self._clean_test_name(test.name)
                        report_lines.append(f"        {i}. {clean_test_name}")
                    
                    if len(failed_tests) > 5:
                        report_lines.append(f"        ... and {len(failed_tests) - 5} more")
        
        # Overall summary at bottom
        report_lines.extend([
            "",
            "=" * 60,
            "🎯 OVERALL RESULTS:",
            f"   Total Tests: {overall_stats['total']}",
            f"   Success Rate: {(overall_stats['passed']/max(overall_stats['total'], 1)*100):.1f}%",
            f"   Tests Requiring Attention: {overall_stats['failed'] + overall_stats['errors']}"
        ])
        
        if overall_stats['failed'] > 0:
            report_lines.append(f"\n🔧 Next Steps: Review failures and create bug reports as needed.")
        
        return "\n".join(report_lines)
    
    def generate_failure_focused_report(self, run_info: Dict[str, Any], 
                                      test_results: Dict[str, Dict[str, TestSuiteResult]], 
                                      run_id: str) -> str:
        """
        Generate failure-focused report for bug triage.
        
        Format: Detailed failure information for creating bug reports
        """
        all_failures = self._get_all_failures(test_results)
        overall_stats = self._calculate_overall_stats(test_results)
        
        if not any(failures for failures in all_failures.values()):
            return self._generate_success_report(run_info, overall_stats, run_id)
        
        report_lines = [
            f"🐛 FAILURE ANALYSIS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 70,
            "",
            f"Run ID: {run_id}",
            f"Workflow: {run_info.get('name', 'Unknown')}",
            f"Branch: {run_info.get('head_branch', 'main')}",
            f"Total Failures: {overall_stats['failed'] + overall_stats['errors']}",
            "",
            "🔍 FAILURES BY MODULE:",
            "=" * 25
        ]
        
        for suite_name, failures in all_failures.items():
            if not failures:
                continue
            
            clean_suite = self._clean_artifact_name(suite_name)
            report_lines.extend([
                f"\n📋 {clean_suite}: {len(failures)} failed",
                "-" * (len(clean_suite) + 20)
            ])
            
            for i, test in enumerate(failures, 1):
                clean_test_name = self._clean_test_name(test.name)
                report_lines.append(f"{i:2d}. {clean_test_name}")
                
                # Add error details if available
                error_msg = test.failure_message or test.error_message
                if error_msg:
                    # Clean and truncate error message
                    clean_error = self._clean_error_message(error_msg)
                    report_lines.append(f"    💬 {clean_error}")
                
                report_lines.append("")  # Empty line between tests
        
        # Add summary for bug creation
        report_lines.extend([
            "=" * 70,
            "📝 FOR BUG CREATION:",
            "  • Review each failure above",
            "  • Check if similar issues exist in bug tracker", 
            "  • Create new bugs for genuine failures",
            "  • Update existing bugs for regressions",
            "",
            f"📊 Quick Stats: {overall_stats['passed']} passed, "
            f"{overall_stats['failed']} failed, {overall_stats['skipped']} skipped"
        ])
        
        return "\n".join(report_lines)
    
    def generate_slack_summary(self, run_info: Dict[str, Any], 
                             test_results: Dict[str, Dict[str, TestSuiteResult]], 
                             run_id: str) -> str:
        """
        Generate Slack-friendly summary (short, with emojis).
        """
        overall_stats = self._calculate_overall_stats(test_results)
        
        if overall_stats['failed'] == 0 and overall_stats['errors'] == 0:
            status = "✅ ALL TESTS PASSED! 🎉"
        else:
            status = f"❌ {overall_stats['failed']} tests failed"
        
        pass_rate = (overall_stats['passed'] / max(overall_stats['total'], 1)) * 100
        
        return f"""🤖 *Nightly Test Results* - {datetime.now().strftime('%Y-%m-%d')}
        
{status}

📊 *Summary:* {overall_stats['passed']}/{overall_stats['total']} passed ({pass_rate:.1f}%)
🌿 *Branch:* {run_info.get('head_branch', 'main')}
🔗 *Run ID:* {run_id}

{f'🐛 *Failed Tests:* {overall_stats["failed"]}' if overall_stats['failed'] > 0 else ''}
{f'⏭️  *Skipped:* {overall_stats["skipped"]}' if overall_stats['skipped'] > 0 else ''}
"""
    
    def _generate_success_report(self, run_info: Dict[str, Any], 
                               overall_stats: Dict[str, int], 
                               run_id: str) -> str:
        """Generate success report when no failures."""
        return f"""🎉 SUCCESS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
✅ ALL TESTS PASSED! 

📊 Results: {overall_stats['total']} tests executed successfully
🌿 Branch: {run_info.get('head_branch', 'main')}  
🔗 Run ID: {run_id}
⏱️  Date: {run_info.get('created_at', 'Unknown')}

🚀 No action required - all systems are green!
"""
    
    # Helper methods
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
                    # Create readable key
                    key = self._clean_artifact_name(f"{artifact_name}::{suite_name}")
                    all_failures[key] = failures
        
        return all_failures
    
    def _clean_artifact_name(self, name: str) -> str:
        """Clean artifact name for display."""
        # Remove common prefixes/suffixes
        clean = name.replace('-test-results', '').replace('_results', '')
        clean = clean.replace('artifact_', '').replace('pytest_', '')
        
        # Handle compound names
        if '::' in clean:
            parts = clean.split('::')
            return f"{parts[0].title()}-{parts[1].title()}"
        
        return clean.replace('-', ' ').replace('_', ' ').title()
    
    def _clean_test_name(self, name: str) -> str:
        """Clean test name for readability."""
        # Remove file paths and keep just the test name
        if '::' in name:
            parts = name.split('::')
            return parts[-1]  # Last part is usually the test name
        
        # Remove test_ prefix if present
        if name.startswith('test_'):
            name = name[5:]
        
        # Replace underscores with spaces
        return name.replace('_', ' ').title()
    
    def _clean_error_message(self, message: str) -> str:
        """Clean and truncate error message."""
        if not message:
            return "No error details available"
        
        # Take first line or first 100 characters
        lines = message.strip().split('\n')
        first_line = lines[0].strip()
        
        if len(first_line) > 100:
            return first_line[:97] + "..."
        
        return first_line
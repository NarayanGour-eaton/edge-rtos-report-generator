#!/usr/bin/env python3
"""
Tabular Report Generator for ETN Regression Reports

This module generates tabular format reports with columns:
Workflow Name | Plan result | Total | Pass | Fail | Skipped | GitHub Actions
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class TabularReportGenerator:
    """Generate tabular reports for ETN regression analysis."""
    
    def __init__(self, config):
        self.config = config
        
    def _get_github_actions_url(self, run_id: str) -> str:
        """Generate GitHub Actions run URL."""
        if not run_id or run_id == '':
            return "No run ID available"
        return f"https://github.com/{self.config.repo_owner}/{self.config.repo_name}/actions/runs/{run_id}"
        
    def generate_tabular_regression_report(self, workflow_summaries: List[Dict], 
                                         date_str: str = None, branch_name: str = None) -> str:
        """
        Generate a tabular regression report from workflow summaries.
        
        Args:
            workflow_summaries: List of workflow summary dictionaries
            date_str: Date string for the report
            branch_name: Branch name for the regression runs (e.g., 'Dev', 'Main')
            
        Returns:
            Formatted tabular report string
        """
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        if not branch_name:
            branch_name = "Dev"  # Default fallback
            
        lines = []
        
        # Header
        lines.append("=" * 120)
        lines.append(f"BL Edge (RTOS) regression test status - {date_str.replace('-', '/')}")
        lines.append("=" * 120)
        lines.append("")
        
        # Regression status header
        lines.append("Please find latest regression status below.")
        lines.append("")
        lines.append(f"Nightly Regression runs: {branch_name} Branch (Build Repository)")
        lines.append("")
        
        # Create the table
        table_lines = self._create_summary_table(workflow_summaries)
        lines.extend(table_lines)
        
        lines.append("")
        lines.append("=" * 120)
        lines.append("")
        
        # Summary statistics
        total_workflows = len(workflow_summaries)
        passed_workflows = sum(1 for w in workflow_summaries if w['status'] == 'PASSED')
        failed_workflows = total_workflows - passed_workflows
        
        # Calculate overall test statistics
        overall_stats = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
        for workflow in workflow_summaries:
            stats = workflow['stats']
            overall_stats['total'] += stats['total']
            overall_stats['passed'] += stats['passed']
            overall_stats['failed'] += stats['failed']
            overall_stats['skipped'] += stats['skipped']
        
        lines.append("📊 SUMMARY STATISTICS:")
        lines.append(f"   Total Workflows: {total_workflows}")
        lines.append(f"   Passed: {passed_workflows}")
        lines.append(f"   Failed: {failed_workflows}")
        lines.append("")
        
        lines.append("📈 OVERALL TEST COUNTS:")
        lines.append(f"   Total Tests: {overall_stats['total']}")
        lines.append(f"   Passed: {overall_stats['passed']}")
        lines.append(f"   Failed: {overall_stats['failed']}")
        lines.append(f"   Skipped: {overall_stats['skipped']}")
        lines.append("")
        
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("ETN Tabular Report Generator")
        
        # Quick Links Section
        lines.append("")
        lines.append("Quick Links:")
        lines.append("PXGreen Bugs - Regression Failed:")
        lines.append("https://eaton-corp.atlassian.net/wiki/spaces/LTK/pages/19376705/PXGreen+Bugs+-+Regression_Failed")
        lines.append("")
        lines.append("Nightly Regression Test Status Spreadsheet:")
        lines.append("https://eaton.sharepoint.com/:x:/s/PlatformsandAnalyticsART/EeAJ-vxC2IdPiSyykB9L6ZQBb90daXGwYuDr6CmylosQvg?e=eCR5qB&clickparams=eyAiWC1BcHBOYW1lIiA6ICJNaWNyb3NvZnQgT3V0bG9vayIsICJYLUFwcFZlcnNpb24iIDogIjE2LjAuMTg5MjUuMjAyMTYiLCAiT1MiIDogIldpbmRvd3MiIH0%3D&CID=AD9152B2-4D87-4C34-AB6E-DCB3AC369764&wdLOR=c756D7BF0-42FA-43B9-ABD3-10D465D24C89")
        lines.append("")
        
        return "\n".join(lines)
        
    def _create_summary_table(self, workflow_summaries: List[Dict]) -> List[str]:
        """Create the main summary table with proper column formatting."""
        lines = []
        
        # Table headers
        headers = ["Workflow Name", "Plan result", "Total", "Pass", "Fail", "Skipped"]
        
        # Calculate column widths for better formatting
        col_widths = [
            max(45, max(len(self._format_workflow_name(w)) for w in workflow_summaries) if workflow_summaries else 20),  # Workflow Name
            12,  # Plan result
            8,   # Total
            8,   # Pass
            8,   # Fail
            8    # Skipped
        ]
        
        # Create separator line
        separator = "+" + "+".join("-" * (width + 2) for width in col_widths) + "+"
        
        # Header row
        lines.append(separator)
        header_row = "|"
        for i, header in enumerate(headers):
            header_row += f" {header:<{col_widths[i]}} |"
        lines.append(header_row)
        lines.append(separator)
        
        # Data rows
        for workflow in workflow_summaries:
            # Extract workflow name and format it
            formatted_name = self._format_workflow_name(workflow)
            
            # Determine plan result
            plan_result = "Failed" if workflow['status'] == 'FAILED' else "Passed"
            
            # Get statistics
            stats = workflow['stats']
            total = stats['total']
            passed = stats['passed'] 
            failed = stats['failed']
            skipped = stats['skipped']
            
            # Create the main row
            data_row = "|"
            values = [formatted_name, plan_result, str(total), str(passed), str(failed), str(skipped)]
            for i, value in enumerate(values):
                data_row += f" {value:<{col_widths[i]}} |"
            lines.append(data_row)
            
            # Add GitHub URL as a sub-row
            github_url = self._get_github_actions_url(workflow.get('run_id', ''))
            github_row = "|"
            github_values = [f"  ➤ {github_url}", "", "", "", "", ""]
            for i, value in enumerate(github_values):
                github_row += f" {value:<{col_widths[i]}} |"
            lines.append(github_row)
            lines.append(separator)
        
        return lines
        
    def _format_workflow_name(self, workflow: Dict[str, Any]) -> str:
        """Format workflow name for display."""
        workflow_name = workflow.get('name', 'Unknown')
        board_type = workflow.get('board_type', '')
        description = workflow.get('description', '')
        
        if board_type and description:
            if board_type in description:
                # If board type is already in description, just use description
                formatted_name = f"{board_type} ({description})"
            else:
                # If board type is not in description, combine them
                if "Development Board Tests" in description or "Board Test" in description:
                    formatted_name = f"{board_type} ({description})"
                else:
                    formatted_name = f"{board_type} ({workflow['description']})"
        elif board_type:
            formatted_name = f"{board_type}"
        else:
            formatted_name = workflow_name
        
        return formatted_name
        
    def generate_csv_report(self, workflow_summaries: List[Dict], 
                           date_str: str = None, branch_name: str = None) -> str:
        """
        Generate CSV format report for easy import into spreadsheets.
        
        Args:
            workflow_summaries: List of workflow summary dictionaries
            date_str: Date string for the report
            branch_name: Branch name for the regression runs
            
        Returns:
            CSV formatted string
        """
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        if not branch_name:
            branch_name = "Dev"  # Default fallback
            
        lines = []
        
        # CSV Header
        lines.append("Workflow Name,Plan result,Total,Pass,Fail,Skipped,Board Type,Run ID,Description,GitHub Actions URL")
        
        # Data rows
        for workflow in workflow_summaries:
            formatted_name = self._format_workflow_name(workflow)
            
            plan_result = "Failed" if workflow['status'] == 'FAILED' else "Passed"
            stats = workflow['stats']
            description = workflow.get('description', '')
            
            csv_row = [
                formatted_name,
                plan_result,
                str(stats['total']),
                str(stats['passed']),
                str(stats['failed']), 
                str(stats['skipped']),
                workflow.get('board_type', ''),
                workflow.get('run_id', ''),
                description,
                self._get_github_actions_url(workflow.get('run_id', ''))
            ]
            
            lines.append(",".join(csv_row))
        
        # Add quick links as comments in CSV
        lines.append("")
        lines.append("# Quick Links:")
        lines.append("# PXGreen Bugs - Regression Failed: https://eaton-corp.atlassian.net/wiki/spaces/LTK/pages/19376705/PXGreen+Bugs+-+Regression_Failed")
        lines.append("# Nightly Regression Test Status Spreadsheet: https://eaton.sharepoint.com/:x:/s/PlatformsandAnalyticsART/EeAJ-vxC2IdPiSyykB9L6ZQBb90daXGwYuDr6CmylosQvg?e=eCR5qB&clickparams=eyAiWC1BcHBOYW1lIiA6ICJNaWNyb3NvZnQgT3V0bG9vayIsICJYLUFwcFZlcnNpb24iIDogIjE2LjAuMTg5MjUuMjAyMTYiLCAiT1MiIDogIldpbmRvd3MiIH0%3D&CID=AD9152B2-4D87-4C34-AB6E-DCB3AC369764&wdLOR=c756D7BF0-42FA-43B9-ABD3-10D465D24C89")
        
        return "\n".join(lines)
        
    def generate_html_table(self, workflow_summaries: List[Dict], 
                           date_str: str = None, branch_name: str = None) -> str:
        """
        Generate HTML table format report.
        
        Args:
            workflow_summaries: List of workflow summary dictionaries  
            date_str: Date string for the report
            branch_name: Branch name for the regression runs
            
        Returns:
            HTML formatted string
        """
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        if not branch_name:
            branch_name = "Dev"  # Default fallback
            
        html = []
        
        # HTML structure
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append(f"<title>BL Edge (RTOS) regression test status - {date_str.replace('-', '/')}</title>")
        html.append("<style>")
        html.append("""
            table { border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; font-weight: bold; }
            .passed { background-color: #d4edda; color: #155724; }
            .failed { background-color: #f8d7da; color: #721c24; }
            .center { text-align: center; }
            h1 { color: #333; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        """)
        html.append("</style>")
        html.append("</head>")
        html.append("<body>")
        
        html.append(f"<h1>BL Edge (RTOS) regression test status - {date_str.replace('-', '/')}</h1>")
        
        # Regression status header
        html.append("<p>Please find latest regression status below.</p>")
        html.append(f"<p><strong>Nightly Regression runs: {branch_name} Branch (Build Repository)</strong></p>")
        html.append("<br>")
        
        # Table
        html.append("<table>")
        
        # Table headers
        html.append("<tr>")
        html.append("<th>Workflow Name</th>")
        html.append("<th>Plan result</th>")
        html.append("<th>Total</th>")
        html.append("<th>Pass</th>")
        html.append("<th>Fail</th>")
        html.append("<th>Skipped</th>")
        html.append("</tr>")
        
        # Table data
        for workflow in workflow_summaries:
            formatted_name = self._format_workflow_name(workflow)
            
            github_url = self._get_github_actions_url(workflow.get('run_id', ''))
            
            status_class = "passed" if workflow['status'] == 'PASSED' else "failed"
            plan_result = "Passed" if workflow['status'] == 'PASSED' else "Failed"
            stats = workflow['stats']
            
            html.append("<tr>")
            html.append(f"<td><a href=\"{github_url}\" target=\"_blank\">{formatted_name}</a></td>")
            html.append(f"<td class=\"{status_class}\">{plan_result}</td>")
            html.append(f"<td class=\"center\">{stats['total']}</td>")
            html.append(f"<td class=\"passed center\">{stats['passed']}</td>")
            html.append(f"<td class=\"failed center\">{stats['failed'] if stats['failed'] > 0 else ''}</td>")
            html.append(f"<td class=\"center\">{stats['skipped'] if stats['skipped'] > 0 else ''}</td>")
            html.append("</tr>")
            
        html.append("</table>")
        
        # Summary
        total_workflows = len(workflow_summaries)
        passed_workflows = sum(1 for w in workflow_summaries if w['status'] == 'PASSED')
        failed_workflows = total_workflows - passed_workflows
        
        html.append("<br>")
        html.append(f"<p><strong>Summary:</strong> {passed_workflows}/{total_workflows} workflows passed</p>")
        
        # Quick Links Section
        html.append("<br>")
        html.append("<h3>Quick Links</h3>")
        html.append('<ul>')
        html.append('<li><a href="https://eaton-corp.atlassian.net/wiki/spaces/LTK/pages/19376705/PXGreen+Bugs+-+Regression_Failed" target="_blank">PXGreen Bugs - Regression Failed</a></li>')
        html.append('<li><a href="https://eaton.sharepoint.com/:x:/s/PlatformsandAnalyticsART/EeAJ-vxC2IdPiSyykB9L6ZQBb90daXGwYuDr6CmylosQvg?e=eCR5qB&clickparams=eyAiWC1BcHBOYW1lIiA6ICJNaWNyb3NvZnQgT3V0bG9vayIsICJYLUFwcFZlcnNpb24iIDogIjE2LjAuMTg5MjUuMjAyMTYiLCAiT1MiIDogIldpbmRvd3MiIH0%3D&CID=AD9152B2-4D87-4C34-AB6E-DCB3AC369764&wdLOR=c756D7BF0-42FA-43B9-ABD3-10D465D24C89" target="_blank">Nightly Regression Test Status Spreadsheet</a></li>')
        html.append('</ul>')
        
        # Generated timestamp moved to the end
        html.append("<br>")
        html.append(f"<p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>")
        
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)


def main():
    """Example usage of the TabularReportGenerator with GitHub Actions links."""
    # Sample workflow data matching the user's example
    sample_workflows = [
        {
            'name': 'BFT_U575zi_q_dev',
            'board_type': 'U575',
            'status': 'PASSED',
            'stats': {'total': 150, 'passed': 148, 'failed': 2, 'skipped': 0},
            'run_id': '17811893255',
            'description': 'STM32U575 Development Board Tests',
            'plan_result': 'PASS'
        },
        {
            'name': 'BFT_h743zi_dev',
            'board_type': 'H743', 
            'status': 'FAILED',
            'stats': {'total': 120, 'passed': 112, 'failed': 6, 'skipped': 2},
            'run_id': '17811893156',
            'description': 'STM32H743 Development Board Tests',
            'plan_result': 'FAIL'
        }
    ]
    
    # Create a dummy config object for testing
    class DummyConfig:
        def __init__(self):
            self.repo_owner = "etn-ccis"
            self.repo_name = "edge-rtos-github-builds"
    
    config = DummyConfig()
    generator = TabularReportGenerator(config)
    
    print("🔗 TESTING GITHUB ACTIONS LINKS IN TABULAR REPORTS")
    print("=" * 55)
    print()
    
    # Test text report
    print("📊 TEXT REPORT WITH GITHUB LINKS:")
    print("-" * 35)
    text_report = generator.generate_tabular_regression_report(sample_workflows, "2025-09-21", "main")
    print(text_report)


if __name__ == "__main__":
    main()
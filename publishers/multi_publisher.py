#!/usr/bin/env python3
"""
Multi-Workflow Regression Report Publisher

This script processes multiple workflow runs from a configuration file
to generate comprehensive regression reports covering all board types
and test suites in a single unified report.

Usage:
    python multi_publisher.py
    python multi_publisher.py --config custom_runs.json
    python multi_publisher.py --interactive
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse
from datetime import datetime
import getpass

# Add parent directory paths to find modules
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "generators"))
sys.path.insert(0, str(Path(__file__).parent.parent / "config"))

from github_api_client import GitHubAPIClient
from artifact_processor import ArtifactProcessor
from regression_report_generator import RegressionReportGenerator
from tabular_report_generator import TabularReportGenerator
from performance_report_generator import PerformanceReportGenerator
from config import Config


class MultiWorkflowProcessor:
    """Process multiple workflow runs for comprehensive reporting."""
    
    def __init__(self, config):
        self.config = config
        self.github_client = GitHubAPIClient(config)
        self.artifact_processor = ArtifactProcessor(config)
        self.regression_generator = RegressionReportGenerator(config)
        self.tabular_generator = TabularReportGenerator(config)
        self.performance_generator = PerformanceReportGenerator()
        
    def load_workflow_config(self, config_file):
        """Load workflow run configuration from JSON file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {config_file}")
            print("💡 Create config.json with your run IDs")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {config_file}: {e}")
            return None
    
    def setup_github_token(self, workflow_config, interactive_mode=False, command_line_token=None, skip_prompt=False):
        """Setup GitHub token from config, environment, or user input."""
        github_token = None
        
        # 1. Try command line argument first
        if command_line_token:
            github_token = command_line_token.strip()
            print("✅ Using GitHub token from command line argument")
        
        # 2. Try to get from workflow config
        if not github_token and workflow_config and 'settings' in workflow_config:
            github_token = workflow_config['settings'].get('github_token', '').strip()
            if github_token:
                print("✅ Using GitHub token from workflow configuration")
        
        # 3. Try to get from environment variable
        if not github_token:
            github_token = os.environ.get('GITHUB_TOKEN', '').strip()
            if github_token:
                print("✅ Using GitHub token from GITHUB_TOKEN environment variable")
        
        # 4. Try to get from main config
        if not github_token and hasattr(self.config, 'github_token') and self.config.github_token:
            github_token = self.config.github_token
            print("✅ Using GitHub token from main configuration")
        
        # 5. If still missing and in interactive mode, ask user
        if not github_token and interactive_mode and not skip_prompt:
            print("\n🔐 GitHub Token Configuration")
            print("-" * 35)
            print("A GitHub token is required to access GitHub Actions API.")
            print("You can:")
            print("1. Set GITHUB_TOKEN environment variable")
            print("2. Add 'github_token' to config.json settings")
            print("3. Use --github-token command line argument")
            print("4. Enter it now (will not be saved)")
            print()
            print("To create a token: https://github.com/settings/tokens")
            print("Required permissions: 'repo' or 'actions:read'")
            print()
            
            # Use getpass to hide token input
            try:
                github_token = getpass.getpass("Enter GitHub token (hidden input): ").strip()
                if github_token:
                    print("✅ GitHub token entered successfully")
            except (KeyboardInterrupt, EOFError):
                print("\n⚠️  Token input cancelled")
            
            if not github_token:
                print("⚠️  No token provided. API rate limits will be very low.")
                print("   You may encounter rate limiting issues.")
        
        # 6. If still missing, show warning but continue
        if not github_token:
            print("\n⚠️  WARNING: No GitHub token configured!")
            print("   - API rate limits will be very low (60 requests/hour)")
            print("   - You may encounter authentication errors")
            print("   - Consider setting GITHUB_TOKEN environment variable")
            print("   - Or add 'github_token' to workflow_runs.json settings")
            print("   - Or use --github-token command line argument")
            
            # Ask if user wants to continue
            if interactive_mode and not skip_prompt:
                continue_choice = input("\nContinue without token? (y/N): ").strip().lower()
                if continue_choice != 'y':
                    return None
        else:
            # Mask token for display (show first 4 and last 4 characters)
            if len(github_token) > 8:
                masked_token = github_token[:4] + "*" * (len(github_token) - 8) + github_token[-4:]
            else:
                masked_token = "****"
            print(f"🔐 GitHub token configured: {masked_token}")
        
        # Update config with token
        if github_token:
            self.config.github_token = github_token
            # Re-initialize GitHub client with token
            self.github_client = GitHubAPIClient(self.config)
        
        return github_token
            
    def validate_workflow_config(self, workflow_config):
        """Validate and filter workflow configuration."""
        if not workflow_config or 'workflows' not in workflow_config:
            print("❌ Invalid configuration: missing 'workflows' section")
            return None
            
        valid_workflows = {}
        skipped_workflows = []
        invalid_workflows = []
        
        for name, config in workflow_config['workflows'].items():
            run_id = config.get('run_id', '').strip()
            if run_id and run_id.isdigit():
                valid_workflows[name] = {
                    'run_id': run_id,
                    'description': config.get('description', name),
                    'board_type': config.get('board_type', 'Unknown')
                }
            elif run_id:
                invalid_workflows.append((name, run_id))
                print(f"⚠️  Invalid run ID for {name}: '{run_id}' (must be numeric)")
            else:
                skipped_workflows.append(name)
                print(f"⏭️  Skipping {name}: run ID is missing or empty")
        
        # Summary of validation results
        if skipped_workflows or invalid_workflows:
            print(f"\n📋 Workflow Validation Summary:")
            print(f"   ✅ Valid workflows: {len(valid_workflows)}")
            if skipped_workflows:
                print(f"   ⏭️  Skipped workflows (missing run ID): {len(skipped_workflows)}")
                for name in skipped_workflows:
                    print(f"      - {name}")
            if invalid_workflows:
                print(f"   ⚠️  Invalid workflows (bad run ID): {len(invalid_workflows)}")
                for name, run_id in invalid_workflows:
                    print(f"      - {name}: '{run_id}'")
            print()
                
        return valid_workflows
        
    def generate_performance_reports(self, workflow_summaries: List[Dict[str, Any]]) -> List[str]:
        """Generate HTML performance reports from CSV files."""
        performance_reports = []
        
        print("\n🔬 Generating Performance Reports...")
        print("=" * 50)
        
        # Look for dynamic_performance_data.csv files in all workflow directories
        reports_dir = Path("nightly_reports")
        csv_files = list(reports_dir.rglob("dynamic_performance_data.csv"))
        
        if not csv_files:
            print("ℹ️  No performance CSV files found")
            return performance_reports
            
        print(f"Found {len(csv_files)} performance CSV files")
        
        for csv_file in csv_files:
            try:
                print(f"📊 Processing: {csv_file}")
                output_file = self.performance_generator.generate_html_report(str(csv_file))
                performance_reports.append(output_file)
                print(f"✅ Generated: {Path(output_file).name}")
            except Exception as e:
                print(f"❌ Error processing {csv_file}: {e}")
                
        print(f"\n🎯 Generated {len(performance_reports)} performance reports")
        return performance_reports
        
    def process_workflow(self, workflow_name, workflow_config, output_dir):
        """Process a single workflow run."""
        run_id = workflow_config['run_id']
        print(f"\n🔄 Processing {workflow_name} (Run ID: {run_id})")
        print(f"   📝 {workflow_config['description']}")
        print(f"   🎯 Board Type: {workflow_config['board_type']}")
        
        try:
            # Fetch workflow data
            run_info = self.github_client.get_run_info(run_id)
            artifacts = self.github_client.get_run_artifacts(run_id)
            
            if not artifacts:
                print(f"⚠️  No artifacts found for {workflow_name}")
                return None
                
            print(f"   📦 Processing {len(artifacts)} artifacts...")
            
            # Process artifacts
            workflow_results = {}
            for artifact in artifacts:
                # Only process artifacts that start with "PyTest test_report="
                if not artifact['name'].startswith("PyTest test_report="):
                    print(f"     ⏭️  Skipping {artifact['name']} (not PyTest test_report)")
                    continue
                    
                print(f"     🔍 Processing PyTest artifact: {artifact['name']}")
                artifact_data = self.github_client.download_artifact(artifact['id'])
                extracted_files = self.artifact_processor.extract_artifact(
                    artifact_data, artifact['name'], output_dir / workflow_name
                )
                
                print(f"     📁 Extracted {len(extracted_files)} files from {artifact['name']}")
                if extracted_files:
                    print(f"     📄 Sample files: {[f.name for f in extracted_files[:3]]}")
                
                test_results = self.artifact_processor.process_test_files(extracted_files)
                if test_results:
                    workflow_results[artifact['name']] = test_results
                    print(f"     ✅ Found {len(test_results)} test suites with results")
                    for suite_name, suite_result in test_results.items():
                        print(f"        📊 {suite_name}: {suite_result.passed}P/{suite_result.failed}F/{suite_result.skipped}S")
                else:
                    print(f"     ⚠️  No test results found in extracted files")
                    # Debug: show what files were extracted
                    for file_path in extracted_files[:5]:  # Show first 5 files
                        print(f"        📄 {file_path.name} ({file_path.suffix})")
                    
            if workflow_results:
                print(f"   ✅ Successfully processed {len(workflow_results)} test artifacts")
                return {
                    'run_info': run_info,
                    'test_results': workflow_results,
                    'workflow_config': workflow_config
                }
            else:
                print(f"   ⚠️  No test results found for {workflow_name}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error processing {workflow_name}: {e}")
            return None
            
    def generate_unified_report(self, all_workflow_data, workflow_config, output_dir):
        """Generate unified regression report from all workflows."""
        print(f"\n📊 Generating unified regression report...")
        
        # Combine all test results
        combined_results = {}
        workflow_summaries = []
        
        for workflow_name, data in all_workflow_data.items():
            if data:
                # Add workflow prefix to test results
                for artifact_name, test_results in data['test_results'].items():
                    combined_key = f"{workflow_name}::{artifact_name}"
                    combined_results[combined_key] = test_results
                    
                # Create workflow summary
                workflow_stats = self.regression_generator._calculate_overall_stats(data['test_results'])
                workflow_summaries.append({
                    'name': workflow_name,
                    'description': data['workflow_config']['description'],
                    'board_type': data['workflow_config']['board_type'],
                    'run_id': data['workflow_config']['run_id'],
                    'stats': workflow_stats,
                    'status': 'PASSED' if workflow_stats['failed'] == 0 else 'FAILED'
                })
        
        if not combined_results:
            print("❌ No test results to generate report")
            return None
            
        # Use first workflow's run_info as template, but create unified version
        sample_run_info = next(iter(all_workflow_data.values()))['run_info']
        unified_run_info = sample_run_info.copy()
        unified_run_info['name'] = 'Multi-Workflow Nightly Regression'
        
        # Create unified run ID for reporting
        run_ids = [data['workflow_config']['run_id'] for data in all_workflow_data.values() if data]
        unified_run_id = f"multi_{'-'.join(run_ids)}"
        
        # Generate regression reports
        date_str = workflow_config.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Extract branch name from the run data (use from first workflow's run_info)
        branch_name = unified_run_info.get('head_branch', 'Dev')
        print(f"   🌿 Using branch name: {branch_name}")
        
        # 1. Multi-workflow regression status
        regression_status = self.generate_multi_workflow_regression_status(
            unified_run_info, combined_results, workflow_summaries, date_str, branch_name
        )
        
        # 2. Email summary
        email_summary = self.generate_multi_workflow_email_summary(
            unified_run_info, workflow_summaries, date_str, branch_name
        )
        
        # 3. JIRA analysis
        jira_analysis = self.regression_generator.generate_detailed_failure_summary(
            unified_run_info, combined_results, unified_run_id
        )
        
        # 4. Tabular reports (new format requested by user)
        tabular_report = self.tabular_generator.generate_tabular_regression_report(
            workflow_summaries, date_str, branch_name
        )
        csv_report = self.tabular_generator.generate_csv_report(
            workflow_summaries, date_str, branch_name
        )
        html_table_report = self.tabular_generator.generate_html_table(
            workflow_summaries, date_str, branch_name
        )
        
        # Save reports
        reports = {
            'regression_status': (regression_status, "📊 Multi-Workflow Regression Status (ETN Format)"),
            'email_summary': (email_summary, "📧 Email Distribution Summary"),
            'jira_analysis': (jira_analysis, "🐛 JIRA Bug Creation Analysis"),
            'tabular_report': (tabular_report, "📋 Tabular Regression Report"),
            'csv_report': (csv_report, "📊 CSV Export for Spreadsheets"),
            'html_table': (html_table_report, "🌐 HTML Table Report")
        }
        
        saved_files = []
        for report_type, (content, title) in reports.items():
            if report_type == 'csv_report':
                filename = output_dir / f"multi_workflow_{report_type}_{date_str}.csv"
            elif report_type == 'html_table':
                filename = output_dir / f"multi_workflow_{report_type}_{date_str}.html"
            else:
                filename = output_dir / f"multi_workflow_{report_type}_{date_str}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            saved_files.append((filename, title))
            
        return saved_files, email_summary, workflow_summaries
        
    def generate_multi_workflow_regression_status(self, run_info, combined_results, workflow_summaries, date_str, branch_name):
        """Generate regression status for multiple workflows."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"NIGHTLY REGRESSION STATUS - {date_str}")
        lines.append("MULTI-WORKFLOW COMPREHENSIVE REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Overall status summary
        total_workflows = len(workflow_summaries)
        passed_workflows = sum(1 for w in workflow_summaries if w['status'] == 'PASSED')
        failed_workflows = total_workflows - passed_workflows
        
        lines.append(f"📊 WORKFLOW SUMMARY:")
        lines.append(f"   Total Workflows: {total_workflows}")
        lines.append(f"   Passed: {passed_workflows}")
        lines.append(f"   Failed: {failed_workflows}")
        lines.append("")
        
        # Per-workflow breakdown
        lines.append("📋 WORKFLOW DETAILS:")
        lines.append("-" * 80)
        lines.append(f"{'Workflow Name':<30} {'Board':<10} {'Status':<8} {'Pass':<6} {'Fail':<6} {'Skip':<6} {'Run ID'}")
        lines.append("-" * 80)
        
        for workflow in workflow_summaries:
            lines.append(f"{workflow['name']:<30} "
                        f"{workflow['board_type']:<10} "
                        f"{workflow['status']:<8} "
                        f"{workflow['stats']['passed']:<6} "
                        f"{workflow['stats']['failed']:<6} "
                        f"{workflow['stats']['skipped']:<6} "
                        f"{workflow['run_id']}")
        
        lines.append("-" * 80)
        lines.append("")
        
        # Failed workflows details
        failed_workflows_list = [w for w in workflow_summaries if w['status'] == 'FAILED']
        if failed_workflows_list:
            lines.append("🚨 FAILED WORKFLOWS - REQUIRE ATTENTION:")
            lines.append("=" * 50)
            for workflow in failed_workflows_list:
                lines.append(f"❌ {workflow['name']} ({workflow['board_type']})")
                lines.append(f"   Description: {workflow['description']}")
                lines.append(f"   Failures: {workflow['stats']['failed']}")
                lines.append(f"   Run ID: {workflow['run_id']}")
                lines.append("")
        else:
            lines.append("🎉 ALL WORKFLOWS PASSED - EXCELLENT WORK!")
            lines.append("")
        
        # Action items
        lines.append("📋 ACTION ITEMS:")
        lines.append("=" * 20)
        if failed_workflows_list:
            lines.append("1. Review individual workflow failures in JIRA analysis report")
            lines.append("2. Create/update bug tickets for new regressions")
            lines.append("3. Notify relevant teams of board-specific failures")
            lines.append("4. Check for common failure patterns across workflows")
            lines.append("5. Update regression tracking spreadsheet")
        else:
            lines.append("✅ No action required - all workflows passed")
        lines.append("")
        
        # Overall statistics
        overall_stats = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
        for workflow in workflow_summaries:
            for key in overall_stats:
                overall_stats[key] += workflow['stats'][key]
        
        lines.append("📈 OVERALL TEST STATISTICS:")
        lines.append("=" * 30)
        lines.append(f"Total Tests: {overall_stats['total']}")
        lines.append(f"Passed: {overall_stats['passed']} ({overall_stats['passed']/overall_stats['total']*100:.1f}%)")
        lines.append(f"Failed: {overall_stats['failed']} ({overall_stats['failed']/overall_stats['total']*100:.1f}%)")
        lines.append(f"Skipped: {overall_stats['skipped']} ({overall_stats['skipped']/overall_stats['total']*100:.1f}%)")
        lines.append("")
        
        lines.append("Generated by Multi-Workflow Regression Publisher")
        lines.append(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)
        
    def generate_multi_workflow_email_summary(self, run_info, workflow_summaries, date_str, branch_name):
        """Generate email-ready summary for multiple workflows."""
        lines = []
        
        # Email subject suggestion
        overall_status = "PASSED" if all(w['status'] == 'PASSED' for w in workflow_summaries) else "FAILED"
        lines.append(f"SUGGESTED EMAIL SUBJECT:")
        lines.append(f"Nightly Regression Status - {date_str} - Multi-Workflow - {overall_status}")
        lines.append("")
        lines.append("=" * 60)
        lines.append("EMAIL BODY:")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append("Team,")
        lines.append("")
        lines.append(f"Nightly regression results for {date_str}:")
        lines.append("")
        
        # Summary table
        lines.append("WORKFLOW STATUS SUMMARY:")
        lines.append("-" * 40)
        for workflow in workflow_summaries:
            status_emoji = "✅" if workflow['status'] == 'PASSED' else "❌"
            lines.append(f"{status_emoji} {workflow['name']} ({workflow['board_type']}): {workflow['status']}")
            lines.append(f"   Tests: {workflow['stats']['passed']}/{workflow['stats']['total']} passed")
            
        lines.append("")
        
        # Overall summary
        total_workflows = len(workflow_summaries)
        passed_workflows = sum(1 for w in workflow_summaries if w['status'] == 'PASSED')
        
        lines.append(f"OVERALL: {passed_workflows}/{total_workflows} workflows passed")
        lines.append("")
        
        # Action items
        failed_workflows = [w for w in workflow_summaries if w['status'] == 'FAILED']
        if failed_workflows:
            lines.append("ACTION REQUIRED:")
            lines.append("• Review failed workflows and create JIRA tickets")
            lines.append("• Check for regression patterns")
            lines.append("• Notify affected teams")
        else:
            lines.append("✅ No action required - all workflows passed")
            
        lines.append("")
        lines.append("Detailed analysis available in regression reports.")
        lines.append("")
        lines.append("Best regards,")
        lines.append("Edge RTOS Automation")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Multi-Workflow Regression Report Publisher")
    parser.add_argument("--config", default="config/config.json", help="Configuration file with workflow run IDs")
    parser.add_argument("--output-dir", default="./nightly_reports", help="Output directory")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode for editing config")
    parser.add_argument("--github-token", help="GitHub token for API access (overrides config/env)")
    parser.add_argument("--no-token-prompt", action="store_true", help="Skip interactive token prompts")
    
    args = parser.parse_args()
    
    print("🏢 Multi-Workflow Regression Report Publisher")
    print("=" * 55)
    print()
    
    # Initialize processor
    config = Config()
    processor = MultiWorkflowProcessor(config)
    
    # Load configuration
    workflow_config = processor.load_workflow_config(args.config)
    if not workflow_config:
        return 1
    
    # Setup GitHub token
    github_token = processor.setup_github_token(
        workflow_config, 
        interactive_mode=True, 
        command_line_token=args.github_token,
        skip_prompt=args.no_token_prompt
    )
    if github_token is None and args.interactive and not args.no_token_prompt:
        print("❌ GitHub token setup cancelled by user")
        return 1
        
    # Interactive mode - allow editing run IDs
    if args.interactive:
        print("🔧 Interactive Mode - Update Run IDs")
        print("-" * 35)
        
        workflows = workflow_config.get('workflows', {})
        for name, wf_config in workflows.items():
            current_run_id = wf_config.get('run_id', '')
            print(f"\n📝 {name} ({wf_config.get('description', 'No description')})")
            print(f"   Current Run ID: {current_run_id if current_run_id else 'Not set'}")
            
            new_run_id = input(f"   Enter new Run ID (or press Enter to keep current): ").strip()
            if new_run_id:
                if new_run_id.isdigit():
                    workflows[name]['run_id'] = new_run_id
                    print(f"   ✅ Updated to: {new_run_id}")
                else:
                    print(f"   ❌ Invalid run ID: {new_run_id}")
            elif not current_run_id:
                workflows[name]['run_id'] = ""  # Explicitly set to skip
                print(f"   ⏭️  Will skip this workflow")
        
        # Save updated configuration
        with open(args.config, 'w', encoding='utf-8') as f:
            json.dump(workflow_config, f, indent=2)
        print(f"\n💾 Configuration saved to {args.config}")
    
    # Validate and filter workflows
    valid_workflows = processor.validate_workflow_config(workflow_config)
    if not valid_workflows:
        print("❌ No valid workflows found in configuration")
        return 1
        
    print(f"\n📊 Processing {len(valid_workflows)} workflows:")
    for name, config in valid_workflows.items():
        print(f"   • {name}: Run ID {config['run_id']} ({config['board_type']})")
    
    # Setup output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each workflow
    print(f"\n🔄 Starting workflow processing...")
    all_workflow_data = {}
    
    for workflow_name, workflow_config in valid_workflows.items():
        result = processor.process_workflow(workflow_name, workflow_config, output_dir)
        all_workflow_data[workflow_name] = result
    
    # Generate unified report
    successful_workflows = {k: v for k, v in all_workflow_data.items() if v is not None}
    if not successful_workflows:
        print("❌ No workflows processed successfully")
        return 1
        
    print(f"\n✅ Successfully processed {len(successful_workflows)}/{len(valid_workflows)} workflows")
    
    saved_files, email_summary, workflow_summaries = processor.generate_unified_report(
        successful_workflows, workflow_config, output_dir
    )
    
    # Generate performance reports from CSV files
    performance_reports = processor.generate_performance_reports(workflow_summaries)
    
    # Add performance reports to saved files list
    for report_file in performance_reports:
        saved_files.append((report_file, f"Performance Report: {Path(report_file).name}"))
    
    # Display results
    print("\n" + "="*70)
    print("📧 MULTI-WORKFLOW REGRESSION STATUS - READY FOR PUBLISHING")
    print("="*70)
    print(email_summary)
    
    print("\n" + "="*70)
    print("📁 REPORTS GENERATED:")
    print("="*70)
    for filepath, title in saved_files:
        print(f"✅ {title}")
        print(f"   📄 {filepath}")
        print()
    
    # Summary statistics
    failed_workflows = [w for w in workflow_summaries if w['status'] == 'FAILED']
    print("🎯 PUBLISHING CHECKLIST:")
    print("=" * 25)
    print(f"✅ 1. Email ready for distribution")
    print(f"✅ 2. {len(workflow_summaries)} workflows analyzed")
    print(f"✅ 3. {len(failed_workflows)} workflows need attention" if failed_workflows else "✅ 3. All workflows passed!")
    print(f"✅ 4. JIRA analysis available for failed tests")
    
    if failed_workflows:
        print(f"\n🚨 FAILED WORKFLOWS ({len(failed_workflows)}):")
        for wf in failed_workflows:
            print(f"   ❌ {wf['name']} ({wf['board_type']}) - {wf['stats']['failed']} failures")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
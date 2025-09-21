#!/usr/bin/env python3
"""
GitHub Actions Test Report Generator

This script automates the generation of test reports from GitHub Actions artifacts.
It downloads artifacts from a specified run, extracts test results, and generates 
formatted reports with pass/fail statistics and detailed failure information.

Usage:
    python main.py --run-id 17811893156
    python main.py  # Will prompt for run ID
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from core.github_api_client import GitHubAPIClient
from core.artifact_processor import ArtifactProcessor
from generators.report_generator import ReportGenerator
from generators.email_report_generator import EmailReportGenerator
from generators.regression_report_generator import RegressionReportGenerator
from config.config import Config


def main():
    """Main entry point for the report generation script."""
    parser = argparse.ArgumentParser(
        description="Generate test reports from GitHub Actions artifacts"
    )
    parser.add_argument(
        "run_id_pos",
        nargs="?",
        help="GitHub Actions run ID (positional argument)"
    )
    parser.add_argument(
        "--run-id", 
        type=str, 
        help="GitHub Actions run ID (e.g., 17811893156)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./reports",
        help="Output directory for generated reports (default: ./reports)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Configuration file path (default: config.json)"
    )
    parser.add_argument(
        "--report-type",
        type=str,
        choices=["detailed", "executive", "team", "failure", "slack", "regression", "all"],
        default="regression",
        help="Type of report to generate (default: regression)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config(args.config)
    
    # Set up logging level
    import logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Get run ID from user if not provided
    run_id = args.run_id or args.run_id_pos
    if not run_id:
        run_id = input("Enter GitHub Actions run ID: ").strip()
        if not run_id:
            logger.error("Run ID is required")
            sys.exit(1)
    
    # Validate run ID format
    if not run_id.isdigit():
        logger.error(f"Invalid run ID format: {run_id}. Must be numeric.")
        sys.exit(1)
    
    logger.info(f"Processing GitHub Actions run: {run_id}")
    
    try:
        # Initialize components
        github_client = GitHubAPIClient(config)
        artifact_processor = ArtifactProcessor(config)
        report_generator = ReportGenerator(config)
        email_generator = EmailReportGenerator(config)
        regression_generator = RegressionReportGenerator(config)
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Fetch run information and artifacts
        logger.info("Fetching GitHub Actions run information...")
        run_info = github_client.get_run_info(run_id)
        artifacts = github_client.get_run_artifacts(run_id)
        
        logger.info(f"Found {len(artifacts)} artifacts for run {run_id}")
        logger.info(f"Workflow: {run_info.get('name', 'Unknown')}")
        
        # Step 2: Download and extract artifacts
        logger.info("Downloading and extracting artifacts...")
        extracted_data = {}
        
        for artifact in artifacts:
            artifact_name = artifact['name']
            logger.info(f"Checking artifact: {artifact_name}")
            
            # Only process artifacts that start with "PyTest test_report="
            if not artifact_name.startswith("PyTest test_report="):
                logger.info(f"Skipping artifact (not PyTest test_report): {artifact_name}")
                continue
            
            logger.info(f"Processing PyTest artifact: {artifact_name}")
            
            # Download and extract artifact
            artifact_data = github_client.download_artifact(artifact['id'])
            extracted_files = artifact_processor.extract_artifact(
                artifact_data, artifact_name, output_dir
            )
            
            extracted_data[artifact_name] = extracted_files
        
        # Step 3: Process extracted files and generate reports
        logger.info("Processing test results...")
        all_test_results = {}
        
        for artifact_name, files in extracted_data.items():
            test_results = artifact_processor.process_test_files(files)
            if test_results:
                all_test_results[artifact_name] = test_results
        
        if not all_test_results:
            logger.warning("No test results found in any artifacts")
            return
        
        # Step 4: Generate summary report
        logger.info("Generating reports...")
        
        # Generate different report types based on user selection
        if args.report_type in ["regression", "all"]:
            # Main regression status report (ETN format)
            regression_report = regression_generator.generate_regression_status_report(
                run_info, all_test_results, run_id, include_historical=True
            )
            regression_file = output_dir / f"regression_status_run_{run_id}.txt"
            with open(regression_file, 'w', encoding='utf-8') as f:
                f.write(regression_report)
            logger.info(f"Regression status saved to: {regression_file}")
            
            # Email-ready regression summary
            regression_email = regression_generator.generate_email_summary(
                run_info, all_test_results, run_id
            )
            email_regression_file = output_dir / f"regression_email_run_{run_id}.txt"
            with open(email_regression_file, 'w', encoding='utf-8') as f:
                f.write(regression_email)
            logger.info(f"Email regression summary saved to: {email_regression_file}")
            
            # Detailed failure analysis for JIRA
            detailed_failure = regression_generator.generate_detailed_failure_summary(
                run_info, all_test_results, run_id
            )
            failure_analysis_file = output_dir / f"jira_failure_analysis_run_{run_id}.txt"
            with open(failure_analysis_file, 'w', encoding='utf-8') as f:
                f.write(detailed_failure)
            logger.info(f"JIRA failure analysis saved to: {failure_analysis_file}")
        
        if args.report_type in ["executive", "all"]:
            executive_report = email_generator.generate_executive_summary(run_info, all_test_results, run_id)
            exec_file = output_dir / f"executive_summary_run_{run_id}.txt"
            with open(exec_file, 'w', encoding='utf-8') as f:
                f.write(executive_report)
            logger.info(f"Executive summary saved to: {exec_file}")
        
        if args.report_type in ["team", "all"]:
            team_report = email_generator.generate_team_summary(run_info, all_test_results, run_id)
            team_file = output_dir / f"team_summary_run_{run_id}.txt"
            with open(team_file, 'w', encoding='utf-8') as f:
                f.write(team_report)
            logger.info(f"Team summary saved to: {team_file}")
        
        if args.report_type in ["failure", "all"]:
            failure_report = email_generator.generate_failure_focused_report(run_info, all_test_results, run_id)
            failure_file = output_dir / f"failure_analysis_run_{run_id}.txt"
            with open(failure_file, 'w', encoding='utf-8') as f:
                f.write(failure_report)
            logger.info(f"Failure analysis saved to: {failure_file}")
        
        if args.report_type in ["slack", "all"]:
            slack_report = email_generator.generate_slack_summary(run_info, all_test_results, run_id)
            slack_file = output_dir / f"slack_summary_run_{run_id}.txt"
            with open(slack_file, 'w', encoding='utf-8') as f:
                f.write(slack_report)
            logger.info(f"Slack summary saved to: {slack_file}")
        
        if args.report_type in ["detailed", "all"]:
            report_file = output_dir / f"detailed_report_run_{run_id}.txt"
            detailed_report = report_generator.generate_detailed_report(
                run_info, all_test_results, run_id
            )
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(detailed_report)
            logger.info(f"Detailed report saved to: {report_file}")
        
        # Always generate JSON report for programmatic access
        json_report_file = output_dir / f"test_report_run_{run_id}.json"
        json_report = report_generator.generate_json_report(
            run_info, all_test_results, run_id
        )
        
        import json
        with open(json_report_file, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2)
        
        # Determine which report to show in console based on selection
        if args.report_type == "regression":
            console_report = regression_email
        elif args.report_type == "executive":
            console_report = executive_report
        elif args.report_type == "team":
            console_report = team_report
        elif args.report_type == "failure":
            console_report = failure_report
        elif args.report_type == "slack":
            console_report = slack_report
        else:
            # Default to regression email summary for console output
            console_report = regression_generator.generate_email_summary(run_info, all_test_results, run_id)
        
        # Print summary to console
        print("\n" + "="*80)
        print(f"NIGHTLY REGRESSION REPORT - RUN {run_id}")
        print("="*80)
        print(console_report)
        print("="*80)
        print(f"\nReports saved to:")
        
        # List generated reports
        if args.report_type in ["regression", "all"]:
            print(f"  📊 Regression Status: {output_dir}/regression_status_run_{run_id}.txt")
            print(f"  📧 Email Summary: {output_dir}/regression_email_run_{run_id}.txt")
            print(f"  🐛 JIRA Analysis: {output_dir}/jira_failure_analysis_run_{run_id}.txt")
        if args.report_type in ["executive", "all"]:
            print(f"  📊 Executive Summary: {output_dir}/executive_summary_run_{run_id}.txt")
        if args.report_type in ["team", "all"]:
            print(f"  👥 Team Summary: {output_dir}/team_summary_run_{run_id}.txt")
        if args.report_type in ["failure", "all"]:
            print(f"  🐛 Failure Analysis: {output_dir}/failure_analysis_run_{run_id}.txt")
        if args.report_type in ["slack", "all"]:
            print(f"  💬 Slack Summary: {output_dir}/slack_summary_run_{run_id}.txt")
        if args.report_type in ["detailed", "all"]:
            print(f"  📋 Detailed Report: {output_dir}/detailed_report_run_{run_id}.txt")
        print(f"  🔧 JSON Data: {json_report_file}")
        
        print(f"\n🎯 READY FOR PUBLISHING:")
        if args.report_type in ["regression", "all"]:
            print(f"  • Use regression_email_*.txt for team distribution")
            print(f"  • Use jira_failure_analysis_*.txt for bug creation")
            print(f"  • Copy regression_status_*.txt for formal reporting")
        
        logger.info("Report generation completed successfully!")
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
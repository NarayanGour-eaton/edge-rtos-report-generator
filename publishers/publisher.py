#!/usr/bin/env python3
"""
Regression Report Publisher - Matches Team Format

This script generates nightly reg        # Generate regression reports
        print("📏 Generating regression reports...")
        
        date_str = run_info.get('created_at', '')[:10] if run_info.get('created_at') else 'unknown'
        
        # 1. Main regression status report (standard table format)n reports in the            'regression_status': (regression_status, "📈 Nightly Regression Status (Standard Format)"),           'regression_status': (regression_status, "📈 Nightly Regression Status (Standard Format)"),exact format
used by the team, ready for immediate publishing and distribution.

Usage:
    python publisher.py 17811893156
    python publisher.py --interactive
"""

import sys
import os
from pathlib import Path
import argparse

# Add current directory and parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "generators"))
sys.path.insert(0, str(Path(__file__).parent.parent / "config"))

from github_api_client import GitHubAPIClient
from artifact_processor import ArtifactProcessor
from regression_report_generator import RegressionReportGenerator
from config import Config


def main():
    parser = argparse.ArgumentParser(description="Regression Report Publisher")
    parser.add_argument("--u575-run-id", help="GitHub Actions run ID for BFT_U575zi_q_dev")
    parser.add_argument("--h743-run-id", help="GitHub Actions run ID for BFT_h743zi_dev")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode (default)")
    parser.add_argument("--output-dir", default="./nightly_reports", help="Output directory")
    parser.add_argument("--include-historical", action="store_true", help="Include historical success/failure data")
    
    args = parser.parse_args()
    
    # Get run IDs for both boards
    print("🏢 Nightly Regression Report Publisher")
    print("=" * 50)
    print("Processing runs for both BFT_U575zi_q_dev and BFT_h743zi_dev")
    print("=" * 50)
    
    # Get U575 run ID
    u575_run_id = args.u575_run_id
    if not u575_run_id:
        while True:
            u575_run_id = input("\n📱 Enter BFT_U575zi_q_dev Run ID: ").strip()
            if u575_run_id and u575_run_id.isdigit():
                break
            print("❌ Please enter a valid numeric run ID for BFT_U575zi_q_dev")
    
    # Get H743 run ID  
    h743_run_id = args.h743_run_id
    if not h743_run_id:
        while True:
            h743_run_id = input("🔧 Enter BFT_h743zi_dev Run ID: ").strip()
            if h743_run_id and h743_run_id.isdigit():
                break
            print("❌ Please enter a valid numeric run ID for BFT_h743zi_dev")
    
    # Validate run IDs
    if not u575_run_id.isdigit():
        print(f"❌ Invalid U575 run ID: {u575_run_id}")
        return 1
    if not h743_run_id.isdigit():
        print(f"❌ Invalid H743 run ID: {h743_run_id}")
        return 1
    
    print(f"\n📊 Processing nightly regression runs:")
    print(f"   BFT_U575zi_q_dev: {u575_run_id}")
    print(f"   BFT_h743zi_dev: {h743_run_id}")
    
    run_ids = [u575_run_id, h743_run_id]
    board_types = ["BFT_U575zi_q_dev", "BFT_h743zi_dev"]
    
    try:
        # Setup
        config = Config()
        github_client = GitHubAPIClient(config)
        artifact_processor = ArtifactProcessor(config)
        regression_generator = RegressionReportGenerator(config)
        
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Fetch data
        print("⬇️  Downloading artifacts...")
        run_info = github_client.get_run_info(args.run_id)
        artifacts = github_client.get_run_artifacts(args.run_id)
        
        print(f"📦 Processing {len(artifacts)} artifacts...")
        all_test_results = {}
        
        for artifact in artifacts:
            # Only process artifacts that start with "PyTest test_report="
            if not artifact['name'].startswith("PyTest test_report="):
                print(f"⏭️  Skipping artifact (not PyTest test_report): {artifact['name']}")
                continue
                
            print(f"🔍 Processing PyTest artifact: {artifact['name']}")
            artifact_data = github_client.download_artifact(artifact['id'])
            extracted_files = artifact_processor.extract_artifact(
                artifact_data, artifact['name'], output_dir
            )
            
            test_results = artifact_processor.process_test_files(extracted_files)
            if test_results:
                all_test_results[artifact['name']] = test_results
        
        if not all_test_results:
            print("⚠️  No test results found")
            return 1
        
        # Generate ETN-format reports
        print("📝 Generating ETN regression reports...")
        
        date_str = run_info.get('created_at', '')[:10] if run_info.get('created_at') else 'unknown'
        
        # 1. Main regression status report (ETN table format)
        regression_status = regression_generator.generate_regression_status_report(
            run_info, all_test_results, args.run_id, include_historical=args.include_historical
        )
        
        # 2. Email-ready summary  
        email_summary = regression_generator.generate_email_summary(
            run_info, all_test_results, args.run_id
        )
        
        # 3. Detailed failure analysis for JIRA creation
        jira_analysis = regression_generator.generate_detailed_failure_summary(
            run_info, all_test_results, args.run_id
        )
        
        # Save reports with standard naming convention
        reports = {
            'regression_status': (regression_status, "📊 Nightly Regression Status (ETN Format)"),
            'email_summary': (email_summary, "📧 Email Distribution Summary"),
            'jira_analysis': (jira_analysis, "🐛 JIRA Bug Creation Analysis")
        }
        
        saved_files = []
        for report_type, (content, title) in reports.items():
            filename = output_dir / f"nightly_{report_type}_{date_str}_run_{args.run_id}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            saved_files.append((filename, title))
        
        # Display results in standard format
        print("\n" + "="*70)
        print("📧 NIGHTLY REGRESSION STATUS - READY FOR PUBLISHING")
        print("="*70)
        
        # Show email summary on screen for immediate use
        print(email_summary)
        
        print("\n" + "="*70)
        print("📁 REPORTS GENERATED:")
        print("="*70)
        
        for filepath, title in saved_files:
            print(f"✅ {title}")
            print(f"   📄 {filepath}")
            print()
        
        # Calculate quick stats for team update
        overall_stats = regression_generator._calculate_overall_stats(all_test_results)
        workflow_name = run_info.get('name', 'Unknown Workflow')
        
        print("🎯 PUBLISHING CHECKLIST:")
        print("=" * 25)
        print(f"✅ 1. Email Subject: 'Nightly Regression Status - {date_str} - "
              f"{'PASSED' if overall_stats['failed'] == 0 else 'FAILED'}'")
        print(f"✅ 2. Copy email_summary content to team distribution list")
        print(f"✅ 3. Use jira_analysis for creating/updating bug tickets")
        print(f"✅ 4. Update regression status spreadsheet with results")
        print(f"✅ 5. Post summary in team channels/Slack")
        
        if overall_stats['failed'] > 0:
            print(f"\n🚨 ACTION ITEMS ({overall_stats['failed']} failures):")
            print(f"   • Review JIRA analysis for new bug creation")
            print(f"   • Check for regressions from recent changes")
            print(f"   • Notify relevant teams of failures")
        else:
            print(f"\n🎉 ALL TESTS PASSED - NO ACTION REQUIRED!")
        
        # Interactive clipboard copy (if available)
        if args.interactive:
            choice = input(f"\nCopy to clipboard? (email/jira/status/none): ").lower()
            if choice in ['email', 'jira', 'status']:
                try:
                    import pyperclip
                    if choice == 'email':
                        pyperclip.copy(email_summary)
                        print("✅ Email summary copied to clipboard!")
                    elif choice == 'jira':
                        pyperclip.copy(jira_analysis)
                        print("✅ JIRA analysis copied to clipboard!")
                    elif choice == 'status':
                        pyperclip.copy(regression_status)
                        print("✅ Regression status copied to clipboard!")
                except ImportError:
                    print("💡 Install pyperclip for clipboard functionality: pip install pyperclip")
        
        print(f"\n📊 Summary Stats for {workflow_name}:")
        print(f"   Total: {overall_stats['total']} | "
              f"Pass: {overall_stats['passed']} | "
              f"Fail: {overall_stats['failed']} | "
              f"Skip: {overall_stats['skipped']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating regression report: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
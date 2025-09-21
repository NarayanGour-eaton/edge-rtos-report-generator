#!/usr/bin/env python3
"""
Daily Report Publisher - Quick Script for Publishing Nightly Test Results

This script is optimized for daily use - just provide a run ID and get
publication-ready reports for email, Slack, and team communication.

Usage:
    python daily_publisher.py 17811893156
    python daily_publisher.py --interactive
"""

import sys
import os
from pathlib import Path
import argparse

# Add parent directory paths to find modules
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "generators"))
sys.path.insert(0, str(Path(__file__).parent.parent / "config"))

from github_api_client import GitHubAPIClient
from artifact_processor import ArtifactProcessor
from email_report_generator import EmailReportGenerator
from config import Config


def main():
    parser = argparse.ArgumentParser(description="Quick daily report publisher")
    parser.add_argument("run_id", nargs="?", help="GitHub Actions run ID")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--output-dir", default="./daily_reports", help="Output directory")
    
    args = parser.parse_args()
    
    # Get run ID
    if args.interactive or not args.run_id:
        print("🚀 Daily Test Report Publisher")
        print("=" * 40)
        
        if not args.run_id:
            args.run_id = input("Enter GitHub Actions run ID: ").strip()
        
        if not args.run_id:
            print("❌ Run ID is required")
            return 1
    
    # Validate run ID
    if not args.run_id.isdigit():
        print(f"❌ Invalid run ID: {args.run_id}")
        return 1
    
    print(f"📊 Processing run: {args.run_id}")
    
    try:
        # Setup
        config = Config()
        github_client = GitHubAPIClient(config)
        artifact_processor = ArtifactProcessor(config)
        email_generator = EmailReportGenerator(config)
        
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Fetch data
        print("⬇️  Downloading artifacts...")
        run_info = github_client.get_run_info(args.run_id)
        artifacts = github_client.get_run_artifacts(args.run_id)
        
        # Process artifacts
        print(f"📦 Processing {len(artifacts)} artifacts...")
        all_test_results = {}
        
        for artifact in artifacts:
            artifact_name = artifact['name']
            
            # Only process artifacts that start with "PyTest test_report="
            if not artifact_name.startswith("PyTest test_report="):
                print(f"⏭️  Skipping artifact (not PyTest test_report): {artifact_name}")
                continue
            
            print(f"🔍 Processing PyTest artifact: {artifact_name}")
                
            artifact_data = github_client.download_artifact(artifact['id'])
            extracted_files = artifact_processor.extract_artifact(
                artifact_data, artifact_name, output_dir
            )
            
            test_results = artifact_processor.process_test_files(extracted_files)
            if test_results:
                all_test_results[artifact_name] = test_results
        
        if not all_test_results:
            print("⚠️  No test results found")
            return 1
        
        # Generate reports
        print("📝 Generating reports...")
        
        # Executive Summary (for management/email)
        exec_report = email_generator.generate_executive_summary(
            run_info, all_test_results, args.run_id
        )
        
        # Team Summary (for team leads)
        team_report = email_generator.generate_team_summary(
            run_info, all_test_results, args.run_id
        )
        
        # Failure Analysis (for bug creation)
        failure_report = email_generator.generate_failure_focused_report(
            run_info, all_test_results, args.run_id
        )
        
        # Slack Summary (for chat notifications)
        slack_report = email_generator.generate_slack_summary(
            run_info, all_test_results, args.run_id
        )
        
        # Save all reports
        date_str = run_info.get('created_at', '')[:10] if run_info.get('created_at') else 'unknown'
        
        reports = {
            'executive_summary': (exec_report, f"📊 Executive Summary - {date_str}"),
            'team_summary': (team_report, f"👥 Team Summary - {date_str}"),
            'failure_analysis': (failure_report, f"🐛 Failure Analysis - {date_str}"),
            'slack_summary': (slack_report, f"💬 Slack Summary - {date_str}")
        }
        
        saved_files = []
        for report_type, (content, title) in reports.items():
            filename = output_dir / f"{report_type}_{date_str}_run_{args.run_id}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            saved_files.append((filename, title))
        
        # Display results
        print("\n" + "="*60)
        print("📧 READY FOR PUBLISHING")
        print("="*60)
        
        # Show executive summary on screen
        print(exec_report)
        
        print("\n" + "="*60)
        print("📁 FILES GENERATED:")
        print("="*60)
        
        for filepath, title in saved_files:
            print(f"✅ {title}")
            print(f"   📄 {filepath}")
            print()
        
        print("🎯 NEXT STEPS:")
        print("  1. Copy executive_summary for management email")
        print("  2. Copy team_summary for team distribution")  
        print("  3. Use failure_analysis for bug creation")
        print("  4. Post slack_summary to team channels")
        
        # Quick copy options
        if args.interactive:
            choice = input("\nCopy to clipboard? (executive/team/failure/slack/none): ").lower()
            if choice in reports:
                try:
                    import pyperclip
                    pyperclip.copy(reports[choice][0])
                    print(f"✅ {reports[choice][1]} copied to clipboard!")
                except ImportError:
                    print("💡 Install pyperclip for clipboard functionality: pip install pyperclip")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
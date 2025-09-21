# Nightly Regression Re## 📈 What You Get (Standard Format)

### 1. **Regression Status Report** (Standard Table Format)t Generator - Quick Start Guide

## 🚀 Ready for Tomorrow's Reports!

This tool now generates reports in **exactly the same format** as your current team process, combining automation with your established workflow.

## Quick Start (2 Minutes Setup)

### 1. Install & Configure
```bash
# Install dependencies
pip install -r requirements.txt

# Set GitHub token (optional but recommended)
export GITHUB_TOKEN="your_github_token_here"
```

### 2. Generate Reports (Your Daily Workflow)

```bash
# Windows - Multi-workflow processing:
batch_scripts\run_multi_workflow_report.bat

# Or run publisher directly:
python publishers\publisher.py 17811893156
```

## 📊 What You Get (ETN Format)

### 1. **Regression Status Report** (Exact ETN Table Format)
```
Nightly Regression runs: Dev Branch (Build Repository)

Workflow Name                           Plan result  Total  Pass  Fail  Skipped  Actions
BFT_h743zi_dev (Functional + Module)   Failed       1746   1602   74    143      [LTK-31955] SNTP Sync with incorrect NTP server :H743
                                                                                  [LTK-31956] HTTP response code mismatch: Audit logging tests

BFT_U575zi_q_dev (Functional + Module) Failed       2319   1951   108   368      [LTK-31956] HTTP response code mismatch: Audit logging tests

Build-All-In-Container                  Successful   -      -     -     -
```

### 2. **Email Summary** (Ready to Send)
```
Subject: Nightly Regression Status - 2025-09-21 - FAILED

❌ NIGHTLY REGRESSION SUMMARY - 2025-09-21

Overall Status: FAILED
Pass Rate: 95.1% (230/242)
Branch: dev
Run ID: 17811893156

🚨 FAILED TESTS (12):
  • rest: test_user_login_negative
  • rest: test_session_timeout
  • modbus: test_connection_timeout
  ...
```

### 3. **JIRA Analysis** (Bug Creation Ready)
```
DETAILED FAILURE ANALYSIS - Run 17811893156

📦 REST: 5 failed
--------------------
  1. test_user_login_negative::test_invalid_credentials
     Error: AssertionError: Expected 401 but got 200
     Suggested JIRA: [LTK-XXXXX] Assertion Failure: User Login Negative - H743

  2. test_user_session::test_session_timeout
     Error: Timeout waiting for session expiry after 300s
     Suggested JIRA: [LTK-XXXXX] Timeout Error: User Session - H743
```

## 📧 Your Publishing Workflow (Unchanged!)

1. **Get Run ID** from GitHub Actions: `17811893156`
2. **Run Tool**: `publisher.py 17811893156`
3. **Publish Results**:
   - Copy `email_summary` → Send to team
   - Use `jira_analysis` → Create bug tickets
   - Copy `regression_status` → Update spreadsheet
   - Post in team channels

## 🔧 Advanced Usage

```bash
# Include historical success/failure percentages
python publisher.py 17811893156 --include-historical

# Interactive mode with clipboard copy
python publisher.py --interactive

# Generate all format types
python main.py --run-id 17811893156 --report-type all
```

## 📁 Output Files Generated

- `nightly_regression_status_2025-09-21_run_17811893156.txt` - Standard table format
- `nightly_email_summary_2025-09-21_run_17811893156.txt` - Team distribution  
- `nightly_jira_analysis_2025-09-21_run_17811893156.txt` - Bug creation

## ⚡ What's Different/Better Now

✅ **Same Format** - Matches your exact table structure  
✅ **Automated** - No manual copy/paste from GitHub  
✅ **JIRA Ready** - Suggests ticket titles and includes error details  
✅ **Historical Data** - Includes success/failure percentages  
✅ **Email Ready** - Perfect subject lines and content  
✅ **Fast** - 2-minute process instead of 15+ minutes  

## 🎯 Tomorrow's Checklist

1. ✅ Get run ID from GitHub Actions
2. ✅ Run: `publisher.py YOUR_RUN_ID`
3. ✅ Copy email summary for team distribution
4. ✅ Use JIRA analysis for bug creation
5. ✅ Update regression spreadsheet with status

**That's it! Same workflow, same format, automated data collection.** 🚀

## Example Daily Command
```bash
# For your H743 run example:
python publisher.py 17811893156

# Results in 3 files ready for your exact workflow
```

The tool now perfectly matches your team's established format while automating the tedious data extraction part!
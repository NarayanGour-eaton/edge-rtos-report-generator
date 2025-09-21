# Edge RTOS Report Generator

This tool automates the generation of test reports from GitHub Actions artifacts for **daily publishing and team communication**. Perfect for nightly test reporting, team updates, and bug triage.

## 🚀 Quick Start for Daily Publishing

### For Immediate Use (Ready for Tomorrow's Reports!)

1. **Download/Copy the tool** to your local machine
2. **Set GitHub Token** (optional but recommended):
   ```bash
   export GITHUB_TOKEN="your_personal_access_token"
   ```
3. **Run for your test results**:
   ```bash
   # Windows users - use multi-workflow processing:
   batch_scripts\run_multi_workflow_report.bat
   
   # Or batch mode with existing configuration:
   batch_scripts\run_batch_multi_workflow.bat
   
   # Or use the daily publisher for single runs:
   python publishers\daily_publisher.py 17811893156
   ```
4. **Get ready-to-publish reports** in multiple formats!

### 📧 Report Types Generated

- **📊 Executive Summary** - For management emails (concise, high-level)
- **👥 Team Summary** - For team distribution (module breakdown)  
- **🐛 Failure Analysis** - For bug creation (detailed failures)
- **💬 Slack Summary** - For team chat notifications

## Features

- 🚀 **Automated Artifact Download**: Fetches all test-related artifacts from GitHub Actions runs
- 📊 **Multi-Format Support**: Processes JUnit XML, JSON, text logs, and other test report formats
- 📈 **Comprehensive Reports**: Generates both human-readable text and machine-readable JSON reports
- 🔍 **Detailed Failure Analysis**: Lists all failed tests with error messages for easy bug reporting
- ⚙️ **Configurable**: Customizable via config file or environment variables
- 🏷️ **Smart Filtering**: Automatically skips build artifacts and focuses on test results

## Quick Start

### 1. Installation

```bash
# Clone or copy the script files to your local machine
# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Set up your GitHub token (optional but recommended for higher rate limits):

```bash
# Option 1: Environment variable (recommended)
export GITHUB_TOKEN="your_github_personal_access_token"

# Option 2: Edit config.json
{
  "repo_owner": "etn-ccis",
  "repo_name": "edge-rtos-github-builds",
  ...
}
```

### 3. Daily Usage

```bash
# For daily publishing - generates all report types
python publishers\daily_publisher.py 17811893156

# Windows users - multi-workflow processing:
batch_scripts\run_multi_workflow_report.bat

# Choose specific report type
python main.py --run-id 17811893156 --report-type executive
python main.py --run-id 17811893156 --report-type team  
python main.py --run-id 17811893156 --report-type failure
python main.py --run-id 17811893156 --report-type slack
```

### 4. Example Output for Publishing

**Executive Summary Format:**
```
=== NIGHTLY TEST REPORT - 2025-09-21 ===

🎯 OVERALL STATUS: ❌ FAILED
📊 PASS RATE: 95.1% (230/242)  
⚡ WORKFLOW: H743 Test Suite
🌿 BRANCH: main
🔗 RUN ID: 17811893156

📈 QUICK STATS:
   • Total Tests: 242
   • Passed: 230 ✅
   • Failed: 12 ❌
   • Skipped: 0 ⏭️

🚨 ACTION REQUIRED:
   Please review failed tests and create appropriate bug reports.
```

**Team Summary Format:**
```
📦 H743-TEST-RESULTS:
  ✅ modbus:
     Total: 45 | Passed: 45 | Failed: 0
  
  ❌ rest:
     Total: 67 | Passed: 62 | Failed: 5  
     ⚠️  FAILURES (5):
        1. test_user_login_negative
        2. test_session_timeout
        3. test_param_validation
        4. test_fw_upload_corrupted
        5. test_unauthorized_access
```

**Failure Analysis Format (for Bug Creation):**
```
🐛 FAILURE ANALYSIS REPORT

📋 Rest: 5 failed
--------------------
 1. test_user_login_negative::test_invalid_credentials
    💬 AssertionError: Expected 401 but got 200
    
 2. test_user_session::test_session_timeout  
    💬 Timeout waiting for session expiry after 300s
```

## Configuration

### config.json

```json
{
  "repo_owner": "etn-ccis",
  "repo_name": "edge-rtos-github-builds",
  "skip_build_artifacts": true,
  "supported_test_formats": [".xml", ".json", ".html", ".txt", ".log"],
  "output_format": "both",
  "include_passed_tests": false,
  "max_failure_message_length": 500
}
```

### Environment Variables

- `GITHUB_TOKEN`: GitHub personal access token
- `REPO_OWNER`: Repository owner (defaults to "etn-ccis")
- `REPO_NAME`: Repository name (defaults to "edge-rtos-github-builds")
- `OUTPUT_FORMAT`: Output format ("text", "json", or "both")

## Supported Test Formats

The tool automatically detects and processes:

- **JUnit XML**: Standard XML test reports
- **pytest JSON**: JSON reports from pytest-json-report
- **Text Logs**: pytest terminal output, log files
- **Custom JSON**: Various JSON report formats

## Advanced Usage

### Finding Run IDs

You can find GitHub Actions run IDs from:

1. **GitHub Web Interface**: 
   - Go to https://github.com/etn-ccis/edge-rtos-github-builds/actions
   - Click on a workflow run
   - The run ID is in the URL: `.../runs/17811893156`

2. **GitHub CLI**:
   ```bash
   gh run list --repo etn-ccis/edge-rtos-github-builds
   ```

3. **Using the Script** (coming soon):
   ```bash
   python main.py --list-recent-runs --workflow "h743"
   ```

### Batch Processing

Process multiple runs:

```bash
# Process last 5 runs
for run_id in $(gh run list --limit 5 --json databaseId --jq '.[].databaseId'); do
    python main.py --run-id $run_id --output-dir "./reports/run_$run_id"
done
```

### Integration with CI/CD

```bash
# In your CI pipeline
python main.py --run-id $GITHUB_RUN_ID --output-dir ./reports
# Upload reports to artifact storage or send notifications
```

## Output Files

For each run, the tool generates:

- `test_report_run_<run_id>.txt`: Human-readable text report
- `test_report_run_<run_id>.json`: Machine-readable JSON report
- `artifacts_<artifact_name>/`: Extracted artifact contents

## Troubleshooting

### Common Issues

1. **Rate Limiting**: Set `GITHUB_TOKEN` environment variable
2. **No Test Results Found**: Check if artifacts contain test reports
3. **Permission Errors**: Ensure GitHub token has `repo` scope

### Debug Mode

```bash
python main.py --run-id 17811893156 --verbose
```

### Logs

The tool uses Python's logging module. Set log level via:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

To extend the tool:

1. **Add New Test Format**: Extend `artifact_processor.py`
2. **Custom Report Format**: Extend `report_generator.py`
3. **Additional APIs**: Extend `github_api_client.py`

## Daily Publishing Workflow

### Recommended Daily Process:

1. **Get the Run ID** from your nightly build:
   - Visit: https://github.com/etn-ccis/edge-rtos-github-builds/actions
   - Click on latest run → copy the run ID from URL

2. **Generate Reports**:
   ```bash
   python daily_publisher.py YOUR_RUN_ID
   ```

3. **Publish Results**:
   - **Email Management**: Copy `executive_summary_*.txt`
   - **Team Distribution**: Copy `team_summary_*.txt` 
   - **Bug Triage**: Use `failure_analysis_*.txt` 
   - **Slack/Teams**: Copy `slack_summary_*.txt`

### Email Templates:

**Subject**: `Nightly Test Results - [DATE] - [STATUS]`

**Body**: Just paste the executive summary content

### Automation Ideas:

```bash
# Schedule daily report generation
# Add to cron/task scheduler:
0 9 * * * cd /path/to/tool && python daily_publisher.py $(get_latest_run_id)

# Or integrate with your CI pipeline
python daily_publisher.py $GITHUB_RUN_ID && send_email.py executive_summary_*.txt
```

## License

This tool is provided as-is for internal use by the development team.

## Support

For issues or feature requests, contact the test automation team or create an issue in the repository.
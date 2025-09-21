# Multi-Workflow Regression Report Generator

This enhanced tool processes multiple workflow runs simultaneously to generate comprehensive regression reports covering all board types and test suites.

## 🚀 Quick Start

### 1. Setup Configuration File

Edit `workflow_runs.json` with your GitHub Actions run IDs:

```json
{
  "date": "2024-12-21",
  "description": "Nightly Regression Run Configuration",
  "workflows": {
    "BFT_U575zi_q_dev": {
      "run_id": "17811893156",
      "description": "STM32U575 Development Board Tests",
      "board_type": "U575"
    },
    "BFT_h743zi_dev": {
      "run_id": "17811893157", 
      "description": "STM32H743 Development Board Tests",
      "board_type": "H743"
    },
    "BFT_integration_test": {
      "run_id": "17811893158",
      "description": "Integration Test Suite",
      "board_type": "Mixed"
    }
  }
}
```

### 2. Run Report Generation

**Interactive Mode (Recommended):**
```batch
run_multi_workflow_report.bat
```

**Batch Mode:**
```batch
run_batch_multi_workflow.bat
```

**Command Line:**
```bash
# Interactive mode - prompts to edit run IDs
python multi_publisher.py --interactive

# Batch mode - uses existing workflow_runs.json
python multi_publisher.py

# Custom configuration file
python multi_publisher.py --config my_custom_runs.json
```

## 📋 Configuration File Format

### Required Fields

```json
{
  "workflows": {
    "workflow_name": {
      "run_id": "12345678901",
      "description": "Human readable description",
      "board_type": "Board identifier"
    }
  }
}
```

### Optional Fields

```json
{
  "date": "YYYY-MM-DD",           // Report date (default: today)
  "description": "Run description",  // Overall description
  "settings": {
    "include_historical_data": false,
    "generate_jira_analysis": true,
    "email_distribution_ready": true
  }
}
```

### Skipping Workflows

Set `run_id` to empty string to skip:
```json
"workflow_name": {
  "run_id": "",  // This workflow will be skipped
  "description": "Will be ignored"
}
```

## 📊 Generated Reports

The tool generates three comprehensive reports:

### 1. Multi-Workflow Regression Status (`multi_workflow_regression_status_YYYY-MM-DD.txt`)
- **ETN table format** with all workflows
- Per-workflow pass/fail status
- Board-specific breakdowns  
- Action items and priorities
- Overall statistics

### 2. Email Distribution Summary (`multi_workflow_email_summary_YYYY-MM-DD.txt`)
- **Ready-to-send email format**
- Suggested subject line
- Workflow status summary
- Action items for team

### 3. JIRA Analysis Report (`multi_workflow_jira_analysis_YYYY-MM-DD.txt`)
- **Detailed failure analysis** 
- Bug creation recommendations
- Test failure patterns
- Historical context

## 🔧 Interactive Mode Features

When running with `--interactive` flag:

1. **Run ID Editing**: Update run IDs for each workflow
2. **Workflow Selection**: Skip workflows by leaving run ID empty
3. **Configuration Saving**: Automatically saves changes to config file
4. **Validation**: Checks run ID format before processing

## 📁 Output Structure

```
nightly_reports/
├── multi_workflow_regression_status_2024-12-21.txt
├── multi_workflow_email_summary_2024-12-21.txt  
├── multi_workflow_jira_analysis_2024-12-21.txt
└── [workflow_name]/          # Individual workflow artifacts
    ├── artifacts/
    └── processed_results/
```

## 💡 Usage Examples

### Daily Regression Workflow

1. **Morning Setup** (5 minutes):
   ```batch
   # Edit workflow_runs.json with yesterday's run IDs
   run_multi_workflow_report.bat
   ```

2. **Email Distribution** (2 minutes):
   - Copy content from `email_summary` file
   - Send to team distribution list
   - Update subject with date and status

3. **JIRA Management** (10 minutes):
   - Review `jira_analysis` file
   - Create/update bug tickets for failures
   - Link to specific run artifacts

### Weekly Status Reports

Use the regression status report for:
- **Team standup summaries**
- **Management dashboards** 
- **Trend analysis** over multiple days
- **Board-specific performance tracking**

### Failure Investigation

The unified report provides:
- **Cross-workflow failure patterns**
- **Board-specific issues**
- **Artifact download links**
- **Historical comparison data**

## 🚀 Advanced Usage

### Custom Configuration Files

Create environment-specific configs:

```bash
# Production runs
python multi_publisher.py --config prod_workflows.json

# Development testing  
python multi_publisher.py --config dev_workflows.json

# Weekly regression
python multi_publisher.py --config weekly_full_regression.json
```

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Generate ETN Report
  run: |
    # Update workflow_runs.json with current run IDs
    python update_config.py --run-id ${{ github.run_id }}
    python multi_publisher.py
    
- name: Upload Reports
  uses: actions/upload-artifact@v3
  with:
    name: etn-regression-reports
    path: nightly_reports/
```

### Automated Email Distribution

```python
# Custom integration example
import subprocess
import smtplib
from email.mime.text import MIMEText

# Generate report
subprocess.run(["python", "multi_publisher.py"])

# Read email summary
with open("nightly_reports/multi_workflow_email_summary_2024-12-21.txt") as f:
    email_body = f.read()

# Send email (configure your SMTP settings)
# ... email sending code ...
```

## 🎯 Team Integration

This tool is designed to fit seamlessly into the team's existing workflow:

- **Maintains exact table format** from current regression emails
- **Preserves JIRA ticket workflow** and bug tracking processes  
- **Supports current board naming** conventions (U575, H743, etc.)
- **Ready-to-copy email summaries** for distribution lists
- **Action-oriented reporting** with clear next steps

## ⚙️ Configuration Tips

### Workflow Naming Best Practices

- Use descriptive names: `BFT_U575zi_q_dev` instead of `test1`
- Include board type: `U575`, `H743`, `Mixed`, `All`
- Group related tests: `integration_test`, `performance_test`

### Board Type Categories

- **`U575`**: STM32U575-specific tests
- **`H743`**: STM32H743-specific tests  
- **`Mixed`**: Tests running on multiple boards
- **`All`**: Tests covering all supported platforms
- **`Performance`**: Benchmark and timing tests
- **`Reliability`**: Long-running stress tests

### Run ID Management

- **Keep config updated**: Use interactive mode daily
- **Archive old configs**: Save weekly snapshots
- **Document special runs**: Add descriptive comments for non-standard runs

## 🔍 Troubleshooting

### Common Issues

**Configuration not found:**
```
❌ Configuration file not found: workflow_runs.json
💡 Create workflow_runs.json with your run IDs
```
**Solution**: Copy the template `workflow_runs.json` and update with your run IDs

**Invalid run IDs:**
```
⚠️ Invalid run ID for BFT_U575zi_q_dev: abc123
```
**Solution**: Run IDs must be numeric (e.g., `17811893156`)

**No test results:**
```
⚠️ No test results found for workflow_name
```
**Solution**: Check if the workflow actually ran tests (not just build)

**Network errors:**
```
❌ Error processing workflow_name: HTTP 403
```
**Solution**: Check GitHub token permissions and rate limits

### Debug Mode

Add debug output by modifying the script:
```bash
# Enable verbose logging
export GITHUB_DEBUG=1
python multi_publisher.py --interactive
```

### Validation Commands

```bash
# Test configuration file
python -c "import json; print(json.load(open('workflow_runs.json')))"

# Check GitHub connectivity  
python -c "from github_api_client import GitHubAPIClient; print('OK')"

# Verify run ID format
python -c "run_id='17811893156'; print('Valid' if run_id.isdigit() else 'Invalid')"
```

---

## 🚀 Ready for Production

This multi-workflow tool is **production-ready** and designed for immediate deployment in your regression workflow:

✅ **Handles multiple board types simultaneously**  
✅ **Matches existing ETN report format exactly**  
✅ **Interactive and batch modes for flexibility**  
✅ **Comprehensive error handling and validation**  
✅ **Email-ready output for distribution**  
✅ **JIRA integration for bug tracking**  
✅ **Windows batch file integration**

Start using it today with your nightly regression runs!
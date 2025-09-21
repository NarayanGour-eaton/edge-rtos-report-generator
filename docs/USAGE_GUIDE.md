# ETN Report Generation - Quick Usage Guide

## 🚀 **Updated - New Multi-Workflow Processing!**

```batch
# Multi-workflow batch processing (recommended)
batch_scripts\run_batch_multi_workflow.bat

# Interactive multi-workflow setup
batch_scripts\run_multi_workflow_report.bat
```

This will process multiple workflows and generate comprehensive ETN regression reports.

## 📋 **Available Options**

### **1. Multi-Workflow Processing (Recommended)**
```batch
# Using batch configuration file
batch_scripts\run_batch_multi_workflow.bat

# Interactive setup
batch_scripts\run_multi_workflow_report.bat
```

### **2. Multiple Workflows (Advanced)**
```batch
# Interactive mode - prompts for each workflow run ID
run_multi_workflow_report.bat

# Batch mode - uses workflow_runs.json
run_batch_multi_workflow.bat
```

### **3. Command Line Options**
```bash
# Basic usage (regression is default)
python main.py 17890913910

# Specify report type
python main.py 17890913910 --report-type regression

# Custom output directory
python main.py 17890913910 --output-dir "./my_reports"

# Include historical data
python main.py 17890913910 --include-historical
```

## 📊 **Report Types Available**

- **`regression`** ✅ ← **ETN Format (Default)**
- `detailed` - Comprehensive technical report
- `executive` - High-level summary  
- `team` - Team-focused format
- `failure` - Failure analysis only
- `slack` - Slack-ready format
- `all` - Generate all report types

## 🔧 **What Was Fixed**

**Problem**: The batch file was calling `publisher.py` which expected separate `--u575-run-id` and `--h743-run-id` arguments.

**Solution**: Updated batch file to use `main.py` which accepts a single run ID and defaults to regression format.

**Old Command**: `python publisher.py 17890913910` ❌  
**New Command**: `python main.py 17890913910 --report-type regression` ✅

## 🎯 **For Your Use Case**

Use the multi-workflow batch script for your reporting needs:

1. ✅ **Accepts single run ID** (17890913910)
2. ✅ **Generates ETN regression format** (default)
3. ✅ **Creates all ETN reports** (status, email, JIRA)
4. ✅ **Uses backward-compatible interface**
5. ✅ **Works exactly as expected**

## 💡 **Next Steps**

- **Use the multi-workflow script**: `run_multi_workflow_report.bat 17890913910`
- **For multiple boards**: Use `run_multi_workflow_report.bat` when you have separate U575/H743 run IDs
- **Daily workflow**: Continue using single batch file for combined runs

Your original workflow is now **fully restored and working**! 🎉
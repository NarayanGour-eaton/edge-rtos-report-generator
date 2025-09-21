# Project Structure

The GitHub Report Automation project is designed to generate consolidated reports from nightly workflow runs. Its folder structure has been organized for clarity, maintainability, and ease of use.

## Folder Structure

```
github_report_automation/
├── core/                    # Core functionality modules
│   ├── github_api_client.py      # GitHub API interaction
│   └── artifact_processor.py     # Artifact processing logic
├── generators/              # Report generation modules
│   ├── consolidated_performance_generator.py # Performance consolidation
│   ├── email_report_generator.py # Email-formatted reports
│   ├── performance_report_generator.py # Performance analysis
│   ├── regression_report_generator.py # Regression status reports
│   ├── report_generator.py       # Basic report generation
│   └── tabular_report_generator.py # Tabular format reports
├── publishers/              # Report publishing modules
│   ├── daily_publisher.py        # Daily report publishing
│   ├── publisher.py              # Report publishing
│   └── multi_publisher.py         # Multi-workflow publishing
├── config/                  # Configuration files
│   ├── config.py                 # Configuration management
│   └── config.json               # Configuration data
├── batch_scripts/           # Windows batch execution scripts
│   ├── run_batch_multi_workflow.bat # Batch multi-workflow
│   ├── run_consolidated_performance.bat # Consolidated performance
│   ├── run_multi_workflow_report.bat # Multi-workflow reports
│   └── run_performance_reports.bat # Performance reports
├── docs/                    # Documentation
│   ├── README.md                 # Main documentation
│   ├── README_GITHUB.md          # GitHub-specific docs
│   ├── USAGE_GUIDE.md            # Usage instructions
│   ├── QUICK_START.md            # Team quick start
│   ├── GITHUB_TOKEN_SETUP.md     # Token setup guide
│   ├── MULTI_WORKFLOW_README.md  # Multi-workflow docs
│   ├── PERFORMANCE_REPORTS.md    # Performance reporting
│   ├── CONSOLIDATED_PERFORMANCE.md # Consolidated docs
│   ├── PYTEST_FILTER_UPDATE.md  # PyTest filtering
│   └── PYTR_HTML_SUPPORT.md      # HTML report support
├── samples/                 # Sample files and outputs
│   ├── sample_report_with_quick_links.html # Sample HTML report
│   ├── SAMPLE_tabular_report_output.txt    # Sample tabular output
│   └── workflow_runs.json                  # Sample workflow data
├── main.py                  # Main entry point
└── requirements.txt         # Python dependencies
```

## Usage

### Main Entry Point
```bash
python main.py --run-id 12345 --report-type regression
```

### Batch Scripts (Windows)
```cmd
# Multi-workflow batch processing
batch_scripts\run_batch_multi_workflow.bat

# Interactive multi-workflow reports  
batch_scripts\run_multi_workflow_report.bat

# Performance analysis
batch_scripts\run_performance_reports.bat

# Consolidated performance dashboard
batch_scripts\run_consolidated_performance.bat
```

### Direct Module Usage
```python
# Import core modules
from core.github_api_client import GitHubAPIClient
from core.artifact_processor import ArtifactProcessor

# Import generators
from generators.regression_report_generator import RegressionReportGenerator
from generators.tabular_report_generator import TabularReportGenerator

# Import config
from config.config import Config
```

## Use Cases by Folder

### Core (core/)
- Essential system functionality
- API interactions
- Data processing

### Generators (generators/)
- Creating different report formats
- Processing test results into readable formats
- Format-specific report generation

### Publishers (publishers/)
- Distributing reports to different channels
- Team-specific formatting and distribution
- Automated publishing workflows

### Config (config/)
- System configuration
- Environment-specific settings
- API credentials and endpoints

### Batch Scripts (batch_scripts/)
- Windows automation
- Quick execution of common tasks
- Batch processing workflows

### Docs (docs/)
- User guides and documentation
- API documentation
- Setup and configuration guides

### Samples (samples/)
- Example outputs and templates
- Test data and sample configurations
- Reference implementations
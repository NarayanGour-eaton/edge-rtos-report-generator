# 🚀 Edge RTOS GitHub Actions Report Automation

Automated regression testing report generation system for Edge RTOS development, integrating with GitHub Actions workflows to provide comprehensive test analysis and reporting.

## ✨ Features

- **📊 Multi-Format Reports**: Generate tabular (text/HTML/CSV), regression status, and email reports
- **🔗 GitHub Integration**: Direct links to GitHub Actions runs in all reports
- **📈 Comprehensive Analytics**: Test statistics, failure analysis, and trend tracking
- **🏗️ Multi-Workflow Support**: Process multiple board types (U575, H743, etc.) in unified reports
- **⚡ Automated Publishing**: Batch scripts for scheduled report generation
- **📱 Quick Links**: Integration with PXGreen bugs tracking and SharePoint dashboards

## 🛠️ Quick Start

### Prerequisites
- Python 3.9+
- GitHub Personal Access Token
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/edge-rtos-github-automation.git
   cd edge-rtos-github-automation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup GitHub token:**
   - Create a GitHub Personal Access Token with `repo` and `actions:read` permissions
   - Set environment variable: `GITHUB_TOKEN=your_token_here`

4. **Configure workflows:**
   ```bash
   # Edit config.json with your workflow run IDs
   # Update repository settings in config.py
   ```

### Usage

**Generate Multi-Workflow Reports:**
```bash
python multi_publisher.py
```

**Generate Tabular Reports:**
```bash
python tabular_report_generator.py
```

**Batch Processing:**
```bash
# Windows
run_multi_workflow_report.bat

# Manual execution
python multi_publisher.py --config workflow_runs.json
```

## 📋 Report Formats

- **📊 Tabular Reports**: Clean table format with clickable GitHub Actions links
- **📧 Email Summaries**: Automated regression status notifications  
- **📈 Regression Analysis**: Edge RTOS-formatted status reports with branch tracking
- **💻 HTML Reports**: Interactive web reports with quick links

## 🔧 Configuration

### workflow_runs.json
```json
{
  "multi_workflow_runs": [
    {
      "run_id": "17811893255",
      "board_type": "U575",
      "description": "STM32U575 Development Board Tests"
    }
  ]
}
```

### Environment Variables
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxx    # Required: GitHub API access
GITHUB_REPO_OWNER=etn-ccis       # Optional: Default repository owner
```

## 📁 Project Structure

```
├── multi_publisher.py       # Main automation script
├── tabular_report_generator.py  # Tabular format reports
├── github_api_client.py         # GitHub API integration
├── regression_report_generator.py # Edge RTOS regression reports
├── config.py                    # Configuration classes
├── workflow_runs.json           # Workflow configurations
├── requirements.txt             # Python dependencies
├── run_*.bat                    # Batch execution scripts
└── nightly_reports/            # Generated reports output
```

## 🎯 Key Scripts

| Script | Purpose |
|--------|---------|
| `multi_publisher.py` | Multi-workflow automation with comprehensive reporting |
| `tabular_report_generator.py` | Generate table-format reports (text/HTML/CSV) |
| `github_api_client.py` | GitHub REST API integration with pagination |
| `regression_report_generator.py` | Edge RTOS-format regression status reports |

## 🔗 Integration Links

- **PXGreen Bugs**: Regression failure tracking
- **SharePoint Dashboard**: Nightly regression status spreadsheet
- **GitHub Actions**: Direct links to workflow runs in all reports

## 🚨 Security Notes

- **Never commit GitHub tokens** to version control
- Use environment variables or secure credential storage
- Review `.gitignore` to ensure sensitive files are excluded

## 📊 Sample Output

### Tabular Report Format:
```
BL Edge (RTOS) regression test status - 2025/09/21
+===============================================+
| U575 (STM32U575 Development Board Tests)     | Passed | 2553 | 2268 | 0 | 281 |
|   ➤ https://github.com/etn-ccis/edge-rtos-github-builds/actions/runs/17811893255 |
+===============================================+
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Check existing documentation in `/docs/` folder
- Review troubleshooting guides in `GITHUB_TOKEN_SETUP.md`
- Open an issue for bugs or feature requests

---
**Built with ❤️ for Edge RTOS Development Team**
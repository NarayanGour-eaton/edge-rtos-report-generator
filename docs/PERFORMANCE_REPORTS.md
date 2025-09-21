# 🔬 Performance Report Generator

Converts dynamic performance CSV data from ETN RTOS testing into interactive HTML reports with comprehensive BLR (Board Level Runtime) metrics analysis.

## ✨ Features

- **📊 CSV to HTML Conversion**: Transform raw performance data into interactive reports
- **🎯 Threshold Analysis**: Automatic pass/fail status based on performance thresholds  
- **📈 Performance Impact Calculation**: Show percentage changes between before/after metrics
- **🔍 Test-by-Test Breakdown**: Detailed analysis for each performance test
- **📋 Summary Statistics**: Overview of all performance metrics with pass/fail counts
- **🎨 Professional Styling**: Clean, readable HTML reports with color-coded results

## 📁 Input Format

The generator expects CSV files named `dynamic_performance_data.csv` with the following structure:

```csv
Class Name,Parameters,Before test execution Metrics,After test execution Metrics,Threshold Value,Status
"px_green\tests\functional_test\iot\test_example.py 09/18/2025, 05:52:20"
,BLR statistics for maximum heap usage in %,6,8,100,Pass
,BLR statistics for maximum cpu utilization in %,100,100,100,Pass
,BLR statistics for maximum tasker loop time in us,11431,343282,250000,Fail
```

## 🚀 Usage

### Command Line Usage:

```bash
# Generate report for specific CSV file
python performance_report_generator.py "path/to/dynamic_performance_data.csv"

# Auto-discover and process all CSV files
run_performance_reports.bat
```

### Integrated Usage:

The performance report generator is automatically integrated into the main automation system:

```bash
# Performance reports are generated automatically
python multi_publisher.py
```

## 📊 Generated Report Features

### 📈 Summary Dashboard
- Total number of tests processed
- Total performance metrics analyzed  
- Pass/Fail counts with visual indicators
- Color-coded summary cards

### 🔍 Detailed Test Analysis
- **Test Information**: Name, execution timestamp
- **Performance Metrics Table**: 
  - Parameter name (cleaned and formatted)
  - Before/After values with monospace formatting
  - Threshold values for comparison
  - Pass/Fail status with color coding
  - Performance impact percentage calculation

### 📋 BLR Metrics Covered
- **Memory Usage**: Maximum heap usage percentages
- **CPU Utilization**: Maximum, average, and median CPU usage
- **Stack Usage**: Maximum stack usage and thread information
- **Task Performance**: Tasker loop time statistics (min/max/average/median)
- **Security**: mbedTLS heap usage tracking

## 🎨 Report Styling

- **Professional Design**: Clean, modern interface using Segoe UI font family
- **Color Coding**: 
  - 🟢 Green backgrounds for passed metrics
  - 🔴 Red backgrounds for failed metrics  
  - 🔵 Blue accents for headers and highlights
- **Responsive Layout**: Grid-based summary cards that adapt to screen size
- **Interactive Elements**: Hover effects and clear visual hierarchy

## 📁 File Organization

```
nightly_reports/
└── BFT_h743zi_dev/
    └── suite_BLR_Test_IoT_SNTP/
        ├── dynamic_performance_data.csv          # Input CSV
        └── dynamic_performance_data_report.html  # Generated HTML report
```

## 🔧 Integration Points

### With Main Automation System:
- Automatically discovers CSV files in `nightly_reports/` directory
- Generates HTML reports for each CSV file found
- Adds performance reports to the main report generation summary

### Batch Processing:
- `run_performance_reports.bat` processes all CSV files in the workspace
- Supports individual file processing via command line argument

## 🎯 Performance Metrics Interpretation

### ✅ Pass Criteria:
- Metric value is within the specified threshold
- Green color coding in the report
- Contributes to overall pass count

### ❌ Fail Criteria:  
- Metric value exceeds the threshold limit
- Red color coding in the report
- Requires investigation and optimization

### 📊 Impact Analysis:
- **↑ +X%**: Performance degradation (increase in resource usage)
- **↓ -X%**: Performance improvement (decrease in resource usage)  
- **No change**: Stable performance between test runs

## 🔗 Integration with ETN Workflow

The performance reports complement the existing ETN automation by:

1. **Automatic Discovery**: Finds all CSV files during report generation
2. **Integrated Reporting**: Includes performance reports in main report summary  
3. **Quality Gates**: Provides detailed analysis for performance regression detection
4. **Historical Tracking**: Enables comparison of performance metrics over time

## 📋 Example Output

```html
🔬 BLR Performance Analysis Report
Generated from: dynamic_performance_data.csv
Generated: 2025-09-21 18:45:32

📈 Performance Summary
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Total Tests │Total Metrics│Passed Metrics│Failed Metrics│
│     17      │    187      │    174      │     13      │
└─────────────┴─────────────┴─────────────┴─────────────┘

📊 Test Performance Details
Test #1: iot\test_c2d_get_multiple_param.py
Executed: 09/18/2025, 05:52:20
[Detailed metrics table with color-coded pass/fail status]
```

## 🚨 Important Notes

- **Threshold Compliance**: Always review failed metrics to identify performance regressions
- **Resource Monitoring**: Pay attention to heap and CPU utilization trends
- **Task Performance**: Monitor tasker loop times for system responsiveness
- **Integration**: Performance reports are automatically included in ETN multi-workflow reports

---
**Built for ETN Edge RTOS Performance Analysis** 🚀
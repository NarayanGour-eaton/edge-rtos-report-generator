# 🔬 Consolidated Performance Dashboard

**Multi-Board BLR Performance Analysis System**

Combines performance data from all boards and test suites into a unified dashboard for comprehensive performance analysis and comparison.

## ✨ Key Features

- **🏗️ Multi-Board Comparison**: Side-by-side performance comparison across H743, U575, and other boards
- **📊 Overall Success Rate**: Consolidated metrics with visual progress indicators
- **🚨 Critical Issues Detection**: Automatic identification of performance bottlenecks
- **💡 Optimization Recommendations**: AI-driven suggestions for performance improvements
- **📈 Trend Analysis**: Performance patterns across different test suites

## 🎯 Dashboard Components

### **📈 Overall Performance Summary**
- **Total Boards**: Number of boards analyzed (e.g., 2 boards)
- **Test Suites**: Total test suites processed (e.g., 14 suites)
- **Total Tests**: Individual test cases analyzed 
- **Total Metrics**: All BLR performance measurements
- **Success Rate**: Overall percentage with visual progress bar

### **🏗️ Board Performance Comparison**
| Board | Test Suites | Total Tests | Metrics | Passed | Failed | Success Rate | Status |
|-------|------------|-------------|---------|--------|--------|-------------|---------|
| H743 (STM32H743) | 7 | 119 | 1,309 | 1,196 | 113 | 91.4% | Good |
| U575 (STM32U575) | 7 | 112 | 1,232 | 1,201 | 31 | 97.5% | Excellent |

### **🔍 Detailed Performance Metrics**
- **Per-Board Analysis**: Detailed breakdown by board type
- **Suite-Level Metrics**: Individual test suite performance
- **Failed Metrics Only**: Focus on issues requiring attention
- **Threshold Analysis**: Comparison against performance limits

### **📊 Performance Analysis & Recommendations**
- **Critical Issues**: Top failing metrics across all boards
- **Optimization Targets**: Priority areas for improvement
- **Recommendations**: Specific suggestions for performance tuning

## 🚀 Usage

### **Automatic Generation (Recommended):**
```bash
# Consolidated dashboard included in main automation
python multi_publisher.py
```

### **Standalone Generation:**
```bash
# Generate consolidated report only
python consolidated_performance_generator.py

# Or use batch script
run_consolidated_performance.bat
```

### **Custom Directory:**
```bash
# Process CSV files from custom location
python consolidated_performance_generator.py --base-dir custom_reports --output dashboard.html
```

## 📁 Input Data Sources

The consolidator automatically discovers CSV files from:
```
nightly_reports/
├── BFT_h743zi_dev/
│   ├── suite_BLR_Test_IoT_SNTP/dynamic_performance_data.csv
│   ├── suite_Cert_Test/dynamic_performance_data.csv
│   └── suite_Rest_Test/dynamic_performance_data.csv
└── BFT_U575zi_q_dev/
    ├── suite_Modbus_RTU_Test/dynamic_performance_data.csv
    └── suite_Rest_FRAM_Test/dynamic_performance_data.csv
```

## 📊 Sample Analysis Output

```
🔬 Consolidated BLR Performance Dashboard
Multi-Board Performance Analysis
Generated: 2025-09-21 18:45:32

📈 Overall Performance Summary
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│Total Boards │ Test Suites │ Total Tests │Total Metrics│Passed Metrics│Failed Metrics│
│      2      │     14      │    231      │    2,541    │    2,397    │     144     │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘

Overall Success Rate: 94.3% ████████████████████░

🚨 Critical Performance Issues
⚠️ Maximum tasker loop time in us
Failed on 89 instances across boards
• H743 (STM32H743) - BLR_Test_IoT_SNTP: Value 4294965649 exceeds threshold 250000
• U575 (STM32U575) - Rest_Test: Value 343282 exceeds threshold 250000

💡 Performance Optimization Recommendations
🔴 Tasker Loop Time: Optimize task processing and reduce blocking operations
🔸 Memory Usage: Consider memory optimization techniques and heap management improvements
```

## 🎨 Visual Features

### **Color-Coded Status System:**
- **🟢 Excellent (≥95%)**: Outstanding performance, minimal issues
- **🔵 Good (90-94%)**: Acceptable performance with minor optimizations needed
- **🟡 Warning (80-89%)**: Moderate issues requiring attention  
- **🔴 Critical (<80%)**: Significant performance problems needing immediate action

### **Interactive Elements:**
- **Hover Effects**: Enhanced visual feedback on summary cards
- **Progress Bars**: Animated success rate indicators
- **Color Transitions**: Gradient progress bars reflecting performance levels
- **Expandable Sections**: Detailed metrics organized by board and suite

## 🔧 Integration Points

### **With Main ETN Automation:**
- Automatically generated as part of `multi_publisher.py`
- Included in main report summary and file listings
- Processes all available CSV data from current workflow runs

### **Standalone Operation:**
- Independent execution for ad-hoc analysis
- Custom directory support for historical data analysis
- Flexible output file naming and location

### **Performance Monitoring Workflow:**
1. **Data Collection**: CSV files generated during test execution
2. **Individual Reports**: Per-suite detailed performance analysis  
3. **Consolidated Dashboard**: Multi-board comparative analysis ← **This Feature**
4. **Trend Analysis**: Historical performance tracking (future enhancement)

## 🚨 Critical Metrics Monitored

### **Memory Performance:**
- **Heap Usage**: Maximum heap utilization percentage
- **mbedTLS Heap**: Security stack memory consumption
- **Stack Usage**: Maximum stack utilization per thread

### **CPU Performance:**
- **Maximum CPU**: Peak processor utilization
- **Average CPU**: Sustained processor load
- **Median CPU**: Typical processor utilization

### **Task Performance:**
- **Tasker Loop Time**: System responsiveness metrics
  - Minimum, Maximum, Average, Median loop times
  - Critical for real-time performance analysis

## 💡 Performance Optimization Workflow

1. **🔍 Identify Issues**: Review consolidated dashboard for failed metrics
2. **📊 Analyze Patterns**: Look for common failures across boards/suites
3. **🎯 Prioritize Fixes**: Focus on critical metrics affecting multiple tests
4. **🔧 Implement Solutions**: Apply recommended optimizations
5. **✅ Validate Results**: Re-run tests to confirm improvements

## 📋 Report File Locations

- **Consolidated Dashboard**: `nightly_reports/consolidated_performance_report_YYYY-MM-DD.html`
- **Individual Reports**: `nightly_reports/[BOARD]/[SUITE]/dynamic_performance_data_report.html`
- **Batch Scripts**: `run_consolidated_performance.bat` for easy execution

## 🎯 Benefits

- **🔍 Quick Overview**: Instant visibility into system-wide performance
- **📊 Data-Driven Decisions**: Quantitative basis for optimization priorities  
- **🚀 Efficiency Gains**: Reduced time identifying performance bottlenecks
- **📈 Quality Assurance**: Continuous monitoring of performance regression
- **👥 Team Collaboration**: Shared dashboard for cross-functional performance analysis

---
**Transform Raw Performance Data into Actionable Insights** 🚀
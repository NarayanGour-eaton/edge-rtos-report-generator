#!/usr/bin/env python3
"""
Performance CSV to HTML Report Generator

Converts dynamic_performance_data.csv files into interactive HTML reports
with performance metrics visualization and threshold analysis.
"""

import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class PerformanceReportGenerator:
    """Generate HTML reports from performance CSV data."""
    
    def __init__(self):
        self.performance_data = []
        
    def parse_csv_file(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """Parse the dynamic_performance_data.csv file."""
        performance_tests = []
        current_test = None
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                
                for row in csv_reader:
                    if len(row) == 0:
                        continue
                        
                    # Check if this is a test header row
                    if len(row) == 1 and 'px_green' in row[0]:
                        if current_test:
                            performance_tests.append(current_test)
                        
                        # Extract test info
                        test_info = row[0].strip('"')
                        current_test = {
                            'test_name': test_info,
                            'metrics': []
                        }
                        continue
                    
                    # Check for header row
                    if row[0] == 'Class Name':
                        continue
                        
                    # Parse metric rows
                    if len(row) >= 5 and current_test:
                        if row[0].strip():  # Skip empty first columns that are part of previous test
                            continue
                            
                        metric = {
                            'parameter': row[1].strip(),
                            'before': row[2].strip() if row[2] else 'N/A',
                            'after': row[3].strip() if row[3] else 'N/A',
                            'threshold': row[4].strip() if row[4] else 'N/A',
                            'status': row[5].strip() if len(row) > 5 else 'Unknown'
                        }
                        current_test['metrics'].append(metric)
                
                # Add the last test
                if current_test:
                    performance_tests.append(current_test)
                    
        except Exception as e:
            print(f"Error parsing CSV file: {e}")
            
        return performance_tests
        
    def generate_html_report(self, csv_file_path: str, output_file: str = None) -> str:
        """Generate HTML report from CSV file."""
        performance_tests = self.parse_csv_file(csv_file_path)
        
        if not performance_tests:
            return "<p>No performance data found in CSV file.</p>"
            
        if not output_file:
            csv_path = Path(csv_file_path)
            output_file = csv_path.parent / f"{csv_path.stem}_report.html"
            
        html_content = self._create_html_report(performance_tests, csv_file_path)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return str(output_file)
        
    def _create_html_report(self, performance_tests: List[Dict], source_file: str) -> str:
        """Create the complete HTML report."""
        html = []
        
        # HTML structure
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append("<meta charset='utf-8'>")
        html.append(f"<title>BLR Performance Report - {datetime.now().strftime('%Y-%m-%d')}</title>")
        html.append(self._get_css_styles())
        html.append("</head>")
        html.append("<body>")
        
        # Header
        html.append(f"<h1>🔬 BLR Performance Analysis Report</h1>")
        html.append(f"<p class='subtitle'>Generated from: {Path(source_file).name}</p>")
        html.append(f"<p class='timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        
        # Summary statistics
        html.append(self._generate_summary_section(performance_tests))
        
        # Performance tests
        html.append("<h2>📊 Test Performance Details</h2>")
        
        for i, test in enumerate(performance_tests, 1):
            html.append(self._generate_test_section(test, i))
            
        # Footer
        html.append(f"<div class='footer'>")
        html.append(f"<p>Report contains {len(performance_tests)} performance tests with BLR metrics analysis</p>")
        html.append("</div>")
        
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)
        
    def _generate_summary_section(self, performance_tests: List[Dict]) -> str:
        """Generate summary statistics section."""
        total_tests = len(performance_tests)
        total_metrics = sum(len(test['metrics']) for test in performance_tests)
        
        # Count pass/fail metrics
        passed_metrics = 0
        failed_metrics = 0
        
        for test in performance_tests:
            for metric in test['metrics']:
                if metric['status'].lower() == 'pass':
                    passed_metrics += 1
                elif metric['status'].lower() == 'fail':
                    failed_metrics += 1
                    
        html = []
        html.append("<div class='summary-section'>")
        html.append("<h2>📈 Performance Summary</h2>")
        html.append("<div class='summary-grid'>")
        html.append(f"<div class='summary-card'><h3>{total_tests}</h3><p>Total Tests</p></div>")
        html.append(f"<div class='summary-card'><h3>{total_metrics}</h3><p>Total Metrics</p></div>")
        html.append(f"<div class='summary-card pass'><h3>{passed_metrics}</h3><p>Passed Metrics</p></div>")
        html.append(f"<div class='summary-card fail'><h3>{failed_metrics}</h3><p>Failed Metrics</p></div>")
        html.append("</div>")
        html.append("</div>")
        
        return "\n".join(html)
        
    def _generate_test_section(self, test: Dict, test_number: int) -> str:
        """Generate HTML section for a single test."""
        html = []
        
        # Extract test name and timestamp
        test_info = test['test_name']
        test_name = test_info.split(' ')[0].replace('px_green\\tests\\functional_test\\', '')
        timestamp = test_info.split(' ', 1)[1] if ' ' in test_info else 'Unknown time'
        
        html.append(f"<div class='test-section'>")
        html.append(f"<h3 class='test-header'>Test #{test_number}: {test_name}</h3>")
        html.append(f"<p class='test-timestamp'>Executed: {timestamp}</p>")
        
        # Metrics table
        html.append("<table class='metrics-table'>")
        html.append("<thead>")
        html.append("<tr>")
        html.append("<th>Performance Metric</th>")
        html.append("<th>Before</th>")
        html.append("<th>After</th>")
        html.append("<th>Threshold</th>")
        html.append("<th>Status</th>")
        html.append("<th>Impact</th>")
        html.append("</tr>")
        html.append("</thead>")
        html.append("<tbody>")
        
        for metric in test['metrics']:
            html.append(self._generate_metric_row(metric))
            
        html.append("</tbody>")
        html.append("</table>")
        html.append("</div>")
        
        return "\n".join(html)
        
    def _generate_metric_row(self, metric: Dict) -> str:
        """Generate HTML row for a single metric."""
        status_class = 'pass' if metric['status'].lower() == 'pass' else 'fail'
        
        # Calculate impact if possible
        impact = self._calculate_impact(metric)
        
        # Clean up parameter name
        param_name = metric['parameter'].replace('BLR statistics for ', '').replace('BLR statictics for ', '')
        
        html = f"""
        <tr class='{status_class}'>
            <td class='metric-name'>{param_name}</td>
            <td class='metric-value'>{metric['before']}</td>
            <td class='metric-value'>{metric['after']}</td>
            <td class='threshold-value'>{metric['threshold']}</td>
            <td class='status-badge {status_class}'>{metric['status']}</td>
            <td class='impact'>{impact}</td>
        </tr>
        """
        return html
        
    def _calculate_impact(self, metric: Dict) -> str:
        """Calculate the performance impact between before and after values."""
        try:
            before = float(metric['before']) if metric['before'].replace('.', '').isdigit() else None
            after = float(metric['after']) if metric['after'].replace('.', '').isdigit() else None
            
            if before is not None and after is not None and before != 0:
                change_pct = ((after - before) / before) * 100
                if abs(change_pct) < 0.1:
                    return "No change"
                elif change_pct > 0:
                    return f"↑ +{change_pct:.1f}%"
                else:
                    return f"↓ {change_pct:.1f}%"
            return "N/A"
        except:
            return "N/A"
            
    def _get_css_styles(self) -> str:
        """Return CSS styles for the HTML report."""
        return """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            
            .subtitle {
                text-align: center;
                color: #7f8c8d;
                font-size: 1.2em;
                margin-bottom: 5px;
            }
            
            .timestamp {
                text-align: center;
                color: #95a5a6;
                font-style: italic;
                margin-bottom: 30px;
            }
            
            .summary-section {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            
            .summary-card {
                background: #ecf0f1;
                padding: 20px;
                border-radius: 6px;
                text-align: center;
                border-left: 4px solid #3498db;
            }
            
            .summary-card.pass {
                border-left-color: #27ae60;
                background: #d5f4e6;
            }
            
            .summary-card.fail {
                border-left-color: #e74c3c;
                background: #fceaea;
            }
            
            .summary-card h3 {
                font-size: 2em;
                margin: 0;
                color: #2c3e50;
            }
            
            .summary-card p {
                margin: 5px 0 0 0;
                color: #7f8c8d;
                font-weight: 500;
            }
            
            .test-section {
                background: white;
                margin-bottom: 25px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .test-header {
                background: #34495e;
                color: white;
                padding: 15px 20px;
                margin: 0;
                font-size: 1.3em;
            }
            
            .test-timestamp {
                background: #ecf0f1;
                padding: 10px 20px;
                margin: 0;
                color: #7f8c8d;
                font-style: italic;
            }
            
            .metrics-table {
                width: 100%;
                border-collapse: collapse;
            }
            
            .metrics-table th {
                background: #f8f9fa;
                padding: 12px;
                text-align: left;
                border-bottom: 2px solid #dee2e6;
                font-weight: 600;
                color: #2c3e50;
            }
            
            .metrics-table td {
                padding: 10px 12px;
                border-bottom: 1px solid #dee2e6;
            }
            
            .metrics-table tr.pass {
                background-color: #f8fff9;
            }
            
            .metrics-table tr.fail {
                background-color: #fff8f8;
            }
            
            .metric-name {
                font-weight: 500;
                color: #2c3e50;
                max-width: 300px;
            }
            
            .metric-value, .threshold-value {
                text-align: center;
                font-family: 'Courier New', monospace;
                font-weight: 500;
            }
            
            .status-badge {
                text-align: center;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 0.85em;
            }
            
            .status-badge.pass {
                color: #27ae60;
            }
            
            .status-badge.fail {
                color: #e74c3c;
            }
            
            .impact {
                text-align: center;
                font-weight: 500;
            }
            
            .footer {
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                background: white;
                border-radius: 8px;
                color: #7f8c8d;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            h2 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
        </style>
        """


def main():
    """Example usage of the PerformanceReportGenerator."""
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # Default to the provided CSV file path
        csv_file = "nightly_reports/BFT_h743zi_dev/suite_BLR_Test_IoT_SNTP/dynamic_performance_data.csv"
    
    if not Path(csv_file).exists():
        print(f"❌ CSV file not found: {csv_file}")
        return
    
    generator = PerformanceReportGenerator()
    output_file = generator.generate_html_report(csv_file)
    
    print(f"✅ HTML performance report generated: {output_file}")
    print(f"🌐 Open in browser: file://{Path(output_file).absolute()}")


if __name__ == "__main__":
    main()
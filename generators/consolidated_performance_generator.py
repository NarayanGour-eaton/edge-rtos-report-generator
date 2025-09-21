#!/usr/bin/env python3
"""
Consolidated Performance Report Generator

Combines multiple dynamic_performance_data.csv files from different boards/suites
into a single comprehensive performance dashboard with comparative analysis.
"""

import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
from collections import defaultdict


class ConsolidatedPerformanceReportGenerator:
    """Generate consolidated HTML reports from multiple performance CSV files."""
    
    def __init__(self):
        self.all_performance_data = []
        self.board_summaries = {}
        
    def discover_csv_files(self, base_dir: str = "nightly_reports") -> List[Tuple[str, str, str]]:
        """Discover all dynamic_performance_data.csv files and extract board/suite info."""
        csv_files = []
        base_path = Path(base_dir)
        
        if not base_path.exists():
            print(f"❌ Directory not found: {base_dir}")
            return csv_files
            
        # Find all CSV files
        for csv_file in base_path.rglob("dynamic_performance_data.csv"):
            # Extract board and suite from path
            path_parts = csv_file.parts
            board_name = "Unknown Board"
            suite_name = "Unknown Suite"
            
            # Try to extract board name (e.g., BFT_h743zi_dev)
            for part in path_parts:
                if part.startswith(('BFT_', 'CFT_', 'PFT_')) and '_dev' in part:
                    board_name = part
                    break
                    
            # Try to extract suite name (e.g., suite_BLR_Test_IoT_SNTP)
            for part in path_parts:
                if part.startswith('suite_'):
                    suite_name = part.replace('suite_', '')
                    break
                    
            csv_files.append((str(csv_file), board_name, suite_name))
            
        return csv_files
        
    def parse_all_csv_files(self, csv_files: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """Parse all CSV files and organize by board/suite."""
        consolidated_data = {
            'boards': {},
            'overall_stats': {
                'total_tests': 0,
                'total_metrics': 0,
                'passed_metrics': 0,
                'failed_metrics': 0,
                'total_boards': 0,
                'total_suites': 0
            }
        }
        
        for csv_file, board_name, suite_name in csv_files:
            try:
                print(f"📊 Processing: {board_name} - {suite_name}")
                suite_data = self.parse_single_csv(csv_file)
                
                if board_name not in consolidated_data['boards']:
                    consolidated_data['boards'][board_name] = {
                        'suites': {},
                        'board_stats': {
                            'total_tests': 0,
                            'total_metrics': 0,
                            'passed_metrics': 0,
                            'failed_metrics': 0
                        }
                    }
                    
                # Add suite data
                consolidated_data['boards'][board_name]['suites'][suite_name] = suite_data
                
                # Update board stats
                board_stats = consolidated_data['boards'][board_name]['board_stats']
                board_stats['total_tests'] += len(suite_data)
                
                for test in suite_data:
                    board_stats['total_metrics'] += len(test['metrics'])
                    consolidated_data['overall_stats']['total_metrics'] += len(test['metrics'])
                    
                    for metric in test['metrics']:
                        if metric['status'].lower() == 'pass':
                            board_stats['passed_metrics'] += 1
                            consolidated_data['overall_stats']['passed_metrics'] += 1
                        elif metric['status'].lower() == 'fail':
                            board_stats['failed_metrics'] += 1
                            consolidated_data['overall_stats']['failed_metrics'] += 1
                
                # Update overall stats
                consolidated_data['overall_stats']['total_tests'] += len(suite_data)
                
            except Exception as e:
                print(f"❌ Error processing {csv_file}: {e}")
                
        # Final stats
        consolidated_data['overall_stats']['total_boards'] = len(consolidated_data['boards'])
        consolidated_data['overall_stats']['total_suites'] = sum(
            len(board_data['suites']) for board_data in consolidated_data['boards'].values()
        )
        
        return consolidated_data
        
    def parse_single_csv(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """Parse a single CSV file (reusing logic from performance_report_generator)."""
        performance_tests = []
        current_test = None
        
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
                    if row[0].strip():  # Skip empty first columns
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
                
        return performance_tests
        
    def generate_consolidated_report(self, base_dir: str = "nightly_reports", 
                                   output_file: str = None) -> str:
        """Generate consolidated HTML report from all CSV files."""
        print("🔬 Generating Consolidated Performance Report...")
        print("=" * 55)
        
        # Discover all CSV files
        csv_files = self.discover_csv_files(base_dir)
        if not csv_files:
            print("❌ No performance CSV files found")
            return ""
            
        print(f"Found {len(csv_files)} performance CSV files across boards:")
        for csv_file, board, suite in csv_files:
            print(f"   📊 {board} - {suite}")
            
        # Parse all data
        consolidated_data = self.parse_all_csv_files(csv_files)
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y-%m-%d')
            output_file = f"nightly_reports/consolidated_performance_report_{timestamp}.html"
            
        # Generate HTML
        html_content = self._create_consolidated_html(consolidated_data, csv_files)
        
        # Write to file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"\n✅ Consolidated report generated: {output_file}")
        return str(output_path.absolute())
        
    def _create_consolidated_html(self, data: Dict[str, Any], csv_files: List[Tuple]) -> str:
        """Create the consolidated HTML report."""
        html = []
        
        # HTML structure
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append("<meta charset='utf-8'>")
        html.append(f"<title>Consolidated BLR Performance Report - {datetime.now().strftime('%Y-%m-%d')}</title>")
        html.append(self._get_consolidated_css())
        html.append("</head>")
        html.append("<body>")
        
        # Header
        html.append("<h1>🔬 Consolidated BLR Performance Dashboard</h1>")
        html.append(f"<p class='subtitle'>Multi-Board Performance Analysis</p>")
        html.append(f"<p class='timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        
        # Overall summary
        html.append(self._generate_overall_summary(data['overall_stats']))
        
        # Board comparison section
        html.append(self._generate_board_comparison(data['boards']))
        
        # Detailed performance metrics
        html.append(self._generate_detailed_metrics(data['boards']))
        
        # Performance trends analysis
        html.append(self._generate_performance_trends(data['boards']))
        
        # Footer
        html.append("<div class='footer'>")
        html.append(f"<p>Report consolidates {len(csv_files)} performance test suites across {data['overall_stats']['total_boards']} boards</p>")
        html.append("<p>🎯 Focus on failed metrics for performance optimization opportunities</p>")
        html.append("</div>")
        
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)
        
    def _generate_overall_summary(self, stats: Dict[str, int]) -> str:
        """Generate overall summary section."""
        html = []
        html.append("<div class='summary-section'>")
        html.append("<h2>📈 Overall Performance Summary</h2>")
        html.append("<div class='summary-grid'>")
        
        # Summary cards
        cards = [
            (stats['total_boards'], "Total Boards", "boards"),
            (stats['total_suites'], "Test Suites", "suites"),
            (stats['total_tests'], "Total Tests", "tests"),
            (stats['total_metrics'], "Total Metrics", "metrics"),
            (stats['passed_metrics'], "Passed Metrics", "pass"),
            (stats['failed_metrics'], "Failed Metrics", "fail"),
        ]
        
        for value, label, card_type in cards:
            html.append(f"<div class='summary-card {card_type}'>")
            html.append(f"<h3>{value}</h3>")
            html.append(f"<p>{label}</p>")
            html.append("</div>")
            
        html.append("</div>")
        
        # Success rate
        if stats['total_metrics'] > 0:
            success_rate = (stats['passed_metrics'] / stats['total_metrics']) * 100
            html.append(f"<div class='success-rate'>")
            html.append(f"<h3>Overall Success Rate: {success_rate:.1f}%</h3>")
            html.append(f"<div class='progress-bar'>")
            html.append(f"<div class='progress-fill' style='width: {success_rate}%'></div>")
            html.append("</div>")
            html.append("</div>")
            
        html.append("</div>")
        return "\n".join(html)
        
    def _generate_board_comparison(self, boards_data: Dict[str, Any]) -> str:
        """Generate board-by-board comparison table."""
        html = []
        html.append("<div class='board-comparison'>")
        html.append("<h2>🏗️ Board Performance Comparison</h2>")
        html.append("<table class='comparison-table'>")
        html.append("<thead>")
        html.append("<tr>")
        html.append("<th>Board</th>")
        html.append("<th>Test Suites</th>")
        html.append("<th>Total Tests</th>")
        html.append("<th>Total Metrics</th>")
        html.append("<th>Passed</th>")
        html.append("<th>Failed</th>")
        html.append("<th>Success Rate</th>")
        html.append("<th>Status</th>")
        html.append("</tr>")
        html.append("</thead>")
        html.append("<tbody>")
        
        for board_name, board_data in boards_data.items():
            stats = board_data['board_stats']
            suite_count = len(board_data['suites'])
            
            if stats['total_metrics'] > 0:
                success_rate = (stats['passed_metrics'] / stats['total_metrics']) * 100
            else:
                success_rate = 0
                
            status_class = "excellent" if success_rate >= 95 else "good" if success_rate >= 90 else "warning" if success_rate >= 80 else "critical"
            status_text = "Excellent" if success_rate >= 95 else "Good" if success_rate >= 90 else "Warning" if success_rate >= 80 else "Critical"
            
            html.append(f"<tr class='{status_class}'>")
            html.append(f"<td class='board-name'>{self._format_board_name(board_name)}</td>")
            html.append(f"<td class='center'>{suite_count}</td>")
            html.append(f"<td class='center'>{stats['total_tests']}</td>")
            html.append(f"<td class='center'>{stats['total_metrics']}</td>")
            html.append(f"<td class='center pass'>{stats['passed_metrics']}</td>")
            html.append(f"<td class='center fail'>{stats['failed_metrics']}</td>")
            html.append(f"<td class='center'>{success_rate:.1f}%</td>")
            html.append(f"<td class='center status-{status_class}'>{status_text}</td>")
            html.append("</tr>")
            
        html.append("</tbody>")
        html.append("</table>")
        html.append("</div>")
        
        return "\n".join(html)
        
    def _generate_detailed_metrics(self, boards_data: Dict[str, Any]) -> str:
        """Generate detailed metrics by board and suite."""
        html = []
        html.append("<div class='detailed-metrics'>")
        html.append("<h2>🔍 Detailed Performance Metrics</h2>")
        
        for board_name, board_data in boards_data.items():
            html.append(f"<div class='board-section'>")
            html.append(f"<h3 class='board-header'>🏗️ {self._format_board_name(board_name)}</h3>")
            
            for suite_name, suite_tests in board_data['suites'].items():
                html.append(f"<div class='suite-section'>")
                html.append(f"<h4 class='suite-header'>📊 {suite_name.replace('_', ' ').title()}</h4>")
                
                # Count suite metrics
                suite_passed = 0
                suite_failed = 0
                suite_total = 0
                
                for test in suite_tests:
                    for metric in test['metrics']:
                        suite_total += 1
                        if metric['status'].lower() == 'pass':
                            suite_passed += 1
                        elif metric['status'].lower() == 'fail':
                            suite_failed += 1
                            
                suite_success = (suite_passed / suite_total * 100) if suite_total > 0 else 0
                
                html.append(f"<div class='suite-summary'>")
                html.append(f"<span class='suite-stats'>")
                html.append(f"Tests: {len(suite_tests)} | ")
                html.append(f"Metrics: {suite_total} | ")
                html.append(f"<span class='pass'>Passed: {suite_passed}</span> | ")
                html.append(f"<span class='fail'>Failed: {suite_failed}</span> | ")
                html.append(f"Success: {suite_success:.1f}%")
                html.append("</span>")
                html.append("</div>")
                
                # Show failed metrics only for cleaner view
                failed_metrics = []
                for test in suite_tests:
                    for metric in test['metrics']:
                        if metric['status'].lower() == 'fail':
                            failed_metrics.append({
                                'test': test['test_name'],
                                'metric': metric
                            })
                            
                if failed_metrics:
                    html.append("<div class='failed-metrics'>")
                    html.append("<h5>❌ Failed Metrics (Requires Attention):</h5>")
                    html.append("<ul>")
                    for failed in failed_metrics:
                        test_name = failed['test'].split('\\')[-1].split(' ')[0] if '\\' in failed['test'] else failed['test']
                        param_name = failed['metric']['parameter'].replace('BLR statistics for ', '').replace('BLR statictics for ', '')
                        html.append(f"<li><strong>{test_name}</strong>: {param_name} - ")
                        html.append(f"Value: {failed['metric']['after']}, Threshold: {failed['metric']['threshold']}</li>")
                    html.append("</ul>")
                    html.append("</div>")
                else:
                    html.append("<div class='all-passed'>✅ All metrics passed thresholds</div>")
                    
                html.append("</div>")  # suite-section
            html.append("</div>")  # board-section
            
        html.append("</div>")  # detailed-metrics
        return "\n".join(html)
        
    def _generate_performance_trends(self, boards_data: Dict[str, Any]) -> str:
        """Generate performance trends analysis."""
        html = []
        html.append("<div class='trends-section'>")
        html.append("<h2>📊 Performance Analysis & Recommendations</h2>")
        
        # Collect all failed metrics for analysis
        critical_metrics = defaultdict(list)
        
        for board_name, board_data in boards_data.items():
            for suite_name, suite_tests in board_data['suites'].items():
                for test in suite_tests:
                    for metric in test['metrics']:
                        if metric['status'].lower() == 'fail':
                            metric_type = metric['parameter'].replace('BLR statistics for ', '').replace('BLR statictics for ', '')
                            critical_metrics[metric_type].append({
                                'board': board_name,
                                'suite': suite_name,
                                'value': metric['after'],
                                'threshold': metric['threshold']
                            })
                            
        if critical_metrics:
            html.append("<div class='critical-analysis'>")
            html.append("<h3>🚨 Critical Performance Issues</h3>")
            
            for metric_type, failures in critical_metrics.items():
                html.append(f"<div class='metric-analysis'>")
                html.append(f"<h4>⚠️ {metric_type}</h4>")
                html.append(f"<p><strong>Failed on {len(failures)} instances across boards</strong></p>")
                html.append("<ul>")
                
                for failure in failures[:5]:  # Show top 5
                    board_formatted = self._format_board_name(failure['board'])
                    html.append(f"<li>{board_formatted} - {failure['suite']}: ")
                    html.append(f"Value {failure['value']} exceeds threshold {failure['threshold']}</li>")
                    
                if len(failures) > 5:
                    html.append(f"<li><em>... and {len(failures) - 5} more instances</em></li>")
                    
                html.append("</ul>")
                html.append("</div>")
                
            html.append("</div>")
            
            # Recommendations
            html.append("<div class='recommendations'>")
            html.append("<h3>💡 Performance Optimization Recommendations</h3>")
            html.append("<div class='recommendation-grid'>")
            
            recommendations = [
                ("Memory Usage", "Consider memory optimization techniques and heap management improvements"),
                ("CPU Utilization", "Review task scheduling and optimize high CPU usage operations"),
                ("Stack Usage", "Analyze stack requirements and optimize recursive functions"),
                ("Tasker Loop Time", "Optimize task processing and reduce blocking operations"),
            ]
            
            for title, desc in recommendations:
                if any(title.lower() in metric.lower() for metric in critical_metrics.keys()):
                    html.append(f"<div class='recommendation-card priority'>")
                else:
                    html.append(f"<div class='recommendation-card'>")
                html.append(f"<h4>{title}</h4>")
                html.append(f"<p>{desc}</p>")
                html.append("</div>")
                
            html.append("</div>")
            html.append("</div>")
        else:
            html.append("<div class='excellent-performance'>")
            html.append("<h3>🎉 Excellent Performance Results</h3>")
            html.append("<p>All metrics are within acceptable thresholds across all boards and test suites.</p>")
            html.append("</div>")
            
        html.append("</div>")
        return "\n".join(html)
        
    def _format_board_name(self, board_name: str) -> str:
        """Format board name for display."""
        if 'h743' in board_name.lower():
            return "H743 (STM32H743)"
        elif 'u575' in board_name.lower():
            return "U575 (STM32U575)" 
        else:
            return board_name.replace('BFT_', '').replace('_dev', '').upper()
            
    def _get_consolidated_css(self) -> str:
        """Return CSS styles for consolidated report."""
        return """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f8f9fa;
            }
            
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 10px;
                font-size: 2.8em;
            }
            
            .subtitle {
                text-align: center;
                color: #7f8c8d;
                font-size: 1.3em;
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
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            
            .summary-card {
                background: #ecf0f1;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                border-left: 5px solid #3498db;
                transition: transform 0.2s;
            }
            
            .summary-card:hover {
                transform: translateY(-2px);
            }
            
            .summary-card.pass { border-left-color: #27ae60; background: #d5f4e6; }
            .summary-card.fail { border-left-color: #e74c3c; background: #fceaea; }
            .summary-card.boards { border-left-color: #9b59b6; background: #f4ecf7; }
            .summary-card.suites { border-left-color: #f39c12; background: #fef9e7; }
            .summary-card.tests { border-left-color: #1abc9c; background: #e8f8f5; }
            .summary-card.metrics { border-left-color: #34495e; background: #eaeded; }
            
            .summary-card h3 {
                font-size: 2.2em;
                margin: 0;
                color: #2c3e50;
            }
            
            .summary-card p {
                margin: 8px 0 0 0;
                color: #7f8c8d;
                font-weight: 600;
            }
            
            .success-rate {
                margin-top: 25px;
                text-align: center;
            }
            
            .progress-bar {
                width: 100%;
                height: 20px;
                background-color: #ecf0f1;
                border-radius: 10px;
                overflow: hidden;
                margin-top: 10px;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #e74c3c, #f39c12, #27ae60);
                transition: width 0.5s ease;
            }
            
            .board-comparison {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            
            .comparison-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            
            .comparison-table th {
                background: #34495e;
                color: white;
                padding: 15px 10px;
                text-align: left;
                font-weight: 600;
            }
            
            .comparison-table td {
                padding: 12px 10px;
                border-bottom: 1px solid #dee2e6;
            }
            
            .comparison-table tr.excellent { background-color: #d5f4e6; }
            .comparison-table tr.good { background-color: #dbeafe; }
            .comparison-table tr.warning { background-color: #fef3cd; }
            .comparison-table tr.critical { background-color: #fceaea; }
            
            .board-name {
                font-weight: 600;
                color: #2c3e50;
            }
            
            .center { text-align: center; }
            .pass { color: #27ae60; font-weight: 600; }
            .fail { color: #e74c3c; font-weight: 600; }
            
            .status-excellent { color: #27ae60; font-weight: 600; }
            .status-good { color: #3498db; font-weight: 600; }
            .status-warning { color: #f39c12; font-weight: 600; }
            .status-critical { color: #e74c3c; font-weight: 600; }
            
            .detailed-metrics {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            
            .board-section {
                margin-bottom: 30px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                overflow: hidden;
            }
            
            .board-header {
                background: #34495e;
                color: white;
                padding: 15px 20px;
                margin: 0;
                font-size: 1.3em;
            }
            
            .suite-section {
                margin: 20px;
            }
            
            .suite-header {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 8px;
            }
            
            .suite-summary {
                background: #f8f9fa;
                padding: 10px 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
            
            .suite-stats {
                font-size: 0.95em;
                color: #2c3e50;
            }
            
            .failed-metrics {
                background: #fff5f5;
                border-left: 4px solid #e74c3c;
                padding: 15px;
                margin: 10px 0;
            }
            
            .failed-metrics ul {
                margin: 10px 0 0 20px;
            }
            
            .failed-metrics li {
                margin-bottom: 5px;
                color: #721c24;
            }
            
            .all-passed {
                background: #f0f9ff;
                border-left: 4px solid #27ae60;
                padding: 10px 15px;
                color: #155724;
                font-weight: 500;
            }
            
            .trends-section {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            
            .critical-analysis {
                margin-bottom: 30px;
            }
            
            .metric-analysis {
                background: #fff8f8;
                border: 1px solid #f8d7da;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 15px;
            }
            
            .recommendations {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
            }
            
            .recommendation-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            
            .recommendation-card {
                background: white;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }
            
            .recommendation-card.priority {
                border-left-color: #e74c3c;
                background: #fff8f8;
            }
            
            .excellent-performance {
                background: #d5f4e6;
                border: 1px solid #27ae60;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
            }
            
            .footer {
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                background: white;
                border-radius: 10px;
                color: #7f8c8d;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            h2 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            h3 { color: #34495e; }
            h4 { color: #7f8c8d; }
        </style>
        """


def main():
    """Generate consolidated performance report from all CSV files."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate consolidated performance report')
    parser.add_argument('--base-dir', default='nightly_reports', 
                       help='Base directory to search for CSV files')
    parser.add_argument('--output', default=None,
                       help='Output HTML file path')
    
    args = parser.parse_args()
    
    generator = ConsolidatedPerformanceReportGenerator()
    output_file = generator.generate_consolidated_report(args.base_dir, args.output)
    
    if output_file:
        print(f"\n🌐 Open in browser: file://{output_file}")
        print("\n🎯 Consolidated Performance Report Features:")
        print("   • Multi-board performance comparison")
        print("   • Overall success rate analysis")  
        print("   • Critical issues identification")
        print("   • Performance optimization recommendations")


if __name__ == "__main__":
    main()
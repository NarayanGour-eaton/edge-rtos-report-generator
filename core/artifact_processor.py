"""
Artifact Processor for extracting and processing GitHub Actions artifacts.

This module handles:
- Extracting ZIP artifacts
- Processing various test report formats (pytest, JUnit XML, etc.)
- Organizing extracted files by test suite
"""

import zipfile
import io
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from dataclasses import dataclass

try:
    from bs4 import BeautifulSoup
    HTML_PARSER_AVAILABLE = True
except ImportError:
    HTML_PARSER_AVAILABLE = False
    BeautifulSoup = None

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Represents a single test result."""
    name: str
    status: str  # 'passed', 'failed', 'skipped', 'error'
    duration: float = 0.0
    failure_message: Optional[str] = None
    error_message: Optional[str] = None
    suite: Optional[str] = None


@dataclass
class TestSuiteResult:
    """Represents results for a test suite."""
    name: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0
    tests: List[TestResult] = None
    
    def __post_init__(self):
        if self.tests is None:
            self.tests = []


class ArtifactProcessor:
    """Processes GitHub Actions artifacts and extracts test results."""
    
    def __init__(self, config):
        """Initialize artifact processor with configuration."""
        self.config = config
        self.supported_formats = ['.xml', '.json', '.html', '.txt', '.log']
    
    def extract_artifact(self, artifact_data: bytes, artifact_name: str, 
                        output_dir: Path) -> List[Path]:
        """
        Extract artifact ZIP file and return list of extracted files.
        
        Args:
            artifact_data: Raw artifact ZIP data
            artifact_name: Name of the artifact
            output_dir: Directory to extract files to
            
        Returns:
            List of extracted file paths
        """
        extracted_files = []
        
        # Extract suite name from artifact name
        suite_name = self._extract_suite_name_from_artifact(artifact_name)
        
        # Create suite-specific directory instead of artifact-specific
        suite_dir = output_dir / f"suite_{suite_name}"
        suite_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Extracting artifact '{artifact_name}' to suite folder: {suite_name}")
        
        try:
            with zipfile.ZipFile(io.BytesIO(artifact_data), 'r') as zip_file:
                for file_info in zip_file.infolist():
                    if file_info.is_dir():
                        continue
                    
                    # Extract file
                    extracted_path = suite_dir / file_info.filename
                    extracted_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with zip_file.open(file_info) as source, \
                         open(extracted_path, 'wb') as target:
                        target.write(source.read())
                    
                    extracted_files.append(extracted_path)
                    logger.debug(f"Extracted: {extracted_path}")
            
            logger.info(f"Extracted {len(extracted_files)} files from {artifact_name} to {suite_name}")
            return extracted_files
            
        except zipfile.BadZipFile as e:
            logger.error(f"Failed to extract artifact {artifact_name}: {e}")
            return []
    
    def _has_meaningful_results(self, passed: int, failed: int, error: int) -> bool:
        """
        Check if test results are meaningful (not just skipped tests).
        Returns False for patterns like 0P/0F/1S (0 passed, 0 failed, only skipped).
        """
        return passed > 0 or failed > 0 or error > 0
    
    def _extract_suite_name_from_artifact(self, artifact_name: str) -> str:
        """
        Extract suite name from artifact name.
        
        Examples:
        'PyTest test_report=BFT PyTest Cert_Test; JobAttempt=1' -> 'Cert_Test'
        'PyTest test_report=BFT PyTest Fus_Negative_Test; JobAttempt=1' -> 'Fus_Negative_Test'
        'artifacts_PyTest test_report=BFT PyTest Rest_ExtFlashDCINV_Test; JobAttempt=1' -> 'Rest_ExtFlashDCINV_Test'
        """
        try:
            # Remove 'artifacts_' prefix if present
            clean_name = artifact_name
            if clean_name.startswith('artifacts_'):
                clean_name = clean_name[10:]  # Remove 'artifacts_' 
            
            # Look for 'BFT PyTest ' pattern and extract what comes after
            if 'BFT PyTest ' in clean_name:
                # Split on 'BFT PyTest ' and get the part after
                parts = clean_name.split('BFT PyTest ', 1)
                if len(parts) > 1:
                    suite_part = parts[1]
                    # Remove '; JobAttempt=X' suffix if present
                    if '; JobAttempt=' in suite_part:
                        suite_part = suite_part.split('; JobAttempt=')[0]
                    return suite_part.strip()
            
            # Fallback: try to extract from PyTest test_report= pattern
            if 'PyTest test_report=' in clean_name:
                # Extract everything after 'PyTest test_report='
                parts = clean_name.split('PyTest test_report=', 1)
                if len(parts) > 1:
                    suite_part = parts[1]
                    # Remove '; JobAttempt=X' suffix if present
                    if '; JobAttempt=' in suite_part:
                        suite_part = suite_part.split('; JobAttempt=')[0]
                    # Remove 'BFT PyTest ' prefix if present
                    if suite_part.startswith('BFT PyTest '):
                        suite_part = suite_part[11:]  # Remove 'BFT PyTest '
                    return suite_part.strip()
            
            # Final fallback: use the full artifact name (cleaned)
            logger.warning(f"Could not extract suite name from artifact: {artifact_name}")
            return clean_name.replace(' ', '_').replace(';', '').replace('=', '_')
            
        except Exception as e:
            logger.warning(f"Error extracting suite name from {artifact_name}: {e}")
            return artifact_name.replace(' ', '_').replace(';', '').replace('=', '_')
    
    def process_test_files(self, files: List[Path]) -> Dict[str, TestSuiteResult]:
        """
        Process extracted files to find and parse test results.
        
        Args:
            files: List of extracted file paths
            
        Returns:
            Dictionary mapping suite names to test results
        """
        test_results = {}
        logger.info(f"Processing {len(files)} extracted files for test results")
        
        # Debug: Show all files first
        for file_path in files:
            logger.debug(f"File: {file_path.name} (size: {file_path.stat().st_size if file_path.exists() else 'missing'})")
        
        processed_count = 0
        for file_path in files:
            if not self._is_test_result_file(file_path):
                logger.debug(f"Skipping non-test file: {file_path.name}")
                continue
                
            logger.info(f"Processing test file: {file_path}")
            processed_count += 1
            
            try:
                if file_path.suffix.lower() == '.xml':
                    suite_results = self._parse_junit_xml(file_path)
                elif file_path.suffix.lower() == '.json':
                    suite_results = self._parse_json_report(file_path)
                elif file_path.suffix.lower() == '.html':
                    suite_results = self._parse_html_report(file_path)
                elif file_path.suffix.lower() in ['.txt', '.log']:
                    suite_results = self._parse_text_report(file_path)
                else:
                    logger.debug(f"Unsupported file format: {file_path}")
                    continue
                
                # Merge results
                for suite_name, suite_result in suite_results.items():
                    if suite_name in test_results:
                        test_results[suite_name] = self._merge_suite_results(
                            test_results[suite_name], suite_result
                        )
                    else:
                        test_results[suite_name] = suite_result
                        
            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")
                continue
        
        logger.info(f"Processed {processed_count} test files, found {len(test_results)} test suites")
        if not test_results and processed_count == 0:
            logger.warning("No test result files detected. Supported patterns: test, result, report, junit, pytest, coverage, pytr")
            logger.warning(f"Supported extensions: {self.supported_formats}")
        
        return test_results
    
    def _is_test_result_file(self, file_path: Path) -> bool:
        """Check if file is likely a test result file."""
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()
        
        # Must have supported extension first
        if suffix not in self.supported_formats:
            logger.debug(f"Skipping {file_path.name}: unsupported extension {suffix}")
            return False
        
        # Check for common test result file patterns
        test_patterns = [
            'test', 'result', 'report', 'junit', 'pytest', 'coverage', 
            'pytr',  # PyTest report files (pytr.xml, pytr.html)
            'pytest-report', 'test-report', 'test_report'
        ]
        
        is_test_file = any(pattern in name for pattern in test_patterns)
        if not is_test_file:
            logger.debug(f"Skipping {file_path.name}: no test patterns found")
        else:
            logger.debug(f"Detected test file: {file_path.name} (pattern match)")
        
        return is_test_file
    
    def _parse_junit_xml(self, file_path: Path) -> Dict[str, TestSuiteResult]:
        """Parse JUnit XML format test results."""
        results = {}
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Handle both <testsuite> and <testsuites> root elements
            if root.tag == 'testsuites':
                suites = root.findall('testsuite')
            else:
                suites = [root]
            
            for suite_elem in suites:
                suite_name = suite_elem.get('name', file_path.stem)
                
                suite_result = TestSuiteResult(name=suite_name)
                suite_result.total = int(suite_elem.get('tests', 0))
                suite_result.failed = int(suite_elem.get('failures', 0))
                suite_result.errors = int(suite_elem.get('errors', 0))
                suite_result.skipped = int(suite_elem.get('skipped', 0))
                suite_result.duration = float(suite_elem.get('time', 0))
                suite_result.passed = suite_result.total - suite_result.failed - suite_result.errors - suite_result.skipped
                
                # Check if results are meaningful (not just skipped tests)
                if not self._has_meaningful_results(suite_result.passed, suite_result.failed, suite_result.errors):
                    logger.info(f"Excluding suite '{suite_name}' with only skipped tests from {file_path.name}")
                    continue
                
                # Parse individual test cases
                for testcase in suite_elem.findall('testcase'):
                    test = TestResult(
                        name=testcase.get('name', 'Unknown'),
                        status='passed',
                        duration=float(testcase.get('time', 0)),
                        suite=suite_name
                    )
                    
                    # Check for failure/error/skip
                    failure = testcase.find('failure')
                    error = testcase.find('error')
                    skipped = testcase.find('skipped')
                    
                    if failure is not None:
                        test.status = 'failed'
                        test.failure_message = failure.get('message', failure.text)
                    elif error is not None:
                        test.status = 'error'
                        test.error_message = error.get('message', error.text)
                    elif skipped is not None:
                        test.status = 'skipped'
                    
                    suite_result.tests.append(test)
                
                results[suite_name] = suite_result
            
        except ET.ParseError as e:
            logger.warning(f"Failed to parse XML file {file_path}: {e}")
        
        return results
    
    def _parse_json_report(self, file_path: Path) -> Dict[str, TestSuiteResult]:
        """Parse JSON format test results (pytest-json-report or similar)."""
        results = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Try to parse pytest-json-report format
            if 'tests' in data and isinstance(data['tests'], list):
                suite_name = file_path.stem
                suite_result = TestSuiteResult(name=suite_name)
                
                for test_data in data['tests']:
                    test = TestResult(
                        name=test_data.get('nodeid', 'Unknown'),
                        status=test_data.get('outcome', 'unknown').lower(),
                        duration=test_data.get('duration', 0),
                        suite=suite_name
                    )
                    
                    if 'call' in test_data and 'longrepr' in test_data['call']:
                        if test.status == 'failed':
                            test.failure_message = test_data['call']['longrepr']
                    
                    suite_result.tests.append(test)
                    
                    # Update counters
                    if test.status == 'passed':
                        suite_result.passed += 1
                    elif test.status == 'failed':
                        suite_result.failed += 1
                    elif test.status == 'skipped':
                        suite_result.skipped += 1
                    else:
                        suite_result.errors += 1
                
                suite_result.total = len(suite_result.tests)
                suite_result.duration = data.get('duration', 0)
                
                # Check if results are meaningful (not just skipped tests)
                if self._has_meaningful_results(suite_result.passed, suite_result.failed, suite_result.errors):
                    results[suite_name] = suite_result
                else:
                    logger.info(f"Excluding JSON report with only skipped tests: {file_path.name}")
            
            # Try to parse summary format
            elif 'summary' in data:
                summary = data['summary']
                suite_name = file_path.stem
                suite_result = TestSuiteResult(
                    name=suite_name,
                    total=summary.get('total', 0),
                    passed=summary.get('passed', 0),
                    failed=summary.get('failed', 0),
                    skipped=summary.get('skipped', 0),
                    errors=summary.get('error', 0),
                    duration=data.get('duration', 0)
                )
                
                # Check if results are meaningful (not just skipped tests)
                if self._has_meaningful_results(suite_result.passed, suite_result.failed, suite_result.errors):
                    results[suite_name] = suite_result
                else:
                    logger.info(f"Excluding JSON summary report with only skipped tests: {file_path.name}")
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse JSON file {file_path}: {e}")
        
        return results
    
    def _parse_html_report(self, file_path: Path) -> Dict[str, TestSuiteResult]:
        """Parse HTML format test results (pytest-html reports)."""
        results = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            suite_name = file_path.stem
            suite_result = TestSuiteResult(name=suite_name)
            
            if HTML_PARSER_AVAILABLE:
                # Use BeautifulSoup for better HTML parsing
                soup = BeautifulSoup(content, 'html.parser')
                
                # Try to find pytest-html summary table
                summary_table = soup.find('table', {'id': 'results-table'}) or soup.find('table', class_='results-table')
                if summary_table:
                    # Extract test counts from pytest-html format
                    rows = summary_table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            key = cells[0].get_text(strip=True).lower()
                            value = cells[1].get_text(strip=True)
                            
                            try:
                                count = int(value)
                                if 'passed' in key or 'pass' in key:
                                    suite_result.passed = count
                                elif 'failed' in key or 'fail' in key:
                                    suite_result.failed = count  
                                elif 'skipped' in key or 'skip' in key:
                                    suite_result.skipped = count
                                elif 'error' in key:
                                    suite_result.errors = count
                            except ValueError:
                                continue
                
                # Look for test results in the test table
                test_table = soup.find('tbody') 
                if test_table:
                    test_rows = test_table.find_all('tr')
                    suite_result.total = len(test_rows)
                    
                    # If we didn't get counts from summary, count from test rows
                    if suite_result.total > 0 and (suite_result.passed + suite_result.failed + suite_result.skipped) == 0:
                        for row in test_rows:
                            result_cell = row.find('td', class_='col-result') 
                            if result_cell:
                                result_text = result_cell.get_text(strip=True).lower()
                                if 'passed' in result_text:
                                    suite_result.passed += 1
                                elif 'failed' in result_text:
                                    suite_result.failed += 1
                                elif 'skipped' in result_text:
                                    suite_result.skipped += 1
                                elif 'error' in result_text:
                                    suite_result.errors += 1
                
            else:
                # Fallback: regex-based parsing without BeautifulSoup
                logger.warning("BeautifulSoup not available. Using basic HTML parsing for pytest reports.")
                logger.info("Install beautifulsoup4 for better HTML parsing: pip install beautifulsoup4")
                
                # Look for common pytest-html patterns
                passed_match = re.search(r'(\d+)\s+passed', content, re.IGNORECASE)
                failed_match = re.search(r'(\d+)\s+failed', content, re.IGNORECASE) 
                skipped_match = re.search(r'(\d+)\s+skipped', content, re.IGNORECASE)
                error_match = re.search(r'(\d+)\s+error', content, re.IGNORECASE)
                
                if passed_match:
                    suite_result.passed = int(passed_match.group(1))
                if failed_match:
                    suite_result.failed = int(failed_match.group(1))
                if skipped_match:
                    suite_result.skipped = int(skipped_match.group(1))
                if error_match:
                    suite_result.errors = int(error_match.group(1))
                    
                # Count total tests from HTML table rows if available
                test_row_pattern = r'<tr[^>]*class="[^"]*results-table-row[^"]*"[^>]*>'
                test_rows = re.findall(test_row_pattern, content, re.IGNORECASE)
                if test_rows:
                    suite_result.total = len(test_rows)
            
            # Calculate total if not set
            if suite_result.total == 0:
                suite_result.total = suite_result.passed + suite_result.failed + suite_result.skipped + suite_result.errors
            
            # Check if results are meaningful (not just skipped tests)
            if not self._has_meaningful_results(suite_result.passed, suite_result.failed, suite_result.errors):
                logger.info(f"Excluding HTML report with only skipped tests: {file_path.name}")
                return results
            
            # Only add results if we found some test data
            if suite_result.total > 0:
                results[suite_name] = suite_result
                logger.info(f"Parsed HTML report: {suite_result.total} tests, {suite_result.passed}P/{suite_result.failed}F/{suite_result.skipped}S")
            else:
                logger.warning(f"No test data found in HTML file: {file_path}")
                
        except Exception as e:
            logger.warning(f"Failed to parse HTML file {file_path}: {e}")
        
        return results

    def _parse_text_report(self, file_path: Path) -> Dict[str, TestSuiteResult]:
        """Parse text/log format test results (pytest output, etc.)."""
        results = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            suite_name = file_path.stem
            suite_result = TestSuiteResult(name=suite_name)
            
            # Try to parse pytest summary
            pytest_patterns = [
                r'=+ (.+) =+',  # Section headers
                r'(\d+) passed',
                r'(\d+) failed',
                r'(\d+) skipped',
                r'(\d+) error',
                r'FAILED (.+?) -',  # Failed test names
            ]
            
            # Extract failed test names
            failed_tests = re.findall(r'FAILED (.+?) -', content)
            for test_name in failed_tests:
                test = TestResult(
                    name=test_name,
                    status='failed',
                    suite=suite_name
                )
                suite_result.tests.append(test)
            
            # Extract summary counts
            passed_match = re.search(r'(\d+) passed', content)
            failed_match = re.search(r'(\d+) failed', content)
            skipped_match = re.search(r'(\d+) skipped', content)
            error_match = re.search(r'(\d+) error', content)
            
            if passed_match:
                suite_result.passed = int(passed_match.group(1))
            if failed_match:
                suite_result.failed = int(failed_match.group(1))
            if skipped_match:
                suite_result.skipped = int(skipped_match.group(1))
            if error_match:
                suite_result.errors = int(error_match.group(1))
            
            suite_result.total = suite_result.passed + suite_result.failed + suite_result.skipped + suite_result.errors
            
            if suite_result.total > 0:
                results[suite_name] = suite_result
                
        except Exception as e:
            logger.warning(f"Failed to parse text file {file_path}: {e}")
        
        return results
    
    def _merge_suite_results(self, existing: TestSuiteResult, new: TestSuiteResult) -> TestSuiteResult:
        """Merge two test suite results."""
        merged = TestSuiteResult(name=existing.name)
        
        merged.total = existing.total + new.total
        merged.passed = existing.passed + new.passed
        merged.failed = existing.failed + new.failed
        merged.skipped = existing.skipped + new.skipped
        merged.errors = existing.errors + new.errors
        merged.duration = existing.duration + new.duration
        merged.tests = existing.tests + new.tests
        
        return merged
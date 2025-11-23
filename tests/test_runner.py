"""
Test runner and configuration for the comprehensive testing suite.

This module provides:
- Test discovery and execution
- Test configuration management
- Custom test runners for different scenarios
- Test reporting and metrics
- Continuous integration support
"""

import pytest
import sys
import os
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestConfiguration:
    """Manage test configuration and settings."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), "test_config.json")
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load test configuration."""
        default_config = {
            "test_timeout": 300,  # 5 minutes per test
            "parallel_workers": 4,
            "coverage_threshold": 80,
            "slow_test_threshold": 5.0,  # seconds
            "test_categories": {
                "unit": {
                    "enabled": True,
                    "pattern": "tests/unit/test_*.py",
                    "timeout": 60
                },
                "integration": {
                    "enabled": True,
                    "pattern": "tests/integration/test_*.py", 
                    "timeout": 180
                },
                "e2e": {
                    "enabled": True,
                    "pattern": "tests/e2e/test_*.py",
                    "timeout": 300
                },
                "performance": {
                    "enabled": True,
                    "pattern": "tests/unit/test_performance_security.py::TestPerformanceBenchmarks",
                    "timeout": 120
                },
                "security": {
                    "enabled": True,
                    "pattern": "tests/unit/test_performance_security.py::TestSecurityValidation",
                    "timeout": 90
                }
            },
            "environment": {
                "test_db_path": ":memory:",
                "mock_api_calls": True,
                "temp_dir_cleanup": True,
                "log_level": "INFO"
            },
            "reporting": {
                "html_report": True,
                "junit_xml": True,
                "coverage_report": True,
                "performance_metrics": True
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                # Merge user config with defaults
                self._merge_config(default_config, user_config)
            except Exception as e:
                print(f"Warning: Could not load test config: {e}")
                print("Using default configuration")
        
        return default_config
    
    def _merge_config(self, default: Dict, user: Dict) -> None:
        """Merge user configuration with defaults."""
        for key, value in user.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def save_config(self) -> None:
        """Save current configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)


class TestRunner:
    """Custom test runner with enhanced features."""
    
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_tests(self, categories: Optional[List[str]] = None, 
                  pattern: Optional[str] = None,
                  verbose: bool = False,
                  collect_only: bool = False) -> Dict[str, Any]:
        """Run tests with specified parameters."""
        self.start_time = time.time()
        
        try:
            if collect_only:
                return self._collect_tests(categories, pattern)
            else:
                return self._execute_tests(categories, pattern, verbose)
        finally:
            self.end_time = time.time()
    
    def _collect_tests(self, categories: Optional[List[str]], 
                      pattern: Optional[str]) -> Dict[str, Any]:
        """Collect tests without running them."""
        collection_result = {
            'collected_tests': [],
            'test_count_by_category': {},
            'collection_time': 0
        }
        
        start_time = time.time()
        
        # Build pytest arguments for collection
        pytest_args = ['--collect-only', '-q']
        
        if pattern:
            pytest_args.append(pattern)
        else:
            test_patterns = self._get_test_patterns(categories)
            pytest_args.extend(test_patterns)
        
        # Run pytest to collect tests
        try:
            result = pytest.main(pytest_args)
            collection_result['collection_success'] = result == 0
        except SystemExit as e:
            collection_result['collection_success'] = e.code == 0
        
        collection_result['collection_time'] = time.time() - start_time
        
        return collection_result
    
    def _execute_tests(self, categories: Optional[List[str]], 
                      pattern: Optional[str],
                      verbose: bool) -> Dict[str, Any]:
        """Execute tests and collect results."""
        results = {
            'overall_result': 'FAILED',
            'category_results': {},
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'execution_time': 0,
            'coverage_percentage': 0,
            'slow_tests': [],
            'failed_test_details': []
        }
        
        if pattern:
            # Run specific pattern
            result = self._run_pytest_category('custom', pattern, verbose)
            results['category_results']['custom'] = result
        else:
            # Run by categories
            target_categories = categories or list(self.config.get('test_categories', {}).keys())
            
            for category in target_categories:
                if self.config.get(f'test_categories.{category}.enabled', True):
                    category_pattern = self.config.get(f'test_categories.{category}.pattern')
                    if category_pattern:
                        result = self._run_pytest_category(category, category_pattern, verbose)
                        results['category_results'][category] = result
        
        # Aggregate results
        self._aggregate_results(results)
        
        return results
    
    def _run_pytest_category(self, category: str, pattern: str, verbose: bool) -> Dict[str, Any]:
        """Run pytest for a specific category."""
        category_result = {
            'category': category,
            'pattern': pattern,
            'exit_code': 0,
            'test_count': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'duration': 0,
            'output': ''
        }
        
        # Build pytest arguments
        pytest_args = [
            pattern,
            '--tb=short',
            '--strict-markers',
            '--disable-warnings'
        ]
        
        if verbose:
            pytest_args.append('-v')
        else:
            pytest_args.append('-q')
        
        # Add timeout if configured
        timeout = self.config.get(f'test_categories.{category}.timeout', 60)
        pytest_args.extend(['--timeout', str(timeout)])
        
        # Add parallel execution if configured
        workers = self.config.get('parallel_workers', 1)
        if workers > 1:
            pytest_args.extend(['-n', str(workers)])
        
        # Add coverage if enabled
        if self.config.get('reporting.coverage_report', False):
            pytest_args.extend([
                '--cov=.',
                '--cov-report=term-missing',
                '--cov-report=html:htmlcov',
                f'--cov-fail-under={self.config.get("coverage_threshold", 80)}'
            ])
        
        # Add JUnit XML if enabled
        if self.config.get('reporting.junit_xml', False):
            junit_file = f'test-results-{category}.xml'
            pytest_args.extend(['--junit-xml', junit_file])
        
        # Add HTML report if enabled
        if self.config.get('reporting.html_report', False):
            html_file = f'test-report-{category}.html'
            pytest_args.extend(['--html', html_file, '--self-contained-html'])
        
        print(f"\n{'='*50}")
        print(f"Running {category.upper()} tests: {pattern}")
        print(f"{'='*50}")
        
        start_time = time.time()
        
        try:
            # Run pytest
            exit_code = pytest.main(pytest_args)
            category_result['exit_code'] = exit_code
            
        except SystemExit as e:
            category_result['exit_code'] = e.code
        except Exception as e:
            print(f"Error running {category} tests: {e}")
            category_result['exit_code'] = 1
            category_result['output'] = str(e)
        
        category_result['duration'] = time.time() - start_time
        
        print(f"\n{category.upper()} tests completed in {category_result['duration']:.2f} seconds")
        print(f"Exit code: {category_result['exit_code']}")
        
        return category_result
    
    def _get_test_patterns(self, categories: Optional[List[str]]) -> List[str]:
        """Get test patterns for specified categories."""
        patterns = []
        
        if not categories:
            categories = list(self.config.get('test_categories', {}).keys())
        
        for category in categories:
            if self.config.get(f'test_categories.{category}.enabled', True):
                pattern = self.config.get(f'test_categories.{category}.pattern')
                if pattern:
                    patterns.append(pattern)
        
        return patterns
    
    def _aggregate_results(self, results: Dict[str, Any]) -> None:
        """Aggregate results from all categories."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        total_duration = 0
        
        all_passed = True
        
        for category, result in results['category_results'].items():
            if result['exit_code'] != 0:
                all_passed = False
            
            total_tests += result.get('test_count', 0)
            passed_tests += result.get('passed', 0)
            failed_tests += result.get('failed', 0)
            skipped_tests += result.get('skipped', 0)
            total_duration += result.get('duration', 0)
        
        results['total_tests'] = total_tests
        results['passed_tests'] = passed_tests
        results['failed_tests'] = failed_tests
        results['skipped_tests'] = skipped_tests
        results['execution_time'] = total_duration
        results['overall_result'] = 'PASSED' if all_passed else 'FAILED'
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report."""
        report = []
        
        report.append("=" * 80)
        report.append("SPANISH CONJUGATION GUI - TEST EXECUTION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("SUMMARY:")
        report.append(f"  Overall Result: {results['overall_result']}")
        report.append(f"  Total Tests: {results['total_tests']}")
        report.append(f"  Passed: {results['passed_tests']}")
        report.append(f"  Failed: {results['failed_tests']}")
        report.append(f"  Skipped: {results['skipped_tests']}")
        report.append(f"  Execution Time: {results['execution_time']:.2f} seconds")
        
        if results['total_tests'] > 0:
            pass_rate = (results['passed_tests'] / results['total_tests']) * 100
            report.append(f"  Pass Rate: {pass_rate:.1f}%")
        
        report.append("")
        
        # Category breakdown
        if results['category_results']:
            report.append("CATEGORY BREAKDOWN:")
            for category, result in results['category_results'].items():
                status = "PASSED" if result['exit_code'] == 0 else "FAILED"
                report.append(f"  {category.upper()}: {status} ({result['duration']:.2f}s)")
        
        report.append("")
        
        # Performance metrics
        if self.config.get('reporting.performance_metrics', False):
            report.append("PERFORMANCE METRICS:")
            slow_threshold = self.config.get('slow_test_threshold', 5.0)
            report.append(f"  Slow Test Threshold: {slow_threshold}s")
            
            if results.get('slow_tests'):
                report.append("  Slow Tests:")
                for test in results['slow_tests']:
                    report.append(f"    - {test['name']}: {test['duration']:.2f}s")
            else:
                report.append("  No slow tests detected")
            
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS:")
        if results['failed_tests'] > 0:
            report.append("  - Review failed tests and fix issues")
            report.append("  - Check test logs for detailed error information")
        
        if results['coverage_percentage'] < self.config.get('coverage_threshold', 80):
            report.append(f"  - Improve test coverage (currently {results['coverage_percentage']:.1f}%)")
        
        if results['execution_time'] > 300:  # 5 minutes
            report.append("  - Consider optimizing slow tests or increasing parallel workers")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def create_test_config():
    """Create default test configuration file."""
    config = TestConfiguration()
    config.save_config()
    print(f"Created test configuration file: {config.config_file}")


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description="Spanish Conjugation GUI Test Runner")
    
    parser.add_argument(
        '--categories',
        nargs='+',
        choices=['unit', 'integration', 'e2e', 'performance', 'security'],
        help='Test categories to run'
    )
    
    parser.add_argument(
        '--pattern',
        help='Specific test pattern to run'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--collect-only',
        action='store_true',
        help='Only collect tests, don\'t run them'
    )
    
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create default test configuration file'
    )
    
    parser.add_argument(
        '--config',
        help='Path to test configuration file'
    )
    
    args = parser.parse_args()
    
    if args.create_config:
        create_test_config()
        return
    
    # Load configuration
    config = TestConfiguration(args.config)
    
    # Create and run test runner
    runner = TestRunner(config)
    
    print("Spanish Conjugation GUI - Comprehensive Test Suite")
    print("=" * 60)
    
    try:
        results = runner.run_tests(
            categories=args.categories,
            pattern=args.pattern,
            verbose=args.verbose,
            collect_only=args.collect_only
        )
        
        if not args.collect_only:
            # Generate and display report
            report = runner.generate_report(results)
            print(report)
            
            # Save report to file
            report_file = "test_execution_report.txt"
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"\nDetailed report saved to: {report_file}")
            
            # Exit with appropriate code
            sys.exit(0 if results['overall_result'] == 'PASSED' else 1)
        else:
            print("\nTest collection completed successfully")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest execution failed with error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
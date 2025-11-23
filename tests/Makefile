# Makefile for Spanish Conjugation GUI Testing Suite
# Provides convenient commands for running different test categories

.PHONY: help install test test-unit test-integration test-e2e test-performance test-security test-all clean coverage lint format check-security

# Default target
help:
	@echo "Spanish Conjugation GUI - Test Suite"
	@echo "====================================="
	@echo ""
	@echo "Available targets:"
	@echo "  install          Install test dependencies"
	@echo "  test            Run all tests"
	@echo "  test-unit       Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-e2e        Run end-to-end tests only"
	@echo "  test-performance Run performance tests only"
	@echo "  test-security   Run security tests only"
	@echo "  test-fast       Run fast tests only (exclude slow ones)"
	@echo "  test-api        Run API-related tests"
	@echo "  test-config     Run configuration tests"
	@echo "  test-deployment Run deployment tests"
	@echo "  coverage        Generate coverage report"
	@echo "  lint            Run code linting"
	@echo "  format          Format code"
	@echo "  check-security  Run security checks"
	@echo "  clean           Clean test artifacts"
	@echo "  report          Generate comprehensive test report"

# Install test dependencies
install:
	@echo "Installing test dependencies..."
	pip install -r tests/requirements.txt
	@echo "Dependencies installed successfully"

# Run all tests
test:
	@echo "Running all tests..."
	python tests/test_runner.py --verbose

# Run unit tests
test-unit:
	@echo "Running unit tests..."
	python tests/test_runner.py --categories unit --verbose

# Run integration tests
test-integration:
	@echo "Running integration tests..."
	python tests/test_runner.py --categories integration --verbose

# Run end-to-end tests
test-e2e:
	@echo "Running end-to-end tests..."
	python tests/test_runner.py --categories e2e --verbose

# Run performance tests
test-performance:
	@echo "Running performance tests..."
	python tests/test_runner.py --categories performance --verbose

# Run security tests
test-security:
	@echo "Running security tests..."
	python tests/test_runner.py --categories security --verbose

# Run fast tests only
test-fast:
	@echo "Running fast tests..."
	pytest tests/ -m "not slow" -v

# Run API-related tests
test-api:
	@echo "Running API tests..."
	python tests/test_runner.py --categories api_key --verbose

# Run configuration tests
test-config:
	@echo "Running configuration tests..."
	python tests/test_runner.py --categories configuration --verbose

# Run deployment tests
test-deployment:
	@echo "Running deployment tests..."
	python tests/test_runner.py --categories deployment --verbose

# Generate coverage report
coverage:
	@echo "Generating coverage report..."
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Coverage report generated in htmlcov/"

# Run linting
lint:
	@echo "Running code linting..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Format code
format:
	@echo "Formatting code..."
	black . --exclude="/(build|dist|\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist)/"
	isort . --profile black

# Run security checks
check-security:
	@echo "Running security checks..."
	bandit -r . -x tests/
	safety check

# Clean test artifacts
clean:
	@echo "Cleaning test artifacts..."
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf test-results.xml
	rm -rf test-report.html
	rm -rf .pytest_cache/
	rm -rf tests/.pytest_cache/
	rm -rf test_reports/
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	rm -rf tests/*/__pycache__/
	rm -rf tests/*/*/__pycache__/
	rm -rf *.pyc
	rm -rf tests/*.pyc
	rm -rf tests/*/*.pyc
	rm -rf tests/*/*/*.pyc
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleanup completed"

# Generate comprehensive report
report:
	@echo "Generating comprehensive test report..."
	python tests/test_runner.py --verbose
	@echo "Report generated: test_execution_report.txt"

# Continuous integration targets
ci-test:
	@echo "Running CI test suite..."
	python tests/test_runner.py --categories unit integration

ci-full:
	@echo "Running full CI test suite..."
	python tests/test_runner.py

# Development workflow targets
dev-test:
	@echo "Running development tests..."
	pytest tests/unit/ tests/integration/ -v --tb=short

dev-watch:
	@echo "Running tests in watch mode..."
	ptw tests/ -- --tb=short -v

# Benchmarking
benchmark:
	@echo "Running performance benchmarks..."
	pytest tests/unit/test_performance_security.py::TestPerformanceBenchmarks --benchmark-only

# Create test configuration
create-config:
	@echo "Creating test configuration..."
	python tests/test_runner.py --create-config

# Validate test setup
validate:
	@echo "Validating test setup..."
	python tests/test_runner.py --collect-only
	@echo "Test setup validation completed"

# Display test statistics
stats:
	@echo "Test Suite Statistics:"
	@echo "====================="
	@find tests/ -name "test_*.py" -type f | wc -l | sed 's/^/Test files: /'
	@grep -r "def test_" tests/ | wc -l | sed 's/^/Test functions: /'
	@grep -r "class Test" tests/ | wc -l | sed 's/^/Test classes: /'
	@echo ""
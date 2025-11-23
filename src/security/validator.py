"""
API Key Validation and Testing Module for Spanish Conjugation GUI
================================================================

This module provides comprehensive validation and testing capabilities for API keys
and credentials, including format validation, connectivity testing, and security checks.

Features:
- Multi-provider API key validation
- Live API testing with rate limiting
- Security vulnerability detection
- Batch validation support
- Health monitoring and status reporting
- Custom validation rules

Author: Brand
Version: 1.0.0
"""

import re
import hashlib
import time
import logging
import asyncio
import aiohttp
from typing import Dict, Optional, Any, List, Tuple, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
import secrets

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ValidationLevel(Enum):
    """Validation strictness levels."""
    BASIC = "basic"          # Format validation only
    STANDARD = "standard"    # Format + basic security checks
    STRICT = "strict"        # Full validation + connectivity test
    COMPREHENSIVE = "comprehensive"  # All checks + vulnerability scan


class ValidationStatus(Enum):
    """Validation result status."""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


class APIProvider(Enum):
    """Supported API providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"


class ValidationResult:
    """Comprehensive validation result."""
    
    def __init__(self, 
                 key_id: str,
                 provider: APIProvider,
                 status: ValidationStatus = ValidationStatus.UNKNOWN):
        self.key_id = key_id
        self.provider = provider
        self.status = status
        self.timestamp = datetime.now()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: Dict[str, Any] = {}
        self.security_issues: List[str] = []
        self.performance_metrics: Dict[str, float] = {}
        self.test_results: Dict[str, Any] = {}
    
    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        if self.status in [ValidationStatus.VALID, ValidationStatus.WARNING]:
            self.status = ValidationStatus.INVALID
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)
        if self.status == ValidationStatus.VALID:
            self.status = ValidationStatus.WARNING
    
    def add_security_issue(self, issue: str) -> None:
        """Add a security issue."""
        self.security_issues.append(issue)
        self.add_warning(f"Security concern: {issue}")
    
    def set_valid(self) -> None:
        """Mark as valid if no errors exist."""
        if not self.errors:
            self.status = ValidationStatus.WARNING if self.warnings else ValidationStatus.VALID
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key_id": self.key_id,
            "provider": self.provider.value,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "valid": self.status in [ValidationStatus.VALID, ValidationStatus.WARNING],
            "errors": self.errors,
            "warnings": self.warnings,
            "security_issues": self.security_issues,
            "info": self.info,
            "performance_metrics": self.performance_metrics,
            "test_results": self.test_results
        }


class APIKeyValidator:
    """
    Comprehensive API key validator with multi-provider support.
    
    Supports validation for multiple AI providers with customizable
    validation levels and comprehensive security checking.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('conjugation_gui.validator')
        
        # Rate limiting for API tests
        self.last_test_time = {}
        self.min_test_interval = 1.0  # Minimum seconds between tests
        
        # Validation patterns for different providers
        self.validation_patterns = {
            APIProvider.OPENAI: {
                'pattern': r'^sk-[A-Za-z0-9]{48}$',
                'prefix': 'sk-',
                'min_length': 51,
                'max_length': 51,
                'description': 'OpenAI API key'
            },
            APIProvider.ANTHROPIC: {
                'pattern': r'^sk-ant-[A-Za-z0-9\-_]{95}$',
                'prefix': 'sk-ant-',
                'min_length': 108,
                'max_length': 108,
                'description': 'Anthropic Claude API key'
            },
            APIProvider.GOOGLE: {
                'pattern': r'^AIza[A-Za-z0-9\-_]{35}$',
                'prefix': 'AIza',
                'min_length': 39,
                'max_length': 39,
                'description': 'Google AI API key'
            },
            APIProvider.HUGGINGFACE: {
                'pattern': r'^hf_[A-Za-z0-9]{34}$',
                'prefix': 'hf_',
                'min_length': 37,
                'max_length': 37,
                'description': 'Hugging Face API token'
            },
            APIProvider.COHERE: {
                'pattern': r'^[A-Za-z0-9]{40}$',
                'prefix': '',
                'min_length': 40,
                'max_length': 40,
                'description': 'Cohere API key'
            }
        }
        
        # Security vulnerability patterns
        self.security_patterns = {
            'test_key': r'(test|demo|example|sample)',
            'placeholder': r'(your-key-here|replace-me|xxx+)',
            'common_leak': r'(github|gitlab|bitbucket)',
            'suspicious_chars': r'[<>"\'\`]'
        }
    
    def detect_provider(self, api_key: str) -> Optional[APIProvider]:
        """
        Auto-detect API provider from key format.
        
        Args:
            api_key: API key to analyze
            
        Returns:
            Detected provider or None if unknown
        """
        if not api_key:
            return None
        
        for provider, config in self.validation_patterns.items():
            if api_key.startswith(config['prefix']):
                if re.match(config['pattern'], api_key):
                    return provider
        
        # Fallback: try pattern matching without prefix
        for provider, config in self.validation_patterns.items():
            if re.match(config['pattern'], api_key):
                return provider
        
        return None
    
    def validate_format(self, 
                       api_key: str, 
                       provider: APIProvider) -> ValidationResult:
        """
        Validate API key format.
        
        Args:
            api_key: API key to validate
            provider: Expected provider
            
        Returns:
            Validation result
        """
        result = ValidationResult(
            key_id=hashlib.sha256(api_key.encode()).hexdigest()[:16],
            provider=provider
        )
        
        if not api_key:
            result.add_error("API key is empty")
            return result
        
        # Get validation config for provider
        config = self.validation_patterns.get(provider)
        if not config:
            result.add_error(f"Validation not supported for provider: {provider.value}")
            return result
        
        result.info['expected_format'] = config['description']
        result.info['key_length'] = len(api_key)
        
        # Check length
        if len(api_key) < config['min_length']:
            result.add_error(f"Key too short (expected {config['min_length']}+ chars)")
        elif len(api_key) > config['max_length']:
            result.add_error(f"Key too long (expected max {config['max_length']} chars)")
        
        # Check prefix
        if config['prefix'] and not api_key.startswith(config['prefix']):
            result.add_error(f"Key should start with '{config['prefix']}'")
        
        # Check pattern
        if not re.match(config['pattern'], api_key):
            result.add_error(f"Key format doesn't match {provider.value} pattern")
        
        # Additional format checks
        self._check_character_validity(api_key, result)
        
        if not result.errors:
            result.set_valid()
            result.info['format_valid'] = True
        
        return result
    
    def _check_character_validity(self, api_key: str, result: ValidationResult) -> None:
        """Check for invalid characters and patterns."""
        # Check for whitespace
        if api_key != api_key.strip():
            result.add_warning("Key has leading/trailing whitespace")
        
        if ' ' in api_key:
            result.add_warning("Key contains spaces")
        
        if '\t' in api_key or '\n' in api_key:
            result.add_error("Key contains invalid whitespace characters")
        
        # Check for suspicious characters
        if re.search(self.security_patterns['suspicious_chars'], api_key):
            result.add_security_issue("Key contains potentially dangerous characters")
    
    def validate_security(self, api_key: str, result: ValidationResult) -> None:
        """
        Perform security validation on API key.
        
        Args:
            api_key: API key to check
            result: Validation result to update
        """
        # Check for test/demo keys
        if re.search(self.security_patterns['test_key'], api_key, re.IGNORECASE):
            result.add_security_issue("Appears to be a test or demo key")
        
        # Check for placeholder values
        if re.search(self.security_patterns['placeholder'], api_key, re.IGNORECASE):
            result.add_error("Key appears to be a placeholder value")
        
        # Check for common leak patterns
        if re.search(self.security_patterns['common_leak'], api_key, re.IGNORECASE):
            result.add_security_issue("Key may have been exposed in version control")
        
        # Check entropy (randomness)
        entropy = self._calculate_entropy(api_key)
        result.info['entropy'] = entropy
        
        if entropy < 3.0:
            result.add_security_issue("Key has low entropy (may be predictable)")
        elif entropy < 4.0:
            result.add_warning("Key has moderate entropy")
        
        # Check for repeated patterns
        if self._has_repeated_patterns(api_key):
            result.add_security_issue("Key contains repeated patterns")
        
        # Check for common weak patterns
        if self._has_weak_patterns(api_key):
            result.add_security_issue("Key contains weak patterns")
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text."""
        if not text:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        text_len = len(text)
        
        for count in char_counts.values():
            probability = count / text_len
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy
    
    def _has_repeated_patterns(self, text: str) -> bool:
        """Check for repeated patterns in text."""
        # Check for immediate repetitions
        for i in range(1, len(text) // 2 + 1):
            pattern = text[:i]
            if text.startswith(pattern * (len(text) // i)):
                return True
        
        # Check for substring repetitions
        for length in range(3, min(len(text) // 2, 8)):
            seen_substrings = set()
            for i in range(len(text) - length + 1):
                substring = text[i:i + length]
                if substring in seen_substrings:
                    return True
                seen_substrings.add(substring)
        
        return False
    
    def _has_weak_patterns(self, text: str) -> bool:
        """Check for common weak patterns."""
        weak_patterns = [
            r'(.)\1{3,}',  # Same character repeated 4+ times
            r'(abc|123|xyz)',  # Sequential patterns
            r'(password|secret|key)',  # Common words
            r'(admin|user|test)',  # Common usernames
            r'(\d{4,})',  # Long number sequences
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    async def test_api_connectivity(self, 
                                   api_key: str, 
                                   provider: APIProvider,
                                   result: ValidationResult) -> None:
        """
        Test API key by making a minimal request.
        
        Args:
            api_key: API key to test
            provider: API provider
            result: Validation result to update
        """
        # Rate limiting
        now = time.time()
        last_test = self.last_test_time.get(provider, 0)
        
        if now - last_test < self.min_test_interval:
            result.add_warning("Skipped API test due to rate limiting")
            return
        
        self.last_test_time[provider] = now
        
        start_time = time.time()
        
        try:
            if provider == APIProvider.OPENAI:
                await self._test_openai_key(api_key, result)
            elif provider == APIProvider.ANTHROPIC:
                await self._test_anthropic_key(api_key, result)
            elif provider == APIProvider.GOOGLE:
                await self._test_google_key(api_key, result)
            else:
                result.add_warning(f"API testing not implemented for {provider.value}")
                return
            
            # Record performance metrics
            elapsed = time.time() - start_time
            result.performance_metrics['response_time'] = elapsed
            result.performance_metrics['test_completed_at'] = datetime.now().isoformat()
            
        except Exception as e:
            result.add_error(f"API test failed: {str(e)}")
            result.performance_metrics['test_error'] = str(e)
    
    async def _test_openai_key(self, api_key: str, result: ValidationResult) -> None:
        """Test OpenAI API key."""
        if not OPENAI_AVAILABLE:
            result.add_warning("OpenAI library not available for testing")
            return
        
        try:
            client = openai.OpenAI(api_key=api_key)
            
            # Make minimal request
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1
            )
            
            result.test_results['api_test'] = 'success'
            result.test_results['model_used'] = 'gpt-3.5-turbo'
            result.info['api_accessible'] = True
            
        except Exception as e:
            error_str = str(e).lower()
            
            if 'authentication' in error_str or 'api_key' in error_str:
                result.add_error("API key authentication failed")
            elif 'rate_limit' in error_str:
                result.add_warning("Rate limit encountered during test")
                result.info['api_accessible'] = True  # Key is valid, just rate limited
            elif 'quota' in error_str:
                result.add_warning("API quota exceeded")
                result.info['api_accessible'] = True  # Key is valid, quota issue
            else:
                result.add_error(f"API test error: {str(e)}")
            
            result.test_results['api_test'] = 'failed'
            result.test_results['error'] = str(e)
    
    async def _test_anthropic_key(self, api_key: str, result: ValidationResult) -> None:
        """Test Anthropic API key."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'x-api-key': api_key,
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                }
                
                # Make minimal request
                data = {
                    'model': 'claude-3-haiku-20240307',
                    'max_tokens': 1,
                    'messages': [{'role': 'user', 'content': 'Hi'}]
                }
                
                async with session.post(
                    'https://api.anthropic.com/v1/messages',
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result.test_results['api_test'] = 'success'
                        result.test_results['model_used'] = 'claude-3-haiku'
                        result.info['api_accessible'] = True
                    else:
                        error_text = await response.text()
                        if response.status == 401:
                            result.add_error("API key authentication failed")
                        elif response.status == 429:
                            result.add_warning("Rate limit encountered")
                            result.info['api_accessible'] = True
                        else:
                            result.add_error(f"API test failed: {response.status}")
                        
                        result.test_results['api_test'] = 'failed'
                        result.test_results['status_code'] = response.status
                        result.test_results['error'] = error_text[:200]
        
        except Exception as e:
            result.add_error(f"API test error: {str(e)}")
            result.test_results['api_test'] = 'error'
            result.test_results['error'] = str(e)
    
    async def _test_google_key(self, api_key: str, result: ValidationResult) -> None:
        """Test Google AI API key."""
        try:
            async with aiohttp.ClientSession() as session:
                # Test with Gemini API
                url = f'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}'
                
                data = {
                    'contents': [{
                        'parts': [{'text': 'Hi'}]
                    }],
                    'generationConfig': {
                        'maxOutputTokens': 1
                    }
                }
                
                async with session.post(
                    url,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result.test_results['api_test'] = 'success'
                        result.test_results['model_used'] = 'gemini-pro'
                        result.info['api_accessible'] = True
                    else:
                        error_text = await response.text()
                        if response.status in [401, 403]:
                            result.add_error("API key authentication failed")
                        elif response.status == 429:
                            result.add_warning("Rate limit encountered")
                            result.info['api_accessible'] = True
                        else:
                            result.add_error(f"API test failed: {response.status}")
                        
                        result.test_results['api_test'] = 'failed'
                        result.test_results['status_code'] = response.status
                        result.test_results['error'] = error_text[:200]
        
        except Exception as e:
            result.add_error(f"API test error: {str(e)}")
            result.test_results['api_test'] = 'error'
            result.test_results['error'] = str(e)
    
    async def validate_key(self, 
                          api_key: str,
                          provider: Optional[APIProvider] = None,
                          level: ValidationLevel = ValidationLevel.STANDARD) -> ValidationResult:
        """
        Perform comprehensive validation of an API key.
        
        Args:
            api_key: API key to validate
            provider: Expected provider (auto-detect if None)
            level: Validation level
            
        Returns:
            Comprehensive validation result
        """
        # Auto-detect provider if not specified
        if not provider:
            detected = self.detect_provider(api_key)
            if not detected:
                result = ValidationResult("unknown", APIProvider.OPENAI)
                result.add_error("Could not detect API provider")
                return result
            provider = detected
        
        # Start with format validation
        result = self.validate_format(api_key, provider)
        
        if level == ValidationLevel.BASIC:
            return result
        
        # Add security validation for standard and above
        if level in [ValidationLevel.STANDARD, ValidationLevel.STRICT, ValidationLevel.COMPREHENSIVE]:
            self.validate_security(api_key, result)
        
        # Add connectivity testing for strict and above
        if level in [ValidationLevel.STRICT, ValidationLevel.COMPREHENSIVE]:
            await self.test_api_connectivity(api_key, provider, result)
        
        # Add comprehensive checks
        if level == ValidationLevel.COMPREHENSIVE:
            await self._comprehensive_checks(api_key, provider, result)
        
        return result
    
    async def _comprehensive_checks(self, 
                                   api_key: str, 
                                   provider: APIProvider,
                                   result: ValidationResult) -> None:
        """Perform comprehensive security and health checks."""
        # Check for common vulnerabilities
        await self._check_vulnerability_databases(api_key, result)
        
        # Check for leaked keys (simplified check)
        self._check_common_leaks(api_key, result)
        
        # Health monitoring
        await self._monitor_api_health(provider, result)
    
    async def _check_vulnerability_databases(self, api_key: str, result: ValidationResult) -> None:
        """Check against known vulnerability databases (placeholder)."""
        # In a real implementation, this would check against:
        # - HaveIBeenPwned API
        # - Known leaked key databases
        # - Security intelligence feeds
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        result.info['key_hash'] = key_hash[:16]  # Store partial hash for logging
        
        # Placeholder check - in practice, never store or transmit actual keys
        if 'test' in api_key.lower() or 'example' in api_key.lower():
            result.add_security_issue("Key appears in common test datasets")
    
    def _check_common_leaks(self, api_key: str, result: ValidationResult) -> None:
        """Check for patterns indicating the key may be leaked."""
        # Check against common leak patterns
        leak_indicators = [
            ('github.com', 'May be exposed in GitHub repositories'),
            ('stackoverflow.com', 'May be exposed in Stack Overflow posts'),
            ('pastebin.com', 'May be exposed in Pastebin'),
            ('config.', 'May be in configuration files'),
            ('.env', 'May be in environment files'),
        ]
        
        key_lower = api_key.lower()
        for pattern, message in leak_indicators:
            if pattern in key_lower:
                result.add_security_issue(message)
    
    async def _monitor_api_health(self, provider: APIProvider, result: ValidationResult) -> None:
        """Monitor API health and status."""
        # Check API status pages (simplified)
        status_urls = {
            APIProvider.OPENAI: 'https://status.openai.com/',
            APIProvider.ANTHROPIC: 'https://status.anthropic.com/',
            APIProvider.GOOGLE: 'https://status.cloud.google.com/',
        }
        
        status_url = status_urls.get(provider)
        if status_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(status_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status == 200:
                            result.info['provider_status'] = 'operational'
                        else:
                            result.info['provider_status'] = 'degraded'
            except:
                result.info['provider_status'] = 'unknown'
    
    def validate_key_sync(self, 
                         api_key: str,
                         provider: Optional[APIProvider] = None,
                         level: ValidationLevel = ValidationLevel.STANDARD) -> ValidationResult:
        """
        Synchronous wrapper for key validation.
        
        Args:
            api_key: API key to validate
            provider: Expected provider
            level: Validation level
            
        Returns:
            Validation result
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.validate_key(api_key, provider, level))
    
    async def batch_validate(self, 
                           keys: List[Tuple[str, Optional[APIProvider]]],
                           level: ValidationLevel = ValidationLevel.STANDARD) -> List[ValidationResult]:
        """
        Validate multiple API keys in batch.
        
        Args:
            keys: List of (api_key, provider) tuples
            level: Validation level
            
        Returns:
            List of validation results
        """
        tasks = []
        for api_key, provider in keys:
            task = asyncio.create_task(self.validate_key(api_key, provider, level))
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def create_validation_report(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Create a comprehensive validation report.
        
        Args:
            results: List of validation results
            
        Returns:
            Validation report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_keys': len(results),
            'summary': {
                'valid': 0,
                'invalid': 0,
                'warnings': 0,
                'errors': 0
            },
            'provider_breakdown': {},
            'security_issues': [],
            'recommendations': [],
            'results': []
        }
        
        for result in results:
            if isinstance(result, ValidationResult):
                report['results'].append(result.to_dict())
                
                # Update summary
                if result.status == ValidationStatus.VALID:
                    report['summary']['valid'] += 1
                elif result.status == ValidationStatus.INVALID:
                    report['summary']['invalid'] += 1
                elif result.status == ValidationStatus.WARNING:
                    report['summary']['warnings'] += 1
                
                report['summary']['errors'] += len(result.errors)
                
                # Provider breakdown
                provider = result.provider.value
                if provider not in report['provider_breakdown']:
                    report['provider_breakdown'][provider] = {'total': 0, 'valid': 0}
                
                report['provider_breakdown'][provider]['total'] += 1
                if result.status == ValidationStatus.VALID:
                    report['provider_breakdown'][provider]['valid'] += 1
                
                # Collect security issues
                report['security_issues'].extend(result.security_issues)
        
        # Generate recommendations
        if report['summary']['invalid'] > 0:
            report['recommendations'].append("Review and replace invalid API keys")
        
        if report['security_issues']:
            report['recommendations'].append("Address security issues with flagged keys")
        
        if report['summary']['warnings'] > 0:
            report['recommendations'].append("Review keys with warnings for potential issues")
        
        return report
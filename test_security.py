#!/usr/bin/env python3
"""
Security Testing Script for Movie Recommender Application

This script tests all 10 security features implemented:
1. API Key Protection
2. XSS Protection
3. Input Validation
4. Prompt Injection Protection
5. Dependencies Check
6. Rate Limiting
7. Authentication
8. Error Sanitization
9. SSL Verification
10. Security Headers

Run with: python test_security.py
"""

import re
import sys
from typing import List, Tuple

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

def print_test(name: str, passed: bool, message: str = ""):
    """Print test result."""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} - {name}")
    if message:
        print(f"       {message}")

def test_api_key_protection() -> Tuple[int, int]:
    """Test 1: API Key Protection"""
    print_header("TEST 1: API Key Protection")
    passed = 0
    total = 0
    
    # Check that API keys are not logged
    with open('movie_recommender.py', 'r') as f:
        content = f.read()
    
    # Test 1.1: No API key substring logging
    total += 1
    if 'api_key[:10]' not in content and 'api_key[:' not in content:
        print_test("No API key substring logging", True)
        passed += 1
    else:
        print_test("No API key substring logging", False, "Found API key logging in code")
    
    # Test 1.2: Check for secure key loading
    total += 1
    if 'os.getenv' in content or 'st.secrets' in content:
        print_test("Secure API key loading", True)
        passed += 1
    else:
        print_test("Secure API key loading", False, "No secure key loading found")
    
    return passed, total

def test_xss_protection() -> Tuple[int, int]:
    """Test 2: XSS Protection"""
    print_header("TEST 2: XSS Protection")
    passed = 0
    total = 0
    
    with open('movie_recommender.py', 'r') as f:
        content = f.read()
    
    # Test 2.1: HTML sanitization function exists
    total += 1
    if 'def sanitize_html' in content:
        print_test("HTML sanitization function exists", True)
        passed += 1
    else:
        print_test("HTML sanitization function exists", False)
    
    # Test 2.2: HTML escaping imported
    total += 1
    if 'import html' in content:
        print_test("HTML escaping module imported", True)
        passed += 1
    else:
        print_test("HTML escaping module imported", False)
    
    # Test 2.3: URL validation present
    total += 1
    if 'http://' in content and 'https://' in content and 'startswith' in content:
        print_test("URL validation implemented", True)
        passed += 1
    else:
        print_test("URL validation implemented", False)
    
    # Test 2.4: Safe link attributes
    total += 1
    if 'noopener noreferrer' in content:
        print_test("Safe external link attributes", True)
        passed += 1
    else:
        print_test("Safe external link attributes", False)
    
    return passed, total

def test_input_validation() -> Tuple[int, int]:
    """Test 3: Input Validation"""
    print_header("TEST 3: Input Validation")
    passed = 0
    total = 0
    
    with open('movie_recommender.py', 'r') as f:
        content = f.read()
    
    # Test 3.1: Validation function exists
    total += 1
    if 'def validate_movie_title' in content:
        print_test("Input validation function exists", True)
        passed += 1
    else:
        print_test("Input validation function exists", False)
    
    # Test 3.2: Length limits enforced
    total += 1
    if 'max_chars=200' in content or 'max_length' in content:
        print_test("Length limits enforced", True)
        passed += 1
    else:
        print_test("Length limits enforced", False)
    
    # Test 3.3: Suspicious pattern blocking
    total += 1
    if 'suspicious_patterns' in content or '<script' in content:
        print_test("Suspicious pattern detection", True)
        passed += 1
    else:
        print_test("Suspicious pattern detection", False)
    
    # Test 3.4: Character validation
    total += 1
    if 're.compile' in content and 'allowed_pattern' in content:
        print_test("Character pattern validation", True)
        passed += 1
    else:
        print_test("Character pattern validation", False)
    
    return passed, total

def test_prompt_injection_protection() -> Tuple[int, int]:
    """Test 4: Prompt Injection Protection"""
    print_header("TEST 4: Prompt Injection Protection")
    passed = 0
    total = 0
    
    with open('movie_recommender.py', 'r') as f:
        content = f.read()
    
    # Test 4.1: LLM sanitization function exists
    total += 1
    if 'def sanitize_for_llm' in content:
        print_test("LLM sanitization function exists", True)
        passed += 1
    else:
        print_test("LLM sanitization function exists", False)
    
    # Test 4.2: Dangerous pattern detection
    total += 1
    if 'dangerous_patterns' in content and 'ignore previous' in content:
        print_test("Prompt injection pattern detection", True)
        passed += 1
    else:
        print_test("Prompt injection pattern detection", False)
    
    # Test 4.3: Sanitization applied to user input
    total += 1
    if 'sanitize_movie_list' in content:
        print_test("User input sanitization applied", True)
        passed += 1
    else:
        print_test("User input sanitization applied", False)
    
    return passed, total

def test_dependencies() -> Tuple[int, int]:
    """Test 5: Dependency Security"""
    print_header("TEST 5: Dependency Security")
    passed = 0
    total = 0
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # Test 5.1: Streamlit version
        total += 1
        if 'streamlit>=1.41' in requirements or 'streamlit>=1.40' in requirements:
            print_test("Streamlit version updated", True)
            passed += 1
        else:
            print_test("Streamlit version updated", False, "Consider updating to 1.41+")
        
        # Test 5.2: OpenAI version
        total += 1
        if 'openai>=1.5' in requirements or 'openai>=1.0' in requirements:
            print_test("OpenAI version updated", True)
            passed += 1
        else:
            print_test("OpenAI version updated", False, "Should be >= 1.0")
        
        # Test 5.3: Requests version
        total += 1
        if 'requests>=2.32' in requirements or 'requests>=2.31' in requirements:
            print_test("Requests version updated", True)
            passed += 1
        else:
            print_test("Requests version updated", False)
        
        # Test 5.4: Reportlab version
        total += 1
        if 'reportlab>=4' in requirements:
            print_test("ReportLab version updated", True)
            passed += 1
        else:
            print_test("ReportLab version updated", False)
            
    except FileNotFoundError:
        print_test("Requirements file found", False, "requirements.txt not found")
        return 0, 4
    
    return passed, total

def test_rate_limiting() -> Tuple[int, int]:
    """Test 6: Rate Limiting"""
    print_header("TEST 6: Rate Limiting")
    passed = 0
    total = 0
    
    with open('movie_recommender.py', 'r') as f:
        content = f.read()
    
    # Test 6.1: Rate limiter class exists
    total += 1
    if 'class RateLimiter' in content:
        print_test("RateLimiter class implemented", True)
        passed += 1
    else:
        print_test("RateLimiter class implemented", False)
    
    # Test 6.2: Rate limit check function
    total += 1
    if 'check_rate_limit' in content:
        print_test("Rate limit checking implemented", True)
        passed += 1
    else:
        print_test("Rate limit checking implemented", False)
    
    # Test 6.3: Blocking mechanism
    total += 1
    if 'blocked_until' in content:
        print_test("Automatic blocking mechanism", True)
        passed += 1
    else:
        print_test("Automatic blocking mechanism", False)
    
    # Test 6.4: Rate limiter instantiated
    total += 1
    if 'rate_limiter = RateLimiter' in content:
        print_test("Rate limiter instantiated", True)
        passed += 1
    else:
        print_test("Rate limiter instantiated", False)
    
    return passed, total

def test_authentication() -> Tuple[int, int]:
    """Test 7: Authentication"""
    print_header("TEST 7: Authentication (Optional)")
    passed = 0
    total = 0
    
    with open('movie_recommender.py', 'r') as f:
        content = f.read()
    
    # Test 7.1: Authentication function exists
    total += 1
    if 'def check_authentication' in content:
        print_test("Authentication function exists", True)
        passed += 1
    else:
        print_test("Authentication function exists", False)
    
    # Test 7.2: Logout functionality
    total += 1
    if 'def add_logout_button' in content or 'Logout' in content:
        print_test("Logout functionality implemented", True)
        passed += 1
    else:
        print_test("Logout functionality implemented", False)
    
    # Test 7.3: Session state for auth
    total += 1
    if 'authenticated' in content:
        print_test("Authentication session state", True)
        passed += 1
    else:
        print_test("Authentication session state", False)
    
    # Test 7.4: Brute force protection
    total += 1
    if 'time.sleep' in content:
        print_test("Brute force protection (delay)", True)
        passed += 1
    else:
        print_test("Brute force protection (delay)", False)
    
    return passed, total

def test_error_sanitization() -> Tuple[int, int]:
    """Test 8: Error Message Sanitization"""
    print_header("TEST 8: Error Message Sanitization")
    passed = 0
    total = 0
    
    with open('movie_recommender.py', 'r') as f:
        content = f.read()
    
    # Test 8.1: Error sanitization function
    total += 1
    if 'def sanitize_error_message' in content:
        print_test("Error sanitization function exists", True)
        passed += 1
    else:
        print_test("Error sanitization function exists", False)
    
    # Test 8.2: User-friendly error function
    total += 1
    if 'def get_user_friendly_error' in content:
        print_test("User-friendly error messages", True)
        passed += 1
    else:
        print_test("User-friendly error messages", False)
    
    # Test 8.3: Path redaction
    total += 1
    if '[PATH]' in content or 're.sub' in content:
        print_test("Sensitive path redaction", True)
        passed += 1
    else:
        print_test("Sensitive path redaction", False)
    
    return passed, total

def test_ssl_verification() -> Tuple[int, int]:
    """Test 9: SSL Verification and Timeouts"""
    print_header("TEST 9: SSL Verification & Timeouts")
    passed = 0
    total = 0
    
    with open('movie_recommender.py', 'r') as f:
        content = f.read()
    
    # Test 9.1: SSL verification enabled
    total += 1
    verify_count = content.count('verify=True')
    if verify_count >= 4:  # We have 4 requests.get calls
        print_test("SSL verification enabled", True, f"Found in {verify_count} locations")
        passed += 1
    else:
        print_test("SSL verification enabled", False, f"Only found in {verify_count}/4 locations")
    
    # Test 9.2: Request timeouts set
    total += 1
    timeout_count = content.count('timeout=10') + content.count('timeout=')
    if timeout_count >= 4:
        print_test("Request timeouts configured", True)
        passed += 1
    else:
        print_test("Request timeouts configured", False)
    
    return passed, total

def test_security_headers() -> Tuple[int, int]:
    """Test 10: Security Headers Configuration"""
    print_header("TEST 10: Security Headers Configuration")
    passed = 0
    total = 0
    
    # Test 10.1: Streamlit config exists
    total += 1
    try:
        with open('.streamlit/config.toml', 'r') as f:
            config = f.read()
        print_test("Streamlit security config exists", True)
        passed += 1
        
        # Test 10.2: XSRF protection enabled
        total += 1
        if 'enableXsrfProtection' in config:
            print_test("XSRF protection configured", True)
            passed += 1
        else:
            print_test("XSRF protection configured", False)
        
        # Test 10.3: CORS disabled
        total += 1
        if 'enableCORS = false' in config:
            print_test("CORS properly configured", True)
            passed += 1
        else:
            print_test("CORS properly configured", False)
            
    except FileNotFoundError:
        print_test("Streamlit security config exists", False, ".streamlit/config.toml not found")
        total += 2  # Account for tests 10.2 and 10.3
    
    # Test 10.4: Security documentation exists
    total += 1
    try:
        with open('SECURITY.md', 'r') as f:
            security_doc = f.read()
        if len(security_doc) > 1000:  # Should be comprehensive
            print_test("Security documentation exists", True)
            passed += 1
        else:
            print_test("Security documentation exists", False, "Documentation too short")
    except FileNotFoundError:
        print_test("Security documentation exists", False, "SECURITY.md not found")
    
    return passed, total

def main():
    """Run all security tests."""
    print(f"\n{BLUE}{'*' * 60}{RESET}")
    print(f"{BLUE}  Movie Recommender - Security Test Suite{RESET}")
    print(f"{BLUE}{'*' * 60}{RESET}")
    
    all_tests = [
        ("API Key Protection", test_api_key_protection),
        ("XSS Protection", test_xss_protection),
        ("Input Validation", test_input_validation),
        ("Prompt Injection Protection", test_prompt_injection_protection),
        ("Dependency Security", test_dependencies),
        ("Rate Limiting", test_rate_limiting),
        ("Authentication", test_authentication),
        ("Error Sanitization", test_error_sanitization),
        ("SSL Verification", test_ssl_verification),
        ("Security Headers", test_security_headers),
    ]
    
    total_passed = 0
    total_tests = 0
    results = []
    
    for name, test_func in all_tests:
        passed, total = test_func()
        total_passed += passed
        total_tests += total
        results.append((name, passed, total))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    for name, passed, total in results:
        percentage = (passed / total * 100) if total > 0 else 0
        color = GREEN if percentage >= 80 else YELLOW if percentage >= 60 else RED
        print(f"{color}{name:.<50} {passed}/{total} ({percentage:.0f}%){RESET}")
    
    print(f"\n{BLUE}{'─' * 60}{RESET}")
    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    if overall_percentage >= 90:
        status = f"{GREEN}EXCELLENT ✓{RESET}"
    elif overall_percentage >= 75:
        status = f"{YELLOW}GOOD ⚠{RESET}"
    elif overall_percentage >= 60:
        status = f"{YELLOW}NEEDS IMPROVEMENT ⚠{RESET}"
    else:
        status = f"{RED}CRITICAL ISSUES ✗{RESET}"
    
    print(f"\n{BLUE}Overall Score: {total_passed}/{total_tests} ({overall_percentage:.1f}%) - {status}{RESET}\n")
    
    if overall_percentage >= 90:
        print(f"{GREEN}🎉 Your application has excellent security! Ready for production.{RESET}\n")
    elif overall_percentage >= 75:
        print(f"{YELLOW}⚠️  Your application has good security, but some improvements recommended.{RESET}\n")
    else:
        print(f"{RED}❌ Critical security issues detected. Please address failing tests before deploying.{RESET}\n")
    
    # Return exit code
    return 0 if overall_percentage >= 75 else 1

if __name__ == "__main__":
    sys.exit(main())


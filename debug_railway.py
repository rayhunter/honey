#!/usr/bin/env python3
"""
Quick diagnostic script to identify Railway deployment issues.
Run this locally to check what might be wrong.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("RAILWAY DEPLOYMENT DIAGNOSTICS")
print("=" * 60)

# Check 1: Environment Variables
print("\n1. ENVIRONMENT VARIABLES:")
print("-" * 60)

env_vars = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
    "TMDB_API_KEY": os.getenv("TMDB_API_KEY"),
    "APP_PASSWORD": os.getenv("APP_PASSWORD"),
}

for var_name, var_value in env_vars.items():
    if var_value:
        # Show first 10 chars only for security
        masked = var_value[:10] + "..." if len(var_value) > 10 else var_value[:5] + "..."
        print(f"✓ {var_name}: SET ({masked})")
    else:
        print(f"✗ {var_name}: NOT SET")

# Check 2: Test OpenAI API
print("\n2. OPENAI API TEST:")
print("-" * 60)
try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
        print("✓ OpenAI client initialized")
        # Try a minimal test
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'test'"}],
                max_tokens=5
            )
            print("✓ OpenAI API working!")
        except Exception as e:
            print(f"✗ OpenAI API call failed: {str(e)[:100]}")
    else:
        print("✗ No OpenAI API key set")
except Exception as e:
    print(f"✗ OpenAI import failed: {e}")

# Check 3: Test TMDB API
print("\n3. TMDB API TEST:")
print("-" * 60)
try:
    import requests
    api_key = os.getenv("TMDB_API_KEY")
    if api_key:
        response = requests.get(
            "https://api.themoviedb.org/3/configuration",
            params={"api_key": api_key},
            timeout=10,
            verify=True
        )
        if response.status_code == 200:
            print("✓ TMDB API working!")
        else:
            print(f"✗ TMDB API error: Status {response.status_code}")
    else:
        print("✗ No TMDB API key set")
except Exception as e:
    print(f"✗ TMDB test failed: {str(e)[:100]}")

# Check 4: Test DeepSeek API (if set)
print("\n4. DEEPSEEK API TEST:")
print("-" * 60)
try:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        from openai import OpenAI
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        print("✓ DeepSeek client initialized")
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "Say 'test'"}],
                max_tokens=5
            )
            print("✓ DeepSeek API working!")
        except Exception as e:
            print(f"✗ DeepSeek API call failed: {str(e)[:100]}")
    else:
        print("⚠ DeepSeek API key not set (optional)")
except Exception as e:
    print(f"✗ DeepSeek test failed: {str(e)[:100]}")

# Check 5: Dependencies
print("\n5. DEPENDENCIES:")
print("-" * 60)
required_packages = ['streamlit', 'openai', 'requests', 'reportlab', 'python-dotenv']
for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"✓ {package}: installed")
    except ImportError:
        print(f"✗ {package}: NOT installed")

# Check 6: Files
print("\n6. REQUIRED FILES:")
print("-" * 60)
required_files = [
    'movie_recommender.py',
    'requirements.txt',
    'Dockerfile',
    '.streamlit/config.toml',
    'style/tailwind_glassmorphism.css'
]
for file in required_files:
    if os.path.exists(file):
        print(f"✓ {file}: exists")
    else:
        print(f"✗ {file}: MISSING")

print("\n" + "=" * 60)
print("DIAGNOSTICS COMPLETE")
print("=" * 60)

# Summary
print("\nCOMMON ISSUES TO CHECK IN RAILWAY:")
print("-" * 60)
print("1. Go to Railway → Your Service → Variables")
print("2. Verify ALL required environment variables are set:")
print("   - OPENAI_API_KEY")
print("   - TMDB_API_KEY")
print("3. Check Railway logs for specific error messages")
print("4. If rate limited, wait 5 minutes")
print("\nIf API keys work locally but not on Railway:")
print("→ Copy the EXACT values from .env to Railway Variables")
print("→ Make sure there are no extra spaces or quotes")
print()


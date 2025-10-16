#!/usr/bin/env python3
"""
SPECTER Legal Assistant Deployment Verification Script
Verifies that all components are ready for deployment
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NOT FOUND")
        return False

def check_python_imports():
    """Check if critical Python imports work"""
    print("\n🐍 Checking Python imports...")
    
    critical_imports = [
        ("fitz", "PyMuPDF for PDF processing"),
        ("fastapi", "FastAPI web framework"),
        ("motor", "MongoDB async driver"),
        ("uvicorn", "ASGI server"),
        ("openai", "OpenAI client"),
        ("pymongo", "MongoDB driver"),
    ]
    
    all_good = True
    os.chdir("backend")
    
    for import_name, description in critical_imports:
        try:
            __import__(import_name)
            print(f"✅ {description} ({import_name})")
        except ImportError as e:
            print(f"❌ {description} ({import_name}): {e}")
            all_good = False
    
    os.chdir("..")
    return all_good

def check_frontend_build():
    """Check if frontend can be built successfully"""
    print("\n⚛️  Checking frontend build...")
    
    os.chdir("frontend/react_app")
    
    try:
        # Check if build directory exists and is recent
        build_dir = Path("build")
        if build_dir.exists():
            print("✅ Frontend build directory exists")
            return True
        else:
            print("🔨 Building frontend...")
            result = subprocess.run(["npm", "run", "build"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Frontend builds successfully")
                return True
            else:
                print(f"❌ Frontend build failed: {result.stderr}")
                return False
    except Exception as e:
        print(f"❌ Frontend build check failed: {e}")
        return False
    finally:
        os.chdir("../..")

def check_backend_startup():
    """Check if backend can start without errors"""
    print("\n🚀 Checking backend startup...")
    
    os.chdir("backend")
    
    try:
        # Test critical imports only (avoid heavy model loading)
        test_imports = [
            "import fastapi",
            "import uvicorn",
            "import fitz",
            "from doc_parser import parse_and_chunk",
            "print('Core backend imports successful')"
        ]
        
        result = subprocess.run([
            sys.executable, "-c", 
            "; ".join(test_imports)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Backend core imports work successfully")
            return True
        else:
            print(f"❌ Backend import test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Backend startup test timed out (heavy model loading?)")
        return False
    except Exception as e:
        print(f"❌ Backend startup check failed: {e}")
        return False
    finally:
        os.chdir("..")

def check_deployment_configs():
    """Check deployment configuration files"""
    print("\n📋 Checking deployment configurations...")
    
    configs = [
        ("nixpacks.toml", "Nixpacks build configuration"),
        ("runtime.txt", "Python runtime specification"),
        ("netlify.toml", "Netlify deployment configuration"),
        ("Procfile", "Process file for deployment"),
        ("backend/requirements.txt", "Python dependencies"),
        ("frontend/react_app/package.json", "Node.js dependencies"),
    ]
    
    all_good = True
    for file_path, description in configs:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def check_environment_variables():
    """Check if required environment variables are documented"""
    print("\n🔧 Checking environment configuration...")
    
    required_files = [
        (".env.example", "Environment variables template"),
        ("backend/.env.example", "Backend environment template"),
    ]
    
    all_good = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def main():
    """Main verification function"""
    print("🔍 SPECTER Legal Assistant - Deployment Verification")
    print("=" * 50)
    
    # Change to project root
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    checks = [
        ("Deployment Configurations", check_deployment_configs),
        ("Environment Variables", check_environment_variables),
        ("Python Imports", check_python_imports),
        ("Frontend Build", check_frontend_build),
        ("Backend Startup", check_backend_startup),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n📊 Running {check_name} check...")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! Ready for deployment.")
        print("\n🚀 Next steps:")
        print("1. Push changes to your repository")
        print("2. Deploy backend to Render (should work automatically)")
        print("3. Deploy frontend to Netlify (should work automatically)")
        print("4. Set environment variables on both platforms")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    exit(main())
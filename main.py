#!/usr/bin/env python3
"""
SeriesDL - Main entry point
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Python 3.7+ required. Please update Python.")
        print("Download from: https://www.python.org/downloads/")
        input("Press Enter to exit...")
        sys.exit(1)

def install_requirements():
    """Install required packages from requirements.txt"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("requirements.txt not found!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("Installing required packages...")
    
    with open(requirements_file, 'r') as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    for i, package in enumerate(packages, 1):
        package_name = package.split('>=')[0].split('==')[0]
        print(f"Installing {package_name} ({i}/{len(packages)})...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package, "--quiet"
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                print(f"Failed to install {package_name}")
                print(f"Error: {result.stderr}")
                input("Press Enter to exit...")
                sys.exit(1)
                
        except subprocess.TimeoutExpired:
            print(f"Timeout installing {package_name}")
            input("Press Enter to exit...")
            sys.exit(1)
        except Exception as e:
            print(f"Error installing {package_name}: {e}")
            input("Press Enter to exit...")
            sys.exit(1)
    
    print("All packages installed successfully!")
    time.sleep(1)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        ('requests', 'requests'),
        ('cloudscraper', 'cloudscraper'), 
        ('bs4', 'beautifulsoup4'),
        ('rich', 'rich')
    ]
    
    missing = []
    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print("Installing missing packages...")
        install_requirements()

def main():
    """Main entry point"""
    try:
        check_python_version()
        check_dependencies()
        
        # import app after dependencies are checked
        from core.app import SeriesDLApp
        
        SeriesDLApp().run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
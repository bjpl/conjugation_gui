"""
Build script for creating a standalone executable of the Spanish Conjugation GUI.
This script uses PyInstaller to package the application.
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("✓ PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed successfully")

def create_executable():
    """Create the executable using PyInstaller."""
    print("\n" + "="*50)
    print("Building Spanish Conjugation Practice Executable")
    print("="*50 + "\n")
    
    # Install PyInstaller if needed
    install_pyinstaller()
    
    # PyInstaller command with options
    command = [
        sys.executable, "-m", "PyInstaller",
        "--name", "SpanishConjugation",
        "--windowed",  # No console window
        "--onefile",   # Single executable file
        "--icon", "NONE",  # You can add an icon file later
        "--add-data", f"app_config.json{os.pathsep}.",
        "--add-data", f".env.example{os.pathsep}.",
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtGui", 
        "--hidden-import", "PyQt5.QtWidgets",
        "--hidden-import", "openai",
        "--hidden-import", "dotenv",
        "--clean",  # Clean PyInstaller cache
        "main.py"
    ]
    
    print("Running PyInstaller with the following options:")
    print(" ".join(command[2:]))  # Skip python and -m
    print("\nThis may take a few minutes...\n")
    
    try:
        subprocess.check_call(command)
        print("\n✓ Build completed successfully!")
        
        # Check if the executable was created
        exe_path = os.path.join("dist", "SpanishConjugation.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\nExecutable created at: {os.path.abspath(exe_path)}")
            print(f"File size: {size_mb:.1f} MB")
            
            # Create a distribution folder with necessary files
            dist_folder = "SpanishConjugation_Distribution"
            if os.path.exists(dist_folder):
                shutil.rmtree(dist_folder)
            os.makedirs(dist_folder)
            
            # Copy executable
            shutil.copy(exe_path, dist_folder)
            
            # Copy .env.example
            shutil.copy(".env.example", dist_folder)
            
            # Create a simple batch file to run with .env
            batch_content = """@echo off
echo Starting Spanish Conjugation Practice...
echo.
if not exist .env (
    echo Please create a .env file with your OpenAI API key.
    echo See .env.example for the format.
    echo.
    pause
    exit
)
SpanishConjugation.exe
"""
            with open(os.path.join(dist_folder, "Run.bat"), "w") as f:
                f.write(batch_content)
            
            # Create a README for distribution
            dist_readme = """Spanish Conjugation Practice - Quick Start

1. SETUP API KEY:
   - Rename '.env.example' to '.env'
   - Open .env and replace 'your_openai_api_key_here' with your actual OpenAI API key
   - Get your API key from: https://platform.openai.com/api-keys

2. RUN THE APPLICATION:
   - Double-click 'Run.bat' to start
   - Or double-click 'SpanishConjugation.exe' directly (if .env is configured)

3. FIRST TIME USE:
   - Click "New Exercise" to generate practice sentences
   - Select your preferred tenses and difficulty
   - Start practicing!

Troubleshooting:
- If the app doesn't start, ensure .env file exists with valid API key
- Windows may show a security warning on first run - click "Run anyway"
"""
            with open(os.path.join(dist_folder, "README.txt"), "w") as f:
                f.write(dist_readme)
            
            print(f"\n✓ Distribution folder created: {os.path.abspath(dist_folder)}")
            print("\nContents:")
            for file in os.listdir(dist_folder):
                print(f"  - {file}")
            
            print("\n" + "="*50)
            print("BUILD SUCCESSFUL!")
            print("="*50)
            print(f"\nYour executable is ready in: {dist_folder}")
            print("\nTo distribute:")
            print("1. Share the entire 'SpanishConjugation_Distribution' folder")
            print("2. Users need to add their OpenAI API key to .env file")
            print("3. Run the app using Run.bat or the .exe directly")
            
        else:
            print("\n✗ Error: Executable not found in dist folder")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_executable()
    if not success:
        print("\nBuild failed. Please check the error messages above.")
        sys.exit(1)
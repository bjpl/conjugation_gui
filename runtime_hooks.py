"""
Runtime hooks for PyInstaller
Handles environment setup and path configuration at runtime
"""
import sys
import os
from pathlib import Path

def setup_environment():
    """Setup environment variables and paths"""
    # Get the directory where the executable is located
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller temporary directory
        base_dir = Path(sys._MEIPASS)
        app_dir = Path(sys.executable).parent
    else:
        # Development mode
        base_dir = Path(__file__).parent
        app_dir = base_dir
    
    # Set environment variables
    os.environ['APP_BASE_DIR'] = str(base_dir)
    os.environ['APP_DIR'] = str(app_dir)
    
    # Add base directory to Python path
    sys.path.insert(0, str(base_dir))
    
    # Ensure .env file is found in the app directory
    env_file = app_dir / '.env'
    if env_file.exists():
        os.environ['ENV_FILE_PATH'] = str(env_file)
    
    # Set up SSL certificate path for requests
    import certifi
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    os.environ['SSL_CERT_FILE'] = certifi.where()

def setup_qt_plugins():
    """Setup Qt plugin paths for PyQt5"""
    if hasattr(sys, '_MEIPASS'):
        # In PyInstaller bundle
        qt_plugins_path = Path(sys._MEIPASS) / 'PyQt5' / 'Qt' / 'plugins'
        if qt_plugins_path.exists():
            os.environ['QT_PLUGIN_PATH'] = str(qt_plugins_path)
        
        # Alternative plugin locations
        plugin_locations = [
            Path(sys._MEIPASS) / 'platforms',
            Path(sys._MEIPASS) / 'imageformats',
            Path(sys._MEIPASS) / 'styles'
        ]
        
        for location in plugin_locations:
            if location.exists():
                current_path = os.environ.get('QT_PLUGIN_PATH', '')
                if current_path:
                    os.environ['QT_PLUGIN_PATH'] = f"{current_path};{location}"
                else:
                    os.environ['QT_PLUGIN_PATH'] = str(location)

def setup_logging():
    """Setup logging directory"""
    if hasattr(sys, '_MEIPASS'):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).parent
    
    # Ensure logs go to the app directory, not temp
    log_file = app_dir / 'logging_doc.txt'
    session_log = app_dir / 'session_log.txt'
    
    os.environ['LOG_FILE_PATH'] = str(log_file)
    os.environ['SESSION_LOG_PATH'] = str(session_log)

def main():
    """Main runtime setup function"""
    try:
        setup_environment()
        setup_qt_plugins()
        setup_logging()
        
        # Import main modules to trigger any initialization
        import PyQt5.QtCore
        import PyQt5.QtWidgets
        
        # Verify SSL setup
        import ssl
        import certifi
        
        print("✅ Runtime hooks executed successfully")
        
    except Exception as e:
        print(f"⚠️ Runtime hook error: {e}")
        # Don't fail the application launch for runtime hook errors

# Execute runtime setup
main()
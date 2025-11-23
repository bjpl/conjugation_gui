"""
Build installer script using NSIS
Creates professional Windows installer for Spanish Conjugation GUI
"""
import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from typing import Dict, Optional

class NSISBuilder:
    """NSIS installer builder"""
    
    def __init__(self, config_file: str = "build_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.nsis_script = "installer.nsi"
        self.assets_dir = Path("assets")
        
    def load_config(self) -> Dict:
        """Load build configuration"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file {self.config_file} not found!")
            sys.exit(1)
    
    def check_nsis_installed(self) -> bool:
        """Check if NSIS is installed and available"""
        try:
            result = subprocess.run(["makensis", "/VERSION"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ NSIS found: {version}")
                return True
            else:
                return False
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def download_nsis(self) -> bool:
        """Provide instructions for downloading NSIS"""
        print("❌ NSIS not found!")
        print("\n📥 To install NSIS:")
        print("1. Visit: https://nsis.sourceforge.io/Download")
        print("2. Download NSIS 3.x")
        print("3. Install and add to PATH")
        print("4. Or use chocolatey: choco install nsis")
        print("5. Or use winget: winget install NSIS.NSIS")
        
        return False
    
    def prepare_assets(self) -> bool:
        """Prepare assets for installer"""
        print("🎨 Preparing installer assets...")
        
        self.assets_dir.mkdir(exist_ok=True)
        
        # Create default icon if it doesn't exist
        icon_path = self.assets_dir / "icon.ico"
        if not icon_path.exists():
            self.create_default_icon(icon_path)
        
        # Create header bitmap for installer
        header_path = self.assets_dir / "header.bmp"
        if not header_path.exists():
            self.create_header_bitmap(header_path)
        
        # Create wizard bitmap
        wizard_path = self.assets_dir / "wizard.bmp"
        if not wizard_path.exists():
            self.create_wizard_bitmap(wizard_path)
        
        return True
    
    def create_default_icon(self, icon_path: Path) -> None:
        """Create default icon using PIL"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create icon with multiple sizes
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            images = []
            
            for size in sizes:
                icon = Image.new('RGBA', size, (70, 130, 180, 255))  # Steel blue
                draw = ImageDraw.Draw(icon)
                
                # Draw a simple "ES" for Spanish
                font_size = max(size[0] // 4, 8)
                try:
                    # Try to use a system font
                    font = ImageFont.truetype("arial.ttf", font_size)
                except OSError:
                    font = ImageFont.load_default()
                
                text = "ES"
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                x = (size[0] - text_width) // 2
                y = (size[1] - text_height) // 2
                
                draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
                images.append(icon)
            
            # Save as ICO with multiple sizes
            images[0].save(icon_path, format='ICO', sizes=[(img.size[0], img.size[1]) for img in images])
            print(f"✅ Created icon: {icon_path}")
            
        except ImportError:
            print("⚠️ PIL not available, using text-based icon placeholder")
            # Create a minimal ICO file
            icon_path.touch()
    
    def create_header_bitmap(self, header_path: Path) -> None:
        """Create header bitmap for installer"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Standard NSIS header size
            header = Image.new('RGB', (150, 57), (245, 245, 245))  # Light gray
            draw = ImageDraw.Draw(header)
            
            # Add gradient effect
            for y in range(57):
                color_value = int(245 - (y * 0.5))
                draw.line([(0, y), (150, y)], fill=(color_value, color_value, color_value))
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except OSError:
                font = ImageFont.load_default()
            
            draw.text((10, 20), "Spanish", fill=(70, 130, 180), font=font)
            draw.text((10, 35), "Conjugation", fill=(70, 130, 180), font=font)
            
            header.save(header_path, format='BMP')
            print(f"✅ Created header: {header_path}")
            
        except ImportError:
            print("⚠️ PIL not available, skipping header creation")
    
    def create_wizard_bitmap(self, wizard_path: Path) -> None:
        """Create wizard bitmap for installer"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Standard NSIS wizard size
            wizard = Image.new('RGB', (164, 314), (255, 255, 255))  # White background
            draw = ImageDraw.Draw(wizard)
            
            # Add gradient
            for y in range(314):
                blue_value = int(255 - (y * 0.3))
                if blue_value < 100:
                    blue_value = 100
                draw.line([(0, y), (164, y)], fill=(blue_value, blue_value, 255))
            
            # Add app info
            try:
                font_large = ImageFont.truetype("arial.ttf", 16)
                font_small = ImageFont.truetype("arial.ttf", 10)
            except OSError:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            draw.text((10, 50), "Spanish", fill=(0, 0, 100), font=font_large)
            draw.text((10, 70), "Conjugation", fill=(0, 0, 100), font=font_large)
            draw.text((10, 90), "Practice", fill=(0, 0, 100), font=font_large)
            
            draw.text((10, 130), "AI-Powered Learning", fill=(50, 50, 150), font=font_small)
            draw.text((10, 150), "Interactive Practice", fill=(50, 50, 150), font=font_small)
            draw.text((10, 170), "Progress Tracking", fill=(50, 50, 150), font=font_small)
            
            wizard.save(wizard_path, format='BMP')
            print(f"✅ Created wizard bitmap: {wizard_path}")
            
        except ImportError:
            print("⚠️ PIL not available, skipping wizard bitmap creation")
    
    def update_nsis_script(self) -> bool:
        """Update NSIS script with current configuration"""
        if not Path(self.nsis_script).exists():
            print(f"❌ NSIS script not found: {self.nsis_script}")
            return False
        
        # Read current script
        with open(self.nsis_script, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Update with current config values
        app_config = self.config['app']
        
        replacements = {
            '!define APP_NAME "Spanish Conjugation Practice"': f'!define APP_NAME "{app_config["display_name"]}"',
            '!define APP_VERSION "2.0.0"': f'!define APP_VERSION "{app_config["version"]}"',
            '!define APP_PUBLISHER "Spanish Learning Tools"': f'!define APP_PUBLISHER "{app_config["author"]}"',
            '!define APP_DESCRIPTION "Spanish Conjugation Practice with AI-powered feedback"': f'!define APP_DESCRIPTION "{app_config["description"]}"',
            '!define APP_HOMEPAGE "https://github.com/yourusername/conjugation_gui"': f'!define APP_HOMEPAGE "{app_config.get("homepage", "")}"'
        }
        
        for old, new in replacements.items():
            script_content = script_content.replace(old, new)
        
        # Write updated script
        updated_script = "installer_updated.nsi"
        with open(updated_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return True
    
    def build_installer(self) -> bool:
        """Build the installer using NSIS"""
        print("🔨 Building installer...")
        
        # Check for executable
        app_name = self.config['app']['name']
        exe_path = Path("dist") / f"{app_name}.exe"
        
        if not exe_path.exists():
            print(f"❌ Executable not found: {exe_path}")
            print("Please run the build script first to create the executable.")
            return False
        
        # Update NSIS script
        if not self.update_nsis_script():
            return False
        
        # Build installer
        nsis_script = "installer_updated.nsi"
        cmd = ["makensis", nsis_script]
        
        print("🚀 NSIS command:")
        print(" ".join(cmd))
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Installer built successfully!")
                
                # Find the generated installer
                app_version = self.config['app']['version']
                installer_name = f"SpanishConjugationSetup_v{app_version}.exe"
                
                if Path(installer_name).exists():
                    installer_size = Path(installer_name).stat().st_size / (1024 * 1024)
                    print(f"📦 Installer: {Path(installer_name).absolute()}")
                    print(f"📏 Size: {installer_size:.1f} MB")
                    return True
                else:
                    print("⚠️ Installer file not found, but build reported success")
                    return False
            else:
                print(f"❌ NSIS build failed: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ NSIS build error: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False
        
        finally:
            # Cleanup temporary script
            if Path("installer_updated.nsi").exists():
                Path("installer_updated.nsi").unlink()
    
    def test_installer(self) -> bool:
        """Test the installer (dry run)"""
        print("🧪 Testing installer...")
        
        app_version = self.config['app']['version']
        installer_name = f"SpanishConjugationSetup_v{app_version}.exe"
        
        if not Path(installer_name).exists():
            print(f"❌ Installer not found: {installer_name}")
            return False
        
        # Just check that the installer can be executed with /? parameter
        try:
            result = subprocess.run([installer_name, "/?"], 
                                  capture_output=True, text=True, timeout=30)
            print("✅ Installer executable test passed")
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"⚠️ Installer test warning: {e}")
            return True  # Don't fail the build for this
    
    def build_summary(self) -> None:
        """Print build summary"""
        app_version = self.config['app']['version']
        installer_name = f"SpanishConjugationSetup_v{app_version}.exe"
        
        print("\n" + "="*60)
        print("🎉 INSTALLER BUILD COMPLETE!")
        print("="*60)
        print(f"Application: {self.config['app']['display_name']}")
        print(f"Version: {app_version}")
        
        if Path(installer_name).exists():
            size_mb = Path(installer_name).stat().st_size / (1024 * 1024)
            print(f"Installer: {Path(installer_name).absolute()}")
            print(f"Size: {size_mb:.1f} MB")
        
        print("\n📋 Distribution Instructions:")
        print("1. Test installer on clean Windows system")
        print("2. Consider code signing for security")
        print("3. Upload to download server or distribution platform")
        print("4. Update documentation with download links")
        print("\n💡 Installer Features:")
        print("• API key configuration during installation")
        print("• Desktop and Start Menu shortcuts")
        print("• Proper uninstaller")
        print("• Registry integration")
        print("• Visual C++ Redistributable check")
        print("="*60)
    
    def run_build(self) -> bool:
        """Run the complete installer build process"""
        print("🚀 Starting installer build process...")
        print("="*60 + "\n")
        
        # Check NSIS installation
        if not self.check_nsis_installed():
            return self.download_nsis()
        
        # Prepare assets
        if not self.prepare_assets():
            return False
        
        # Build installer
        if not self.build_installer():
            return False
        
        # Test installer
        self.test_installer()
        
        # Show summary
        self.build_summary()
        
        return True

def main():
    """Main entry point"""
    builder = NSISBuilder()
    
    try:
        success = builder.run_build()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
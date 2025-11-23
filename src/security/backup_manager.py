"""
Backup and Recovery Manager for Spanish Conjugation GUI
=======================================================

This module provides comprehensive backup and recovery functionality for
credentials, configuration, and application data with encryption and
versioning support.

Features:
- Automated backup scheduling
- Encrypted backup storage
- Version management and rotation
- Recovery and restoration
- Backup integrity verification
- Cross-platform support

Author: Brand
Version: 1.0.0
"""

import os
import json
import shutil
import logging
import hashlib
import zipfile
import tempfile
from typing import Dict, Optional, Any, List, Callable
from pathlib import Path
from datetime import datetime, timedelta
import threading
import schedule

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

from .credentials_manager import CredentialsManager


class BackupError(Exception):
    """Base exception for backup operations"""
    pass


class BackupManager:
    """
    Comprehensive backup and recovery manager.
    
    Provides automated backup functionality with encryption, versioning,
    and integrity verification for all application data.
    """
    
    def __init__(self, 
                 app_name: str = "SpanishConjugationGUI",
                 backup_dir: Optional[Path] = None):
        """
        Initialize backup manager.
        
        Args:
            app_name: Application name
            backup_dir: Custom backup directory
        """
        self.app_name = app_name
        self.logger = logging.getLogger(f'{app_name}.backup')
        
        # Set up backup directory
        if backup_dir:
            self.backup_dir = Path(backup_dir)
        else:
            # Use platform-appropriate backup location
            if os.name == 'nt':  # Windows
                base_dir = Path.home() / 'Documents' / app_name / 'Backups'
            else:  # Linux/macOS
                base_dir = Path.home() / '.local' / 'share' / app_name.lower() / 'backups'
            self.backup_dir = base_dir
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.max_backups = 10
        self.backup_retention_days = 30
        self.compression_enabled = True
        self.encryption_enabled = CRYPTO_AVAILABLE
        
        # Backup types
        self.backup_types = {
            'full': 'Complete system backup',
            'credentials': 'Credentials and keys only',
            'config': 'Configuration files only',
            'data': 'User data and progress only',
            'minimal': 'Essential files only'
        }
        
        # Scheduler for automatic backups
        self.scheduler_thread = None
        self.scheduler_running = False
        
        self.logger.info("Backup manager initialized")
    
    def create_backup(self, 
                     backup_type: str = 'full',
                     encrypt: bool = True,
                     password: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a backup of specified type.
        
        Args:
            backup_type: Type of backup ('full', 'credentials', 'config', 'data', 'minimal')
            encrypt: Whether to encrypt the backup
            password: Encryption password (optional)
            
        Returns:
            Backup result information
        """
        if backup_type not in self.backup_types:
            raise BackupError(f"Unknown backup type: {backup_type}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{self.app_name}_{backup_type}_{timestamp}"
        
        try:
            # Create temporary directory for backup preparation
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_backup_dir = Path(temp_dir) / backup_name
                temp_backup_dir.mkdir()
                
                # Collect files based on backup type
                files_backed_up = self._collect_backup_files(backup_type, temp_backup_dir)
                
                # Create backup metadata
                metadata = {
                    'backup_name': backup_name,
                    'backup_type': backup_type,
                    'timestamp': datetime.now().isoformat(),
                    'app_name': self.app_name,
                    'files_count': len(files_backed_up),
                    'files': files_backed_up,
                    'encrypted': encrypt and self.encryption_enabled,
                    'compressed': self.compression_enabled,
                    'version': '1.0'
                }
                
                # Save metadata
                metadata_file = temp_backup_dir / 'backup_metadata.json'
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                # Create backup archive
                if self.compression_enabled:
                    backup_file = self.backup_dir / f"{backup_name}.zip"
                    self._create_zip_backup(temp_backup_dir, backup_file, encrypt, password)
                else:
                    backup_file = self.backup_dir / backup_name
                    shutil.copytree(temp_backup_dir, backup_file)
                    if encrypt and self.encryption_enabled:
                        self._encrypt_directory(backup_file, password)
                
                # Calculate backup hash for integrity
                backup_hash = self._calculate_file_hash(backup_file)
                metadata['backup_hash'] = backup_hash
                metadata['backup_size'] = backup_file.stat().st_size
                
                # Save final metadata alongside backup
                final_metadata_file = backup_file.parent / f"{backup_name}_metadata.json"
                with open(final_metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Backup created: {backup_file}")
                
                # Cleanup old backups
                self._cleanup_old_backups(backup_type)
                
                return {
                    'success': True,
                    'backup_file': str(backup_file),
                    'metadata': metadata,
                    'message': f'Successfully created {backup_type} backup'
                }
                
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create {backup_type} backup'
            }
    
    def _collect_backup_files(self, backup_type: str, target_dir: Path) -> List[Dict[str, Any]]:
        """Collect files for backup based on type."""
        files_backed_up = []
        
        # Get application directories
        credentials_manager = CredentialsManager(self.app_name)
        config_dir = credentials_manager.config_dir
        
        # Common directories to consider
        app_dirs = {
            'config': config_dir,
            'data': config_dir,  # For now, data is in config dir
            'logs': config_dir / 'logs' if (config_dir / 'logs').exists() else None,
            'cache': config_dir / 'cache' if (config_dir / 'cache').exists() else None
        }
        
        if backup_type == 'full':
            # Include everything
            include_patterns = ['*']
            exclude_patterns = ['*.tmp', '*.lock', '__pycache__', '*.pyc']
            
        elif backup_type == 'credentials':
            # Only credentials and security files
            include_patterns = ['*.enc', 'master.key', 'credentials.*', 'api_config.*']
            exclude_patterns = []
            
        elif backup_type == 'config':
            # Configuration files
            include_patterns = ['*.json', '*.ini', '*.cfg', '*.toml', '*.yaml', '*.yml']
            exclude_patterns = ['*.enc']  # Exclude encrypted files
            
        elif backup_type == 'data':
            # User data and progress
            include_patterns = ['*.db', '*progress*', '*session*', '*statistics*', '*.log']
            exclude_patterns = []
            
        elif backup_type == 'minimal':
            # Essential files only
            include_patterns = ['api_config.json', '*.db', 'credentials.enc']
            exclude_patterns = []
        
        # Collect files from each relevant directory
        for dir_type, dir_path in app_dirs.items():
            if dir_path and dir_path.exists():
                target_subdir = target_dir / dir_type
                target_subdir.mkdir(exist_ok=True)
                
                files_in_dir = self._copy_files_with_patterns(
                    dir_path, target_subdir, include_patterns, exclude_patterns
                )
                files_backed_up.extend(files_in_dir)
        
        # Also backup the main application files if they exist
        app_root = Path.cwd()
        app_files = [
            'main.py',
            'pyproject.toml',
            'requirements.txt',
            'README.md',
            '.env.template'
        ]
        
        if backup_type in ['full', 'config']:
            app_target = target_dir / 'app'
            app_target.mkdir(exist_ok=True)
            
            for filename in app_files:
                app_file = app_root / filename
                if app_file.exists():
                    target_file = app_target / filename
                    shutil.copy2(app_file, target_file)
                    files_backed_up.append({
                        'source': str(app_file),
                        'target': str(target_file),
                        'size': app_file.stat().st_size,
                        'modified': datetime.fromtimestamp(app_file.stat().st_mtime).isoformat()
                    })
        
        return files_backed_up
    
    def _copy_files_with_patterns(self, 
                                 source_dir: Path,
                                 target_dir: Path,
                                 include_patterns: List[str],
                                 exclude_patterns: List[str]) -> List[Dict[str, Any]]:
        """Copy files matching include patterns and not matching exclude patterns."""
        import fnmatch
        
        files_copied = []
        
        for file_path in source_dir.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(source_dir)
                
                # Check include patterns
                included = False
                for pattern in include_patterns:
                    if fnmatch.fnmatch(file_path.name, pattern) or pattern == '*':
                        included = True
                        break
                
                if not included:
                    continue
                
                # Check exclude patterns
                excluded = False
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(file_path.name, pattern):
                        excluded = True
                        break
                
                if excluded:
                    continue
                
                # Copy the file
                target_file = target_dir / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(file_path, target_file)
                    files_copied.append({
                        'source': str(file_path),
                        'target': str(target_file),
                        'relative_path': str(relative_path),
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to copy {file_path}: {e}")
        
        return files_copied
    
    def _create_zip_backup(self, 
                          source_dir: Path,
                          target_file: Path,
                          encrypt: bool,
                          password: Optional[str]) -> None:
        """Create compressed backup archive."""
        with zipfile.ZipFile(target_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
        
        # Encrypt if requested
        if encrypt and self.encryption_enabled:
            self._encrypt_file(target_file, password)
    
    def _encrypt_file(self, file_path: Path, password: Optional[str] = None) -> None:
        """Encrypt a file in place."""
        if not CRYPTO_AVAILABLE:
            self.logger.warning("Encryption requested but cryptography library not available")
            return
        
        try:
            # Generate or derive key
            if password:
                key = self._derive_key_from_password(password)
            else:
                key = Fernet.generate_key()
                # Store key securely (in practice, use better key management)
                key_file = file_path.with_suffix(file_path.suffix + '.key')
                with open(key_file, 'wb') as f:
                    f.write(key)
            
            # Encrypt file
            fernet = Fernet(key)
            
            with open(file_path, 'rb') as f:
                original_data = f.read()
            
            encrypted_data = fernet.encrypt(original_data)
            
            # Write encrypted data
            encrypted_file = file_path.with_suffix(file_path.suffix + '.enc')
            with open(encrypted_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Remove original and rename
            file_path.unlink()
            encrypted_file.rename(file_path)
            
        except Exception as e:
            self.logger.error(f"File encryption failed: {e}")
            raise BackupError(f"Encryption failed: {e}")
    
    def _derive_key_from_password(self, password: str) -> bytes:
        """Derive encryption key from password."""
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        
        salt = b"backup_salt_v1"  # In practice, use random salt and store it
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file."""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def list_backups(self, backup_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available backups.
        
        Args:
            backup_type: Filter by backup type (optional)
            
        Returns:
            List of backup information
        """
        backups = []
        
        # Find backup files
        for backup_file in self.backup_dir.iterdir():
            if backup_file.is_file() and not backup_file.name.endswith('_metadata.json'):
                # Look for corresponding metadata
                metadata_file = backup_file.parent / f"{backup_file.stem}_metadata.json"
                
                backup_info = {
                    'backup_file': str(backup_file),
                    'name': backup_file.stem,
                    'size': backup_file.stat().st_size,
                    'created': datetime.fromtimestamp(backup_file.stat().st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
                }
                
                # Load metadata if available
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        backup_info.update(metadata)
                    except Exception as e:
                        self.logger.warning(f"Failed to load metadata for {backup_file}: {e}")
                        backup_info['metadata_error'] = str(e)
                
                # Filter by type if specified
                if backup_type is None or backup_info.get('backup_type') == backup_type:
                    backups.append(backup_info)
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x.get('timestamp', x['created']), reverse=True)
        
        return backups
    
    def restore_backup(self, 
                      backup_name: str,
                      restore_type: str = 'full',
                      password: Optional[str] = None) -> Dict[str, Any]:
        """
        Restore from backup.
        
        Args:
            backup_name: Name of backup to restore
            restore_type: Type of restoration ('full', 'credentials', 'config', 'data')
            password: Decryption password if needed
            
        Returns:
            Restoration result
        """
        try:
            # Find backup file
            backup_file = None
            for file_path in self.backup_dir.iterdir():
                if backup_name in file_path.name:
                    backup_file = file_path
                    break
            
            if not backup_file or not backup_file.exists():
                return {
                    'success': False,
                    'error': 'Backup file not found',
                    'message': f'Could not find backup: {backup_name}'
                }
            
            # Load backup metadata
            metadata_file = backup_file.parent / f"{backup_file.stem}_metadata.json"
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            # Verify backup integrity
            if 'backup_hash' in metadata:
                current_hash = self._calculate_file_hash(backup_file)
                if current_hash != metadata['backup_hash']:
                    return {
                        'success': False,
                        'error': 'Backup integrity check failed',
                        'message': 'Backup file appears to be corrupted'
                    }
            
            # Extract/decrypt backup
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_extract_dir = Path(temp_dir) / 'extract'
                
                if backup_file.suffix == '.zip':
                    # Handle zip file
                    if metadata.get('encrypted'):
                        # Decrypt first
                        decrypted_file = Path(temp_dir) / 'decrypted.zip'
                        self._decrypt_file(backup_file, decrypted_file, password)
                        with zipfile.ZipFile(decrypted_file, 'r') as zipf:
                            zipf.extractall(temp_extract_dir)
                    else:
                        with zipfile.ZipFile(backup_file, 'r') as zipf:
                            zipf.extractall(temp_extract_dir)
                else:
                    # Handle directory backup
                    if metadata.get('encrypted'):
                        self._decrypt_directory(backup_file, temp_extract_dir, password)
                    else:
                        shutil.copytree(backup_file, temp_extract_dir)
                
                # Restore files based on restore type
                restored_files = self._restore_files(temp_extract_dir, restore_type, metadata)
                
                return {
                    'success': True,
                    'restored_files': len(restored_files),
                    'files': restored_files,
                    'message': f'Successfully restored {restore_type} from backup'
                }
                
        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to restore from backup: {backup_name}'
            }
    
    def _decrypt_file(self, encrypted_file: Path, output_file: Path, password: Optional[str]) -> None:
        """Decrypt a file."""
        if not CRYPTO_AVAILABLE:
            raise BackupError("Decryption requires cryptography library")
        
        try:
            # Get decryption key
            if password:
                key = self._derive_key_from_password(password)
            else:
                key_file = encrypted_file.with_suffix(encrypted_file.suffix + '.key')
                if key_file.exists():
                    with open(key_file, 'rb') as f:
                        key = f.read()
                else:
                    raise BackupError("No decryption key available")
            
            fernet = Fernet(key)
            
            with open(encrypted_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            
            with open(output_file, 'wb') as f:
                f.write(decrypted_data)
                
        except Exception as e:
            raise BackupError(f"Decryption failed: {e}")
    
    def _restore_files(self, 
                      source_dir: Path,
                      restore_type: str,
                      metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Restore files from extracted backup."""
        restored_files = []
        
        credentials_manager = CredentialsManager(self.app_name)
        config_dir = credentials_manager.config_dir
        
        # Determine what to restore based on type
        if restore_type == 'full':
            # Restore everything
            for subdir in source_dir.iterdir():
                if subdir.is_dir():
                    if subdir.name == 'config':
                        target_dir = config_dir
                    elif subdir.name == 'data':
                        target_dir = config_dir  # Data is in config dir for now
                    elif subdir.name == 'app':
                        target_dir = Path.cwd()
                    else:
                        continue
                    
                    restored = self._copy_directory_contents(subdir, target_dir)
                    restored_files.extend(restored)
        
        elif restore_type == 'credentials':
            # Restore only credentials
            config_subdir = source_dir / 'config'
            if config_subdir.exists():
                for file_pattern in ['*.enc', 'master.key', 'credentials.*']:
                    for file_path in config_subdir.glob(file_pattern):
                        target_file = config_dir / file_path.name
                        shutil.copy2(file_path, target_file)
                        restored_files.append({
                            'source': str(file_path),
                            'target': str(target_file),
                            'type': 'credential'
                        })
        
        elif restore_type == 'config':
            # Restore configuration files
            config_subdir = source_dir / 'config'
            if config_subdir.exists():
                for file_pattern in ['*.json', '*.ini', '*.cfg']:
                    for file_path in config_subdir.glob(file_pattern):
                        if not file_path.name.endswith('.enc'):  # Skip encrypted files
                            target_file = config_dir / file_path.name
                            shutil.copy2(file_path, target_file)
                            restored_files.append({
                                'source': str(file_path),
                                'target': str(target_file),
                                'type': 'config'
                            })
        
        elif restore_type == 'data':
            # Restore user data
            data_subdir = source_dir / 'data'
            if data_subdir.exists():
                for file_pattern in ['*.db', '*progress*', '*session*']:
                    for file_path in data_subdir.glob(file_pattern):
                        target_file = config_dir / file_path.name
                        shutil.copy2(file_path, target_file)
                        restored_files.append({
                            'source': str(file_path),
                            'target': str(target_file),
                            'type': 'data'
                        })
        
        return restored_files
    
    def _copy_directory_contents(self, source_dir: Path, target_dir: Path) -> List[Dict[str, Any]]:
        """Copy directory contents and return list of copied files."""
        copied_files = []
        target_dir.mkdir(parents=True, exist_ok=True)
        
        for item in source_dir.rglob('*'):
            if item.is_file():
                relative_path = item.relative_to(source_dir)
                target_file = target_dir / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(item, target_file)
                    copied_files.append({
                        'source': str(item),
                        'target': str(target_file),
                        'relative_path': str(relative_path)
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to restore {item}: {e}")
        
        return copied_files
    
    def _cleanup_old_backups(self, backup_type: str) -> None:
        """Remove old backups based on retention policy."""
        backups = self.list_backups(backup_type)
        
        # Remove excess backups (keep only max_backups)
        if len(backups) > self.max_backups:
            old_backups = backups[self.max_backups:]
            for backup in old_backups:
                try:
                    backup_file = Path(backup['backup_file'])
                    metadata_file = backup_file.parent / f"{backup_file.stem}_metadata.json"
                    
                    if backup_file.exists():
                        backup_file.unlink()
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    self.logger.info(f"Removed old backup: {backup_file.name}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove old backup {backup['backup_file']}: {e}")
        
        # Remove backups older than retention period
        cutoff_date = datetime.now() - timedelta(days=self.backup_retention_days)
        
        for backup in backups:
            backup_date = datetime.fromisoformat(backup.get('timestamp', backup['created']).replace('Z', '+00:00'))
            if backup_date < cutoff_date:
                try:
                    backup_file = Path(backup['backup_file'])
                    metadata_file = backup_file.parent / f"{backup_file.stem}_metadata.json"
                    
                    if backup_file.exists():
                        backup_file.unlink()
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    self.logger.info(f"Removed expired backup: {backup_file.name}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove expired backup: {e}")
    
    def schedule_automatic_backups(self, 
                                  backup_type: str = 'full',
                                  schedule_time: str = '02:00',
                                  interval_days: int = 7) -> bool:
        """
        Schedule automatic backups.
        
        Args:
            backup_type: Type of backup to create
            schedule_time: Time to run backup (HH:MM format)
            interval_days: Interval between backups in days
            
        Returns:
            True if scheduling successful
        """
        try:
            # Clear existing schedule
            schedule.clear()
            
            # Schedule new backup
            schedule.every(interval_days).days.at(schedule_time).do(
                self._scheduled_backup, backup_type
            )
            
            # Start scheduler thread if not running
            if not self.scheduler_running:
                self.scheduler_thread = threading.Thread(target=self._run_scheduler)
                self.scheduler_thread.daemon = True
                self.scheduler_thread.start()
                self.scheduler_running = True
            
            self.logger.info(f"Scheduled {backup_type} backups every {interval_days} days at {schedule_time}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to schedule backups: {e}")
            return False
    
    def _scheduled_backup(self, backup_type: str) -> None:
        """Perform scheduled backup."""
        try:
            result = self.create_backup(backup_type)
            if result['success']:
                self.logger.info(f"Scheduled backup completed: {backup_type}")
            else:
                self.logger.error(f"Scheduled backup failed: {result.get('error')}")
        except Exception as e:
            self.logger.error(f"Scheduled backup error: {e}")
    
    def _run_scheduler(self) -> None:
        """Run the backup scheduler."""
        while self.scheduler_running:
            try:
                schedule.run_pending()
                threading.Event().wait(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
    
    def stop_scheduler(self) -> None:
        """Stop the backup scheduler."""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        schedule.clear()
        self.logger.info("Backup scheduler stopped")
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Get current backup status and statistics."""
        backups = self.list_backups()
        
        status = {
            'backup_dir': str(self.backup_dir),
            'total_backups': len(backups),
            'backup_types': {},
            'total_size': 0,
            'oldest_backup': None,
            'newest_backup': None,
            'scheduler_running': self.scheduler_running,
            'next_scheduled': None,
            'settings': {
                'max_backups': self.max_backups,
                'retention_days': self.backup_retention_days,
                'compression_enabled': self.compression_enabled,
                'encryption_enabled': self.encryption_enabled
            }
        }
        
        # Analyze backups
        if backups:
            for backup in backups:
                backup_type = backup.get('backup_type', 'unknown')
                if backup_type not in status['backup_types']:
                    status['backup_types'][backup_type] = 0
                status['backup_types'][backup_type] += 1
                status['total_size'] += backup.get('size', 0)
            
            # Get oldest and newest
            sorted_backups = sorted(backups, key=lambda x: x.get('timestamp', x['created']))
            status['oldest_backup'] = sorted_backups[0]['name']
            status['newest_backup'] = sorted_backups[-1]['name']
            
            # Get next scheduled backup
            if self.scheduler_running:
                next_run = schedule.next_run()
                if next_run:
                    status['next_scheduled'] = next_run.isoformat()
        
        return status
"""
Update Manager for StosOS
Handles version checking, downloading, and applying updates
"""

import os
import sys
import json
import shutil
import subprocess
import requests
import hashlib
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from packaging import version
import logging
from .config_manager import ConfigManager


class UpdateManager:
    """Manages StosOS updates and version control"""
    
    def __init__(self, config_manager: ConfigManager, logger: logging.Logger):
        self.config = config_manager
        self.logger = logger
        self.current_version = self._get_current_version()
        self.update_server_url = "https://api.github.com/repos/stosos/stosos/releases"
        self.auto_check_enabled = True
        self.last_check_time = None
        
    def _get_current_version(self) -> str:
        """Get current StosOS version"""
        try:
            version_file = os.path.join(os.path.dirname(__file__), '..', 'VERSION')
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            self.logger.error(f"Error reading version file: {e}")
        
        # Fallback to git if available
        try:
            result = subprocess.run(
                ['git', 'describe', '--tags', '--always'],
                cwd=os.path.dirname(__file__),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
            
        return "unknown"
        
    def get_version_info(self) -> Dict[str, Any]:
        """Get detailed version information"""
        info = {
            'current_version': self.current_version,
            'last_check': self.last_check_time,
            'auto_check_enabled': self.auto_check_enabled
        }
        
        # Add git information if available
        try:
            git_info = self._get_git_info()
            info.update(git_info)
        except:
            pass
            
        return info
        
    def _get_git_info(self) -> Dict[str, str]:
        """Get git repository information"""
        git_dir = os.path.join(os.path.dirname(__file__), '..', '.git')
        if not os.path.exists(git_dir):
            return {}
            
        info = {}
        
        try:
            # Get current branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=os.path.dirname(__file__),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info['branch'] = result.stdout.strip()
                
            # Get last commit hash
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                cwd=os.path.dirname(__file__),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info['commit'] = result.stdout.strip()
                
            # Get last commit date
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ci'],
                cwd=os.path.dirname(__file__),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info['commit_date'] = result.stdout.strip()
                
        except Exception as e:
            self.logger.error(f"Error getting git info: {e}")
            
        return info
        
    def check_for_updates(self, force: bool = False) -> Optional[Dict[str, Any]]:
        """Check for available updates"""
        if not force and not self._should_check_for_updates():
            return None
            
        self.logger.info("Checking for updates...")
        self.last_check_time = datetime.now().isoformat()
        
        try:
            # Check GitHub releases
            response = requests.get(self.update_server_url, timeout=30)
            response.raise_for_status()
            
            releases = response.json()
            if not releases:
                return None
                
            latest_release = releases[0]  # First release is the latest
            latest_version = latest_release['tag_name'].lstrip('v')
            
            # Compare versions
            if self._is_newer_version(latest_version, self.current_version):
                update_info = {
                    'available': True,
                    'version': latest_version,
                    'current_version': self.current_version,
                    'release_notes': latest_release.get('body', ''),
                    'download_url': latest_release.get('zipball_url'),
                    'published_at': latest_release.get('published_at'),
                    'prerelease': latest_release.get('prerelease', False)
                }
                
                self.logger.info(f"Update available: {latest_version}")
                return update_info
            else:
                self.logger.info("No updates available")
                return {'available': False, 'current_version': self.current_version}
                
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return None
            
    def _should_check_for_updates(self) -> bool:
        """Determine if we should check for updates"""
        if not self.auto_check_enabled:
            return False
            
        if not self.last_check_time:
            return True
            
        try:
            last_check = datetime.fromisoformat(self.last_check_time)
            return datetime.now() - last_check > timedelta(hours=24)
        except:
            return True
            
    def _is_newer_version(self, new_version: str, current_version: str) -> bool:
        """Compare version strings"""
        try:
            return version.parse(new_version) > version.parse(current_version)
        except:
            # Fallback to string comparison
            return new_version != current_version
            
    def download_update(self, update_info: Dict[str, Any]) -> Optional[str]:
        """Download update package"""
        if not update_info.get('available'):
            return None
            
        download_url = update_info.get('download_url')
        if not download_url:
            self.logger.error("No download URL provided")
            return None
            
        try:
            self.logger.info(f"Downloading update {update_info['version']}...")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix='stosos_update_')
            update_file = os.path.join(temp_dir, f"stosos-{update_info['version']}.zip")
            
            # Download with progress
            response = requests.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Log every MB
                                self.logger.info(f"Download progress: {progress:.1f}%")
                                
            self.logger.info(f"Update downloaded to: {update_file}")
            return update_file
            
        except Exception as e:
            self.logger.error(f"Error downloading update: {e}")
            return None
            
    def apply_update(self, update_file: str, backup: bool = True) -> bool:
        """Apply downloaded update"""
        if not os.path.exists(update_file):
            self.logger.error(f"Update file not found: {update_file}")
            return False
            
        try:
            self.logger.info("Applying update...")
            
            stosos_dir = os.path.dirname(os.path.dirname(__file__))
            
            # Create backup if requested
            if backup:
                backup_dir = self._create_backup(stosos_dir)
                self.logger.info(f"Backup created at: {backup_dir}")
                
            # Extract update
            import zipfile
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                # Extract to temporary directory first
                temp_extract_dir = tempfile.mkdtemp(prefix='stosos_extract_')
                zip_ref.extractall(temp_extract_dir)
                
                # Find the extracted directory (GitHub creates a subdirectory)
                extracted_dirs = [d for d in os.listdir(temp_extract_dir) 
                                if os.path.isdir(os.path.join(temp_extract_dir, d))]
                
                if not extracted_dirs:
                    raise Exception("No directory found in update package")
                    
                source_dir = os.path.join(temp_extract_dir, extracted_dirs[0])
                
                # Copy files (excluding certain directories)
                exclude_dirs = {'.git', '__pycache__', 'venv', 'data', 'logs'}
                
                for item in os.listdir(source_dir):
                    if item in exclude_dirs:
                        continue
                        
                    source_path = os.path.join(source_dir, item)
                    dest_path = os.path.join(stosos_dir, item)
                    
                    if os.path.isdir(source_path):
                        if os.path.exists(dest_path):
                            shutil.rmtree(dest_path)
                        shutil.copytree(source_path, dest_path)
                    else:
                        shutil.copy2(source_path, dest_path)
                        
                # Cleanup
                shutil.rmtree(temp_extract_dir)
                
            # Update dependencies if requirements.txt changed
            self._update_dependencies(stosos_dir)
            
            # Reload systemd service
            self._reload_service()
            
            self.logger.info("Update applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying update: {e}")
            return False
            
    def _create_backup(self, stosos_dir: str) -> str:
        """Create backup of current installation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"/tmp/stosos_backup_{timestamp}"
        
        # Copy entire directory excluding certain subdirectories
        exclude_dirs = {'venv', '__pycache__', '.git'}
        
        os.makedirs(backup_dir)
        
        for item in os.listdir(stosos_dir):
            if item in exclude_dirs:
                continue
                
            source_path = os.path.join(stosos_dir, item)
            dest_path = os.path.join(backup_dir, item)
            
            if os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
                
        return backup_dir
        
    def _update_dependencies(self, stosos_dir: str):
        """Update Python dependencies"""
        requirements_file = os.path.join(stosos_dir, 'requirements.txt')
        if not os.path.exists(requirements_file):
            return
            
        venv_python = os.path.join(stosos_dir, 'venv', 'bin', 'python')
        if not os.path.exists(venv_python):
            return
            
        try:
            subprocess.run([
                venv_python, '-m', 'pip', 'install', '--upgrade',
                '-r', requirements_file
            ], check=True, timeout=300)
            
            self.logger.info("Dependencies updated")
        except Exception as e:
            self.logger.error(f"Error updating dependencies: {e}")
            
    def _reload_service(self):
        """Reload systemd service"""
        try:
            subprocess.run(['systemctl', '--user', 'daemon-reload'], 
                         check=True, timeout=30)
            self.logger.info("Systemd service reloaded")
        except Exception as e:
            self.logger.error(f"Error reloading service: {e}")
            
    def rollback_update(self, backup_dir: str) -> bool:
        """Rollback to previous version from backup"""
        if not os.path.exists(backup_dir):
            self.logger.error(f"Backup directory not found: {backup_dir}")
            return False
            
        try:
            self.logger.info(f"Rolling back from backup: {backup_dir}")
            
            stosos_dir = os.path.dirname(os.path.dirname(__file__))
            
            # Remove current files (except data, logs, venv)
            preserve_dirs = {'data', 'logs', 'venv', '__pycache__'}
            
            for item in os.listdir(stosos_dir):
                if item in preserve_dirs:
                    continue
                    
                item_path = os.path.join(stosos_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                    
            # Restore from backup
            for item in os.listdir(backup_dir):
                source_path = os.path.join(backup_dir, item)
                dest_path = os.path.join(stosos_dir, item)
                
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path)
                else:
                    shutil.copy2(source_path, dest_path)
                    
            self.logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during rollback: {e}")
            return False
            
    def set_auto_update_enabled(self, enabled: bool):
        """Enable or disable automatic update checking"""
        self.auto_check_enabled = enabled
        self.logger.info(f"Auto-update checking {'enabled' if enabled else 'disabled'}")
        
    def get_update_history(self) -> list:
        """Get history of applied updates"""
        try:
            history_file = os.path.join(self.config.get_data_dir(), 'update_history.json')
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error reading update history: {e}")
        return []
        
    def _record_update(self, version: str, success: bool):
        """Record update in history"""
        try:
            history = self.get_update_history()
            
            record = {
                'version': version,
                'timestamp': datetime.now().isoformat(),
                'success': success,
                'previous_version': self.current_version
            }
            
            history.append(record)
            
            # Keep only last 10 records
            history = history[-10:]
            
            history_file = os.path.join(self.config.get_data_dir(), 'update_history.json')
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error recording update: {e}")
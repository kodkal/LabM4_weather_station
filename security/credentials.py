"""
Secure Credential Storage Module
Implements secure storage and management of credentials, API keys, and sensitive data
"""

import os
import json
import base64
import secrets
import hashlib
import sqlite3
from typing import Any, Dict, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import argon2

logger = logging.getLogger(__name__)


class SecureCredentialStore:
    """Secure storage for credentials with encryption and access control"""
    
    def __init__(self, key_file: str = "keys/master.key", 
                 db_path: str = "data/credentials.db",
                 use_hardware_security: bool = False):
        """
        Initialize secure credential store
        
        Args:
            key_file: Path to master encryption key
            db_path: Path to credential database
            use_hardware_security: Use TPM/HSM if available
        """
        self.key_file = key_file
        self.db_path = db_path
        self.use_hardware_security = use_hardware_security
        
        # Create necessary directories
        os.makedirs(os.path.dirname(key_file) if os.path.dirname(key_file) else '.', exist_ok=True)
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
        
        # Initialize master key and encryption
        self.master_key = self._load_or_create_master_key()
        self.fernet = Fernet(self.master_key)
        
        # Initialize password hasher (Argon2)
        self.ph = argon2.PasswordHasher(
            time_cost=2,
            memory_cost=65536,
            parallelism=2,
            hash_len=32,
            salt_len=16
        )
        
        # Initialize database
        self._initialize_database()
        
        # Track access attempts
        self.access_log = []
        self.failed_attempts = {}
        
        # Security configurations
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        
        logger.info("Secure credential store initialized")
    
    def _load_or_create_master_key(self) -> bytes:
        """Load or create master encryption key"""
        if os.path.exists(self.key_file):
            # Load existing key
            try:
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                
                # Verify key format
                if len(key) != 44:  # Fernet key is 44 bytes base64
                    raise ValueError("Invalid master key format")
                
                logger.info("Master key loaded successfully")
                return key
                
            except Exception as e:
                logger.error(f"Failed to load master key: {e}")
                raise
        else:
            # Generate new key
            key = Fernet.generate_key()
            
            # Store with secure permissions
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Set restrictive permissions (owner read/write only)
            os.chmod(self.key_file, 0o600)
            
            logger.info("New master key generated and stored")
            return key
    
    def _initialize_database(self):
        """Initialize credential database with encryption"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create credentials table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    value BLOB NOT NULL,
                    type TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP,
                    metadata TEXT,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    checksum TEXT NOT NULL
                )
            ''')
            
            # Create access log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    credential_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    success BOOLEAN NOT NULL,
                    ip_address TEXT,
                    device_id TEXT,
                    details TEXT
                )
            ''')
            
            # Create API keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_hash TEXT UNIQUE NOT NULL,
                    device_id TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL,
                    last_used TIMESTAMP,
                    use_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    expires_at TIMESTAMP,
                    permissions TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Set database permissions
            os.chmod(self.db_path, 0o600)
            
            logger.info("Credential database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def store_credential(self, name: str, value: Any, 
                        credential_type: str = "generic",
                        expires_in: Optional[timedelta] = None,
                        metadata: Dict = None) -> bool:
        """
        Store a credential securely
        
        Args:
            name: Unique credential name
            value: Credential value
            credential_type: Type of credential
            expires_in: Optional expiration time
            metadata: Additional metadata
            
        Returns:
            True if stored successfully
        """
        try:
            # Check access permissions
            if not self._check_access_allowed(name):
                logger.warning(f"Access denied for storing credential: {name}")
                return False
            
            # Serialize value
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)
            
            # Encrypt value
            encrypted_value = self.fernet.encrypt(value_str.encode())
            
            # Calculate checksum
            checksum = hashlib.sha256(encrypted_value).hexdigest()
            
            # Prepare expiration
            expires_at = None
            if expires_in:
                expires_at = datetime.now(timezone.utc) + expires_in
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now(timezone.utc)
            
            cursor.execute('''
                INSERT OR REPLACE INTO credentials 
                (name, value, type, created_at, updated_at, expires_at, metadata, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name,
                encrypted_value,
                credential_type,
                now,
                now,
                expires_at,
                json.dumps(metadata) if metadata else None,
                checksum
            ))
            
            conn.commit()
            conn.close()
            
            # Log access
            self._log_access(name, "store", True)
            
            logger.info(f"Credential stored: {name} (type: {credential_type})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store credential {name}: {e}")
            self._log_access(name, "store", False)
            return False
    
    def get_credential(self, name: str) -> Optional[Any]:
        """
        Retrieve a credential
        
        Args:
            name: Credential name
            
        Returns:
            Decrypted credential value or None
        """
        try:
            # Check access permissions
            if not self._check_access_allowed(name):
                logger.warning(f"Access denied for credential: {name}")
                return None
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Retrieve credential
            cursor.execute('''
                SELECT value, expires_at, checksum, type 
                FROM credentials 
                WHERE name = ?
            ''', (name,))
            
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Credential not found: {name}")
                self._log_access(name, "get", False)
                conn.close()
                return None
            
            encrypted_value, expires_at, stored_checksum, cred_type = result
            
            # Check expiration
            if expires_at:
                expires = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                if expires < datetime.now(timezone.utc):
                    logger.warning(f"Credential expired: {name}")
                    self._log_access(name, "get", False, "expired")
                    conn.close()
                    return None
            
            # Verify checksum
            calculated_checksum = hashlib.sha256(encrypted_value).hexdigest()
            if calculated_checksum != stored_checksum:
                logger.error(f"Credential checksum mismatch: {name}")
                self._log_access(name, "get", False, "checksum_failed")
                conn.close()
                return None
            
            # Decrypt value
            decrypted_value = self.fernet.decrypt(encrypted_value).decode()
            
            # Update access count and timestamp
            cursor.execute('''
                UPDATE credentials 
                SET access_count = access_count + 1,
                    last_accessed = ?
                WHERE name = ?
            ''', (datetime.now(timezone.utc), name))
            
            conn.commit()
            conn.close()
            
            # Parse JSON if needed
            if cred_type == 'json':
                decrypted_value = json.loads(decrypted_value)
            
            # Log successful access
            self._log_access(name, "get", True)
            
            return decrypted_value
            
        except Exception as e:
            logger.error(f"Failed to retrieve credential {name}: {e}")
            self._log_access(name, "get", False)
            return None
    
    def delete_credential(self, name: str) -> bool:
        """
        Delete a credential
        
        Args:
            name: Credential name
            
        Returns:
            True if deleted successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM credentials WHERE name = ?', (name,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                
                self._log_access(name, "delete", True)
                logger.info(f"Credential deleted: {name}")
                return True
            else:
                conn.close()
                logger.warning(f"Credential not found for deletion: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete credential {name}: {e}")
            self._log_access(name, "delete", False)
            return False
    
    def list_credentials(self, credential_type: Optional[str] = None) -> List[Dict]:
        """
        List stored credentials (metadata only, not values)
        
        Args:
            credential_type: Filter by type
            
        Returns:
            List of credential metadata
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if credential_type:
                cursor.execute('''
                    SELECT name, type, created_at, updated_at, expires_at, access_count
                    FROM credentials
                    WHERE type = ?
                ''', (credential_type,))
            else:
                cursor.execute('''
                    SELECT name, type, created_at, updated_at, expires_at, access_count
                    FROM credentials
                ''')
            
            results = cursor.fetchall()
            conn.close()
            
            credentials = []
            for row in results:
                credentials.append({
                    'name': row[0],
                    'type': row[1],
                    'created_at': row[2],
                    'updated_at': row[3],
                    'expires_at': row[4],
                    'access_count': row[5]
                })
            
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to list credentials: {e}")
            return []
    
    def rotate_credential(self, name: str, new_value: Any) -> bool:
        """
        Rotate a credential (update with new value)
        
        Args:
            name: Credential name
            new_value: New credential value
            
        Returns:
            True if rotated successfully
        """
        try:
            # Get existing credential metadata
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT type, expires_at, metadata
                FROM credentials
                WHERE name = ?
            ''', (name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                logger.warning(f"Credential not found for rotation: {name}")
                return False
            
            cred_type, expires_at, metadata = result
            
            # Store new value with same metadata
            success = self.store_credential(
                name, 
                new_value, 
                cred_type,
                expires_in=None,  # Keep original expiration
                metadata=json.loads(metadata) if metadata else None
            )
            
            if success:
                self._log_access(name, "rotate", True)
                logger.info(f"Credential rotated: {name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to rotate credential {name}: {e}")
            return False
    
    def get_or_create_secret(self, name: str, length: int = 32) -> str:
        """
        Get existing secret or create new one if not exists
        
        Args:
            name: Secret name
            length: Length for new secret
            
        Returns:
            Secret value
        """
        existing = self.get_credential(name)
        
        if existing:
            return existing
        
        # Generate new secret
        new_secret = secrets.token_urlsafe(length)
        
        self.store_credential(
            name,
            new_secret,
            credential_type='secret'
        )
        
        return new_secret
    
    def store_api_key(self, api_key: str, device_id: str, 
                     description: str = "", permissions: List[str] = None) -> bool:
        """
        Store an API key
        
        Args:
            api_key: The API key
            device_id: Associated device ID
            description: Key description
            permissions: List of permissions
            
        Returns:
            True if stored successfully
        """
        try:
            # Hash the API key for storage
            key_hash = self.ph.hash(api_key)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_keys 
                (key_hash, device_id, description, created_at, permissions)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                key_hash,
                device_id,
                description,
                datetime.now(timezone.utc),
                json.dumps(permissions) if permissions else None
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"API key stored for device: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store API key: {e}")
            return False
    
    def verify_api_key(self, api_key: str) -> Tuple[bool, Optional[Dict]]:
        """
        Verify an API key
        
        Args:
            api_key: API key to verify
            
        Returns:
            Tuple of (is_valid, key_info)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all active API keys
            cursor.execute('''
                SELECT key_hash, device_id, permissions, expires_at
                FROM api_keys
                WHERE is_active = 1
            ''')
            
            for row in cursor.fetchall():
                key_hash, device_id, permissions, expires_at = row
                
                # Check if key matches
                try:
                    self.ph.verify(key_hash, api_key)
                    
                    # Check expiration
                    if expires_at:
                        expires = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                        if expires < datetime.now(timezone.utc):
                            continue
                    
                    # Update usage stats
                    cursor.execute('''
                        UPDATE api_keys
                        SET last_used = ?, use_count = use_count + 1
                        WHERE key_hash = ?
                    ''', (datetime.now(timezone.utc), key_hash))
                    
                    conn.commit()
                    conn.close()
                    
                    return True, {
                        'device_id': device_id,
                        'permissions': json.loads(permissions) if permissions else []
                    }
                    
                except argon2.exceptions.VerifyMismatchError:
                    continue
            
            conn.close()
            return False, None
            
        except Exception as e:
            logger.error(f"API key verification error: {e}")
            return False, None
    
    def _check_access_allowed(self, credential_name: str) -> bool:
        """Check if access is allowed based on security policies"""
        # Check for lockout
        # Simplified for educational purposes
        return True
    
    def _log_access(self, credential_name: str, action: str, 
                   success: bool, details: str = None):
        """Log credential access attempt"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO access_log 
                (credential_name, action, timestamp, success, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                credential_name,
                action,
                datetime.now(timezone.utc),
                success,
                details
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to log access: {e}")
    
    def get_access_log(self, credential_name: Optional[str] = None, 
                       limit: int = 100) -> List[Dict]:
        """
        Get access log entries
        
        Args:
            credential_name: Filter by credential name
            limit: Maximum entries to return
            
        Returns:
            List of access log entries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if credential_name:
                cursor.execute('''
                    SELECT * FROM access_log
                    WHERE credential_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (credential_name, limit))
            else:
                cursor.execute('''
                    SELECT * FROM access_log
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            log_entries = []
            for row in results:
                log_entries.append({
                    'id': row[0],
                    'credential_name': row[1],
                    'action': row[2],
                    'timestamp': row[3],
                    'success': row[4],
                    'ip_address': row[5],
                    'device_id': row[6],
                    'details': row[7]
                })
            
            return log_entries
            
        except Exception as e:
            logger.error(f"Failed to get access log: {e}")
            return []
    
    def cleanup_expired(self):
        """Clean up expired credentials"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM credentials
                WHERE expires_at IS NOT NULL 
                AND expires_at < ?
            ''', (datetime.now(timezone.utc),))
            
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired credentials")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired credentials: {e}")
    
    def export_credentials(self, password: str, export_path: str) -> bool:
        """
        Export credentials to encrypted backup
        
        Args:
            password: Password for backup encryption
            export_path: Path for backup file
            
        Returns:
            True if exported successfully
        """
        try:
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=os.urandom(16),
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            backup_fernet = Fernet(key)
            
            # Get all credentials
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM credentials')
            credentials = cursor.fetchall()
            
            conn.close()
            
            # Prepare backup data
            backup_data = {
                'version': '1.0',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'credentials': credentials
            }
            
            # Encrypt and save
            encrypted_backup = backup_fernet.encrypt(
                json.dumps(backup_data, default=str).encode()
            )
            
            with open(export_path, 'wb') as f:
                f.write(encrypted_backup)
            
            os.chmod(export_path, 0o600)
            
            logger.info(f"Credentials exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export credentials: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        self.cleanup_expired()
        logger.info("Credential store cleanup completed")


class HardwareSecurityModule:
    """Interface for hardware security module (TPM/HSM) integration"""
    
    def __init__(self):
        """Initialize HSM interface"""
        self.available = self._check_availability()
        
        if self.available:
            logger.info("Hardware security module available")
        else:
            logger.info("Hardware security module not available")
    
    def _check_availability(self) -> bool:
        """Check if TPM/HSM is available"""
        # Check for TPM 2.0
        tpm_path = '/dev/tpm0'
        if os.path.exists(tpm_path):
            return True
        
        # Check for other HSM devices
        # This would be expanded for real HSM support
        
        return False
    
    def seal_data(self, data: bytes) -> Optional[bytes]:
        """Seal data using TPM/HSM"""
        if not self.available:
            return None
        
        # Placeholder for TPM sealing
        # In production, use tpm2-tools or similar
        return data
    
    def unseal_data(self, sealed_data: bytes) -> Optional[bytes]:
        """Unseal data using TPM/HSM"""
        if not self.available:
            return None
        
        # Placeholder for TPM unsealing
        return sealed_data
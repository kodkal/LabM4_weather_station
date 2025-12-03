"""
Secure Data Transmission Module
Implements encryption and secure communication for IoT data
"""

import os
import json
import base64
import secrets
import hashlib
import hmac
from typing import Dict, Any, Optional, Tuple, Union
from datetime import datetime, timezone
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
import ssl

logger = logging.getLogger(__name__)


class SecureDataTransmission:
    """Handles secure data transmission with multiple encryption options"""
    
    def __init__(self, cert_file: str = None, key_file: str = None,
                 ca_cert: str = None, encryption_method: str = 'AES256'):
        """
        Initialize secure transmission handler
        
        Args:
            cert_file: Path to TLS certificate file
            key_file: Path to private key file
            ca_cert: Path to CA certificate for verification
            encryption_method: Encryption method (AES256, RSA, Fernet)
        """
        self.cert_file = cert_file
        self.key_file = key_file
        self.ca_cert = ca_cert
        self.encryption_method = encryption_method
        
        # Initialize encryption keys
        self._initialize_encryption()
        
        # TLS context for secure connections
        self.ssl_context = self._create_ssl_context()
        
        # Session management
        self.active_sessions = {}
        
        logger.info(f"Secure transmission initialized with {encryption_method}")
    
    def _initialize_encryption(self):
        """Initialize encryption keys and parameters"""
        # Fernet key for symmetric encryption
        self.fernet_key = self._load_or_create_fernet_key()
        self.fernet = Fernet(self.fernet_key)
        
        # AES key for AES encryption
        self.aes_key = self._load_or_create_aes_key()
        
        # RSA keys for asymmetric encryption
        self.rsa_private_key = None
        self.rsa_public_key = None
        
        if self.key_file and os.path.exists(self.key_file):
            self._load_rsa_keys()
    
    def _load_or_create_fernet_key(self) -> bytes:
        """Load or create Fernet encryption key"""
        key_path = 'keys/fernet.key'
        os.makedirs('keys', exist_ok=True)
        
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
            os.chmod(key_path, 0o600)  # Secure file permissions
            logger.info("Generated new Fernet key")
            return key
    
    def _load_or_create_aes_key(self) -> bytes:
        """Load or create AES encryption key"""
        key_path = 'keys/aes.key'
        os.makedirs('keys', exist_ok=True)
        
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            key = secrets.token_bytes(32)  # 256-bit key
            with open(key_path, 'wb') as f:
                f.write(key)
            os.chmod(key_path, 0o600)
            logger.info("Generated new AES key")
            return key
    
    def _load_rsa_keys(self):
        """Load RSA keys from files"""
        try:
            with open(self.key_file, 'rb') as f:
                self.rsa_private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            self.rsa_public_key = self.rsa_private_key.public_key()
            logger.info("RSA keys loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load RSA keys: {e}")
    
    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context for TLS connections"""
        try:
            if not self.cert_file or not os.path.exists(self.cert_file):
                logger.warning("TLS certificate not found")
                return None
            
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            
            # Load certificate and key
            context.load_cert_chain(self.cert_file, self.key_file)
            
            # Set strong security options
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
            
            # Load CA certificate if provided
            if self.ca_cert and os.path.exists(self.ca_cert):
                context.load_verify_locations(self.ca_cert)
                context.verify_mode = ssl.CERT_REQUIRED
            
            logger.info("TLS context created successfully")
            return context
            
        except Exception as e:
            logger.error(f"Failed to create SSL context: {e}")
            return None
    
    def encrypt_data(self, data: Union[Dict, str, bytes]) -> str:
        """
        Encrypt data using configured method
        
        Args:
            data: Data to encrypt (dict, string, or bytes)
            
        Returns:
            Base64 encoded encrypted data
        """
        try:
            # Convert data to bytes
            if isinstance(data, dict):
                data_bytes = json.dumps(data).encode('utf-8')
            elif isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # Encrypt based on method
            if self.encryption_method == 'Fernet':
                encrypted = self._encrypt_fernet(data_bytes)
            elif self.encryption_method == 'AES256':
                encrypted = self._encrypt_aes(data_bytes)
            elif self.encryption_method == 'RSA' and self.rsa_public_key:
                encrypted = self._encrypt_rsa(data_bytes)
            else:
                # Fallback to Fernet
                encrypted = self._encrypt_fernet(data_bytes)
            
            # Return base64 encoded
            return base64.b64encode(encrypted).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> Dict:
        """
        Decrypt data
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted data as dictionary
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Decrypt based on method
            if self.encryption_method == 'Fernet':
                decrypted = self._decrypt_fernet(encrypted_bytes)
            elif self.encryption_method == 'AES256':
                decrypted = self._decrypt_aes(encrypted_bytes)
            elif self.encryption_method == 'RSA' and self.rsa_private_key:
                decrypted = self._decrypt_rsa(encrypted_bytes)
            else:
                decrypted = self._decrypt_fernet(encrypted_bytes)
            
            # Parse JSON
            return json.loads(decrypted.decode('utf-8'))
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def _encrypt_fernet(self, data: bytes) -> bytes:
        """Encrypt using Fernet (symmetric)"""
        return self.fernet.encrypt(data)
    
    def _decrypt_fernet(self, encrypted: bytes) -> bytes:
        """Decrypt using Fernet"""
        return self.fernet.decrypt(encrypted)
    
    def _encrypt_aes(self, data: bytes) -> bytes:
        """Encrypt using AES-256-GCM"""
        # Generate random IV
        iv = os.urandom(12)  # 96-bit IV for GCM
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.aes_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Return IV + ciphertext + tag
        return iv + ciphertext + encryptor.tag
    
    def _decrypt_aes(self, encrypted: bytes) -> bytes:
        """Decrypt using AES-256-GCM"""
        # Extract components
        iv = encrypted[:12]
        tag = encrypted[-16:]
        ciphertext = encrypted[12:-16]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.aes_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        
        # Decrypt data
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def _encrypt_rsa(self, data: bytes) -> bytes:
        """Encrypt using RSA (asymmetric)"""
        # RSA can only encrypt limited data, so we use hybrid encryption
        # Generate symmetric key for this session
        session_key = secrets.token_bytes(32)
        
        # Encrypt session key with RSA
        encrypted_key = self.rsa_public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Encrypt data with session key (using AES)
        iv = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(session_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Return encrypted_key + iv + ciphertext + tag
        return encrypted_key + iv + ciphertext + encryptor.tag
    
    def _decrypt_rsa(self, encrypted: bytes) -> bytes:
        """Decrypt using RSA (hybrid)"""
        # Extract components
        key_size = self.rsa_private_key.key_size // 8
        encrypted_key = encrypted[:key_size]
        iv = encrypted[key_size:key_size + 12]
        tag = encrypted[-16:]
        ciphertext = encrypted[key_size + 12:-16]
        
        # Decrypt session key
        session_key = self.rsa_private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Decrypt data
        cipher = Cipher(
            algorithms.AES(session_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def sign_data(self, data: Union[str, bytes]) -> str:
        """
        Create digital signature for data integrity
        
        Args:
            data: Data to sign
            
        Returns:
            Base64 encoded signature
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Create HMAC signature
            signature = hmac.new(
                self.aes_key,  # Use AES key for HMAC
                data,
                hashlib.sha256
            ).digest()
            
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Signing failed: {e}")
            raise
    
    def verify_signature(self, data: Union[str, bytes], signature: str) -> bool:
        """
        Verify data signature
        
        Args:
            data: Data to verify
            signature: Base64 encoded signature
            
        Returns:
            True if signature is valid
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Decode signature
            provided_signature = base64.b64decode(signature)
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.aes_key,
                data,
                hashlib.sha256
            ).digest()
            
            # Constant-time comparison
            return hmac.compare_digest(provided_signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def create_secure_session(self, device_id: str) -> Dict[str, str]:
        """
        Create a secure session for a device
        
        Args:
            device_id: Device identifier
            
        Returns:
            Session information including session ID and keys
        """
        try:
            # Generate session ID
            session_id = secrets.token_urlsafe(32)
            
            # Generate session keys
            session_key = Fernet.generate_key()
            
            # Store session
            self.active_sessions[session_id] = {
                'device_id': device_id,
                'session_key': session_key,
                'created_at': datetime.now(timezone.utc),
                'last_used': datetime.now(timezone.utc)
            }
            
            logger.info(f"Secure session created for device: {device_id}")
            
            return {
                'session_id': session_id,
                'session_key': base64.b64encode(session_key).decode('utf-8')
            }
            
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            raise
    
    def validate_session(self, session_id: str) -> bool:
        """Validate an active session"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        # Check session age (24 hour timeout)
        age = datetime.now(timezone.utc) - session['created_at']
        if age.total_seconds() > 86400:
            del self.active_sessions[session_id]
            logger.info(f"Session expired: {session_id}")
            return False
        
        # Update last used
        session['last_used'] = datetime.now(timezone.utc)
        return True
    
    def generate_certificate_request(self, device_id: str, 
                                    organization: str = "IoT Weather Station") -> bytes:
        """
        Generate a certificate signing request (CSR) for a device
        
        Args:
            device_id: Device identifier
            organization: Organization name
            
        Returns:
            CSR in PEM format
        """
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Create CSR
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Utah"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Provo"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COMMON_NAME, f"device-{device_id}"),
            ])
            
            csr = x509.CertificateSigningRequestBuilder().subject_name(
                subject
            ).sign(private_key, hashes.SHA256(), default_backend())
            
            # Save private key
            key_path = f'keys/device_{device_id}.key'
            with open(key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            os.chmod(key_path, 0o600)
            
            logger.info(f"CSR generated for device: {device_id}")
            
            return csr.public_bytes(serialization.Encoding.PEM)
            
        except Exception as e:
            logger.error(f"CSR generation failed: {e}")
            raise
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up expired sessions"""
        now = datetime.now(timezone.utc)
        expired = []
        
        for session_id, session in self.active_sessions.items():
            age = now - session['created_at']
            if age.total_seconds() > (max_age_hours * 3600):
                expired.append(session_id)
        
        for session_id in expired:
            del self.active_sessions[session_id]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")


class EncryptionValidator:
    """Utilities for validating encryption and security"""
    
    @staticmethod
    def validate_tls_certificate(cert_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a TLS certificate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            # Check expiration
            now = datetime.now(timezone.utc)
            if cert.not_valid_after_utc < now:
                return False, "Certificate has expired"
            
            if cert.not_valid_before_utc > now:
                return False, "Certificate is not yet valid"
            
            # Check key usage
            try:
                key_usage = cert.extensions.get_extension_for_oid(
                    x509.oid.ExtensionOID.KEY_USAGE
                ).value
                
                if not key_usage.digital_signature or not key_usage.key_agreement:
                    return False, "Certificate missing required key usage flags"
            except:
                pass  # Key usage extension might not be present
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def check_encryption_strength(method: str, key_size: int = None) -> bool:
        """Check if encryption method meets security requirements"""
        min_key_sizes = {
            'AES': 256,
            'RSA': 2048,
            'ECDSA': 256
        }
        
        for algo, min_size in min_key_sizes.items():
            if algo in method.upper():
                if key_size and key_size < min_size:
                    return False
                return True
        
        return True  # Unknown methods assumed OK for educational purposes
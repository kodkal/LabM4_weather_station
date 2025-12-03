"""
JWT Authentication Module
Implements secure token-based authentication for the weather station API
"""

import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any, Tuple
import logging
import hashlib
import hmac

logger = logging.getLogger(__name__)


class JWTManager:
    """Manages JWT token generation and validation"""
    
    def __init__(self, secret_key: str = None, algorithm: str = 'HS256', 
                 token_expiry: timedelta = timedelta(hours=24)):
        """
        Initialize JWT Manager
        
        Args:
            secret_key: Secret key for signing tokens (auto-generated if not provided)
            algorithm: JWT signing algorithm (HS256, HS384, HS512, RS256, etc.)
            token_expiry: Token expiration time
        """
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = algorithm
        self.token_expiry = token_expiry
        
        # Token blacklist for revocation (in production, use Redis)
        self.blacklisted_tokens = set()
        
        # Track token usage for rate limiting
        self.token_usage = {}
        
        # Security configurations
        self.max_tokens_per_device = 5
        self.require_device_id = True
        
        logger.info(f"JWT Manager initialized with algorithm: {algorithm}")
    
    def generate_token(self, payload: Dict[str, Any], 
                      custom_expiry: Optional[timedelta] = None) -> str:
        """
        Generate a new JWT token
        
        Args:
            payload: Data to encode in the token
            custom_expiry: Override default expiry time
            
        Returns:
            Encoded JWT token
        """
        try:
            # Validate payload
            if self.require_device_id and 'device_id' not in payload:
                raise ValueError("device_id is required in token payload")
            
            # Add security claims
            now = datetime.now(timezone.utc)
            expiry = custom_expiry or self.token_expiry
            
            claims = {
                **payload,
                'iat': now,  # Issued at
                'exp': now + expiry,  # Expiration
                'nbf': now,  # Not before
                'jti': secrets.token_urlsafe(16),  # JWT ID for tracking
                'iss': 'secure-weather-station',  # Issuer
                'token_version': '1.0'
            }
            
            # Check token limit per device
            device_id = payload.get('device_id')
            if device_id:
                self._check_token_limit(device_id)
            
            # Generate token
            token = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
            
            # Track token
            self._track_token(claims['jti'], device_id)
            
            logger.info(f"Token generated for device: {device_id}",
                       extra={"event": "token_generated", "jti": claims['jti']})
            
            return token
            
        except Exception as e:
            logger.error(f"Token generation failed: {e}",
                        extra={"event": "token_generation_error"})
            raise
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Tuple of (is_valid, decoded_payload)
        """
        try:
            # Check if token is blacklisted
            if self._is_blacklisted(token):
                logger.warning("Attempted use of blacklisted token",
                             extra={"event": "blacklisted_token_attempt"})
                return False, None
            
            # Decode and verify
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_nbf': True,
                    'verify_iat': True
                }
            )
            
            # Additional security checks
            if not self._validate_payload_security(payload):
                return False, None
            
            # Check rate limiting
            jti = payload.get('jti')
            if jti and not self._check_rate_limit(jti):
                logger.warning("Token rate limit exceeded",
                             extra={"event": "rate_limit_exceeded", "jti": jti})
                return False, None
            
            logger.debug("Token verified successfully",
                        extra={"event": "token_verified", 
                             "device_id": payload.get('device_id')})
            
            return True, payload
            
        except jwt.ExpiredSignatureError:
            logger.info("Token expired", extra={"event": "token_expired"})
            return False, {"error": "Token has expired"}
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}",
                          extra={"event": "invalid_token"})
            return False, {"error": "Invalid token"}
            
        except Exception as e:
            logger.error(f"Token verification error: {e}",
                        extra={"event": "token_verification_error"})
            return False, {"error": "Token verification failed"}
    
    def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh an existing valid token
        
        Args:
            token: Current valid token
            
        Returns:
            New token or None if refresh failed
        """
        try:
            # Verify current token
            is_valid, payload = self.verify_token(token)
            
            if not is_valid:
                logger.warning("Refresh attempted with invalid token")
                return None
            
            # Check if token is eligible for refresh
            exp = datetime.fromtimestamp(payload['exp'], timezone.utc)
            now = datetime.now(timezone.utc)
            
            # Don't refresh if more than half the expiry time remains
            time_remaining = exp - now
            if time_remaining > (self.token_expiry / 2):
                logger.info("Token refresh denied - too much time remaining")
                return None
            
            # Blacklist old token
            self.revoke_token(token)
            
            # Generate new token with same claims
            new_payload = {
                k: v for k, v in payload.items() 
                if k not in ['iat', 'exp', 'nbf', 'jti']
            }
            
            new_token = self.generate_token(new_payload)
            
            logger.info("Token refreshed successfully",
                       extra={"event": "token_refreshed",
                            "device_id": payload.get('device_id')})
            
            return new_token
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}",
                        extra={"event": "token_refresh_error"})
            return None
    
    def revoke_token(self, token: str):
        """
        Revoke a token by adding it to the blacklist
        
        Args:
            token: Token to revoke
        """
        try:
            # Decode without verification to get JTI
            unverified = jwt.decode(token, options={"verify_signature": False})
            jti = unverified.get('jti')
            
            if jti:
                self.blacklisted_tokens.add(jti)
                logger.info("Token revoked",
                           extra={"event": "token_revoked", "jti": jti})
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
    
    def _is_blacklisted(self, token: str) -> bool:
        """Check if a token is blacklisted"""
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            jti = unverified.get('jti')
            return jti in self.blacklisted_tokens if jti else False
        except:
            return False
    
    def _validate_payload_security(self, payload: Dict[str, Any]) -> bool:
        """Perform additional security validation on token payload"""
        # Check required fields
        required_fields = ['jti', 'iss', 'iat', 'exp']
        if not all(field in payload for field in required_fields):
            logger.warning("Token missing required fields",
                          extra={"event": "invalid_token_structure"})
            return False
        
        # Verify issuer
        if payload.get('iss') != 'secure-weather-station':
            logger.warning("Invalid token issuer",
                          extra={"event": "invalid_issuer", 
                               "issuer": payload.get('iss')})
            return False
        
        # Check token age (prevent replay of very old tokens)
        iat = datetime.fromtimestamp(payload['iat'], timezone.utc)
        now = datetime.now(timezone.utc)
        
        if now - iat > timedelta(days=7):
            logger.warning("Token too old",
                          extra={"event": "old_token_rejected"})
            return False
        
        return True
    
    def _check_token_limit(self, device_id: str):
        """Check if device has exceeded token limit"""
        if device_id not in self.token_usage:
            self.token_usage[device_id] = []
        
        # Clean up expired tokens
        now = datetime.now(timezone.utc)
        self.token_usage[device_id] = [
            (jti, exp) for jti, exp in self.token_usage[device_id]
            if exp > now
        ]
        
        # Check limit
        if len(self.token_usage[device_id]) >= self.max_tokens_per_device:
            raise ValueError(f"Token limit exceeded for device {device_id}")
    
    def _track_token(self, jti: str, device_id: Optional[str]):
        """Track token issuance"""
        if device_id:
            if device_id not in self.token_usage:
                self.token_usage[device_id] = []
            
            exp_time = datetime.now(timezone.utc) + self.token_expiry
            self.token_usage[device_id].append((jti, exp_time))
    
    def _check_rate_limit(self, jti: str) -> bool:
        """Check if token is being used within rate limits"""
        # Simplified rate limiting - in production use Redis
        # This is a placeholder for actual rate limiting logic
        return True
    
    def generate_api_key(self, device_id: str, description: str = "") -> str:
        """
        Generate a long-lived API key for a device
        
        Args:
            device_id: Device identifier
            description: Optional description of the key
            
        Returns:
            API key string
        """
        # Create API key with embedded metadata
        timestamp = int(datetime.now(timezone.utc).timestamp())
        
        # Create key components
        prefix = "swsk"  # Secure Weather Station Key
        random_part = secrets.token_urlsafe(32)
        
        # Create signature
        message = f"{prefix}_{device_id}_{timestamp}_{random_part}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()[:8]
        
        api_key = f"{prefix}_{random_part}_{signature}"
        
        logger.info(f"API key generated for device: {device_id}",
                   extra={"event": "api_key_generated", 
                        "device_id": device_id,
                        "description": description})
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> bool:
        """
        Verify an API key
        
        Args:
            api_key: API key to verify
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parts = api_key.split('_')
            if len(parts) != 3 or parts[0] != "swsk":
                return False
            
            # In production, verify against stored keys in database
            # This is simplified for educational purposes
            return True
            
        except Exception:
            return False
    
    def cleanup_expired(self):
        """Clean up expired tokens and data"""
        now = datetime.now(timezone.utc)
        
        # Clean token usage tracking
        for device_id in list(self.token_usage.keys()):
            self.token_usage[device_id] = [
                (jti, exp) for jti, exp in self.token_usage[device_id]
                if exp > now
            ]
            
            if not self.token_usage[device_id]:
                del self.token_usage[device_id]
        
        # In production, also clean blacklist based on token expiry
        logger.debug("Cleaned up expired token data")


class TokenValidator:
    """Additional token validation utilities"""
    
    @staticmethod
    def validate_token_format(token: str) -> bool:
        """Validate JWT token format"""
        parts = token.split('.')
        return len(parts) == 3
    
    @staticmethod
    def extract_claims_unverified(token: str) -> Optional[Dict]:
        """Extract claims without verification (for logging/debugging only)"""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except:
            return None
    
    @staticmethod
    def is_token_expired(token: str) -> bool:
        """Check if token is expired without full verification"""
        try:
            claims = jwt.decode(token, options={"verify_signature": False})
            exp = datetime.fromtimestamp(claims['exp'], timezone.utc)
            return exp < datetime.now(timezone.utc)
        except:
            return True
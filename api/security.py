# Basic authentication for the seller portal
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import hashlib
import os
from typing import Optional

security = HTTPBearer()

# Simple API key storage (in production, use a database)
# Format: {"store_id_suffix": "hashed_api_key"}
VALID_API_KEYS = {
    "test_store": hashlib.sha256("default_test_key_change_in_production".encode()).hexdigest(),
}

def get_api_key_hash(api_key: str) -> str:
    """Hash an API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_portal_auth(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """
    Verify authentication credentials for portal access.
    In development, uses simple bearer token.
    In production, should use more robust methods.
    Returns the authenticated store identifier if valid.
    """
    token = credentials.credentials
    
    # Check against valid keys
    for store_id, hashed_key in VALID_API_KEYS.items():
        if hashlib.sha256(token.encode()).hexdigest() == hashed_key:
            return store_id
    
    # If no match, raise unauthorized error
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "Bearer"},
    )

def verify_store_ownership(store_id: int, authenticated_store: Optional[str] = None) -> bool:
    """
    Verify that the authenticated user owns the store.
    In production, fetch from database.
    """
    # Development: allow all authenticated requests
    if authenticated_store:
        return True
    return False

class SessionManager:
    """Manage user sessions for the portal"""
    
    def __init__(self, session_timeout: int = 3600):
        self.sessions = {}  # {session_id: {store_id, created_at, last_accessed}}
        self.session_timeout = session_timeout
    
    def create_session(self, store_id: int) -> str:
        """Create a new session for the store"""
        import uuid
        import time
        
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "store_id": store_id,
            "created_at": time.time(),
            "last_accessed": time.time(),
        }
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[int]:
        """Validate session and return store_id if valid"""
        import time
        
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        current_time = time.time()
        
        # Check if session expired
        if current_time - session["last_accessed"] > self.session_timeout:
            del self.sessions[session_id]
            return None
        
        # Update last accessed time
        session["last_accessed"] = current_time
        return session["store_id"]
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate (logout) a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

# Global session manager
session_manager = SessionManager()

import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
from typing import Optional
import json

class FirebaseService:
    _instance: Optional['FirebaseService'] = None
    _app: Optional[firebase_admin.App] = None
    _db: Optional[firestore.Client] = None
    
    def __new__(cls) -> 'FirebaseService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self):
        """Initialize Firebase Admin SDK"""
        if self._app is not None:
            return self._app
            
        try:
            # For development, we'll use the project ID directly
            # In production, you should use a service account key file
            project_id = os.getenv('FIREBASE_PROJECT_ID', 'realestate-456c4')
            
            # Initialize with project ID only for development
            # This requires the application to run with appropriate credentials
            cred = credentials.ApplicationDefault()
            self._app = firebase_admin.initialize_app(cred, {
                'projectId': project_id
            })
            
            self._db = firestore.client()
            return self._app
            
        except Exception as e:
            print(f"Failed to initialize Firebase: {e}")
            # For development without service account, create a minimal setup
            try:
                self._app = firebase_admin.initialize_app(options={
                    'projectId': project_id
                })
                return self._app
            except Exception as fallback_error:
                print(f"Fallback initialization failed: {fallback_error}")
                return None
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify Firebase ID token"""
        try:
            if self._app is None:
                self.initialize()
            
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None
    
    def get_firestore_client(self) -> Optional[firestore.Client]:
        """Get Firestore client"""
        if self._db is None and self._app is not None:
            self._db = firestore.client()
        return self._db

# Global Firebase service instance
firebase_service = FirebaseService()
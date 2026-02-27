"""
Firebase-based storage manager for metrics, actions, and system state.
Handles all database operations with comprehensive error handling.
"""
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging
from pydantic import BaseModel, Field

from .config import firebase_config, logger


class PerformanceMetric(BaseModel):
    """Data model for performance metrics"""
    metric_id: str
    metric_type: str
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    metadata: Dict[str, Any] = {}
    tags: List[str] = []


class CorrectiveAction(BaseModel):
    """Data model for corrective actions"""
    action_id: str
    action_type: str
    trigger_metric_id: str
    parameters: Dict[str, Any]
    status: str = "pending"  # pending, executing, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class StorageManager:
    """Manages all Firebase Firestore operations"""
    
    def __init__(self):
        """Initialize Firebase connection"""
        self.logger = logging.getLogger(__name__)
        self._initialize_firebase()
        self.db = firestore.client()
        
    def _initialize_firebase(self):
        """Initialize Firebase app with error handling"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate({
                    "project_id": firebase_config.project_id,
                    "private_key": firebase_config.private_key,
                    "client_email": firebase_config.client_email
                })
                firebase_admin.initialize_app(cred, {
                    'databaseURL': firebase_config.database_url
                })
                self.logger.info("Firebase initialized successfully")
        except ValueError as e:
            self.logger.warning(f"Firebase already initialized: {e}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    def store_metric(self, metric: PerformanceMetric) -> str:
        """
        Store a performance metric in Firestore
        Returns: Document ID of stored metric
        """
        try:
            # Ensure timestamp is serializable
            metric_dict = metric.dict()
            metric_dict['timestamp'] = metric.timestamp.isoformat()
            
            doc_ref =
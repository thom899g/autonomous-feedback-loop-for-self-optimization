"""
Configuration management for the Autonomous Feedback Loop system.
Centralizes all configs to ensure consistency and type safety.
"""
import os
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics the system monitors"""
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    SUCCESS_RATE = "success_rate"


@dataclass
class FirebaseConfig:
    """Firebase configuration with validation"""
    project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    private_key: str = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')
    client_email: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    database_url: str = os.getenv("FIREBASE_DATABASE_URL", "")
    
    def __post_init__(self):
        """Validate Firebase configuration"""
        missing = []
        for field, value in self.__dict__.items():
            if not value:
                missing.append(field)
        
        if missing:
            error_msg = f"Missing Firebase configs: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Firebase configuration validated successfully")


@dataclass
class LoopConfig:
    """Feedback loop operational configuration"""
    collection_interval_seconds: int = 30
    analysis_window_minutes: int = 60
    anomaly_threshold_stddev: float = 2.5
    corrective_action_cooldown_seconds: int = 300
    max_concurrent_actions: int = 3
    retention_days: int = 30
    
    # Performance thresholds (adjust based on system requirements)
    performance_thresholds: Dict[MetricType, Dict[str, float]] = None
    
    def __post_init__(self):
        """Initialize default thresholds if not provided"""
        if self.performance_thresholds is None:
            self.performance_thresholds = {
                MetricType.RESPONSE_TIME: {"warning": 1.0, "critical": 3.0},
                MetricType.ERROR_RATE: {"warning": 0.01, "critical": 0.05},
                MetricType.MEMORY_USAGE: {"warning": 70.0, "critical": 85.0},
                MetricType.CPU_USAGE: {"warning": 75.0, "critical": 90.0},
                MetricType.SUCCESS_RATE: {"warning": 95.0, "critical": 90.0}
            }
        logger.info(f"Loop config initialized with {len(self.performance_thresholds)} metric thresholds")


# Global configuration instances
firebase_config = FirebaseConfig()
loop_config = LoopConfig()
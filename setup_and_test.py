"""
Setup and test script for Healthcare PII/PHI Detection System.
Initializes the environment and runs basic tests to verify functionality.
"""

import os
import sys
import logging
import yaml
import uvicorn
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import asyncio
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        "data/synthetic",
        "data/processed",
        "keys",
        "logs",
        "configs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def initialize_database():
    """Initialize the database with tables."""
    from backend.models.database import Base
    from backend.api.dependencies import engine
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

def generate_test_data():
    """Generate synthetic test data."""
    from backend.utils.data_generator import MedicalDataGenerator
    
    try:
        generator = MedicalDataGenerator()
        dataset = generator.generate_dataset(num_patients=5)
        generator.save_dataset(dataset)
        logger.info("Generated synthetic test data")
        return dataset
    except Exception as e:
        logger.error(f"Test data generation failed: {e}")
        sys.exit(1)

async def test_phi_detection():
    """Test PHI detection functionality."""
    from backend.models.phi_detector import PHIDetector
    
    try:
        detector = PHIDetector()
        test_text = """
        Patient John Doe (DOB: 01/15/1980) was admitted on 05/20/2023.
        Contact: (555) 123-4567, email: john.doe@email.com
        SSN: 123-45-6789
        Insurance ID: INS-12345678
        """
        
        result = detector.analyze_document(test_text)
        logger.info("PHI Detection Test Results:")
        logger.info(f"Found {result['total_entities']} PHI entities")
        logger.info(f"Entity types: {result['entity_types']}")
        
        return result
    except Exception as e:
        logger.error(f"PHI detection test failed: {e}")
        sys.exit(1)

async def test_encryption():
    """Test encryption functionality."""
    from backend.utils.encryption import EncryptionManager
    
    try:
        encryption_manager = EncryptionManager()
        test_data = {
            "patient_name": "John Doe",
            "ssn": "123-45-6789",
            "medical_record": "Test medical record"
        }
        
        # Test encryption
        encrypted = encryption_manager.encrypt_data(test_data)
        decrypted = encryption_manager.decrypt_data(encrypted)
        
        assert decrypted == test_data
        logger.info("Encryption test passed")
        
        return True
    except Exception as e:
        logger.error(f"Encryption test failed: {e}")
        sys.exit(1)

async def test_api_endpoints():
    """Test API endpoints."""
    import httpx
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/",
        "/health",
        "/auth/token",  # Will fail without credentials, but should return 401
        "/phi/analyze"  # Will fail without authentication, but should return 401
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                response = await client.get(f"{base_url}{endpoint}")
                logger.info(f"Tested endpoint {endpoint}: Status {response.status_code}")
            except Exception as e:
                logger.error(f"API endpoint test failed for {endpoint}: {e}")

def main():
    """Main setup and test function."""
    try:
        # Create directories
        create_directories()
        
        # Initialize database
        initialize_database()
        
        # Generate test data
        test_data = generate_test_data()
        
        # Run async tests
        asyncio.run(test_phi_detection())
        asyncio.run(test_encryption())
        
        # Start API server for endpoint testing
        logger.info("Starting API server for endpoint testing...")
        
        # Run API tests
        asyncio.run(test_api_endpoints())
        
        logger.info("Setup and testing completed successfully")
        
        # Print setup instructions
        print("\nSetup Complete!")
        print("\nTo start the API server, run:")
        print("python -m uvicorn backend.api.main:app --reload")
        print("\nAPI documentation will be available at:")
        print("http://localhost:8000/docs")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

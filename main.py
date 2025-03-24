#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for TailorTrip - AI Travel Planning System
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('./config/.env')

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(levelname)s - %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(
            os.path.join(os.getenv('LOG_DIR', 'data/logs'), 'tailortrip.log'),
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to initialize and run TailorTrip"""
    try:
        from interface.app import start_app
        start_app()
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

if __name__ == "__main__":
    main()

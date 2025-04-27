#!/usr/bin/env python3
"""
Script for running all RAG module unit tests
"""
import unittest
import sys
import os

# Add parent directory to path for correct imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load all tests
loader = unittest.TestLoader()
start_dir = os.path.dirname(os.path.abspath(__file__))
suite = loader.discover(start_dir, pattern="test_*.py")

# Run tests
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Exit with error code if there were failed tests
sys.exit(not result.wasSuccessful())

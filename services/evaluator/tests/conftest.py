# Test configuration
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Test settings
TEST_DATABASE_URL = "sqlite:///test.db"
TEST_STORAGE_PATH = "./test_storage"
TEST_API_KEYS = {
    "OPENAI_API_KEY": "test-openai-key",
    "GOOGLE_API_KEY": "test-google-key", 
    "OPENROUTER_API_KEY": "test-openrouter-key"
}

# Mock environment variables for testing
def setup_test_env():
    """Setup test environment variables"""
    for key, value in TEST_API_KEYS.items():
        os.environ.setdefault(key, value)
    
    os.environ.setdefault("STORAGE_PATH", TEST_STORAGE_PATH)
    os.environ.setdefault("DEBUG", "True")
    os.environ.setdefault("DEVELOPMENT_MODE", "True")

# Call setup when imported
setup_test_env()
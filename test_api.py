import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_upload_cv():
    """Test CV upload and parsing"""
    # Endpoint for uploading CV
    url = f"{BASE_URL}/document/upload"
    
    # Path to your test CV (PDF file)
    cv_path = "test_cv.pdf"  # Make sure this file exists
    
    # Prepare the files
    files = {
        'files': ('test_cv.pdf', open(cv_path, 'rb'), 'application/pdf')
    }
    
    # Optional folder_id
    data = {
        'folder_id': None
    }
    
    # Make the request
    response = requests.post(url, files=files, data=data)
    print("\nUpload Response:", response.json())
    
    # Get the document ID from the response (you'll need to parse it from the response)
    return response.json()

def test_search_cv(query="python developer"):
    """Test CV search functionality"""
    # Endpoint for searching
    url = f"{BASE_URL}/document/search"
    
    # Search payload
    payload = {
        "query": query,
        "limit": 5
    }
    
    # Make the request
    response = requests.post(url, json=payload)
    print("\nSearch Response:", json.dumps(response.json(), indent=2))
    return response.json()

def test_get_cv(document_id):
    """Test getting a specific CV"""
    # Endpoint for getting CV
    url = f"{BASE_URL}/document/{document_id}"
    
    # Make the request
    response = requests.get(url)
    print("\nGet CV Response:", json.dumps(response.json(), indent=2))
    return response.json()

if __name__ == "__main__":
    # First, make sure the server is running
    try:
        requests.get(f"{BASE_URL}/")
        print("Server is running!")
    except requests.exceptions.ConnectionError:
        print("Error: Please start the server first using 'uvicorn main:app --reload'")
        exit(1)

    # Create test CV if it doesn't exist
    if not Path("test_cv.pdf").exists():
        print("Please create a test_cv.pdf file before running the tests")
        exit(1)

    # Run tests
    print("\n=== Testing CV Parser API ===")
    
    # 1. Upload CV
    print("\n1. Testing CV Upload...")
    upload_result = test_upload_cv()
    
    # 2. Search CVs
    print("\n2. Testing CV Search...")
    search_result = test_search_cv("python developer with machine learning experience")
    
    # 3. Get specific CV (you'll need to get the document_id from previous responses)
    if search_result:
        print("\n3. Testing Get CV...")
        document_id = list(search_result.keys())[0]  # Get first document ID
        cv_result = test_get_cv(document_id) 
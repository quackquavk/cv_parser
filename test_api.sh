#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base URL for the API
BASE_URL="http://localhost:8000"

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
        echo -e "${RED}Error: $3${NC}"
    fi
}

echo "Starting API tests..."
echo "===================="

# Test 1: Check if API is running
echo "Testing root endpoint..."
response=$(curl -s -w "%{http_code}" $BASE_URL/)
http_code=${response: -3}
body=${response:0:${#response}-3}

if [ $http_code -eq 200 ]; then
    print_result 0 "Root endpoint test passed" ""
else
    print_result 1 "Root endpoint test failed" "HTTP Status: $http_code"
fi

# Test 2: Check documents endpoint
echo -e "\nTesting documents endpoint..."
response=$(curl -s -w "%{http_code}" $BASE_URL/document/)
http_code=${response: -3}
body=${response:0:${#response}-3}

if [ $http_code -eq 200 ]; then
    print_result 0 "Documents endpoint test passed" ""
else
    print_result 1 "Documents endpoint test failed" "HTTP Status: $http_code"
fi

# Test 3: Try to access static files directory
echo -e "\nTesting static files access..."
response=$(curl -s -w "%{http_code}" $BASE_URL/documents/)
http_code=${response: -3}

if [ $http_code -eq 200 ] || [ $http_code -eq 404 ]; then
    print_result 0 "Static files endpoint accessible" ""
else
    print_result 1 "Static files endpoint test failed" "HTTP Status: $http_code"
fi

echo -e "\nTests completed!" 
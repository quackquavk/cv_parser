#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base URL for the API
BASE_URL="http://localhost:8000"

echo "Starting API endpoint tests..."

# Test 1: Check if API is running
echo -e "\n${GREEN}Testing API health check endpoint${NC}"
HEALTH_CHECK=$(curl -s -X GET "${BASE_URL}/")
echo $HEALTH_CHECK

# Test 2: Upload CV document
echo -e "\n${GREEN}Testing document upload endpoint${NC}"
UPLOAD_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/document/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@cv.pdf")
echo "Upload Response:"
echo $UPLOAD_RESPONSE

# Extract document ID from upload response (updated extraction)
DOCUMENT_ID=$(echo $UPLOAD_RESPONSE | grep -o '"document_id":"[^"]*' | head -1 | cut -d'"' -f4)
if [ -z "$DOCUMENT_ID" ]; then
    echo -e "${RED}Failed to get document ID from upload response${NC}"
    exit 1
fi
echo -e "${GREEN}Uploaded document ID: $DOCUMENT_ID${NC}"

# Wait for processing
echo "Waiting for document processing..."
sleep 5

# Test 3: Search documents
echo -e "\n${GREEN}Testing document search endpoint${NC}"
SEARCH_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/document/search" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"python developer experience\"}")
echo "Search Response:"
echo $SEARCH_RESPONSE

# Test 4: Get specific document
echo -e "\n${GREEN}Testing get document endpoint${NC}"
GET_RESPONSE=$(curl -s -X GET \
  "${BASE_URL}/document/${DOCUMENT_ID}" \
  -H "accept: application/json")
echo "Get Document Response:"
echo $GET_RESPONSE

# Test 5: Bulk search documents
echo -e "\n${GREEN}Testing bulk search endpoint${NC}"
BULK_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/document/search/bulk?query=machine%20learning" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{\"document_ids\": [\"${DOCUMENT_ID}\"]}")
echo "Bulk Search Response:"
echo $BULK_RESPONSE

# Optional: Test delete document
# echo -e "\n${GREEN}Testing delete document endpoint${NC}"
# DELETE_RESPONSE=$(curl -s -X DELETE \
#   "${BASE_URL}/document/${DOCUMENT_ID}" \
#   -H "accept: application/json")
# echo "Delete Response:"
# echo $DELETE_RESPONSE

echo -e "\n${GREEN}All tests completed!${NC}" 
# CV Parser API

A powerful CV/Resume parsing and semantic search API built with FastAPI, MongoDB Atlas Vector Search, and Google's Generative AI.

## Features

- 📄 **CV Parsing**: Automatically extracts structured information from PDF resumes including:
  - Personal Information (name, contact details, location)
  - Work Experience
  - Education
  - Skills
  - Projects
  - Certifications
  - Ratings and Scores

- 🔍 **Semantic Search**: Advanced search capabilities using vector embeddings
  - Natural language queries
  - Similarity-based matching
  - Contextual understanding
  - Bulk search support
  - Configurable search parameters

- 💾 **Vector Store Integration**
  - MongoDB Atlas Vector Search integration
  - Efficient document embedding storage
  - Fast similarity search
  - Metadata management

- 🔄 **Real-time Processing**
  - Asynchronous operations
  - Efficient file handling
  - Robust error handling
  - Debug endpoints for monitoring

## Tech Stack

- **Backend**: FastAPI
- **Database**: MongoDB Atlas
- **Vector Search**: MongoDB Atlas Vector Search
- **AI/ML**: 
  - Google Generative AI (Gemini)
  - LangChain for embeddings and document processing
- **Testing**: Custom test suite with httpx

## Prerequisites

- Python 3.11+
- MongoDB Atlas account
- Google Cloud API key (for Gemini)
- MongoDB Atlas Vector Search index configured

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cv_parser
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```env
MONGODB_URI=your_mongodb_atlas_uri
DATABASE=cv_parser
GOOGLE_API_KEY=your_google_api_key
```

## Configuration

1. MongoDB Atlas Vector Search Index:
   - Create an index named "default" on the "vectorstore" collection
   - Configure the index with the following fields:
     - embedding_key: "embedding"
     - text_key: "text"
     - metadata_key: "metadata"

2. Create necessary directories:
```bash
mkdir documents
```

## Usage

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. API Endpoints:

### Document Upload
```http
POST /document/upload
Content-Type: multipart/form-data

files: [PDF files]
folder_id: (optional) string
```

### Semantic Search
```http
POST /document/search
Content-Type: application/json

{
    "query": "search query string"
}
```

### Bulk Search
```http
POST /document/search/bulk?query=search_query
Content-Type: application/json

{
    "document_ids": ["id1", "id2", ...]
}
```

### Get Document
```http
GET /document/{document_id}
```

### Delete Document
```http
DELETE /document/{document_id}
```

### Debug Vector Store
```http
GET /document/debug/vector-store
```

## Testing

Run the comprehensive test suite:
```bash
python test_all_endpoints.py
```

The test suite covers:
- Server health check
- CV upload
- Semantic search with various queries
- Bulk search functionality
- Document retrieval
- Vector store debugging

## Response Examples

### CV Upload Response
```json
{
  "results": [{
    "filename": "example.pdf",
    "document_id": "document_id",
    "parsed_cv": {
      "name": "John Doe",
      "position": "Software Engineer",
      "skills": ["Python", "FastAPI", "MongoDB"],
      ...
    }
  }]
}
```

### Search Response
```json
{
  "document_id": {
    "similarity_score": 0.85,
    "parsed_cv": {
      "name": "John Doe",
      "position": "Software Engineer",
      ...
    },
    "matching_content": [{
      "content": "matched text",
      "score": 0.85
    }]
  }
}
```

## Error Handling

The API implements comprehensive error handling:
- File validation
- PDF parsing errors
- Database connection issues
- Search query validation
- Vector store operations

## Performance Considerations

- Uses async/await for non-blocking operations
- Implements connection pooling for MongoDB
- Optimizes vector search with proper indexing
- Handles large PDF files efficiently
- Implements proper cleanup of temporary files

## Security

- Input validation for all endpoints
- Secure file handling
- Environment variable management
- API key protection
- CORS configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


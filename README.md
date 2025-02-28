# CV Parser

A FastAPI-based service that converts CV/Resume PDFs into structured JSON format using Google's Generative AI.

## Features

- PDF to JSON conversion with detailed field extraction
- Scoring system for experience, education, skills, and projects
- Vector storage for semantic search capabilities
- MongoDB integration for data persistence

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```
MONGODB_URI=your_mongodb_connection_string
DATABASE=cv_parser
GOOGLE_API_KEY=your_google_api_key
```

4. Run the application:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Upload CV
```http
POST /document/document
```
Parameters:
- `files`: List of PDF files (multipart/form-data)
- `folder_id`: String (optional)

Response:
```json
{
    "message": "Document uploaded successfully"
}
```

The parsed CV will be stored in MongoDB with the following structure:
```json
{
    "_id": "document_id",
    "parsed_cv": {
        "name": "string",
        "email": "string",
        "phone_number": "string",
        "address": "string",
        "linkedin_url": "string",
        "position": "string",
        "scores": {
            "experience": "int",
            "education": "int",
            "skill": "int",
            "project": "int",
            "presentation": "int"
        },
        "work_experience": [...],
        "education": [...],
        "skills": [...],
        ...
    }
}
```

## Requirements

- Python 3.8+
- MongoDB
- Google Cloud API key with Generative AI access 
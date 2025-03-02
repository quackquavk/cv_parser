# Project Documentation

## Overview

This project is a FastAPI application designed for uploading, managing, and retrieving CV documents. It provides a RESTful API for document handling, including uploading, fetching, and deleting documents.

## Installation

To set up the project, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Upload Document

- **Endpoint:** `POST /upload`
- **Description:** Upload and parse CV documents.
- **Request Body:**
  - `files`: A list of files to upload (required).
  - `folder_id`: An optional identifier for the folder where documents will be stored.
- **Response:**
  - Returns a response from the document upload controller.
- **Error Handling:**
  - Returns a 500 status code with an error message if an exception occurs.
- **Sample Fetch API Call:**
  ```javascript
  const formData = new FormData();
  formData.append('files', fileInput.files[0]); // Assuming fileInput is an input element of type file
  formData.append('folder_id', 'your-folder-id');

  fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData,
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
  ```

### Get All Documents

- **Endpoint:** `GET /document/all`
- **Description:** Retrieve all uploaded documents.
- **Response:**
  - Returns a list of all documents.
- **Error Handling:**
  - Returns a 500 status code with an error message if an exception occurs.
- **Sample Fetch API Call:**
  ```javascript
  fetch('http://localhost:8000/document/all')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
  ```

### Get Document

- **Endpoint:** `GET /{document_id}`
- **Description:** Retrieve a specific document's parsed data.
- **Path Parameters:**
  - `document_id`: The ID of the document to retrieve (required).
- **Response:**
  - Returns the parsed data of the specified document.
- **Error Handling:**
  - Returns a 404 status code if the document is not found.
  - Returns a 500 status code with an error message if an exception occurs.
- **Sample Fetch API Call:**
  ```javascript
  const documentId = 'your-document-id';
  fetch(`http://localhost:8000/${documentId}`)
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
  ```

### Delete Document

- **Endpoint:** `DELETE /{document_id}`
- **Description:** Delete a document and its associated data.
- **Path Parameters:**
  - `document_id`: The ID of the document to delete (required).
- **Response:**
  - Returns a success message upon successful deletion.
- **Error Handling:**
  - Returns a 500 status code with an error message if an exception occurs.
- **Sample Fetch API Call:**
  ```javascript
  const documentId = 'your-document-id';
  fetch(`http://localhost:8000/${documentId}`, {
      method: 'DELETE',
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
  ```

## Database Integration

This application integrates with a database to manage document storage and retrieval. The database operations are handled through a controller, which abstracts the database interactions.

## Error Handling

The application uses FastAPI's built-in exception handling to return appropriate HTTP status codes and error messages for various failure scenarios.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.


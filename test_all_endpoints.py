import asyncio
import json
import httpx
import os
import time
from typing import List, Dict, Any

class CVParserTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.document_ids = []
        self.client = None

    async def wait_for_server(self, max_retries: int = 5, delay: int = 2):
        """Wait for server to be available"""
        print("\n⏳ Checking server availability...")
        for i in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.base_url}/")
                    if response.status_code == 200:
                        print("✅ Server is running")
                        return True
            except Exception:
                print(f"⏳ Waiting for server (attempt {i+1}/{max_retries})...")
                await asyncio.sleep(delay)
        
        print("❌ Server not available")
        return False

    async def setup(self):
        """Initialize the test client and check server"""
        if not await self.wait_for_server():
            raise Exception("Server is not running. Please start the FastAPI server first.")
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def cleanup(self):
        if self.client:
            await self.client.aclose()

    async def test_health_check(self):
        """Test API health check endpoint"""
        try:
            print("\n🔍 Testing API health check...")
            response = await self.client.get("/")
            print(f"Response: {response.json()}")
            assert response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {str(e)}")
            raise

    async def test_upload_cv(self, file_path: str = "cv.pdf"):
        """Test CV upload functionality"""
        try:
            print("\n📄 Testing CV upload...")
            
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"❌ Error: File {file_path} not found")
                print(f"Current working directory: {os.getcwd()}")
                print(f"Available files: {os.listdir('.')}")
                raise FileNotFoundError(f"File {file_path} not found")

            # Read file content
            file_content = open(file_path, "rb").read()
            
            # Prepare multipart form data
            files = {
                "files": (
                    os.path.basename(file_path),
                    file_content,
                    "application/pdf"
                )
            }
            
            print(f"Uploading file: {file_path}")
            try:
                response = await self.client.post(
                    "/document/upload",
                    files=files,
                    timeout=30.0
                )
            except httpx.RequestError as e:
                print(f"❌ Connection error: {str(e)}")
                raise
            except Exception as e:
                print(f"❌ Upload request error: {str(e)}")
                raise
            
            # Check response status
            if response.status_code != 200:
                print(f"❌ Upload failed with status {response.status_code}")
                print(f"Error response: {response.text}")
                raise Exception(f"Upload failed: {response.text}")

            try:
                result = response.json()
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse response JSON: {response.text}")
                raise

            print(f"Upload Response: {json.dumps(result, indent=2)}")
            
            if "results" in result and result["results"]:
                self.document_ids.append(result["results"][0]["document_id"])
            else:
                print("⚠️ No document ID in response")
            
            return result
                
        except FileNotFoundError as e:
            print(f"❌ File error: {str(e)}")
            raise
        except Exception as e:
            print(f"❌ Upload error: {str(e)}")
            print(f"Response details: {getattr(e, 'response', None)}")
            raise

    async def test_semantic_search(self, queries: List[str]):
        """Test semantic search with various queries"""
        try:
            print("\n🔎 Testing semantic search...")
            for query in queries:
                print(f"\nSearching for: {query}")
                response = await self.client.post(
                    "/document/search",
                    json={"query": query}
                )
                if response.status_code != 200:
                    print(f"❌ Search failed: {response.text}")
                    continue
                    
                result = response.json()
                print(f"Found {len(result)} matching documents")
                print(f"Top match score: {self._get_top_score(result)}")
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            raise

    async def test_bulk_search(self, query: str):
        """Test bulk search functionality"""
        try:
            print("\n📚 Testing bulk search...")
            if not self.document_ids:
                print("⚠️ No documents available for bulk search")
                return
                
            print(f"Performing bulk search with query: {query}")
            print(f"Document IDs: {self.document_ids}")
            
            response = await self.client.post(
                "/document/search/bulk",
                params={"query": query},
                json={"document_ids": self.document_ids}
            )
            
            if response.status_code != 200:
                print(f"❌ Bulk search failed: {response.text}")
                return
                
            result = response.json()
            if not result:
                print("⚠️ No results found in bulk search")
            else:
                print(f"Found {len(result)} matching documents")
                for doc_id, doc_data in result.items():
                    print(f"\nDocument {doc_id}:")
                    print(f"Similarity Score: {doc_data.get('similarity_score', 'N/A')}")
                    print(f"Name: {doc_data.get('parsed_cv', {}).get('name', 'N/A')}")
                    print(f"Position: {doc_data.get('parsed_cv', {}).get('position', 'N/A')}")
            
            print(f"\nBulk Search Response: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"❌ Bulk search error: {str(e)}")
            raise

    async def test_get_document(self):
        """Test retrieving specific documents"""
        try:
            print("\n📑 Testing document retrieval...")
            if not self.document_ids:
                print("⚠️ No documents available to retrieve")
                return
                
            for doc_id in self.document_ids:
                response = await self.client.get(f"/document/{doc_id}")
                if response.status_code != 200:
                    print(f"❌ Failed to retrieve document {doc_id}: {response.text}")
                    continue
                    
                result = response.json()
                print(f"\nDocument {doc_id}:")
                print(f"Name: {result.get('parsed_cv', {}).get('name')}")
                print(f"Position: {result.get('parsed_cv', {}).get('position')}")
        except Exception as e:
            print(f"❌ Document retrieval error: {str(e)}")
            raise

    async def test_vector_store_debug(self):
        """Test vector store debug information"""
        try:
            print("\n🔧 Testing vector store debug...")
            response = await self.client.get("/document/debug/vector-store")
            if response.status_code != 200:
                print(f"❌ Debug info failed: {response.text}")
                return
                
            print(f"Debug Info: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"❌ Debug info error: {str(e)}")
            raise

    async def test_delete_documents(self):
        """Test document deletion"""
        try:
            print("\n🗑️ Testing document deletion...")
            if not self.document_ids:
                print("⚠️ No documents available to delete")
                return
                
            for doc_id in self.document_ids:
                response = await self.client.delete(f"/document/{doc_id}")
                if response.status_code != 200:
                    print(f"❌ Failed to delete document {doc_id}: {response.text}")
                    continue
                    
                print(f"Deleted document {doc_id}: {response.json()}")
        except Exception as e:
            print(f"❌ Document deletion error: {str(e)}")
            raise

    def _get_top_score(self, results: Dict[str, Any]) -> float:
        if not results:
            return 0.0
        scores = [doc.get("similarity_score", 0) for doc in results.values()]
        return max(scores) if scores else 0.0

    async def run_all_tests(self):
        """Run all tests in sequence"""
        try:
            await self.setup()

            # Test 1: Health Check
            await self.test_health_check()

            # Test 2: Upload CV
            await self.test_upload_cv()

            # Test 3: Semantic Search with various queries
            search_queries = [
                "React and Next.js developer",
                "Frontend developer with UI/UX experience",
                "Full stack developer with MongoDB experience",
                "Developer with animation and design skills",
                "TypeScript and React developer",
                "Developer with real-time websocket experience"
            ]
            await self.test_semantic_search(search_queries)

            # Test 4: Bulk Search
            await self.test_bulk_search("full stack developer with modern tech stack")

            # Test 5: Get Document Details
            await self.test_get_document()

            # Test 6: Debug Vector Store
            await self.test_vector_store_debug()

            # Test 7: Delete Documents (optional)
            # await self.test_delete_documents()

        except Exception as e:
            print(f"\n❌ Test suite failed: {str(e)}")
        finally:
            await self.cleanup()

if __name__ == "__main__":
    tester = CVParserTester()
    asyncio.run(tester.run_all_tests()) 
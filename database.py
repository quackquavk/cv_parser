from motor.motor_asyncio import AsyncIOMotorClient
from config import config

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(config.MONGODB_URI)
        self.db = self.client[config.DATABASE]
        self.controller = None

    def init_app(self):
        from controllers.document_controller import DocumentController
        from controllers.vector_controller import VectorController

        class Controller:
            def __init__(self, db):
                self.document_controller = DocumentController(db)
                self.vector_controller = VectorController(db)

        self.controller = Controller(self.db)

database = Database()
database.init_app() 
from pydantic import BaseModel, Field
from typing import List

class Folder(BaseModel):
    name: str = Field(default = "TestFolder", example = "Name of the folder")
    document_id: List[str] = Field(default = [], example = ["Document_id1", "Document_id2"])
    document_name: List[str] = Field(default = [], example = ["Document_name1", "Document_name2"])

class MoveFiles(BaseModel):
    from_folder: str = Field(default = None, example = "Folder_id1")
    to_folder: str = Field(default = None, example = "Folder_id2")
    document_id: List[str] = Field(default = [""], example = ["Document_id1", "Document_id2"])

class Rename(BaseModel):
    folder_id: str = Field(default = None, example = "Folder_id")
    new_name: str = Field(default = None, example = "New name")

class ListFolder(BaseModel):
    folder_ids: List[str] = Field(default = [], example = ["Folder_id1", "Folder_id2"])
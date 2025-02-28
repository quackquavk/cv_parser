from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough

from fastapi import HTTPException

import os, re
from config import config

from .prompt import cv_parser_prompt
from .model import cv_parser


os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY


class LLMGenerator:
    def __init__(self):
        self._set_environment_variables()
        self.llm_cache: Dict[str, Any] = {}
        self.prompt_cache: Dict[str, Any] = {
            'cv_parser': cv_parser_prompt
        }

    def _set_environment_variables(self):
        os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY

    
    def get_llm(self, llm_name: str):
        if llm_name not in self.llm_cache:
            if llm_name == 'gemini':
                self.llm_cache[llm_name] = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature = 0.1)
            else:
                raise ValueError(f"LLM {llm_name} not found.")
        return self.llm_cache[llm_name]


    def get_prompt(self, llm_type: str):
        if llm_type not in self.prompt_cache:
            raise ValueError(f"Prompt {llm_type} not found.")
        return self.prompt_cache[llm_type]

    async def generate_parsed_cv(self, llm_type: str, cv: str, llm_name: str = 'gemini'):
        llm = self.get_llm(llm_name)
        prompt = self.get_prompt(llm_type)
        if llm_type == 'cv_parser':
            chain = (
                {'cv': RunnablePassthrough()}
                | prompt
                | llm
                | cv_parser
            )

            result = await chain.ainvoke({"cv": cv})
        if result is None:
            raise HTTPException(status_code=500, detail="Error parsing the CV")
        return result



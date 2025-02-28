from langchain_core.prompts import PromptTemplate

from .model import cv_parser


PROMPT_CV_PARSER = """
<input>
{cv}
<input>

<instructions>
Instructions:
   0. Make sure to write everything in SMALL LETTERS.
   1. Ensure the JSON object starts with '{{' and ends with '}}' and there are no new line separators and slashes in the JSON object.
   2. Do not include the string 'json' or any backticks in your output.
   3. Extract the relevant information according to the following format instructions:
   {format_instructions}
   4. Output ONLY valid JSON. Do not include any explanatory text, markdown formatting, or anything else outside the JSON object.
   5. Only include details that has been speicifically mentioned on the <cv> input.
"""

cv_parser_prompt = PromptTemplate(template = PROMPT_CV_PARSER, input_variables = {"cv"}, partial_variables = {"format_instructions": cv_parser.get_format_instructions()})

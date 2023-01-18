import os
import sys
import requests
import regex as re
from PyPDF2 import PdfReader

import ai21
from langchain import LLMChain, PromptTemplate
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("AI21LAB_KEY")


class FileTooLargeError(Exception):
    pass


def read_pdf(filename):
    with open(filename, "wb") as f:
        f.write(filename)
    reader = PdfReader(filename)
    file_size = os.path.getsize(filename) / 1000
    if file_size > 1000:
        raise FileTooLargeError("Error: File size should be less than 1MB")
    else:
        PAGES_LEN = len(reader.pages)
        output = ""
        for index in range(0, PAGES_LEN):
            output += reader.pages[index].extract_text()
        doc_search = re.search(
            r"Introduction((.*)(\d)references|(.*)(\d). Bibliographical References|(.*)References)",
            output,
            flags=re.DOTALL | re.IGNORECASE | re.MULTILINE,
        )
        return doc_search.group(1)


def call_ai21(text):
    response = requests.post(
        url=f"https://api.ai21.com/studio/v1/experimental/summarize",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"text": text},
    )
    return response


def split_text(text):
    chunks = []
    while len(text) > 10000:
        chunks.append(text[:10000])
        text = text[10000:]
    chunks.append(text)
    return chunks

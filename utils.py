import os
import requests
import regex as re
from PyPDF2 import PdfReader

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("AI21LAB_KEY")


class FileTooLargeError(Exception):
    pass


def read_pdf(filename):
    reader = PdfReader(open(filename, "rb"))
    file_size = os.path.getsize(filename) / 1000
    if file_size > 500:
        raise FileTooLargeError("Error: File size should be less than 500KB")
    else:
        PAGES_LEN = len(reader.pages)
        output = "".join(
            [reader.pages[index].extract_text() for index in range(0, PAGES_LEN)]
        )
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

import os
import uvicorn


import regex as re
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from utils import split_text, call_ai21, read_pdf, FileTooLargeError

app = FastAPI()

templates = Jinja2Templates(directory="templates")


def return_summarized_texts(filename):
    try:
        pdf_texts = read_pdf(filename)
    except FileTooLargeError as e:
        return e.__str__()
    text_lists = split_text(pdf_texts)
    summarized_docs = []
    for text in text_lists:
        summarized_docs.append(call_ai21(text).json()["summaries"][0]["text"])
    text = " ".join(summarized_docs)
    # Replace newlines with spaces
    text = text.replace("\n", " ")
    # Replace unicode characters with empty string
    text = re.sub(r"[^\x00-\x7F]+", "", text)
    return text


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request})


@app.post("/", response_class=HTMLResponse)
def upload_file(request: Request, pdf_file: UploadFile = File()):
    with open("/tmp/file.pdf", "wb") as f:
        content = pdf_file.file.read()
        f.write(content)
    texts = return_summarized_texts("/tmp/file.pdf")
    if "Error" in texts:
        return templates.TemplateResponse(
            "home.html", context={"request": request, "error": texts}
        )
    return templates.TemplateResponse(
        "home.html", context={"request": request, "text": texts}
    )


@app.exception_handler(404)
def custom_404_handler(request: Request, __):
    return templates.TemplateResponse(
        "404.html", context={"request": request, "error": True}
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)

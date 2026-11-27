import pdfplumber
import io

def extract_text_from_pdf(uploaded_file) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def extract_text_from_txt(uploaded_file) -> str:
    return uploaded_file.read().decode("utf-8").strip()
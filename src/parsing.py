import PyPDF2
import docx
from odf import text, teletype
from odf.opendocument import load
import os


def parse_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    try:
        if file_extension.lower() == '.pdf':
            return parse_pdf(file_path)
        elif file_extension.lower() == '.docx':
            return parse_docx(file_path)
        elif file_extension.lower() == '.odt':
            return parse_odt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    except Exception as e:
        print(f"Parsing error {file_path}: {e}")
        return None


def parse_pdf(file_path):
    try:
        # Since PdfFileReader is deprecated, we use PdfReader instead
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            file_text = ""
            for page in range(len(reader.pages)):
                file_text += reader.pages[page].extract_text()

        return file_text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None


def parse_docx(file_path):
    try:
        doc = docx.Document(file_path)
        file_text = '\n'.join([para.text for para in doc.paragraphs])
        return file_text
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return None


def parse_odt(file_path):
    try:
        textdoc = load(file_path)
        alltexts = textdoc.getElementsByType(text.P)
        file_text = "\n\n".join(teletype.extractText(s) for s in alltexts)
        return file_text
    except Exception as e:
        print(f"Error reading ODT: {e}")
        return None

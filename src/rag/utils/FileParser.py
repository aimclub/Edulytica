import PyPDF2
import docx
from odf import text, teletype
from odf.opendocument import load
import os


class FileParser:
    """
    A class that provides functionality to parse different file types: PDF, DOCX, ODT.
    """

    def __init__(self, file_path: str):
        """
        Initializes the FileParser with the path to the file.

        :param file_path: The path to the file that needs to be parsed.
        """
        self.file_path = file_path
        _, self.file_extension = os.path.splitext(file_path)

    def parse(self):
        """
        Parses the file based on the extension and returns its text content.

        :return: The text content of the file.
        """

        try:
            if self.file_extension.lower() == ".pdf":
                return self._parse_pdf()
            if self.file_extension.lower() == ".docx":
                return self._parse_docx()
            if self.file_extension.lower() == ".odt":
                return self._parse_odt()
            raise ValueError(f"Unsupported file type: {self.file_extension}")
        except Exception as e:
            print(f"Parsing error {self.file_path}: {e}")
            return None

    def _parse_pdf(self):
        """
        Parses a PDF file and extracts its text content.

        :return: The text content of the PDF file.
        """

        try:
            with open(self.file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                file_text = ""
                for page in range(len(reader.pages)):
                    file_text += reader.pages[page].extract_text()

            return file_text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None

    def _parse_docx(self):
        """
        Parses a DOCX file and extracts its text content.

        :return: The text content of the DOCX file.
        """

        try:
            doc = docx.Document(self.file_path)
            file_text = "\n".join([para.text for para in doc.paragraphs])
            return file_text
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            return None

    def _parse_odt(self):
        """
        Parses an ODT file and extracts its text content.

        :return: The text content of the ODT file.
        """

        try:
            textdoc = load(self.file_path)
            alltexts = textdoc.getElementsByType(text.P)
            file_text = "\n\n".join(teletype.extractText(s) for s in alltexts)
            return file_text
        except Exception as e:
            print(f"Error reading ODT: {e}")
            return None

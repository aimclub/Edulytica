import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from typing import List, Dict, Union, IO
import pdfplumber
from src.edulytica_api.parser.Elem import Elem
from src.edulytica_api.parser.schemas import schemas


class Parser:
    """
    Handles file type detection, unpacking of DOCX files, and routes the parsing process to the appropriate method based on the file type.

    Attributes:
        path (Union[str, IO[bytes]]): The file-like object for the document.
        filename (str): The name of the file, used for type detection.
        _temp_dir (str): The path to a temporary directory for storing unpacked DOCX files.
        file_type (str): The detected type of the file ('docx' or 'pdf').
    """
    def __init__(self, path: Union[str, IO[bytes]], filename: str = None):
        self.path = path
        self.filename = filename
        self._temp_dir = tempfile.mkdtemp()
        self.file_type = self._get_file_type()
        if self.file_type == 'docx':
            self._extract_files()

    def _get_file_type(self) -> str:
        """
        Determines the file type by checking the filename, content type, or file signature.
        """
        filename = self.filename or getattr(self.path, 'name', None)
        content_type = getattr(self.path, 'content_type', None)

        if content_type:
            if 'pdf' in content_type:
                return 'pdf'
            elif 'openxmlformats-officedocument.wordprocessingml.document' in content_type:
                return 'docx'

        if filename and isinstance(filename, str):
            if filename.lower().endswith('.pdf'):
                return 'pdf'
            elif filename.lower().endswith('.docx'):
                return 'docx'

        if hasattr(self.path, 'read') and hasattr(self.path, 'seek'):
            try:
                original_position = self.path.tell()
                header = self.path.read(4)
                self.path.seek(original_position)
                if header.startswith(b'%PDF'):
                    return 'pdf'
                elif header.startswith(b'PK\x03\x04'):
                    return 'docx'
            except Exception as e:
                raise ValueError(f"Не удалось прочитать заголовок файла: {e}")
        raise ValueError("Не удалось определить тип файла. Поддерживаются только PDF и DOCX.")

    def _extract_files(self):
        """
        Unpacks the DOCX file (a zip archive) into a temporary directory for parsing.
        """
        with zipfile.ZipFile(self.path, 'r') as zr:
            zr.extractall(self._temp_dir)

    def parse(self) -> (List[Elem], bool):
        """
        Runs the main parsing logic based on the detected file type.
        """
        if self.file_type == 'docx':
            return self._parse_docx()
        else:
            return self._parse_pdf()

    def _parse_docx(self) -> (List[Elem], bool):
        """
        Parses the 'word/document.xml' part of an unpacked DOCX file to find structured content.
        """
        try:
            tree = ET.parse(os.path.join(self._temp_dir, 'word', 'document.xml'))
            root = tree.getroot()
            paragraphs = []
            for element in root.iter(f'{{{schemas.w}}}sdt'):
                for content in element.iter(f'{{{schemas.w}}}sdtContent'):
                    for para in content.iter(f'{{{schemas.w}}}p'):
                        paragraphs.append(para)
            return self._parse_paragraphs(paragraphs)
        except ET.ParseError as e:
            return [], True

    def _parse_pdf(self) -> (List[Elem], bool):
        """
        Parses a PDF document page by page, extracting text from each page.
        """
        struct = []
        potentially_damaged = False
        try:
            with pdfplumber.open(self.path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        struct.append(Elem(str(i + 1), text.strip(), None))
        except Exception as e:
            potentially_damaged = True
            print(f"Ошибка парсинга PDF: {e}")
        return struct, potentially_damaged

    def parse_paragraphs_from_anchor(self, anchor_id: str, next_anchor_id, list_view: bool = True):
        """
        Extracts all text content located between two specified bookmarks (anchors) in a DOCX file.
        For PDF files, this method returns all text content from the document.
        """
        if self.file_type == 'pdf':
            with pdfplumber.open(self.path) as pdf:
                text = [p.extract_text().strip() for p in pdf.pages if p.extract_text()]
                return text if list_view else '\n'.join(text)

        tree = ET.parse(os.path.join(self._temp_dir, 'word', 'document.xml'))
        root = tree.getroot()
        check = False
        text = []
        for p in root.iter(f"{{{schemas.w}}}p"):
            if next_anchor_id and p.findall(
                    f'.//{{{schemas.w}}}bookmarkStart[@{{{schemas.w}}}name="{next_anchor_id}"]') and check:
                break
            if check:
                text.append(self._parse_text_from_anchor(p))
            if anchor_id and p.findall(f'.//{{{schemas.w}}}bookmarkStart[@{{{schemas.w}}}name="{anchor_id}"]'):
                check = True
        return text if list_view else '\n'.join(text)

    def _parse_text_from_anchor(self, paragraph: Element) -> str:
        """
        A helper method to extract all text from a single XML paragraph element.
        """
        return ''.join(paragraph.itertext())

    def _parse_paragraphs(self, paragraphs: List[Element]) -> (List[Elem], bool):
        """
        Analyzes a list of paragraph elements from a DOCX file to build a hierarchical structure
        based on their styling.
        """
        struct: List[Elem] = []
        potentially_damaged = False
        return struct, potentially_damaged

    def get_other_text(self) -> List[str]:
        """
        Extracts all non-structured text from the document body.
        """
        if self.file_type == 'pdf':
            with pdfplumber.open(self.path) as pdf:
                return [p.extract_text().strip() for p in pdf.pages if p.extract_text()]

        tree = ET.parse(os.path.join(self._temp_dir, 'word', 'document.xml'))
        root = tree.getroot()
        all_text = []
        for para in root.findall(f'.//{{{schemas.w}}}body//{{{schemas.w}}}p'):
            para_text = ''.join(para.itertext())
            if para_text.strip():
                all_text.append(para_text.strip())
        return all_text


def _handle_json(obj):
    """
    Custom JSON serializer function to handle non-standard objects like 'Elem' and 'None'.
    """
    if isinstance(obj, Elem):
        return obj.to_dict()
    if obj is None:
        return "null"
    return str(obj)


def get_structural_paragraphs(file_stream: IO[bytes], filename: str = None) -> Dict:
    """
    Main function to process a file stream. It initializes the Parser,
    runs the parsing process, and returns the document's content as a structured dictionary.

    Args:
        file_stream (IO[bytes]): A file-like object opened in binary mode.
        filename (str, optional): The original name of the file.

    Returns:
        Dict: A dictionary containing the parsed table of contents, any other text,
              and a flag indicating potential damage to the file.
    """
    def struct_to_dict(elements: List[Elem], p: Parser) -> List[Dict]:
        if not elements:
            return []

        result_list = []
        for i, elem in enumerate(elements):
            next_elem = elements[i + 1] if i + 1 < len(elements) else None
            elem_dict = convert_element_to_dict(elem, p, next_elem)
            result_list.append(elem_dict)
        return result_list

    def convert_element_to_dict(elem: Elem, p: Parser, next_elem: Elem = None) -> Dict:
        next_anchor_id = None
        if elem.sub_elements:
            next_anchor_id = elem.sub_elements[0].anchor_id
        elif next_elem:
            next_anchor_id = next_elem.anchor_id

        elem_dict = {
            "num": elem.num,
            "title": elem.text,
            "text": p.parse_paragraphs_from_anchor(elem.anchor_id, next_anchor_id, list_view=False),
            "sub_elements": struct_to_dict(elem.sub_elements, p)  # Рекурсивный вызов
        }
        return elem_dict

    try:
        p = Parser(path=file_stream, filename=filename)
        structure, is_damaged = p.parse()

        result = {
            'potentially_damage': is_damaged,
            'table_of_content': struct_to_dict(structure, p),
            'other_text': p.get_other_text()
        }
        return result
    except Exception as e:
        return {
            'potentially_damage': True,
            'table_of_content': [],
            'other_text': []
        }

import json
import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from os.path import join
from xml.etree.ElementTree import Element
from .schemas import schemas
from .Elem import Elem
from typing import List, Dict


class Parser:
    """
    Class, that parses DOCX-document and saves it in json-format
    :param self.path: path to file
    :param self._temp_dir: path to the temp directory, where the unpacked DOCX-document is stored
    """

    def __init__(self, path):
        self.path = path
        self._temp_dir = tempfile.mkdtemp()
        self._extract_files()

    def _extract_files(self):
        """
        Unpacks DOCX-document in temp directory
        """
        with zipfile.ZipFile(self.path, "r") as zr:
            zr.extractall(self._temp_dir)

    def parse(self):
        """
        Parses document.xml part and returns content and flag (potentially damaged)
        """
        tree = ET.parse(os.path.join(self._temp_dir, "word", "document.xml"))
        root = tree.getroot()
        paragraphs = []
        for element in root.iter(f"{{{schemas.w}}}sdt"):
            for content in element.iter(f"{{{schemas.w}}}sdtContent"):
                for para in content.iter(f"{{{schemas.w}}}p"):
                    paragraphs.append(para)
        return self._parse_paragraphs(paragraphs)

    def parse_paragraphs_from_anchor(self, anchor_id: str, next_anchor_id, list_view: bool = True):
        """
        Parses text, that attached to a chapter by anchor_id
        """
        tree = ET.parse(os.path.join(self._temp_dir, "word", "document.xml"))
        root = tree.getroot()

        check = False
        text = []
        for p in root.iter(f"{{{schemas.w}}}p"):
            if p.findall(f'{{{schemas.w}}}bookmarkStart[@{{{schemas.w}}}name="{next_anchor_id}"]') and check:
                return text if list_view else "\n".join(text)
            if check:
                text.append(self._parse_text_from_anchor(p))
            if p.findall(f'{{{schemas.w}}}bookmarkStart[@{{{schemas.w}}}name="{anchor_id}"]'):
                check = True
        return text if list_view else "\n".join(text)

    def _parse_text_from_anchor(self, paragraph: Element):
        return "".join([i for i in paragraph.itertext()])

    def _parse_paragraphs(self, paragraphs: List[Element]):
        struct = []
        potentially_damage = False
        for para in paragraphs:
            for pPr in para.iter(f"{{{schemas.w}}}pPr"):
                for style in pPr.iter(f"{{{schemas.w}}}pStyle"):
                    val = style.attrib[f"{{{schemas.w}}}val"]
                    hyperlink = para.iter(f"{{{schemas.w}}}hyperlink")
                    hyperlink_id = None
                    for i in hyperlink:
                        hyperlink_id = i.attrib[f"{{{schemas.w}}}anchor"]
                    if not val.isdigit():
                        continue
                    elif int(val) // 10 == 1:
                        for text in para.iter(f"{{{schemas.w}}}t"):
                            struct.append(Elem(str(len(struct) + 1), text.text, hyperlink_id))
                            break
                    elif int(val) // 10 == 2:
                        for text in para.iter(f"{{{schemas.w}}}t"):
                            if len(struct) == 0:
                                struct.append(Elem(str(len(struct) + 1), text.text, hyperlink_id))
                                potentially_damage = True
                                break
                            else:
                                num = f"{str(len(struct))}.{str(len(struct[-1]) + 1)}"
                                struct[-1].append(Elem(num, text.text, hyperlink_id))
                                break
                    elif int(val) // 10 == 3:
                        for text in para.iter(f"{{{schemas.w}}}t"):
                            if len(struct) == 0:
                                potentially_damage = True
                                struct.append(Elem(str(len(struct) + 1), text.text, hyperlink_id))
                                break
                            elif len(struct[-1]) == 0:
                                potentially_damage = True
                                num = f"{str(len(struct))}.{str(len(struct[-1]) + 1)}"
                                struct[-1].append(Elem(num, text.text, hyperlink_id))
                                break
                            else:
                                num = (
                                    f"{str(len(struct))}.{str(len(struct[-1]))}."
                                    f"{str(len(struct[-1].sub_elements) + 1)}"
                                )
                                struct[-1].sub_elements[-1].append(Elem(num, text.text, hyperlink_id))
                                break
        return struct, potentially_damage

    def save(self, struct: Dict, path: str = None):
        """
        Save DOCX-document as JSON
        """
        if path is None:
            path = self.path
        with open(f"{path[:-5]}.json", "w", encoding="utf-8") as json_file:
            json.dump(struct, json_file, indent=4, default=_handle_none, ensure_ascii=False)

    def get_other_text(self):
        """
        Gets other text from a document
        """
        tree = ET.parse(os.path.join(self._temp_dir, "word", "document.xml"))
        root = tree.getroot()
        all_text = []
        for para in root.findall(f".//{{{schemas.w}}}body//{{{schemas.w}}}p"):
            para_text = ""
            for t in para.iter(f"{{{schemas.w}}}t"):
                para_text += f"{t.text} "
            all_text.append(para_text)
        return all_text


def _handle_none(obj):
    if obj is None:
        return "null"
    return obj


def get_structural_paragraphs(file):
    def struct_to_dict(elements: List[Elem], p: Parser):
        """
        Converts a list of chapter-elements to dict
        :param elements: list of elements
        :param p: parser
        """

        def convert_element_to_dict(elem: Elem, p: Parser, next_elem=None):
            next_anchor_id = None
            if elem.sub_elements is not None:
                next_anchor_id = elem.sub_elements[0].anchor_id
            else:
                if next_elem is not None:
                    next_anchor_id = next_elem.anchor_id
            elem_dict = {
                "num": elem.num,
                "title": elem.text,
                "text": p.parse_paragraphs_from_anchor(elem.anchor_id, next_anchor_id),
            }
            temp = []
            if elem.sub_elements:
                for i, sub_elem in enumerate(elem.sub_elements):
                    if i < len(elem.sub_elements) - 1:
                        temp.append(convert_element_to_dict(sub_elem, p, elem.sub_elements[i + 1]))
                    else:
                        temp.append(convert_element_to_dict(sub_elem, p))
            elem_dict["sub_elements"] = temp
            return elem_dict

        if elements is None:
            return
        temp = []
        for i, elem in enumerate(elements):
            if i < len(elements) - 1:
                temp.append(convert_element_to_dict(elem, p, elements[i + 1]))
            else:
                temp.append(convert_element_to_dict(elem, p))
        return temp

    try:
        import io

        with io.BytesIO(file.read()) as f:
            p = Parser(path=f)
            s, pot = p.parse()
            n = {"potentially_damage": pot, "table_of_content": struct_to_dict(s, p), "other_text": p.get_other_text()}
            return n
    except Exception as _e:
        raise _e

import csv
import os

import pdfplumber
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTRect, LTChar


# noinspection DuplicatedCode
class PDFParser:
    def parse_files(self, pdfs_directory):
        os.chdir(pdfs_directory)
        with open('../pdfs_data.csv', 'a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=['id', 'data'], escapechar='\\')
            pdf_filenames = sorted(filter(lambda x: x[-4:] == '.pdf', os.listdir()))
            for i, filename in enumerate(pdf_filenames):
                print(i, filename)
                if filename[-4:] == '.pdf':
                    try:
                        writer.writerow({'id': i, 'data': self.parse_file(filename)})
                    except Exception as e:
                        print(e)

    def parse_file(self, pdf_path: str):
        pages = []
        for page_num, page in enumerate(extract_pages(pdf_path)):
            text_from_tables = []
            page_content = []
            table_num = 0
            first_element_flag = True
            table_extraction_flag = False
            pdf = pdfplumber.open(pdf_path)
            page_tables = pdf.pages[page_num]
            tables = page_tables.find_tables()

            page_elements = [(element.y1, element) for element in page._objs]
            page_elements.sort(key=lambda x: -x[0])

            lower_side, upper_side = 0, 0
            for i, component in enumerate(page_elements):
                element = component[1]

                if isinstance(element, LTTextContainer):
                    if not table_extraction_flag:
                        line_text, format_for_line = self._extract_text(element)
                        page_content.append(line_text)

                if isinstance(element, LTRect) and table_num < len(tables):
                    if first_element_flag:
                        lower_side = page.bbox[3] - tables[table_num].bbox[3]
                        upper_side = element.y1
                        table = self._extract_table(pdf_path, page_num, table_num)
                        table_string = self._table_converter(table)
                        text_from_tables.append(table_string)
                        page_content.append(table_string)
                        table_extraction_flag = True
                        first_element_flag = False
                    if element.y0 >= lower_side and element.y1 <= upper_side:
                        pass
                    elif i + 1 < len(page_elements) and not isinstance(page_elements[i + 1][1], LTRect):
                        table_extraction_flag = False
                        first_element_flag = True
                        table_num += 1
            pages.append(page_content)

        return ''.join(row for page in pages for row in page).replace('\n', ' \\n ')

    @staticmethod
    def _extract_text(element):
        line_text = element.get_text()
        line_formats = []
        for text_line in element:
            if isinstance(text_line, LTTextContainer):
                for character in text_line:
                    if isinstance(character, LTChar):
                        line_formats.append(character.fontname)
                        line_formats.append(character.size)
        format_per_line = list(set(line_formats))

        return line_text, format_per_line

    @staticmethod
    def _extract_table(pdf_path, page_num, table_num):
        return pdfplumber.open(pdf_path).pages[page_num].extract_tables()[table_num]

    @staticmethod
    def _table_converter(table):
        table_string = ''
        for row_num in range(len(table)):
            row = table[row_num]
            cleansed_row = [
                item.replace('\n', '') if item is not None and '\n' in item else 'None' if item is None else item for
                item in row]
            table_string += f"|{'|'.join(cleansed_row)}|\n"
        return table_string[:-1]


if __name__ == '__main__':
    pdf_parser = PDFParser()
    pdf_parser.parse_files('../../../VKRsData')

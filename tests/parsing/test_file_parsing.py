import unittest

from src.rag.utils.parsing import FileParser


class TestFileParser(unittest.TestCase):
    def setUp(self):
        self.pdf_path = 'files/test.pdf'
        self.docx_path = 'files/test.docx'
        self.odt_path = 'files/test.odt'
        self.invalid_path = 'files/test.txt'

        self.create_test_documents()

    def create_test_documents(self):
        self.create_test_pdf(self.pdf_path)
        self.create_test_docx(self.docx_path)
        self.create_test_odt(self.odt_path)

    @staticmethod
    def create_test_pdf(file_path):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(100, 750, "This is a test PDF content")
        c.save()

    @staticmethod
    def create_test_docx(file_path):
        import docx
        doc = docx.Document()
        doc.add_paragraph("This is a test DOCX content")
        doc.save(file_path)

    @staticmethod
    def create_test_odt(file_path):
        from odf.opendocument import OpenDocumentText
        from odf.text import P
        doc = OpenDocumentText()
        p = P(text="This is a test ODT content")
        doc.text.addElement(p)
        doc.save(file_path)

    def test_parse_pdf(self):
        parser = FileParser(self.pdf_path)
        result = parser.parse()
        self.assertEqual(result.strip(), "This is a test PDF content")

    def test_parse_docx(self):
        parser = FileParser(self.docx_path)
        result = parser.parse()
        self.assertEqual(result.strip(), "This is a test DOCX content")

    def test_parse_odt(self):
        parser = FileParser(self.odt_path)
        result = parser.parse()
        self.assertEqual(result.strip(), "This is a test ODT content")

    def test_parse_invalid_file(self):
        parser = FileParser(self.invalid_path)
        result = parser.parse()
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

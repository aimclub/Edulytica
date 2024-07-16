# Data Handling

---
An auxiliary module that stores parsers of data and documents for generating datasets.

---
## Structure:

- **PDFParser** - Parse text from pdf to csv:
  - *parse_files* - Parse all pdfs in directory and save to csv file;
  - *parse_file* - Parse pdf file and return it contains as a string without pages before a introduction and used 
  references page;
  - *_extract_text* - Extract text from LTRect object;
  - *_extract_table* - Extract table from pdf file;
  - *_table_converter* - Convert table to string;
  - *clear_csv* - Clear csv file.
- **ParserVKR** - This class is responsible for parsing VKR files from SPBU:
  - *_parse_vkrs* - Method to parse persons data from VKRs website;
  - *_make_request* - Static Method to make a get request with User-Agent.
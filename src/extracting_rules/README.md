# Extracting Rules

---
This module is devoted to an experiment with extracting design rules using LLM.

---
## Structure:

- **config** - The directory stores promts and instructions (recommendations for the model);
- **docs** - The directory stores documents for processing - GOST and others (pdf, txt);
- **helpers** - The directory stores document formatting code, chunking:
  - *DocumentFormatter* - An auxiliary class containing methods for formatting json objects and splitting documents 
  into chunks.
- **logs** - Logs are stored in the directory after processing and response, and if everything is correct, then they
are combined and written to data;
- **data** - The directory stores responses to queries;
- **models** - The directory stores the access classes to the models that were used in the experiments:
  - *GeminiModel* - A class that provides access to the Gemini model;
  - *GigaModel* - A class that provides access to the GigaChat model;
  - *OpenModel* - A class that provides access to the ChatGPT model.
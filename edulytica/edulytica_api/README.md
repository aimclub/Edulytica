# Edulytica API

---
This module stores the source code of the web service.

---
## Structure:

- **auth** - A submodule that provides authorization and authentication in the application;
- **celery** - A submodule that provides celery as an asynchronous distributed task queue 
for parallel work of several users;
- **front_end** - A submodule that implements the client part of the service using the React framework;
- **llms** - A submodule that provides access to trained models;
- **parser** - A submodule containing classes and objects for extracting information from DOCX format documents;
- **database.py** - Configuration class for connecting to the database;
- **settings.py** - Configuration file with keys for application.
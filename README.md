![ITMO](https://raw.githubusercontent.com/aimclub/open-source-ops/43bb283758b43d75ec1df0a6bb4ae3eb20066323/badges/ITMO_badge_rus.svg)
[![license](https://badgen.net/static/license/MIT/blue)](https://badgen.net/static/license/MIT/blue)
[![Visitors](https://api.visitorbadge.io/api/combined?path=https%3A%2F%2Fgithub.com%2Faimclub%2FEdulytica&label=Visitors&labelColor=%23697689&countColor=%23263759&style=plastic)](https://visitorbadge.io/status?path=https%3A%2F%2Fgithub.com%2Faimclub%2FEdulytica)
[![codecov](https://codecov.io/gh/aimclub/Edulytica/branch/development/graph/badge.svg?token=L1I8M0KDS6)](https://codecov.io/gh/aimclub/Edulytica)
![build](https://github.com/aimclub/Edulytica/actions/workflows/build-test.yml/badge.svg?branch=development)
![docs](https://github.com/aimclub/Edulytica/actions/workflows/documentation.yml/badge.svg?branch=development)

<p>Built with:</p>

[![python](https://badgen.net/badge/python/3.10/blue?icon=python)](https://www.python.org/)
![Jupyter Notebook](https://img.shields.io/badge/Jupyter-%23F37626?logo=jupyter&logoColor=white&labelColor=red&color=red)
![FastAPI](https://img.shields.io/badge/FastAPI-%23009688?logo=fastapi&logoColor=green&labelColor=006666&color=006666)
![Docker](https://img.shields.io/badge/Docker-%232496ED?logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-%232088FF?logo=github%20actions&logoColor=white&labelColor=blue&color=blue)

# Edulytica
![logo](src/images/logo.png)

## Description
Edulytica is an open-source framework for evaluating text results of educational and scientific activities based on 
LLMs, which provides an integrated web application out of the box.

The goal is to provide experts with supporting materials in solving the tasks of reviewing final qualifying papers and 
articles by young scientists, as well as to reduce the time required for in-depth analysis of works.

## Features
- The extraction of goals and objectives from the text of the introduction of final qualifying papers has been implemented;
- As part of the work with scientific articles, the functionality of forming a primary review has been implemented;
- Algorithms for summarizing large texts and evaluating the achievement of stated goals and objectives;
- A web application for interacting with features and trained models through a user-friendly interface;
- Separate models have been trained to [summarize](https://huggingface.co/slavamarcin/saiga_llama3_8b-qdora-4bit_purpose) 
and [assess the achievability of goals and objectives](https://huggingface.co/slavamarcin/saiga3_8b_Qdora_4bit_sum);
- Datasets have been prepared for training models, separately for [summarization](https://huggingface.co/datasets/slavamarcin/sum_dataset_v1), 
separately for [goals and objectives](https://huggingface.co/datasets/slavamarcin/purpose_dataset_v1).
> Please help us improve this project, share your feedback with [opening issue](https://github.com/aimclub/Edulytica/issues)!

## Installation
#### 1. Clone the repository 
```git clone https://github.com/aimclub/Edulytica.git```

#### 2. Launch docker containers or follow the instructions starting from point 3
```docker-compose up --build```

#### 3. Activate venv
```source ~/PyProject/Edulytica/api_venv/bin/activate```

#### 4. Install requirements
```pip install -r requirements.txt```

#### 5. Start Application
```python3 src/edulytica_api/app.py```

#### 6. Activate Celery
```celery -A src.edulytica_api.celery.tasks worker --loglevel=info -E -P gevent```

#### 7. Run npm
```npm start```

#### 7. Run Celery task
```celery -A src.edulytica_api.celery.tasks flower```

## Getting started
![example](src/images/example.gif)

First, you can familiarize yourself with the [examples](https://github.com/aimclub/Edulytica/tree/development/examples) 
in JSON format of the system's responses to the test sample of works.

When you have managed to launch the service, you can send the documents yourself and get acquainted with the results of 
their verification!

## Events inside the web application
As part of working with RAG technology, the specifics of the following measures are taken into account when generating 
a response from the system:
1. kmu_event - suitable for articles by undergraduates and graduate students of junior courses submitted to open 
university conferences of young scientists, language - Russian;
2. epi_event - suitable for "adult" articles in the field of economics, management in organizational systems and 
related fields, language - Russian;
3. ysc_event is suitable for articles by young scientists that are submitted to Web of Science or Scopus journals, 
conferences with the publication of works in Web of Science or Scopus publications on advanced computer science, 
including artificial intelligence, language - English;
4. fruct_event - suitable for articles by young scientists that are submitted to Web of Science or Scopus journals, 
conferences with the publication of papers in Web of Science or Scopus publications on computer science (may include 
work in the field of applied artificial intelligence), language - English;
5. pps_event - suitable for articles by students, graduate students, and young teachers submitted to open university 
educational and methodological conferences, the language is Russian.

Choosing an event at the stage of sending a document is **mandatory** and affects the quality of the response generated.

## Documentation
Details of the documentation can be found at the links below:
- **[algorithms](https://github.com/aimclub/Edulytica/tree/development/src/algorithms)** - part of the task of 
analyzing the text how much it is necessary to change the source text (which is written by AI) so that AI recognition
systems do not recognize AI in this text;
- **[data_handling](https://github.com/aimclub/Edulytica/tree/development/src/data_handling)** - an auxiliary module
that stores parsers of data and documents for generating datasets;
- **[edulytica_api](https://github.com/aimclub/Edulytica/tree/development/src/edulytica_api)** - this module stores 
the source code of the web service;
- **[extracting_rules](https://github.com/aimclub/Edulytica/tree/development/src/extracting_rules)** - This module is
devoted to an experiment with extracting design rules using LLM;
- **[rag](https://github.com/aimclub/Edulytica/tree/development/src/rag)** - Package for an experiment with semantic
search, kNN and the mBERT model are used.

Code documentation is available at [the link](https://aimclub.github.io/Edulytica/index.html).

## Requirements
For more information, see the file **[requiremets.txt](https://github.com/aimclub/Edulytica/blob/development/requirements.txt)**.

## Contacts
Our contacts:
- Tereshchenko Vladislav, vvtereshchenko@itmo.ru.

## Publications about Edulytica
We also published several posts devoted to different aspects of the project:

In Russian:
- [Edulytica: LLM-ассистент для проверки научных работ](https://youtu.be/kDNREVv1IoI?si=lDzHTxTh333EcSaZ) - Scientific Open Source Meetup №8, October 2024, 1:05:15 - 1:22:36;
- [Как мы научили LLM-ассистента рецензировать научные работы студентов ИТМО: вновь о проекте Edulytica](https://vkvideo.ru/video-173944682_456239041) - Scientific Open Source Meetup №10, July 2025, 1:07:30 - 1:34:00.

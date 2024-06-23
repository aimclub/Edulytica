![ITMO](https://raw.githubusercontent.com/aimclub/open-source-ops/43bb283758b43d75ec1df0a6bb4ae3eb20066323/badges/ITMO_badge_rus.svg)
[![python](https://badgen.net/badge/python/3.10|3.11/blue?icon=python)](https://www.python.org/)
[![codecov](https://codecov.io/gh/LISA-ITMO/Edulytica/graph/badge.svg?token=L1I8M0KDS6)](https://codecov.io/gh/LISA-ITMO/Edulytica)
![build](https://github.com/LISA-ITMO/Edulytica/actions/workflows/build-test.yml/badge.svg?branch=development)

# Edulytica
![logo](./.github/workflows/sources/logo2.png)
## Description
The purpose of the study is to automate the analysis of scientific and educational documents in the context of 
research works using LLM (Large language model, large language models) to reduce the time and intellectual costs of 
teachers. The result is two LLMs, trained on specially collected data, capable of summarizing the text of a large 
document and revealing whether the stated goals and objectives of the work have been achieved.

## Features
- Data parser from ISU;
- Data processor from telegram channels;
- Data parser from WRC;
- An algorithm for identifying changes in the text for analyzing AI text generation;
- Fast APP is an application for interacting with trained models;
- Code for highlighting goals and objectives using LLM;
- Added settings for ChatGPT and GigaChat models. The functionality of splitting text into blocks has been implemented. A Yandex bot has been implemented to highlight the rules. Work with the database has been configured for the experiment of identifying requirements from regulatory documents using LLM.

## Requirements
```
aiohttp==3.9.5
aiosignal==1.3.1
annotated-types==0.7.0
anyio==4.4.0
async-timeout==4.0.3
attrs==23.2.0
...
```
For more information, see the file 'requiremets.txt';

## Installation
```git clone https://github.com/LISA-ITMO/Edulytica.git```

## Getting started
```in dev```

## Docs
The documentation is available at [the link](https://lisa-itmo.github.io/Edulytica/index.html)

## Contacts
Our contacts:

slavamarcin@yandex.ru\
vlad-tershch@yandex.ru

## Conferences
1) XIII Конгресс молодых ученых ИТМО:
   - Дворников А.С., Стрижов Д.А., Унтила А.А., Федоров Д.А. ИССЛЕДОВАНИЕ СГЕНЕРИРОВАННОГО ТЕКСТА НА ПРЕДМЕТ РАСПОЗНАВАНИЯ ИЗМЕНЕНИЙ СЕРВИСАМИ ИДЕНТИФИКАЦИИ ИСКУССТВЕННОГО ИНТЕЛЛЕКТА - 2024;
   - Мищенко М.Ю., Мустафин Д.Э., Унтила А.А. Оценка релевантности неструктурированных данных для анализа и дообучения LLM - 2024;
   - Маракулин А.А., Дедкова А.В., Аминов Н.С., Федоров Д.А. СРАВНИТЕЛЬНЫЙ АНАЛИЗ МЕТОДОВ PEFT ДЛЯ ДООБУЧЕНИЯ БОЛЬШИХ ЯЗЫКОВЫХ МОДЕЛЕЙ - 2024;
   - Богданов М.А., Никифоров М.А., Аминов Н.С., Терещенко В.В., Федоров Д.А. АНАЛИЗ БОЛЬШИХ ДОКУМЕНТОВ ПРИ ПОМОЩИ БОЛЬШИХ ЯЗЫКОВЫХ МОДЕЛЕЙ - 2024;
2) 53 конференция ППС:
   - Мустафин Д.Э., Крылов М.М., Терещенко В.В.ХРАНЕНИЕ ГЕТЕРОГЕННЫХ ДАННЫХ ДЛЯ ИХ ПОСЛЕДУЮЩЕЙ ОБРАБОТКИ - 2023;
   - Богданов М.А., Терещенко В.В., Аминов Н.С.ПРЕДВАРИТЕЛЬНЫЙ АНАЛИЗ ДОКУМЕНТОВ УЧЕБНОГО ПРОЦЕССА ДЛЯ ПОСЛЕДУЮЩЕГО ИХ ТЕМАТИЧЕСКОГО МОДЕЛИРОВАНИЯ - 2023;
   - Синюков Л.В., Лаптев Е.И., Терещенко В.В.ОЦЕНКА ВЛИЯНИЯ ОБРАЗОВАТЕЛЬНЫХ ДИСЦИПЛИН НА РЕЗУЛЬТАТ КУРСОВЫХ РАБОТ С ИСПОЛЬЗОВАНИЕМ ТЕМАТИЧЕСКОГО МОДЕЛИРОВАНИЯ - 2023;
   - Дворников А.С., Стрижов Д.А., Аминов Н.С. РАЗРАБОТКА LLM-МОДЕЛИ КЛАССИФИКАЦИИ ТЕКСТА С ЦЕЛЬЮ АВТОМАТИЧЕСКОГО ОПРЕДЕЛЕНИЯ ДОКУМЕНТА, НАПИСАННОГО ИСКУССТВЕННЫМ ИНТЕЛЛЕКТОМ - 2023.

## Authors
[Tereshchenko Vladislav](https://github.com/Vl-Tershch)\
[Martsinkevich Viacheslav](https://github.com/slavamarcin)\
[Maxim Mischenko](https://github.com/L33tl)\
[Maxim Bogdanov](https://github.com/exPriceD)\
[Artem Dvornikov](https://github.com/DvornikovArtem)
[Egor Laptev](https://github.com/EgorLaptev)\
[Lev Sinyukov](https://github.com/MrL013)
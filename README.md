[![python](https://badgen.net/badge/python/3.9|3.10|3.11/blue?icon=python)](https://www.python.org/)
![ITMO](https://raw.githubusercontent.com/aimclub/open-source-ops/43bb283758b43d75ec1df0a6bb4ae3eb20066323/badges/ITMO_badge_rus.svg)
[![codecov](https://codecov.io/gh/LISA-ITMO/Edulytica/graph/badge.svg?token=L1I8M0KDS6)](https://codecov.io/gh/LISA-ITMO/Edulytica)

# Edulytica
![itmo](https://camo.githubusercontent.com/b9e4dd42874893b566fbc4c77daa19012408f5b5411a0625bb6b1a8e0212b39f/68747470733a2f2f69746d6f2e72752f66696c652f70616765732f3231332f6c6f676f5f6e615f706c6173686b655f727573736b69795f62656c79792e706e67)
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
- Added settings for CHhatGPT and GigaChat models. The functionality of splitting text into blocks has been implemented. A Yandex bot has been implemented to highlight the rules. Work with the database has been configured for the experiment of identifying requirements from regulatory documents using LLM.

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

## Authors
[Tereshchenko Vladislav](https://github.com/Vl-Tershch)\
[Martsinkevich Viacheslav](https://github.com/slavamarcin)\
[Maxim_Mischenko](https://github.com/L33tl)\
[Maxim_Bogdanov](https://github.com/exPriceD)\
[Artem_Dvornikov](https://github.com/DvornikovArtem)
[Egor_Laptev](https://github.com/EgorLaptev)\
[Lev_Sinyukov](https://github.com/MrL013)
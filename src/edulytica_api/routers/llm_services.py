# from src.edulytica_api.llms.llm_model import LLM, Conversation
from src.edulytica_api.models.auth import User
from fastapi import APIRouter, Depends, UploadFile
from src.edulytica_api.database import SessionLocal
from src.edulytica_api.auth.auth_bearer import access_token_auth
from src.edulytica_api.schemas import llm_schema
from typing import Annotated
from sqlalchemy.orm import Session
import json


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


DEFAULT_MESSAGE_TEMPLATE = "<|start_header_id|>{role}<|end_header_id|>{content}<|eot_id|>"
DEFAULT_RESPONSE_TEMPLATE = "<|begin_of_text|>"
SUMMARIZE_DEFAULT_SYSTEM_PROMPT = '''Ты опытный преподаватель университета, твоя задача делать суммаризацию научных текстов.
                           Суммаризируй часть научной работы, сохрани основные пункты, главные факты, термины и выводы.
                           Твой ответ должен быть кратким, содержать от 10 до 15 предложений.
                           Не добавляй в ответ ничего от себя, опирайся только на исходный текст.
                           Вот научный текст для суммаризации:'''

EXTRACT_DEFAULT_SYSTEM_PROMPT = '''Ты ассистент. Твоя задача - анализировать предоставленный текст и выявлять из него конкретные цели и задачи. Цели представляют собой конечные результаты, которых стремится достичь автор текста, а задачи - это конкретные действия или шаги, которые необходимо выполнить для достижения этих целей. Обрати внимание на следующие правила:
Не придумывай цели и задачи, которых нет в тексте: Тебе запрещено добавлять собственные интерпретации или домыслы. Твои выводы должны строго основываться на информации, представленной в тексте.
Отчет о невозможности выявления целей или задач: Если в тексте не удается определить ни цели, ни задачи, ты должен явно указать это в своем отчете. Напиши, что цели или задачи не были выявлены.
Разделение целей и задач: В тексте могут присутствовать только цели, только задачи, или и то, и другое. Важно различать эти категории и правильно их классифицировать.
Процесс выявления целей и задач должен быть систематичным и логичным. Прежде чем писать отчет, внимательно прочитай текст несколько раз, чтобы полностью понять его содержание и контекст. Используй ключевые слова и фразы, которые могут указывать на намерения или план действий.
Примеры: Цель: "Увеличить прибыль компании на 20% в следующем году." Задача: "Разработать и внедрить новую маркетинговую стратегию к концу текущего квартала."
Пример структурированного отчета: 
Цели:
Увеличить прибыль компании на 20% в следующем году. 
Задачи:
Разработать и внедрить новую маркетинговую стратегию к концу текущего квартала.
Провести обучение сотрудников новым методам продаж.
Отчет при отсутствии целей или задач:
Цели: не выявлены. 
Задачи: не выявлены.
Приступай к выполнению задачи, внимательно следуя этим инструкциям.'''

PURPOSE_DEFAULT_SYSTEM_PROMPT = '''Ты - ассистент преподавателя, который оценивает научную работу. Как и в любой работе, в тексте есть цели и задачи работы. Цель обычно одна, а задач - несколько. Твоя задача просмотреть и проанализировать весь текст работы и оценить соответствие текста поставленной цели и задачам. Тебе нужно проверить, соответствует ли текст поставленной цели и задачам. Если цель или задачи отсутствуют - так и напиши, что задачи не найдены. Также удели внимание источникам информации. Проанализируй их, на сколько они актуальны и применены в этой работе. \
\
Для этого следуй данному плану:\
    1. Сначала тебе будет дан текст работы ('all_text' или 'Текст работы'), где будет вся работа (весь текст для анализа), затем будут будут указаны цель и задачи ('goals' или 'Цели работы'), возможно методы исследования и гипотезы,  - определи эти части и проанализируй их;\
    2. Прочитай и проанализируй цель и задачи ('goals' или Цели работы), запомни их;\
    3. Прочитай и проанализируй весь текст ('all_text' или 'Текст работы'), запомни его;\
    4. Проанализируй соответствие цели и задач, а также гипотезы и методы исследования (при наличии) ('goals' или Цели работы), тексту работы ('all_text' или 'Текст работы');\
    5. Оцени соответствие текста поставленной цели и задачам. Делай оценку конкретной и объективной, с примерами (подробнее про это будет в правилах ниже);\
    6. Сделай подробный отчет.\
\
Обрати внимание на следующие правила: \
  1. Не придумывай цели и задачи, которых нет в тексте: Тебе запрещено добавлять собственные интерпретации или домыслы. Твои выводы должны строго основываться на информации, представленной в тексте (all_text и goals).\
  2. Если увидишь, что в тексте есть информация, которая не содержится в цели и задачах, выдели ее в отчете, как некорректные данные.\
  3. Поскольку задачи и цель могут формулироваться разными вариантами, учти небольшую погрешность в отклонениях.\
  4. Процесс определения соответствия текста цели и задачам должен быть систематичным и логичным. Прежде чем писать отчет, внимательно прочитай текст несколько раз, чтобы полностью понять его содержание и контекст. Используй ключевые слова и фразы, которые могут указывать на намерения или план действий.\
  5. Текст будет разбиваться по чанкам, поэтому анализировать нужно только после последнего чанка.\
  6. Последний чанк будет иметь строку: 'ПОСЛЕДНИЙ ЧАНК'.\
  7. Оценив текст на соответствие поставленной цели и задачам, укажи в отчете подробно, что сделано правильно, а что нет. В этой задаче постарайся как похвалить автора, так и дать какие-то рекомендации по исправлениям, если они требуются.\
  8. В последнем пункте отчета попробуй сделать численную оценку в процентах на соответствие цели и задачам и объясни, почему оценка именно такая.\
  9. Заметь, что в тексте написаны цель и задачи. Тебе нужно найти цель и задачи, затем прочитать и проанализировать весь текст и, после этого, сравнить текст на соответствие цели и задачам, которые присутствуют в тексте.\
  10. Важно! Не допускай повторений. Каждое из требований ты должен выполнить один раз. Например, не делай больше 1 раза численную оценку в процентах, это нужно сделать только 1 раз в конце отчета. Тоже самое и с другими пунктами, повторений быть не должно! Твой ответ должен быть последовательным и структурированным, а также логически выстроенным.'''

# purpose_llm = LLM('IlyaGusev/saiga_llama3_8b', 'slavamarcin/saiga_llama3_8b-qdora-4bit_purpose')
# summarize_llm = LLM('IlyaGusev/saiga_llama3_8b', 'slavamarcin/qdora')

llm_router = APIRouter(prefix="/llm")


@llm_router.post("/purpose")
def get_purpose(file: UploadFile, current_user: Annotated[User, Depends(access_token_auth)],
                db: Session = Depends(get_session)):
    def chunk_text(text, chunk_size, overlap):
        if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
            raise ValueError("Некорректные параметры: размер чанка должен быть положительным числом, "
                             "нахлёст должен быть неотрицательным числом и меньше размера чанка.")

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap

            if start >= text_length:
                break

        return chunks

    # def prepare_answer(all_text, goals):
    #     PROMPT_TEMPLATE = "Текст работы:\n{all_text}\n\nЦели работы:\n{goals}\n\n"
    #     combined_text = PROMPT_TEMPLATE.format(all_text=all_text, goals=goals)
    #     print(combined_text)
    #     chunks = chunk_text(combined_text, 8000, 0)
    #     purpose_conversation = Conversation()
    #     for i, chunk in enumerate(chunks):
    #         if i == len(chunks) - 1:
    #             chunk += 'ПОСЛЕДНИЙ ЧАНК'
    #
    #         purpose_conversation.add_user_message(chunk)
    #     prompt = purpose_conversation.get_prompt(purpose_llm.tokenizer)
    #
    #     return purpose_llm.generate(prompt)
    #
    # from src.edulytica_api.parser.Parser import get_structural_paragraphs
    # data = get_structural_paragraphs(file.file)
    # intro = " ".join(data['table_of_content'][0]['text'])
    # main_text = " ".join(data['other_text'])
    # extract_conversation = Conversation(message_template=DEFAULT_MESSAGE_TEMPLATE,
    #                                     response_template=DEFAULT_RESPONSE_TEMPLATE,
    #                                     system_prompt=EXTRACT_DEFAULT_SYSTEM_PROMPT)
    # extract_conversation.add_user_message(intro)
    # prompt = extract_conversation.get_prompt(purpose_llm.tokenizer)
    # output = purpose_llm.generate(prompt)
    # goals = output
    # result_data = prepare_answer(main_text, goals)
    #
    # res = {'goal': goals, 'result': result_data}
    #
    # return json.dumps(res)


@llm_router.post("/accordance")
def get_accordance():
    pass


@llm_router.post("/summary")
def get_summary(data: llm_schema.SummarizeData, current_user: Annotated[User, Depends(access_token_auth)],
                db: Session = Depends(get_session)):
    # text = data.text
    # result_data = []
    # for inpt in text:
    #     summarize_conversation = Conversation(message_template = DEFAULT_MESSAGE_TEMPLATE, response_template = DEFAULT_RESPONSE_TEMPLATE, system_prompt = SUMMARIZE_DEFAULT_SYSTEM_PROMPT)
    #     summarize_conversation.add_user_message(inpt)
    #     prompt = summarize_conversation.get_prompt(summarize_llm.tokenizer)
    #     output = summarize_llm.generate(prompt)
    #     result_data.append([output])
    # res = {'result': result_data}
    # return json.dumps(res)
    pass

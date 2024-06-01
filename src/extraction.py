# from peft import PeftModel, PeftConfig
from google.colab import drive
import os
import json
import pprint
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

drive.mount('/content/drive')

torch.cuda.is_available()

train_data = []

for file in os.listdir("drive/MyDrive/compare"):
    try:
        outfile = open('drive/MyDrive/compare/' + file, encoding="utf-8")
        data = json.load(outfile)
        train_data.append(data)
    except Exception as e:
        pprint.pp(e)


MODEL_NAME = "IlyaGusev/saiga_llama3_8b"
# config = PeftConfig.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    # config.base_model_name_or_path,
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
)
# model = PeftModel.from_pretrained(
#     model,
#     MODEL_NAME,
#     torch_dtype=torch.float16
# )
model.eval()

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
generation_config = GenerationConfig.from_pretrained(MODEL_NAME)
print(generation_config)

def generate(model, tokenizer, prompt, generation_config):
    data = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    data = {k: v.to(model.device) for k, v in data.items()}
    output_ids = model.generate(
        **data,
        generation_config=generation_config
    )[0]
    output_ids = output_ids[len(data["input_ids"][0]):]
    output = tokenizer.decode(output_ids, skip_special_tokens=True)
    return output.strip()

DEFAULT_MESSAGE_TEMPLATE = "<|im_start|>{role}\n{content}"
DEFAULT_RESPONSE_TEMPLATE = "<|im_end|>"
DEFAULT_SYSTEM_PROMPT = "Ты ассистент. Твоя задача - анализировать предоставленный текст и выявлять из него конкретные цели и задачи. Цели представляют собой конечные результаты, которых стремится достичь автор текста, а задачи - это конкретные действия или шаги, которые необходимо выполнить для достижения этих целей. Обрати внимание на следующие правила: \
1. Не придумывай цели и задачи, которых нет в тексте: Тебе запрещено добавлять собственные интерпретации или домыслы. Твои выводы должны строго основываться на информации, предоставленной в тексте.\
2. Отчет о невозможности выявления целей или задач: Если в тексте не удается определить ни цели, ни задачи, ты должен явно указать это в своем отчете. Напиши, что цели или задачи не были выявлены.\
3. Разделение целей и задач: В тексте могут присутствовать только цели, только задачи, или и то, и другое. Важно различать эти категории и правильно их классифицировать.\
4. Процесс выявления целей и задач должен быть систематичным и логичным. Прежде чем писать отчет, внимательно прочитай текст несколько раз, чтобы полностью понять его содержание и контекст. Используй ключевые слова и фразы, которые могут указывать на намерения или план действий.\
5. Текст будет разбиваться по чанкам, поэтому анализировать нужно только после последнего чанка\
6. Последний чанк будет иметь строку: 'ПОСЛЕДНИЙ ЧАНК'\
7. Не пиши в начале 'assistant'. В выводе должны быть только цели и задачи\
\
Примеры:\
    Цель: Увеличить прибыль компании на 20% в следующем году.\
    Задача: Разработать и внедрить новую маркетинговую стратегию к концу текущего квартала.\
\
Пример структурированного отчета:\
    Цели:\
        Увеличить прибыль компании на 20% в следующем году.\
    Задачи:\
        Разработать и внедрить новую маркетинговую стратегию к концу текущего квартала.\
        Провести обучение сотрудников новым методам продаж.\
\
Отчет при отсутствии целей или задач:\
Цели: не выявлены.\
Задачи: не выявлены.\
Приступай к выполнению задачи, внимательно следуя этим инструкциям."

class Conversation:
    def __init__(
        self,
        message_template=DEFAULT_MESSAGE_TEMPLATE,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        response_template=DEFAULT_RESPONSE_TEMPLATE
    ):
        self.message_template = message_template
        self.response_template = response_template
        self.messages = [{
            "role": "system",
            "content": system_prompt
        }]

    def add_user_message(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })

    def add_bot_message(self, message):
        self.messages.append({
            "role": "bot",
            "content": message
        })

    def get_prompt(self, tokenizer):
        final_text = ""
        for message in self.messages:
            message_text = self.message_template.format(**message)
            final_text += message_text
        final_text += DEFAULT_RESPONSE_TEMPLATE
        return final_text.strip()

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

def prepare_answer(inpt):

    output = ''

    conversation = Conversation()
    prompt = conversation.get_prompt(tokenizer)

    conversation.add_user_message(inpt)

    output = generate(model, tokenizer, prompt, generation_config)

    return output

for i in range(421, 633):
    try:
      out = train_data[i]
      text = ' '.join(out['text'])
      generated_data = prepare_answer(text)
      out['goals'] = generated_data

      with open(f'drive/MyDrive/compare_modif/bachelor_{i+1}.json', 'w+', encoding='utf-8') as result_file:
        json.dump(out, result_file, indent=4, ensure_ascii=False)

    except Exception as e:
        raise e
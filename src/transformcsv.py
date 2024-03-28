import pandas as pd
from nltk.corpus import stopwords
from pymystem3 import Mystem

def textTransform(text):
    mystem = Mystem()

    lemmatized_text = mystem.lemmatize(text.lower())
    tokens = [word for word in lemmatized_text if word.isalpha()]  # Оставляем только буквенные токены

    stop_words = set(stopwords.words('russian'))
    filtered_tokens = [word for word in tokens if word not in stop_words]

    filtered_text = " ".join(filtered_tokens)
    print(filtered_text)
    return filtered_text

def process_text_column(file_name):
    df = pd.read_csv(file_name)

    df['text'] = df['text'].apply(textTransform)

    df.to_csv(file_name, index=False)

    print(f"Файл {file_name} обновлен")

process_text_column('example.csv')

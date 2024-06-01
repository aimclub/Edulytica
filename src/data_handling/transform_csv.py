import pandas as pd
from nltk.corpus import stopwords
from pymystem3 import Mystem
import nltk
nltk.download('stopwords')
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def remove_empty_rows(file_name):
    df = pd.read_csv(file_name)
    df = df.dropna(subset=['text'])
    df.to_csv(file_name, index=False)

def remove_urlsm(file_name):
    df = pd.read_csv(file_name)

    def remove_urls(text):
        return re.sub(r'http\S+', '', text)

    df['text'] = df['text'].apply(remove_urls)

    df.to_csv(file_name, index=False)

def remove_punctuationm(file_name):
    df = pd.read_csv(file_name)
    def remove_punctuation(text):
        return re.sub(r'[^\w\s]', '', text)
    df['text'] = df['text'].apply(remove_punctuation)
    df.to_csv(file_name, index=False)

def textTransform(text):
    mystem = Mystem()

    lemmatized_text = mystem.lemmatize(text.lower())
    tokens = [word for word in lemmatized_text if word.isalpha()]

    stop_words = set(stopwords.words('russian'))

    filtered_tokens = [word for word in tokens if word not in stop_words]

    filtered_text = " ".join(filtered_tokens)
    return filtered_text

def process_text_column(file_name):
    df = pd.read_csv(file_name)

    df['text'] = df['text'].apply(textTransform)

    df.to_csv(file_name, index=False)

    print(f"Файл {file_name} обновлен")

def lowercase_text(file_name):
    df = pd.read_csv(file_name)

    df['text'] = df['text'].str.lower()
    df.to_csv(file_name, index=False)

def apply_tfidf_to_column(file_name):
    df = pd.read_csv(file_name)

    tfidf_vectorizer = TfidfVectorizer()

    tfidf_matrix = tfidf_vectorizer.fit_transform(df['text'])

    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names_out())

    result_df = pd.concat([df, tfidf_df], axis=1)

    result_file_name = file_name.replace('.csv', '_tfidf.csv')
    result_df.to_csv(result_file_name, index=False)

    print("Результаты TF-IDF сохранены в файле", result_file_name)


def visualize_tfidf_from_csv(file_name):
    df = pd.read_csv(file_name)

    word_tfidf = df.drop(columns=['text']).mean().to_dict()

    wordcloud = WordCloud(width=3200, height=1600, background_color='white').generate_from_frequencies(word_tfidf)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

file_name = 'test.csv'

if __name__ == '__main__':
    remove_empty_rows(file_name)
    remove_urlsm(file_name)
    remove_empty_rows(file_name)
    lowercase_text(file_name)
    remove_empty_rows(file_name)
    remove_punctuationm(file_name)
    remove_empty_rows(file_name)
    process_text_column(file_name)
    remove_empty_rows(file_name)
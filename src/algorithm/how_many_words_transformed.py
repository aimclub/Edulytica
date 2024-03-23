import unicodedata
import nltk
from nltk.corpus import stopwords
stop_words = stopwords.words('russian')

def transformed_words(text1, text2):

    sentence1 = text1
    sentence2 = text2

    punctuation_marks = ['!', ',', '(', ')', ':', '-', '?', '.', '..', '...']

    tokens = []

    for sentence in sentence1, sentence2:
        sen = sentence.lower().split()
        s_words = []
        for s in sen:
            if s not in stop_words:
                s_new = ''
                for p in s:
                    if p not in punctuation_marks:
                        s_new += p
                s_words.append(s_new)
        tokens.append(s_words)

    #критерий 1: кол-во добавленных слов
    #count1 = len(tokens[1])-len(tokens[0])
    #if count1 < 0:
    #    count1 = 0

    count1 = 0
    for s2 in tokens[1]:
        if s2 not in tokens[0]:
            count1 += 1
    if count1 <= len(tokens[0]):
        c1 = (count1/len(tokens[1])%0.5)
    else:
        c1 = 0.5
    #print('кол-во добавленных слов:', count1)
    #print(unicodedata.lookup("GREEK SMALL LETTER THETA"), '=', c1)

    #критерий 2: кол-во удалённых слов
    count2 = 0
    for s1 in tokens[0]:
        if s1 not in tokens[1]:
            count2 += 1
    if count2 <= len(tokens[0]):
        c2 = (count2/len(tokens[0])%0.5)
    else:
        c2 = 0.5
    #print('кол-во удалённых слов:', count2)
    #print(unicodedata.lookup("GREEK SMALL LETTER MU"), '=', c2)

    #print('исходное предложение было изменено на', round((c1+c2)/2*100, 2), '%')
    #return round((count1 + count2)/2), round((c1+c2)/2*100, 2)
    return round((c1+c2)*100, 2)


#t1 = input()
#t2 = input()
#print(transformed_words(t1, t2))
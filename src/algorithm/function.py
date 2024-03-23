from nltk.corpus import stopwords
stop_words = stopwords.words('russian')

def transformed_words(text1, text2):

    sentence1 = text1
    sentence2 = text2

    punctuation_marks = ['!', ',', '(', ')', ':', '-', '?', '.', '[', ']', '{', '}']

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
    count1 = 0
    for s2 in tokens[1]:
        if s2 not in tokens[0]:
            count1 += 1
    if count1 <= len(tokens[1]):
        c1 = (count1/len(tokens[1])%0.5)
    else:
        c1 = 0.5

    #критерий 2: кол-во удалённых слов
    count2 = 0
    for s1 in tokens[0]:
        if s1 not in tokens[1]:
            count2 += 1
    if count2 <= len(tokens[0]):
        c2 = (count2/len(tokens[0])%0.5)
    else:
        c2 = 0.5

    return round((c1+c2)*100, 2)
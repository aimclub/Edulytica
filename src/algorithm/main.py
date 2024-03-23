from function import transformed_words

texts = []
n = 5
slova = ['исходный текст', 'изменённый AI текст', 'изменённый человеком текст (1)', 'изменённый человеком текст (2)',
         'изменённый человеком текст (3)']
for i in range(n):
    print(f'Введите {slova[i]}:')
    s = []
    s_ = str(input())
    while (s_ != "stop"):
        if s_ != '':
            s += [s_ + '. ']
        s_ = str(input())
    texts.append(''.join(s))

puncuation_marks = [',', '.', ':', '(', ')', '[', ']', '{', '}', '?', '!', '"', "'", ';']
for i in range(n):
    t = texts[i]
    new_t = t
    for k in puncuation_marks:
        pr_t = t.split(sep = k)
        t = ''.join(pr_t)
        new_t = t
    texts[i] = new_t

print(f'Слов в первом тексте 1: {len(texts[0].split())}')
print(f'Слов во втором тексте 2: {len(texts[1].split())}')
print(f'Слов в третьем тексте 3: {len(texts[2].split())}')
print(f'Слов в четвёртом тексте 4: {len(texts[3].split())}')
print(f'Слов в пятом тексте 5: {len(texts[4].split())}')
print('---------------------------------------------------------------')
print(f'Процент изменений второго текста по сравнению с первым 1 -> 2: {transformed_words(texts[0], texts[1])}')
print(f'Процент изменений третьего текста по сравнению с первым 1 -> 3: {transformed_words(texts[0], texts[2])}')
print(f'Процент изменений четвёртого текста по сравнению с первым 1 -> 4: {transformed_words(texts[0], texts[3])}')
print(f'Процент изменений пятого текста по сравнению с первым 1 -> 5: {transformed_words(texts[0], texts[4])}')
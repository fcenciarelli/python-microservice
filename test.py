words_remove = []
with open('remove list.txt', 'r') as f:
    for line in f:
        b = line.strip()
        a= b.split('\n')
        words_remove.append(a[0])
    print(words_remove)
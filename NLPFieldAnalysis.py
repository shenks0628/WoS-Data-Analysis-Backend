import os
import glob
import requests
import threading
from NLP import model, tokenizer
import torch
from sklearn.metrics.pairwise import cosine_similarity

lock = threading.Lock()

parent = dict()
size = dict()

def find(x):
    global parent
    if x == parent[x]:
        return x
    parent[x] = find(parent[x])
    return parent[x]

def union(x, y):
    global parent, size
    x = find(x)
    y = find(y)
    if x != y:
        if size[x] < size[y]:
            x, y = y, x
        parent[y] = x
        size[x] += size[y]

def NLPonFieldByYear(files, filesToAnalyze, start, end, threshold):
    global lock, parent, size
    count = 0
    conditionCount = 0
    field_count = dict()
    field_list = list()
    for file in files:
        fileName = file.get('name')
        if fileName not in filesToAnalyze:
            continue
        fileURL = file.get('url')
        response = requests.get(fileURL)
        response.encoding = 'utf-8'
        content = response.text
        field = ""
        insideSC = False
        for line in content.split('\n'):
            if line.startswith("TI "):
                count += 1
            elif line.startswith("SC "):
                insideSC = True
                field += line[3:].strip()
            elif line.startswith("   ") and insideSC:
                field += line[3:].strip()
            elif line.startswith("PY "):
                year = int(line[3:].strip())
            else:
                if insideSC:
                    if year >= start and year <= end:
                        if field != "":
                            conditionCount += 1
                            field = field.split(';')
                            for word in field:
                                word = word.strip().lower()
                                if field_count.get(word, False):
                                    field_count[word] += 1
                                else:
                                    field_count[word] = 1
                    field = ""
                    insideSC = False
    temp = sorted(field_count.items(), key=lambda x: x[1], reverse=True)
    field_list = [item[0] for item in temp]
    print(len(field_list))
    minimumLength = min(len(field_list), 1000)
    field_list = field_list[:minimumLength]
    print(field_list)
    field_tokens = tokenizer(field_list, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**field_tokens)
    embeddings = outputs.last_hidden_state.squeeze(0)
    embeddings = torch.mean(embeddings, dim=1)
    similarity = cosine_similarity(embeddings)
    print(similarity)
    similarityThreshold = 0.95
    lock.acquire()
    # disjoint set union find
    parent = dict()
    size = dict()
    for field in field_list:
        parent[field] = field
        size[field] = 1
    for i in range(len(field_list)):
        for j in range(i + 1, len(field_list)):
            if similarity[i, j] >= similarityThreshold:
                union(field_list[i], field_list[j])
    for field in field_list:
        find(field)
    for field in field_list:
        if parent[field] != field:
            field_count[parent[field]] += field_count[field]
            field_count.pop(field)
    lock.release()
    sorted_fields = sorted(field_count.items(), key=lambda x: x[1], reverse=True)
    results = []
    cnt = 0
    for field in sorted_fields:
        if field[1] < threshold:
            break
        results.append({
            'field': field[0],
            'count': field[1]
        })
        cnt += 1
        if cnt >= 100:
            break
    return count, conditionCount, results

def NLPonFieldEachYear(files, filesToAnalyze, target):
    global lock, parent, size

    # first pass to get the fields
    field_count = dict()
    field_list = list()
    fileContent = dict()
    fileNames = list()
    for file in files:
        fileName = file.get('name')
        if fileName not in filesToAnalyze:
            continue
        fileURL = file.get('url')
        response = requests.get(fileURL)
        response.encoding = 'utf-8'
        content = response.text
        fileNames.append(fileName)
        fileContent[fileName] = content
        field = ""
        insideSC = False
        for line in content.split('\n'):
            if line.startswith("SC "):
                insideSC = True
                field += line[3:].strip()
            elif line.startswith("   ") and insideSC:
                field += line[3:].strip()
            else:
                if field != "":
                    field = field.lower()
                    field = field.split(';')
                    for word in field:
                        word = word.strip().lower()
                        if field_count.get(word, False):
                            field_count[word] += 1
                        else:
                            field_count[word] = 1
                field = ""
                insideSC = False
    
    # get the top 1000 fields
    temp = sorted(field_count.items(), key=lambda x: x[1], reverse=True)
    field_list = [item[0] for item in temp]
    print(len(field_list))
    minimumLength = min(len(field_list), 1000)
    field_list = field_list[:minimumLength]

    # put the target field in the list
    target = target.lower()
    if target not in field_list:
        field_list.append(target)
        field_count[target] = 0
    print(field_list)

    # get the tokens, embeddings, and similarity
    field_tokens = tokenizer(field_list, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**field_tokens)
    embeddings = outputs.last_hidden_state.squeeze(0)
    embeddings = torch.mean(embeddings, dim=1)
    similarity = cosine_similarity(embeddings)
    print(similarity)
    similarityThreshold = 0.95

    # acquire lock
    lock.acquire()

    # disjoint set union find
    parent = dict()
    size = dict()
    for field in field_list:
        parent[field] = field
        size[field] = 1
    for i in range(len(field_list)):
        for j in range(i + 1, len(field_list)):
            if similarity[i, j] >= similarityThreshold:
                union(field_list[i], field_list[j])
    for field in field_list:
        find(field)

    # second pass to get the year count
    count = 0
    conditionCount = 0
    year_count = dict()
    for fileName in fileNames:
        content = fileContent[fileName]
        field = ""
        insideSC = False
        for line in content.split('\n'):
            if line.startswith("TI "):
                count += 1
            elif line.startswith("SC "):
                insideSC = True
                field += line[3:].strip()
            elif line.startswith("   ") and insideSC:
                field += line[3:].strip()
            elif line.startswith("PY "):
                year = int(line[3:].strip())
            else:
                if insideSC:
                    if field != "":
                        field = field.lower()
                        field = field.split(';')
                        for word in field:
                            word = word.strip().lower()
                            if parent.get(word, False):
                                if parent[word] == parent[target]:
                                    conditionCount += 1
                                    if year_count.get(year, False):
                                        year_count[year] += 1
                                    else:
                                        year_count[year] = 1
                    field = ""
                    insideSC = False

    # release lock
    lock.release()

    # sort the year count and return the results
    sorted_year = sorted(year_count.items(), key=lambda x: x[0], reverse=False)
    print(sorted_year)
    results = []
    for year in sorted_year:
        results.append({
            'year': year[0],
            'count': year[1]
        })
    start = min(year_count.keys())
    end = max(year_count.keys())
    return count, conditionCount, start, end, results

def NLPonFieldByOccurence(files, filesToAnalyze, threshold):
    global lock, parent, size
    titleCount = 0
    field_count = dict()
    field_list = list()
    for file in files:
        fileName = file.get('name')
        if fileName not in filesToAnalyze:
            continue
        fileURL = file.get('url')
        response = requests.get(fileURL)
        response.encoding = 'utf-8'
        content = response.text
        field = ""
        insideSC = False
        for line in content.split('\n'):
            if line.startswith("TI "):
                titleCount += 1
            elif line.startswith("SC "):
                insideSC = True
                field += line[3:].strip()
            elif line.startswith("   ") and insideSC:
                field += line[3:].strip()
            else:
                if field != "":
                    field = field.lower()
                    field = field.split(';')
                    for word in field:
                        word = word.strip().lower()
                        if field_count.get(word, False):
                            field_count[word] += 1
                        else:
                            field_count[word] = 1
                field = ""
                insideSC = False
    temp = sorted(field_count.items(), key=lambda x: x[1], reverse=True)
    field_list = [item[0] for item in temp]
    print(len(field_list))
    minimumLength = min(len(field_list), 1000)
    field_list = field_list[:minimumLength]
    print(field_list)
    field_tokens = tokenizer(field_list, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**field_tokens)
    embeddings = outputs.last_hidden_state.squeeze(0)
    embeddings = torch.mean(embeddings, dim=1)
    similarity = cosine_similarity(embeddings)
    print(similarity)
    similarityThreshold = 0.95
    lock.acquire()
    # disjoint set union find
    parent = dict()
    size = dict()
    for field in field_list:
        parent[field] = field
        size[field] = 1
    for i in range(len(field_list)):
        for j in range(i + 1, len(field_list)):
            if similarity[i, j] >= similarityThreshold:
                union(field_list[i], field_list[j])
    for field in field_list:
        find(field)
    for field in field_list:
        if parent[field] != field:
            field_count[parent[field]] += field_count[field]
            field_count.pop(field)
    lock.release()
    sorted_fields = sorted(field_count.items(), key=lambda x: x[1], reverse=True)
    results = []
    cnt = 0
    for field in sorted_fields:
        if field[1] < threshold:
            break
        results.append({
            'field': field[0],
            'count': field[1]
        })
        cnt += 1
        if cnt >= 100:
            break
    return titleCount, results
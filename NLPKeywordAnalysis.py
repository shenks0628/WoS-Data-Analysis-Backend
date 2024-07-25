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

def NLPonKeywordByYear(files, filesToAnalyze, start, end, threshold):
    global lock, parent, size
    count = 0
    conditionCount = 0
    keyword_count = dict()
    keyword_list = list()
    for file in files:
        fileName = file.get('name')
        if fileName not in filesToAnalyze:
            continue
        fileURL = file.get('url')
        response = requests.get(fileURL)
        response.encoding = 'utf-8'
        content = response.text
        keyword = ""
        insideDE = False
        for line in content.split('\n'):
            if line.startswith("TI "):
                count += 1
            elif line.startswith("DE "):
                insideDE = True
                keyword += line[3:].strip()
            elif line.startswith("   ") and insideDE:
                keyword += line[3:].strip()
            elif line.startswith("PY "):
                year = int(line[3:].strip())
                if year >= start and year <= end:
                    if keyword != "":
                        conditionCount += 1
                        keyword = keyword.split(';')
                        for word in keyword:
                            word = word.strip().lower()
                            if keyword_count.get(word, False):
                                keyword_count[word] += 1
                            else:
                                keyword_count[word] = 1
                keyword = ""
                insideDE = False
            else:
                insideDE = False
    temp = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
    keyword_list = [item[0] for item in temp]
    print(len(keyword_list))
    minimumLength = min(len(keyword_list), 1000)
    keyword_list = keyword_list[:minimumLength]
    print(keyword_list)
    keyword_tokens = tokenizer(keyword_list, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**keyword_tokens)
    embeddings = outputs.last_hidden_state.squeeze(0)
    embeddings = torch.mean(embeddings, dim=1)
    similarity = cosine_similarity(embeddings)
    print(similarity)
    similarityThreshold = 0.95
    lock.acquire()
    # disjoint set union find
    parent = dict()
    size = dict()
    for keyword in keyword_list:
        parent[keyword] = keyword
        size[keyword] = 1
    for i in range(len(keyword_list)):
        for j in range(i + 1, len(keyword_list)):
            if similarity[i, j] >= similarityThreshold:
                union(keyword_list[i], keyword_list[j])
    for keyword in keyword_list:
        find(keyword)
    for keyword in keyword_list:
        if parent[keyword] == "autonomous vehicles":
            print(keyword)
        if parent[keyword] != keyword:
            keyword_count[parent[keyword]] += keyword_count[keyword]
            keyword_count.pop(keyword)
    lock.release()
    sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
    results = []
    cnt = 0
    for keyword in sorted_keywords:
        if keyword[1] < threshold:
            break
        results.append({
            'keyword': keyword[0],
            'count': keyword[1]
        })
        cnt += 1
        if cnt >= 100:
            break
    return count, conditionCount, results

def NLPonKeywordEachYear(files, filesToAnalyze, target):
    global lock, parent, size

    # first pass to get the keywords
    keyword_count = dict()
    keyword_list = list()
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
        keyword = ""
        insideDE = False
        for line in content.split('\n'):
            if line.startswith("DE "):
                insideDE = True
                keyword += line[3:].strip()
            elif line.startswith("   ") and insideDE:
                keyword += line[3:].strip()
            else:
                if keyword != "":
                    keyword = keyword.lower()
                    keyword = keyword.split(';')
                    for word in keyword:
                        word = word.strip().lower()
                        if keyword_count.get(word, False):
                            keyword_count[word] += 1
                        else:
                            keyword_count[word] = 1
                keyword = ""
                insideDE = False
    
    # get the top 1000 keywords
    temp = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
    keyword_list = [item[0] for item in temp]
    print(len(keyword_list))
    minimumLength = min(len(keyword_list), 1000)
    keyword_list = keyword_list[:minimumLength]

    # put the target keyword in the list
    target = target.lower()
    if target not in keyword_list:
        keyword_list.append(target)
        keyword_count[target] = 0
    print(keyword_list)

    # get the tokens, embeddings, and similarity
    keyword_tokens = tokenizer(keyword_list, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**keyword_tokens)
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
    for keyword in keyword_list:
        parent[keyword] = keyword
        size[keyword] = 1
    for i in range(len(keyword_list)):
        for j in range(i + 1, len(keyword_list)):
            if similarity[i, j] >= similarityThreshold:
                union(keyword_list[i], keyword_list[j])
    for keyword in keyword_list:
        find(keyword)

    # second pass to get the year count
    count = 0
    conditionCount = 0
    year_count = dict()
    for fileName in fileNames:
        content = fileContent[fileName]
        keyword = ""
        insideDE = False
        for line in content.split('\n'):
            if line.startswith("TI "):
                count += 1
            elif line.startswith("DE "):
                insideDE = True
                keyword += line[3:].strip()
            elif line.startswith("   ") and insideDE:
                keyword += line[3:].strip()
            elif line.startswith("PY "):
                year = int(line[3:].strip())
                if keyword != "":
                    keyword = keyword.lower()
                    keyword = keyword.split(';')
                    for word in keyword:
                        word = word.strip().lower()
                        if parent.get(word, False):
                            if parent[word] == parent[target]:
                                conditionCount += 1
                                if year_count.get(year, False):
                                    year_count[year] += 1
                                else:
                                    year_count[year] = 1
                keyword = ""
                insideDE = False
            else:
                insideDE = False

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

def NLPonKeywordByOccurence(files, filesToAnalyze, threshold):
    global lock, parent, size
    titleCount = 0
    keyword_count = dict()
    keyword_list = list()
    for file in files:
        fileName = file.get('name')
        if fileName not in filesToAnalyze:
            continue
        fileURL = file.get('url')
        response = requests.get(fileURL)
        response.encoding = 'utf-8'
        content = response.text
        keyword = ""
        insideDE = False
        for line in content.split('\n'):
            if line.startswith("TI "):
                titleCount += 1
            elif line.startswith("DE "):
                insideDE = True
                keyword += line[3:].strip()
            elif line.startswith("   ") and insideDE:
                keyword += line[3:].strip()
            else:
                if keyword != "":
                    keyword = keyword.lower()
                    keyword = keyword.split(';')
                    for word in keyword:
                        word = word.strip().lower()
                        if keyword_count.get(word, False):
                            keyword_count[word] += 1
                        else:
                            keyword_count[word] = 1
                keyword = ""
                insideDE = False
    temp = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
    keyword_list = [item[0] for item in temp]
    print(len(keyword_list))
    minimumLength = min(len(keyword_list), 1000)
    keyword_list = keyword_list[:minimumLength]
    print(keyword_list)
    keyword_tokens = tokenizer(keyword_list, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**keyword_tokens)
    embeddings = outputs.last_hidden_state.squeeze(0)
    embeddings = torch.mean(embeddings, dim=1)
    similarity = cosine_similarity(embeddings)
    print(similarity)
    similarityThreshold = 0.95
    lock.acquire()
    # disjoint set union find
    parent = dict()
    size = dict()
    for keyword in keyword_list:
        parent[keyword] = keyword
        size[keyword] = 1
    for i in range(len(keyword_list)):
        for j in range(i + 1, len(keyword_list)):
            if similarity[i, j] >= similarityThreshold:
                union(keyword_list[i], keyword_list[j])
    for keyword in keyword_list:
        find(keyword)
    for keyword in keyword_list:
        if parent[keyword] != keyword:
            keyword_count[parent[keyword]] += keyword_count[keyword]
            keyword_count.pop(keyword)
    lock.release()
    sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
    results = []
    cnt = 0
    for keyword in sorted_keywords:
        if keyword[1] < threshold:
            break
        results.append({
            'keyword': keyword[0],
            'count': keyword[1]
        })
        cnt += 1
        if cnt >= 100:
            break
    return titleCount, results
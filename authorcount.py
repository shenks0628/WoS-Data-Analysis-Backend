import os
import glob
import requests

def author(files, filesToAnalyze, start, end, threshold):
    count = 0
    conditionCount = 0
    author_count = dict()
    for file in files:
        fileName = file.get('name')
        if fileName not in filesToAnalyze:
            continue
        fileURL = file.get('url')
        response = requests.get(fileURL)
        response.encoding = 'utf-8'
        content = response.text
        author = ""
        insideAF = False
        for line in content.split('\n'):
            if line.startswith("TI "):
                count+=1
                insideAF = False
            elif line.startswith("AF "):
                insideAF = True
                author += line[3:].strip()
                author += ';'
            elif line.startswith("   ") and insideAF:
                author += line[3:].strip()
                author += ';'
            elif line.startswith("PY "):
                year = int(line[3:].strip())
                if year >= start and year <= end:
                    if author != "":
                        conditionCount+=1
                        author = author.strip(';')
                        author = author.split(';')
                        for word in author:
                            #word = word.strip().lower()
                            if author_count.get(word, False):
                                author_count[word] += 1
                            else:
                                author_count[word] = 1
                author = ""
                insideAF = False
            else:
                insideAF = False
    sorted_authors = sorted(author_count.items(), key=lambda x: x[1], reverse=True)
    results = []
    cnt = 0
    for author in sorted_authors:
        if author[1] < threshold:
            break
        results.append({
            'author': author[0],
            'count': author[1]
        })
        cnt += 1
        if cnt >= 100:
            break
    return count, conditionCount, results
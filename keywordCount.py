import os
import glob
import requests

def get_keywords(files):
    keyword_count = dict()
    for file in files:
        fileURL = file.get('url')
        response = requests.get(fileURL)
        response.encoding = 'utf-8'
        content = response.text
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
                    keyword = keyword.split(';')
                    for word in keyword:
                        word = word.strip().lower()
                        if keyword_count.get(word, False):
                            keyword_count[word] += 1
                        else:
                            keyword_count[word] = 1
                keyword = ""
                insideDE = False
    sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_keywords

def year(files, filesToAnalyze, start, end):
    keyword_count = dict()
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
            if line.startswith("DE "):
                insideDE = True
                keyword += line[3:].strip()
            elif line.startswith("   ") and insideDE:
                keyword += line[3:].strip()
            elif line.startswith("PY "):
                year = int(line[3:].strip())
                if year >= start and year <= end:
                    if keyword != "":
                        keyword = keyword.split(';')
                        for word in keyword:
                            word = word.strip().lower()
                            if keyword_count.get(word, False):
                                keyword_count[word] += 1
                            else:
                                keyword_count[word] = 1
                keyword = ""
                insideDE = False
    sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
    results = []
    cnt = 0
    for keyword in sorted_keywords:
        results.append({
            'keyword': keyword[0],
            'count': keyword[1]
        })
        cnt += 1
        if cnt >= 100:
            break
    return results
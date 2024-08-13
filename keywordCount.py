import os
import glob
import requests

def year(files, filesToAnalyze, start, end, threshold):
    count = 0
    conditionCount = 0
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

def keywordEachYear(files, filesToAnalyze, target):
    count = 0
    conditionCount = 0
    year_count = dict()
    for file in files:
        fileName = file.get('name')
        if fileName not in filesToAnalyze:
            continue
        fileURL = file.get('url')
        response = requests.get(fileURL)
        response.encoding = 'utf-8'
        content = response.text
        target = target.lower()
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
                        if target == word.strip().lower():
                            conditionCount += 1
                            if year_count.get(year, False):
                                year_count[year] += 1
                            else:
                                year_count[year] = 1
                keyword = ""
                insideDE = False
            else:
                insideDE = False
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

def keywordOccurence(files, filesToAnalyze, threshold):
    keyword_count = dict()
    titleCount = 0
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
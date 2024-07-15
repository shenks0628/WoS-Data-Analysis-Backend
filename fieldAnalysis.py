import os
import glob
import requests
def fieldAnalysis(files, filesToAnalyze, start, end):
    count = 0
    conditionCount = 0
    fieldAnalysis_count = dict()
    for file in files:
        fileName = file.get('name')
        if fileName not in filesToAnalyze:
            continue
        fileURL = file.get('url')
        response = requests.get(fileURL)
        response.encoding = 'utf-8'
        content = response.text
        fieldAnalysis = ""
        insideSC = False
        for line in content.split('\n'):
            if line.startswith("TI "):
                count += 1
            elif line.startswith("SC "):
                insideSC = True
                fieldAnalysis += line[3:].strip()
                fieldAnalysis += ';'
            elif line.startswith("   ") and insideSC:
                fieldAnalysis += line[3:].strip()
                fieldAnalysis += ';'
            elif line.startswith("PY "):
                year = int(line[3:].strip())
                insideSC = False
            else:
                if insideSC:
                    if year >= start and year <= end:
                        if fieldAnalysis != "":
                            conditionCount += 1
                            fieldAnalysis = fieldAnalysis.split(';')
                            for word in fieldAnalysis:
                                word = word.strip().lower()
                                if fieldAnalysis_count.get(word, False):
                                    fieldAnalysis_count[word] += 1
                                else:
                                    fieldAnalysis_count[word] = 1
                    fieldAnalysis = ""
                    insideSC = False
    sorted_fieldAnalysis = sorted(fieldAnalysis_count.items(), key=lambda x: x[1], reverse=True)
    results = []
    cnt = 0
    for fieldAnalysis in sorted_fieldAnalysis:
        results.append({
            'fieldAnalysis': fieldAnalysis[0],
            'count': fieldAnalysis[1]
        })
        cnt += 1
        if cnt >= 100:
            break
    return count, conditionCount, results
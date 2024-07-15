import os
import glob
import requests

def fieldAnalysisyear(files, filesToAnalyze, start, end):
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
            if line.startswith("SC "):
                insideSC = True
                fieldAnalysis += line[3:].strip()
            elif line.startswith("   ") and insideSC:
                fieldAnalysis += line[3:].strip()
            elif line.startswith("PY "):
                year = int(line[3:].strip())
                if year >= start and year <= end:
                    if fieldAnalysis != "":
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
            'author': fieldAnalysis[0],
            'count': fieldAnalysis[1]
        })
        cnt += 1
        if cnt >= 100:
            break
    return results
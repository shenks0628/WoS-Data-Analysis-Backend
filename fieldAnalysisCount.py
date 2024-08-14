import os
import glob
import requests
def fieldEachYear(files, filesToAnalyze, start, end, threshold):
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
            elif line.startswith("   ") and insideSC:
                fieldAnalysis += line[3:].strip()
            elif line.startswith("PY "):
                year = int(line[3:].strip())
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
        if fieldAnalysis[1] < threshold:
            break
        results.append({
            'field': fieldAnalysis[0],
            'count': fieldAnalysis[1]
        })
        cnt += 1
        if cnt >= 100:
            break
    return count, conditionCount, results

def fieldOccurence(files, filesToAnalyze, threshold):
    field_count = dict()
    titleCount = 0
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
                    field = field.split(';')
                    for word in field:
                        word = word.strip().lower()
                        if field_count.get(word, False):
                            field_count[word] += 1
                        else:
                            field_count[word] = 1
                field = ""
                insideSC = False
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

def fieldField(files, filesToAnalyze, field):
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
        target = field.lower()
        fields = ""
        insideSC = False
        for line in content.split('\n'):
            if line.startswith("TI "):
                count += 1
            elif line.startswith("SC "):
                insideSC = True
                fields += line[3:].strip()
            elif line.startswith("   ") and insideSC:
                fields += line[3:].strip()
            elif line.startswith("PY "):
                year = int(line[3:].strip())
            else:
                if insideSC:
                    if fields != "":
                        fields = fields.lower()
                        fields = fields.split(';')
                        for word in fields:
                            if target == word.strip().lower():
                                conditionCount += 1
                                if year_count.get(year, False):
                                    year_count[year] += 1
                                else:
                                    year_count[year] = 1
                    fields = ""
                    insideSC = False
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
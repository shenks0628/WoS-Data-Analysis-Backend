import os
import glob
import requests

def get_referencesInfo(files, filesToAnalyze, threshold):
    TI = set()
    reference_count = dict()
    count = 0
    for file in files:
        fileName = file.get('name')
        if fileName not in filesToAnalyze:
            continue
        fileURL = file.get('url')
        response = requests.get(fileURL)
        response.encoding = 'utf-8'
        content = response.text
        ti = ""
        ref_cnt = 0
        insideAF = False
        insideTI = False
        author = []
        for line in content.split('\n'):
            if line.startswith("AF "):
                insideAF = True
                author.append(line[3:].strip())
            elif line.startswith("   ") and insideAF:
                author.append(line[3:].strip())
            else :
                insideAF = False

            # starts of a title
            if line.startswith("TI "):
                insideTI = True
                count += 1
                ti += line[3:].strip()
            elif line.startswith("   ") and insideTI:
                ti += line[3:].strip()
            else:
                insideTI = False
            
            if line.startswith("Z9 "):
                ref_cnt = int(line[3:].strip())
                if ti != "":
                    if reference_count.get(ti, False):
                        reference_count[ti]["count"] += ref_cnt
                        reference_count[ti]["author"] = author
                    else:
                        TI.add(ti)
                        reference_count[ti] = dict()
                        reference_count[ti]["title"] = ti
                        reference_count[ti]["count"] = ref_cnt
                        reference_count[ti]["author"] = author
                ti = ""
                author = []
                ref_cnt = 0
                insideTI = False

    sorted_references = sorted(reference_count.items(), key=lambda x: x[1]['count'], reverse=True)

    results = []
    cnt = 0
    for item in sorted_references:
        if item[1]['count'] < threshold:
            break
        results.append({
            "title": item[1]["title"],
            "author": item[1]["author"],
            "count": item[1]["count"]
        })
        cnt += 1
        if cnt >= 100:
            break
        
    return count, results
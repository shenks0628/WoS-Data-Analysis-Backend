import os
import glob
import requests

def get_referencesInfo(files):
    TI = set()
    reference_count = dict()
    for file in files:
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
                ti += line[3:].strip()
            elif line.startswith("   ") and insideTI:
                ti += line[3:].strip()
            elif line.startswith("SO "):
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
    for item in sorted_references:
        results.append({
            "title": item[1]["title"],
            "author": item[1]["author"],
            "count": item[1]["count"]
        })
        
    return results
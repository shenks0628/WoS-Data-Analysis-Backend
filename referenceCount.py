import os
import glob
import requests

def get_references(files):
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
            elif line.startswith("Z9 "):
                ref_cnt = int(line[3:].strip())
                TI.add(ti)
                if ti != "":
                    if reference_count.get(ti, False):
                        reference_count[ti]["reference"] += ref_cnt
                        reference_count[ti]["author"] = author
                    else:
                        reference_count[ti] = dict()
                        reference_count[ti]["reference"] = ref_cnt
                        reference_count[ti]["author"] = author
                ti = ""
                author = []
                ref_cnt = 0
    sorted_references = sorted(reference_count.items(), key=lambda x: x[1]['reference'], reverse=True)
    return sorted_references
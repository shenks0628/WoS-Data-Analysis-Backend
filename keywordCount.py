import os
import glob
import requests

def get_keywords(files):
    keywords = set()
    keyword_count = dict()
    for file in files:
        file_url = file.get('url')
        response = requests.get(file_url)
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
                        keywords.add(word)
                        if keyword_count.get(word, False):
                            keyword_count[word] += 1
                        else:
                            keyword_count[word] = 1
                keyword = ""
                insideDE = False
    sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_keywords
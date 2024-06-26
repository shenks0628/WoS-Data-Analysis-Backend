import os
import glob
import requests

def checkTitle(files):
    count = 0
    titles = set()
    title_file = dict()
    title_author = dict()
    results = []
    for file in files:
        fileName = file.get('name')
        fileURL = file.get('url')
        response = requests.get(fileURL)
        response.encoding = 'utf-8'
        content = response.text
        # initialize author and insideAF
        author = []
        insideAF = False
        # initialize title and insideTI
        title = ""
        insideTI = False
        # iterate through each line
        for line in content.split('\n'):
            # starts of an author
            if line.startswith("AF "):
                insideAF = True
                author.append(line[3:].strip())
            # contents inside the AF tag
            elif line.startswith("   ") and insideAF:
                author.append(line[3:].strip())
            else:
                insideAF = False
            # starts of a title
            if line.startswith("TI "):
                insideTI = True
                title += line[3:].strip()
            # contents inside the TI tag
            elif line.startswith("   ") and insideTI:
                title += line[3:].strip()
            else:
                # print the current (title, file) and correspond (title, file) if the title has been seen before
                if title in titles:
                    print("---")
                    print(f'Title "{title}" appears in "{fileName}".')
                    print(f'Title "{title}" appears in "{title_file[title]}".')
                    # check if the authors are same
                    print(len(author))
                    for i in author:
                        print(i, end=" ")
                    print()
                    for i in title_author[title]:
                        print(i, end=" ")
                    print()
                    if len(set(author).intersection(title_author[title])) == len(author):
                        print(f'All Same!')
                    else:
                        print(f'Different!')
                    print("---")
                    results.append({
                        'title': title,
                        'file1': fileName,
                        'file2': title_file[title],
                        'author1': author,
                        'author2': title_author[title]
                    })
                # add title count and add title, author into the set and dictionary
                if title != "" and len(author) != 0:
                    count += 1
                    titles.add(title)
                    title_file[title] = fileName
                    title_author[title] = author
                    # re-initialize author and insideAF
                    author = []
                    insideAF = False
                    # re-initialize title and insideTI
                    title = ""
                    insideTI = False
    return count, results
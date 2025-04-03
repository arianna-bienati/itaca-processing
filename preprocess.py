import argparse

parser = argparse.ArgumentParser()
parser.add_argument("infolder", help="Folder containing TXT files")
parser.add_argument("outfolder", help="Output folder")
parser.add_argument("--list", help="TSV containing list of files")
parser.add_argument("--tint", help="Tint URL", default="https://dh.fbk.eu/tint-demo-api/tint/")
parser.add_argument("--conn", help="List of connectives")
parser.add_argument("--skiplist", help="List of file to skip")
parser.add_argument("--cachefolder", help="Folder for Tint cache")
parser.add_argument('--overwrite', action='store_true')
parser.add_argument('--annotators', help="List of annotators' names", nargs="+")
parser.add_argument('--outindex', help="Output index")
args = parser.parse_args()

import os
import random
from pathlib import Path
import requests
import json
import csv
from webanno_tsv import Document, Annotation
from dataclasses import replace
from tqdm import tqdm
from unidecode import unidecode
import re

def isSubArray(A, B):
    i = 0
    j = 0
    n = len(A)
    m = len(B)
    ret = []

    while i < n and j < m:
        if A[i] == B[j]:
            i += 1
            j += 1
            if j == m:
                # index is +1 just not to confuse 0 and False
                ret.append(i - j + 1)

                i = i - j + m
                j = 0
                # return i - j + 1
        else:
            i = i - j + 1
            j = 0

    return ret

# https://www.geeksforgeeks.org/python-intersection-two-lists/
def intersection(lst1, lst2):
    temp = set(lst2)
    lst3 = [value for value in lst1 if value in temp]
    return lst3

overwrite = args.overwrite
outindexFile = args.outindex

toDo = {}

fileListInput = args.list
if fileListInput:
    with open(fileListInput) as f:
        for line in f:
            line = line.strip()
            parts = line.split("\t")
            if len(parts) <= 2:
                continue
            fileName = parts[1].strip()
            if fileName in toDo:
                print("File already exists: ", fileName)
                continue
            if parts[2].strip().lower() == "yes":
                toDo[fileName] = True
            if parts[2].strip().lower() == "no":
                toDo[fileName] = False

skipListInput = args.skiplist
if skipListInput:
    with open(skipListInput) as f:
        for line in f:
            fileName = line.strip()
            if fileName not in toDo:
                print("Cannot skip: ", fileName)
                continue
            del toDo[fileName]

annotators = args.annotators
if annotators:
    annotators = [re.sub(r"[^A-Z]", "", unidecode(x.upper())) for x in annotators]

# print(len(toDo))
# print(annotators)
# exit()

"""
Documentation for connectives file:

0: token
1: X if the token has another meaning without accent(s)
2: list of POS (negative with ~)
3: list of expressions to skip

"""

# not used right now, it can be added using POS information
connectivesToCheck = set()
checkPos = {}

connectives = set()
checkPosNeg = {}
ignorePhrases = {}
if args.conn:
    with open(args.conn) as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tsv_file:
            t = line[0].lower()
            connectives.add(t)
            if line[3]:
                phrases = line[3].split(",")
                ignorePhrases[t] = set()
                for phrase in phrases:
                    ignorePhrases[t].add(phrase.lower())
            if line[2]:
                parts = line[2].split(",")
                pos = set()
                neg = set()
                for part in parts:
                    part = part.strip()
                    if part.startswith("~"):
                        part = part[1:]
                        if len(part):
                            neg.add(part)
                    else:
                        if len(part):
                            pos.add(part)
                if len(pos) > 0 and len(neg) > 0:
                    print("Error: pos and neg in the same line")
                else:
                    if len(pos) > 0:
                        checkPos[t] = pos
                    if len(neg) > 0:
                        checkPosNeg[t] = neg
            if line[1]:
                connectivesToCheck.add(unidecode(t))
            else:
                connectives.add(unidecode(t))

# print(checkPos)
# print(checkPosNeg)
# print(ignorePhrases)
# exit()

layer_defs = [
    ('webanno.custom.StrutturaCapoverso', ['Capoverso']),
    ('webanno.custom.Connettivoproblematico', ['Problematico']),
    ('webanno.custom.SegmentazioneVirgoladitroppo', ['Virgoladitroppo']),
    ('webanno.custom.Segmentazione', ['Virgolasplice']),
    ('webanno.custom.ConnettivoproblematicoTint', ['Tint'])
]
# annotations = [
#     Annotation(tokens=doc.tokens[1:2], layer='Layer1', field='Field1', label='ABC'),
#     Annotation(tokens=doc.tokens[1:3], layer='Layer2', field='Field3', label='XYZ', label_id=1)
# ]

# sentence = "Il cane ha sia sia sia sia bevuto"
# sp = sentence.split(" ")
# print(isSubArray(sp, ['sia']))
# exit()

input_folder = args.infolder
output_folder = args.outfolder
cache_folder = args.cachefolder

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

if cache_folder and not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

numFiles = 0
for file in Path(input_folder).rglob('*.txt'):
    numFiles += 1

count = 0
skipped = 0

outputIndex = {}
pbar = tqdm(Path(input_folder).rglob('*.txt'), total=numFiles)
for path in pbar:
# for path in Path(input_folder).rglob('*.txt'):
    pbar.set_description(path.name)
    filename = os.path.join(path.parent, path.name)
    # outfile = filename + ".tsv"

    # print("Input:", filename)

    outName = path.name

    if len(toDo) > 0:

        if outName not in toDo:
            # print("File not in to do list, skipping:", outName)
            skipped += 1
            continue
        prefix = "SI_"
        if not toDo[outName]:
            outputIndex[outName] = "NO"
            prefix = "ZNO_"
        else:
            if annotators and len(annotators) > 0:
                annotatorName = annotators[count % len(annotators)]
                outputIndex[outName] = annotatorName
                prefix = prefix + annotatorName + "_"

        toDo.pop(outName)
        random.seed(outName)
        r = random.randint(0, 999)
        prefix += f'{r:03}' + "_"
        outName = prefix + outName

    count += 1

    outfile = os.path.join(output_folder, outName + ".tsv")
    if os.path.exists(outfile) and not overwrite:
        # print("File exists, skipping")
        continue

    with open(filename, 'r') as file:
        text = file.read()
        if cache_folder and os.path.exists(os.path.join(cache_folder, path.name)):
            with open(os.path.join(cache_folder, path.name), "r") as jf:
                data = json.load(jf)
        else:
            myobj = {'text' : text}
            # print("  Calling Tint...")
            x = requests.post(args.tint, data = myobj)
            data = json.loads(x.text)
            if cache_folder:
                with open(os.path.join(cache_folder, path.name), 'w') as fw:
                    fw.write(x.text)

        # print("  Extracting information...")
        sentences = []
        rawAnnotations = []
        thisIndex = 0
        for sentence in data['sentences']:
            thisSentence = []
            thisSentenceIndex = 0
            thisSentenceLower = []
            thisSentencePos = []
            sentenceStartIndex = thisIndex

            # capoverso
            b = sentence['characterOffsetBegin']
            # print("Text:", sentence['text'])
            capoverso = False
            if b == 0:
                capoverso = True
            for i in reversed(range(b)):
                t = text[i:i+1]
                if t.strip() != "":
                    break
                if t == '\n':
                    capoverso = True
                    break
            # e = sentence['characterOffsetEnd']
            # sentenceText = sentence['text']
            # print(sentenceText, text[b:e])
            if capoverso:
                rawAnnotations.append({
                    "tokenStart": sentenceStartIndex,
                    "tokenEnd": sentenceStartIndex + 1,
                    "layer": 'webanno.custom.StrutturaCapoverso',
                    "field": 'Capoverso',
                    "label": 'true'
                    })

            # tokens
            tokensMap = {}
            for token in sentence['tokens']:
                tokensMap[token['index']] = thisSentenceIndex
                if token['isMultiwordToken'] and not token['isMultiwordFirstToken']:
                    continue
                thisSentence.append(token['originalText'])
                thisSentenceIndex += 1
                thisSentenceLower.append(token['originalText'].lower())
                thisSentencePos.append(token['pos'].upper())
                thisIndex += 1

            # commas
            for i in range(len(thisSentence)):
                if thisSentence[i] == ",":
                    rawAnnotations.append({
                        "tokenStart": sentenceStartIndex + i,
                        "tokenEnd": sentenceStartIndex + i + 1,
                        "layer": 'webanno.custom.Segmentazione',
                        "field": 'Virgolasplice',
                        "label": 'Corretto'
                        })


            # dependencies
            deps = sentence['basic-dependencies']
            coord_connections = {}
            for dep in deps:

                # cc to names
                if dep['dep'] == "cc":
                    coord_connections[sentenceStartIndex + tokensMap[dep['dependent']]] = sentenceStartIndex + tokensMap[dep['governor']]

                # wrong commas
                if dep['dep'] == "nsubj":
                    tokenStart = min(dep['governor'], dep['dependent'])
                    tokenEnd = max(dep['governor'], dep['dependent'])
                    tokenStart = tokensMap[tokenStart]
                    tokenEnd = tokensMap[tokenEnd]
                    commaCount = set()
                    for i in range(tokenEnd - tokenStart + 1):
                        if thisSentence[i + tokenStart] == ",":
                            commaCount.add(i + tokenStart)
                    if len(commaCount) == 1:
                        for i in commaCount:
                            rawAnnotations.append({
                                "tokenStart": sentenceStartIndex + i,
                                "tokenEnd": sentenceStartIndex + i + 1,
                                "layer": 'webanno.custom.SegmentazioneVirgoladitroppo',
                                "field": 'Virgoladitroppo',
                                "label": 'true'
                                })

            # check connectives
            connAnnotations = {}
            connTintAnnotations = {}
            connOccupied = {}
            for connective in connectives:
                parts = connective.split(" ")
                foundList = isSubArray(thisSentenceLower, parts)
                for found in foundList:
                    found -= 1
                    tokenStart = thisIndex - len(thisSentenceLower) + found
                    tokenEnd = tokenStart + len(parts)

                    if tokenStart in coord_connections:
                        if thisSentencePos[coord_connections[tokenStart] - thisIndex].startswith("S"):
                            connTintAnnotations[tokenStart] = {
                                "tokenStart": tokenStart,
                                "tokenEnd": tokenEnd,
                                "layer": 'webanno.custom.ConnettivoproblematicoTint',
                                "field": 'Tint',
                                "label": 'coord-name'
                                }
                            continue

                    # check phrases
                    skipThis = False
                    if connective in ignorePhrases:
                        thisConnectiveTokens = []
                        for i in range(tokenEnd - tokenStart):
                            thisConnectiveTokens.append(found + 1 + i)
                        for phrase in ignorePhrases[connective]:
                            phraseParts = phrase.split(" ")
                            sets = isSubArray(thisSentenceLower, phraseParts)
                            for s in sets:
                                thisPhraseTokens = []
                                for i in range(len(phraseParts)):
                                    thisPhraseTokens.append(s + i)
                                # print(thisPhraseTokens)
                                # print(thisConnectiveTokens)
                                # print(intersection(thisPhraseTokens, thisConnectiveTokens))
                                inters = intersection(thisPhraseTokens, thisConnectiveTokens)
                                if len(inters) > 0:
                                    skipThis = True

                    if skipThis:
                        connTintAnnotations[tokenStart] = {
                            "tokenStart": tokenStart,
                            "tokenEnd": tokenEnd,
                            "layer": 'webanno.custom.ConnettivoproblematicoTint',
                            "field": 'Tint',
                            "label": 'in-phrase'
                            }
                        continue

                    # check pos
                    if connective in checkPos:
                        pass # to do

                    if connective in checkPosNeg:
                        present = False
                        for i in range(len(parts)):
                            index = tokenStart - thisIndex + i
                            if thisSentencePos[index] in checkPosNeg[connective]:
                                present = True
                        if present:
                            connTintAnnotations[tokenStart] = {
                                "tokenStart": tokenStart,
                                "tokenEnd": tokenEnd,
                                "layer": 'webanno.custom.ConnettivoproblematicoTint',
                                "field": 'Tint',
                                "label": 'pos-not'
                                }
                            continue

                    # remove duplicates
                    length = tokenEnd - tokenStart
                    maxLength = 0
                    totalList = {}
                    for i in range(length):
                        index = tokenStart + i
                        if index in connAnnotations:
                            totalList[index] = connAnnotations[index]['tokenEnd'] - connAnnotations[index]['tokenStart']
                        if index in connOccupied:
                            newIndex = connOccupied[index]
                            totalList[newIndex] = connAnnotations[newIndex]['tokenEnd'] - connAnnotations[newIndex]['tokenStart']
                    for i in totalList:
                        if totalList[i] > maxLength:
                            maxLength = totalList[i]
                    if maxLength > 0:
                        if length > maxLength:
                            indexToRemove = set()
                            for index in totalList:
                                for i in range(totalList[index]):
                                    indexToRemove.add(index + i)
                            indexToRemove = sorted(indexToRemove, reverse=True)
                            for i in indexToRemove:
                                if i in connOccupied:
                                    connOccupied.pop(i)
                                if i in connAnnotations:
                                    ts = connAnnotations[i]["tokenStart"]
                                    te = connAnnotations[i]["tokenEnd"]
                                    connTintAnnotations[i] = {
                                        "tokenStart": ts,
                                        "tokenEnd": te,
                                        "layer": 'webanno.custom.ConnettivoproblematicoTint',
                                        "field": 'Tint',
                                        "label": 'overlap'
                                        }
                                    connAnnotations.pop(i)
                        else:
                            connTintAnnotations[tokenStart] = {
                                "tokenStart": tokenStart,
                                "tokenEnd": tokenEnd,
                                "layer": 'webanno.custom.ConnettivoproblematicoTint',
                                "field": 'Tint',
                                "label": 'overlap'
                                }
                            continue

                    for i in range(len(parts)):
                        connOccupied[tokenStart + i] = tokenStart
                    connAnnotations[tokenStart] = {
                        "tokenStart": tokenStart,
                        "tokenEnd": tokenEnd,
                        "layer": 'webanno.custom.Connettivoproblematico',
                        "field": 'Problematico',
                        "label": 'false'
                        }
                    # print(thisSentence)
                    # print(parts)
                    # print(found, len(parts))

            for i in connAnnotations:
                rawAnnotations.append(connAnnotations[i])
            for i in connTintAnnotations:
                rawAnnotations.append(connTintAnnotations[i])
            sentences.append(thisSentence)

        doc = Document.from_token_lists(sentences)
        annotations = []
        for rawAnnotation in rawAnnotations:
            annotations.append(Annotation(
                tokens=doc.tokens[rawAnnotation['tokenStart']:rawAnnotation['tokenEnd']],
                layer=rawAnnotation['layer'],
                field=rawAnnotation['field'],
                label=rawAnnotation['label']))
        doc = replace(doc, annotations=annotations, layer_defs=layer_defs)

        # print("  Saving file...")
        fout = open(outfile, "w")
        fout.write(doc.tsv())
        fout.close()
        # print(doc.tsv())

if outindexFile:
    with open(outindexFile, "w") as fw:
        for i in outputIndex:
            fw.write(i)
            fw.write("\t")
            fw.write(outputIndex[i])
            fw.write("\n")

print("Total parsed files:", count)
print("Skipped files:", skipped)
# for file in toDo:
#     print("Remaining:", file)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("infolder", help="Export from Inception (TSV WebAnno format)")
parser.add_argument('--annotators', help="List of annotators' user names", nargs="+", required=True)
args = parser.parse_args()

do_virgolaDiTroppo = False
do_virgolaSplice = False
do_connettivoProblematico = False
do_remaNonEspanso = False
do_segmentazioneInciso = False
do_strutturaTipo = False
do_disposizioneErrata = False

do_accordoProblematico = True
do_anafora = True
do_contraddizione = True

regexp = r"^SI_[0-9]+"

from webanno_tsv_custom import webanno_tsv_read_file
import os
import re
import statsmodels.api as sm
import statsmodels as sm
import numpy as np

def toArray(d, annotators, pr=False, conversionDict={}):
    if len(conversionDict) == 0:
        allInts = True
        valueList = set()
        for k in d:
            for a in d[k]:
                if type(d[k][a]) != int:
                    allInts = False
                    valueList.add(d[k][a])
        conversionDict = {}
        index = 0
        if not allInts:
            for v in valueList:
                if v not in conversionDict:
                    conversionDict[v] = index
                    index += 1

    ks = d.keys()
    annIndexes = {}
    if pr:
        print(35 * " ", end='')

    for idx, x in enumerate(annotators):
        if pr:
            print("%20s" % x, end='')
        annIndexes[x] = idx

    if pr:
        print()
        print((35 + 20 * len(annotators)) * "-")

    mat = np.zeros((len(d.keys()), len(annotators)), dtype=int)
    index = 0
    for k in sorted(d):
        for a in d[k]:
            if len(conversionDict) == 0:
                mat[index][annIndexes[a]] = d[k][a]
            else:
                mat[index][annIndexes[a]] = conversionDict[d[k][a]]
        index += 1
    if pr:
        s = sorted(d)
        for i in range(len(s)):
            k = s[i]
            print("%-35s" % k, end='')
            for a in mat[i]:
                print("%20d" % a, end='')
            print()
    return mat

input_folder = args.infolder
annotators = args.annotators

webannoTsvs = {}

annotation_folder = os.path.join(input_folder, "annotation")
for folder in os.listdir(annotation_folder):
    origName = re.sub(r"\.tsv", "", folder)
    if not re.match(regexp, folder):
        continue
    webannoTsvs[origName] = {}
    folder = os.path.join(annotation_folder, folder)
    for f in os.listdir(folder):
        if not re.match(r"^[a-z0-9_]+\.tsv$", f):
            continue
        fileName = os.path.join(folder, f)
        f = re.sub(r"\.tsv$", "", f)
        if f not in annotators:
            continue
        webannoTsvs[origName][f] = webanno_tsv_read_file(fileName)
    
    if len(webannoTsvs[origName]) != len(annotators):
        print("Error! Missing file for folder", folder)

### Spans

if do_virgolaDiTroppo:
    print("### Virgola di troppo")
    virgolaDiTroppoAlone = {}
    for file in webannoTsvs:
        for annotator in webannoTsvs[file]:
            annotations = webannoTsvs[file][annotator].match_annotations(layer="webanno.custom.SegmentazioneVirgoladitroppo")
            for annotation in annotations:
                subject = file + "_" + str(annotation.start).zfill(4)
                if subject not in virgolaDiTroppoAlone:
                    virgolaDiTroppoAlone[subject] = {}
                virgolaDiTroppoAlone[subject][annotator] = annotation.label

    conversionDict = {'true': 1, 'false': 2}
    a = toArray(virgolaDiTroppoAlone, annotators, pr=True, conversionDict=conversionDict)
    ar, _ = sm.stats.inter_rater.aggregate_raters(a)
    print("Agreement - alone:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
    print()

if do_virgolaSplice:
    print("### Virgola splice (corretto/non corretto)")
    virgoleSplice = {}
    virgoleSpliceAlone = {}
    virgoleSpliceType = {}
    virgoleSpliceTypeAlone = {}
    for file in webannoTsvs:
        for annotator in webannoTsvs[file]:
            annotations = webannoTsvs[file][annotator].match_annotations(layer="webanno.custom.Segmentazione")
            for annotation in annotations:
                subject = file + "_" + str(annotation.start).zfill(4)
                if subject not in virgoleSpliceType:
                    virgoleSpliceType[subject] = {}
                if subject not in virgoleSplice:
                    virgoleSplice[subject] = {}
                virgoleSpliceType[subject][annotator] = annotation.label
                if annotation.label != "Corretto":
                    virgoleSplice[subject][annotator] = 1
    for s in virgoleSplice:
        valueSum = 0
        for a in virgoleSplice[s]:
            valueSum += virgoleSplice[s][a]
        if valueSum != 0:
            virgoleSpliceTypeAlone[s] = virgoleSpliceType[s]
            virgoleSpliceAlone[s] = virgoleSplice[s]


    a = toArray(virgoleSplice, annotators, pr=False)
    ar, _ = sm.stats.inter_rater.aggregate_raters(a)
    print("Agreement (c/nc):", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
    a = toArray(virgoleSpliceAlone, annotators, pr=True)
    ar, _ = sm.stats.inter_rater.aggregate_raters(a)
    print("Agreement (c/nc) - alone:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
    conversionDict = {'Punto e virgola': 1, 'Punto': 1, 'Corretto': 0, 'Due punti': 2}
    a = toArray(virgoleSpliceType, annotators, pr=False, conversionDict=conversionDict)
    ar, _ = sm.stats.inter_rater.aggregate_raters(a)
    print("Agreement (type):", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
    a = toArray(virgoleSpliceTypeAlone, annotators, pr=True, conversionDict=conversionDict)
    ar, _ = sm.stats.inter_rater.aggregate_raters(a)
    print("Agreement (type) - alone:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
    print(conversionDict)
    print()

if do_connettivoProblematico:
    print("### Connettivo problematico")
    connettivoProblematico = {}
    for file in webannoTsvs:
        for annotator in webannoTsvs[file]:
            annotations = webannoTsvs[file][annotator].match_annotations(layer="webanno.custom.Connettivoproblematico", field="Problematico")
            for annotation in annotations:
                subject = file + "_" + str(annotation.start).zfill(4)
                if subject not in connettivoProblematico:
                    connettivoProblematico[subject] = {}
                connettivoProblematico[subject][annotator] = annotation.label

    conversionDict = {'true': 1, 'false': 2}
    a = toArray(connettivoProblematico, annotators, pr=True, conversionDict=conversionDict)
    ar, _ = sm.stats.inter_rater.aggregate_raters(a)
    print("Agreement:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
    print()

if do_remaNonEspanso:
    print("### Rema non espanso")
    remaNonEspanso = {}
    for file in webannoTsvs:
        for annotator in webannoTsvs[file]:
            annotations = webannoTsvs[file][annotator].match_annotations(layer="webanno.custom.Remanonespanso")
            for annotation in annotations:
                for t in annotation.tokens:
                    subject = file + "_" + str(t.start).zfill(4)
                    if subject not in remaNonEspanso:
                        remaNonEspanso[subject] = {}
                    remaNonEspanso[subject][annotator] = 1

    a = toArray(remaNonEspanso, annotators, pr=True)
    ar, _ = sm.stats.inter_rater.aggregate_raters(a)
    print("Agreement:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
    print()

if do_segmentazioneInciso:
    print("### Segmentazione - Inciso")
    segmentazioneInciso = {}
    for file in webannoTsvs:
        for annotator in webannoTsvs[file]:
            annotations = webannoTsvs[file][annotator].match_annotations(layer="webanno.custom.SegmentazioneInciso", field="Inciso")
            for annotation in annotations:
                for t in annotation.tokens:
                    subject = file + "_" + str(t.start).zfill(4)
                    if subject not in segmentazioneInciso:
                        segmentazioneInciso[subject] = {}
                    segmentazioneInciso[subject][annotator] = annotation.label

    conversionDict = {'Correttamente segnalato': 1, 'Manca virgola finale': 2, 'Manca virgola iniziale': 3, 'Non segnalato': 4, '*': 5}
    a = toArray(segmentazioneInciso, annotators, pr=True, conversionDict=conversionDict)
    ar, _ = sm.stats.inter_rater.aggregate_raters(a)
    print("Agreement:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
    print(conversionDict)
    print()

if do_strutturaTipo:
    print("### Struttura - Tipo")
    strutturaTipo = {}
    for file in webannoTsvs:
        for annotator in webannoTsvs[file]:
            annotations = webannoTsvs[file][annotator].match_annotations(layer="webanno.custom.Struttura", field="Tipo")
            for annotation in annotations:
                for t in annotation.tokens:
                    subject = file + "_" + str(t.start).zfill(4)
                    if subject not in strutturaTipo:
                        strutturaTipo[subject] = {}
                    strutturaTipo[subject][annotator] = annotation.label

    conversionDict = {'Intro': 1, 'Tesi': 2, 'Argopro': 3, 'Argocontro': 4, 'Temp': 5, 'Concessione': 6, 'Confutazione': 7, 'Digr': 8, 'Concl': 9, 'Altro': 10, '*': 11}
    a = toArray(strutturaTipo, annotators, pr=True, conversionDict=conversionDict)
    ar, _ = sm.stats.inter_rater.aggregate_raters(a)
    print("Agreement:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
    print(conversionDict)
    print()

if do_disposizioneErrata:
    print("### Disposizione errata")
    disposizioneErrata = {}
    for file in webannoTsvs:
        for annotator in webannoTsvs[file]:
            annotations = webannoTsvs[file][annotator].match_annotations(layer="webanno.custom.Disposizioneerrata", field="Tipo")
            for annotation in annotations:
                for t in annotation.tokens:
                    subject = file + "_" + str(t.start).zfill(4)
                    if subject not in disposizioneErrata:
                        disposizioneErrata[subject] = {}
                    disposizioneErrata[subject][annotator] = annotation.label

    conversionDict = {'Spostare': 1, 'Togliere': 2, '*': 3}
    a = toArray(disposizioneErrata, annotators, pr=True, conversionDict=conversionDict)
    ar, _ = sm.stats.inter_rater.aggregate_raters(a)
    print("Agreement:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
    print(conversionDict)
    print()

### Relations

if do_accordoProblematico:
    print("### Accordo problematico")
    accordoProblematico = {}
    for file in webannoTsvs:
        for annotator in webannoTsvs[file]:
            relations = webannoTsvs[file][annotator].match_rel_annotations(layer="webanno.custom.Accordoproblematico")
            for relation in relations:
                if relation.field not in accordoProblematico:
                    accordoProblematico[relation.field] = {}
                subject = ""
                o1 = set()
                o2 = set()
                if relation.governor.tokens[0].start > relation.dependent.tokens[0].start:
                    subject = file + "_" + str(relation.dependent.tokens[0].start).zfill(4) + "_" + str(relation.governor.tokens[0].start).zfill(4)
                    l = relation.dependent.tokens[len(relation.dependent.tokens) - 1].end - relation.dependent.tokens[0].start
                    for index in range(l):
                        o1.add(relation.dependent.tokens[0].start + index)
                    l = relation.governor.tokens[len(relation.governor.tokens) - 1].end - relation.governor.tokens[0].start
                    for index in range(l):
                        o2.add(relation.governor.tokens[0].start + index)
                else:
                    subject = file + "_" + str(relation.governor.tokens[0].start).zfill(4) + "_" + str(relation.dependent.tokens[0].start).zfill(4)
                    l = relation.dependent.tokens[len(relation.dependent.tokens) - 1].end - relation.dependent.tokens[0].start
                    for index in range(l):
                        o2.add(relation.dependent.tokens[0].start + index)
                    l = relation.governor.tokens[len(relation.governor.tokens) - 1].end - relation.governor.tokens[0].start
                    for index in range(l):
                        o1.add(relation.governor.tokens[0].start + index)

                subj = None
                for s in accordoProblematico[relation.field]:
                    x1 = accordoProblematico[relation.field][s]['o1'].intersection(o1)
                    x2 = accordoProblematico[relation.field][s]['o2'].intersection(o2)
                    if len(x1) > 0 and len(x2) > 0:
                        subj = s

                if subj is not None:
                    accordoProblematico[relation.field][subj][annotator] = relation.label
                    accordoProblematico[relation.field][subj]['o1'] = accordoProblematico[relation.field][subj]['o1'].union(o1)
                    accordoProblematico[relation.field][subj]['o2'] = accordoProblematico[relation.field][subj]['o2'].union(o2)
                else:
                    if subject not in accordoProblematico[relation.field]:
                        accordoProblematico[relation.field][subject] = {}
                        accordoProblematico[relation.field][subject]['o1'] = o1
                        accordoProblematico[relation.field][subject]['o2'] = o2
                    accordoProblematico[relation.field][subject][annotator] = relation.label

    for field in accordoProblematico:
        toSend = accordoProblematico[field]
        for s in toSend:
            toSend[s].pop("o1")
            toSend[s].pop("o2")
        print("####", field)
        conversionDict = {'true': 1, 'false': 2}
        a = toArray(toSend, annotators, pr=True, conversionDict=conversionDict)
        ar, _ = sm.stats.inter_rater.aggregate_raters(a)
        print("Agreement:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
        print()

# if do_anafora:
#     print("### Anafora")
#     anafora = {}
#     for file in webannoTsvs:
#         for annotator in webannoTsvs[file]:
#             relations = webannoTsvs[file][annotator].match_rel_annotations(layer="webanno.custom.Anafora")
#             for relation in relations:
#                 subject = ""
#                 if relation.governor.tokens[0].start > relation.dependent.tokens[0].start:
#                     subject = file + "_" + str(relation.dependent.tokens[0].start).zfill(4) + "_" + str(relation.governor.tokens[0].start).zfill(4)
#                 else:
#                     subject = file + "_" + str(relation.governor.tokens[0].start).zfill(4) + "_" + str(relation.dependent.tokens[0].start).zfill(4)
#                 if subject not in anafora:
#                     anafora[subject] = {}
#                 anafora[subject][annotator] = relation.label

#     conversionDict = {'true': 1, 'false': 1, '*': 1}
#     a = toArray(anafora, annotators, pr=True, conversionDict=conversionDict)
#     ar, _ = sm.stats.inter_rater.aggregate_raters(a)
#     print("Agreement:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
#     print()

if do_anafora:
    print("### Anafora")
    anafora = {}
    for file in webannoTsvs:
        for annotator in webannoTsvs[file]:
            relations = webannoTsvs[file][annotator].match_rel_annotations(layer="webanno.custom.Anafora")
            for relation in relations:
                subject = ""
                o1 = set()
                o2 = set()
                if relation.governor.tokens[0].start > relation.dependent.tokens[0].start:
                    subject = file + "_" + str(relation.dependent.tokens[0].start).zfill(4) + "_" + str(relation.governor.tokens[0].start).zfill(4)
                    l = relation.dependent.tokens[len(relation.dependent.tokens) - 1].end - relation.dependent.tokens[0].start
                    for index in range(l):
                        o1.add(relation.dependent.tokens[0].start + index)
                    l = relation.governor.tokens[len(relation.governor.tokens) - 1].end - relation.governor.tokens[0].start
                    for index in range(l):
                        o2.add(relation.governor.tokens[0].start + index)
                else:
                    subject = file + "_" + str(relation.governor.tokens[0].start).zfill(4) + "_" + str(relation.dependent.tokens[0].start).zfill(4)
                    l = relation.dependent.tokens[len(relation.dependent.tokens) - 1].end - relation.dependent.tokens[0].start
                    for index in range(l):
                        o2.add(relation.dependent.tokens[0].start + index)
                    l = relation.governor.tokens[len(relation.governor.tokens) - 1].end - relation.governor.tokens[0].start
                    for index in range(l):
                        o1.add(relation.governor.tokens[0].start + index)

                subj = None
                for s in anafora:
                    x1 = anafora[s]['o1'].intersection(o1)
                    x2 = anafora[s]['o2'].intersection(o2)
                    if len(x1) > 0 and len(x2) > 0:
                        subj = s

                if subj is not None:
                    anafora[subj][annotator] = relation.label
                    anafora[subj]['o1'] = anafora[subj]['o1'].union(o1)
                    anafora[subj]['o2'] = anafora[subj]['o2'].union(o2)
                else:
                    if subject not in anafora:
                        anafora[subject] = {}
                        anafora[subject]['o1'] = o1
                        anafora[subject]['o2'] = o2
                    anafora[subject][annotator] = relation.label

    toSend = anafora
    for s in toSend:
        toSend[s].pop("o1")
        toSend[s].pop("o2")
    conversionDict = {'true': 1, 'false': 1, '*': 1}
    a = toArray(toSend, annotators, pr=True, conversionDict=conversionDict)
    ar, _ = sm.stats.inter_rater.aggregate_raters(a)
    print("Agreement:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
    print()

# if do_contraddizione:
#     print("### Contraddizione")
#     contraddizione = {}
#     for file in webannoTsvs:
#         for annotator in webannoTsvs[file]:
#             relations = webannoTsvs[file][annotator].match_rel_annotations(layer="webanno.custom.ContraddizioneRelation")
#             for relation in relations:
#                 subject = ""
#                 if relation.governor.tokens[0].start > relation.dependent.tokens[0].start:
#                     subject = file + "_" + str(relation.dependent.tokens[0].start).zfill(4) + "_" + str(relation.governor.tokens[0].start).zfill(4)
#                 else:
#                     subject = file + "_" + str(relation.governor.tokens[0].start).zfill(4) + "_" + str(relation.dependent.tokens[0].start).zfill(4)
#                 if subject not in contraddizione:
#                     contraddizione[subject] = {}
#                 contraddizione[subject][annotator] = relation.label

#     conversionDict = {'*': 1}
#     a = toArray(contraddizione, annotators, pr=True, conversionDict=conversionDict)
#     ar, _ = sm.stats.inter_rater.aggregate_raters(a)
#     print("Agreement:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
#     print()

if do_contraddizione:
    print("### Contraddizione")
    contraddizione = {}
    for file in webannoTsvs:
        for annotator in webannoTsvs[file]:
            relations = webannoTsvs[file][annotator].match_rel_annotations(layer="webanno.custom.ContraddizioneRelation")
            for relation in relations:
                subject = ""
                o1 = set()
                o2 = set()
                if relation.governor.tokens[0].start > relation.dependent.tokens[0].start:
                    subject = file + "_" + str(relation.dependent.tokens[0].start).zfill(4) + "_" + str(relation.governor.tokens[0].start).zfill(4)
                    l = relation.dependent.tokens[len(relation.dependent.tokens) - 1].end - relation.dependent.tokens[0].start
                    for index in range(l):
                        o1.add(relation.dependent.tokens[0].start + index)
                    l = relation.governor.tokens[len(relation.governor.tokens) - 1].end - relation.governor.tokens[0].start
                    for index in range(l):
                        o2.add(relation.governor.tokens[0].start + index)
                else:
                    subject = file + "_" + str(relation.governor.tokens[0].start).zfill(4) + "_" + str(relation.dependent.tokens[0].start).zfill(4)
                    l = relation.dependent.tokens[len(relation.dependent.tokens) - 1].end - relation.dependent.tokens[0].start
                    for index in range(l):
                        o2.add(relation.dependent.tokens[0].start + index)
                    l = relation.governor.tokens[len(relation.governor.tokens) - 1].end - relation.governor.tokens[0].start
                    for index in range(l):
                        o1.add(relation.governor.tokens[0].start + index)

                subj = None
                for s in contraddizione:
                    x1 = contraddizione[s]['o1'].intersection(o1)
                    x2 = contraddizione[s]['o2'].intersection(o2)
                    if len(x1) > 0 and len(x2) > 0:
                        subj = s

                if subj is not None:
                    contraddizione[subj][annotator] = relation.label
                    contraddizione[subj]['o1'] = contraddizione[subj]['o1'].union(o1)
                    contraddizione[subj]['o2'] = contraddizione[subj]['o2'].union(o2)
                else:
                    if subject not in contraddizione:
                        contraddizione[subject] = {}
                        contraddizione[subject]['o1'] = o1
                        contraddizione[subject]['o2'] = o2
                    contraddizione[subject][annotator] = relation.label

    toSend = contraddizione
    for s in toSend:
        toSend[s].pop("o1")
        toSend[s].pop("o2")
    conversionDict = {'*': 1}
    a = toArray(toSend, annotators, pr=True, conversionDict=conversionDict)
    ar, _ = sm.stats.inter_rater.aggregate_raters(a)
    print("Agreement:", sm.stats.inter_rater.fleiss_kappa(ar), len(ar))
    print()

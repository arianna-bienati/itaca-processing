import json
import os.path
import re
import itertools
from sklearn.metrics import cohen_kappa_score
from sklearn.preprocessing import LabelEncoder

from webanno_tsv import webanno_tsv_read_file

possible_results = {
    "comparison": {"contrast", "similarity", "concession"},
    "temporal": {"synchronous", "asynchronous"},
    "contingency": {"cause", "negative", "condition", "purpose"},
    "expansion": {"conjunction", "disjunction", "equivalence", "instantiation"},
}
map = {
    "non è un connettivo": "false",
    "expansion": "expansion:conjunction",
    "level-of-detail": "false",
    "condizione": "contingency:condition",
    "non è presente": "false",
    "contrastive": "comparison:contrast",
    "causale": "contingency:cause",
    "temporal": "temporal:asynchronous",
    "condizionale": "contingency:condition",
    "consequence": "contingency:cause",
    "finalità": "contingency:purpose",
    "finale": "contingency:purpose",
    "addizione": "expansion:conjunction",
    "addittivo": "expansion:conjunction",
    "sequenziale": "temporal:asynchronous",
    "causal": "contingency:cause",
}
connettivi_conversion = {
    "ed": "e",
    "perchè": "perché",
    "grazie alle": "grazie a",
    "grazie alla": "grazie a",
    "grazie al": "grazie a",
    "grazie all'": "grazie a",
    "in seguito alla": "in seguito a",
    "per via del": "per via di",
    "per via della": "per via di",
    "per via dei": "per via di",
    "a causa della": "a causa di",
    "a causa del": "a causa di",
    "prima della": "prima di",
    "prima del": "prima di",
    "prima dell'": "prima di",
    "prima delle": "prima di",
    "perche": "perché",
    "cosi": "così",
    "pero": "però",
}
folder = "dataset/annotation"
allowed_basenames = ["arianna.bienati@eurac.edu.tsv", "mariachiara.pascucci@phd.unipi.it.tsv"]

test_list = set()
people_list = set()

for l in possible_results.keys():
    for o in possible_results[l]:
        map[o] = f"{l}:{o}"

all_results = {}
for llm in ['llama', 'openai']:
    for prompt in ['long', 'short']:
        filename = f"output-sent-{llm}-temp_0.5-{prompt}-1.txt"
        with open(filename) as f:
            results = json.load(f)

        test_list.update(results.keys())
        for fn in results.keys():
            for sentence_index in results[fn].keys():
                response = results[fn][sentence_index]['response']
                parts = response.split("\n")
                for part in parts:
                    part = part.strip()
                    if len(part) == 0:
                        continue
                    parts2 = part.split(":")
                    if len(parts2) < 2:
                        continue
                    word = parts2[0].strip().lower()
                    if word.startswith("-") or word.startswith("*"):
                        word = word[1:]
                    word = re.sub(r"\(.*\)", "", word)
                    word = word.strip()
                    result = parts2[1].strip().lower()
                    formatted_result = None
                    for p1 in possible_results.keys():
                        if p1 in result:
                            for p2 in possible_results[p1]:
                                if p2 in result:
                                    formatted_result = f"{p1}:{p2}"

                    if formatted_result is None:
                        for p in map.keys():
                            if p in result:
                                formatted_result = map[p]

                    if formatted_result is None:
                        formatted_result = "false"

                    key = f"{fn}-{sentence_index}-{word}"
                    if key not in all_results:
                        all_results[key] = {}

                    people_list.add(f"{llm}-{prompt}")
                    all_results[key][f"{llm}-{prompt}"] = formatted_result

for fn in test_list:
    for name in allowed_basenames:
        filename = os.path.join(folder, fn, name)
        doc = webanno_tsv_read_file(filename)
        for annotation in doc.annotations:
            if annotation.layer == "webanno.custom.Connettivo":
                # print(annotation)
                # sentence_text = " ".join(t.text for t in doc.annotation_sentences(annotation))
                field_text = " ".join([t.text.lower() for t in annotation.tokens])
                if field_text in connettivi_conversion:
                    field_text = connettivi_conversion[field_text]
                if annotation.field == "CategoriaPDTB" or annotation.field == "Connettivo":
                    label = annotation.label
                    if label == "true":
                        continue
                    label = label.lower()
                    sentence_index = doc.annotation_sentences(annotation)[0].idx
                    key = f"{fn}-{sentence_index}-{field_text}"
                    if key not in all_results:
                        # print(f"Missing key: {key}")
                        # for k in all_results.keys():
                        #     if k.startswith(f"{fn}-{sentence_index}"):
                        #         print(k)
                        # print()
                        all_results[key] = {}
                    all_results[key][name] = label
                    people_list.add(name)

for key in all_results:
    for person in people_list:
        if person not in all_results[key]:
            all_results[key][person] = "false"

# for key in all_results:
#     print(key, all_results[key])

pairs = list(itertools.combinations(people_list, 2))
for pair in pairs:
    annotator_1 = []
    annotator_2 = []
    for k in all_results.keys():
        label_1 = all_results[k][pair[0]]
        label_2 = all_results[k][pair[1]]
        annotator_1.append(label_1)
        annotator_2.append(label_2)

    label_encoder = LabelEncoder()
    all_labels = list(set(annotator_1 + annotator_2))  # Get all unique labels
    label_encoder.fit(all_labels)
    encoded_annotator_1 = label_encoder.transform(annotator_1)
    encoded_annotator_2 = label_encoder.transform(annotator_2)
    kappa = cohen_kappa_score(encoded_annotator_1, encoded_annotator_2)
    print(f"Annotators: {pair[0]} and {pair[1]}")
    print("Cohen’s Kappa:", kappa)
    print()

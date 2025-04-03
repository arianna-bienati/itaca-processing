import glob
import os.path
import random
import time

from itaca.webanno_tsv import webanno_tsv_read_file
from sklearn.preprocessing import MultiLabelBinarizer
from iterstrat.ml_stratifiers import MultilabelStratifiedShuffleSplit
from openai import OpenAI

folder = "dataset/annotation"
allowed_basenames = ["arianna.bienati@eurac.edu.tsv", "mariachiara.pascucci@phd.unipi.it.tsv"]
test_basenames = {"AC20PA_BAZ14M.tsv", "AC20PA_MOH28R.tsv", "AL07BN_BAS27F.tsv", "AL07BN_BAS28S.tsv",
                  "AL07BN_BIA21M.tsv"}
random_state = 42
min_examples = 10
max_examples_for_type = 10
max_requests = 20
max_loops = 5
pause = 0

short_prompt = True
temperature = 0.5

test = True

# output_file = "output-llama-temp_0.5-long-3.txt"
# openai_api_key = "EMPTY"
# openai_api_base = "http://localhost:8000/v1"
# model = "meta-llama/Llama-3.3-70B-Instruct"
# client = OpenAI(
#     api_key=openai_api_key,
#     base_url=openai_api_base,
# )

output_file = "output-test.txt"
openai_api_key = ""
model = "gpt-4o"
client = OpenAI(
    api_key=openai_api_key,
)

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

all_files = {}
for d in glob.glob(os.path.join(folder, "*")):

    # Check that d is a directory
    if not os.path.isdir(d):
        continue

    all_files[d] = []

    # List all tsv files in the directory
    for f in glob.glob(os.path.join(d, "*.tsv")):
        # Check that f is a file
        if not os.path.isfile(f):
            continue

        # Get the basename of the file
        bn = os.path.basename(f)
        if not bn in allowed_basenames:
            continue

        all_files[d].append(f)

    if len(all_files[d]) != len(allowed_basenames):
        del all_files[d]

# if all-res-backup.pickle exists, load it
# if not, create it

import pickle

# load the pickle
try:
    with open("all-res-backup.pickle", "rb") as fd:
        print("Loading all-res-backup.pickle")
        all_res = pickle.load(fd)
except FileNotFoundError:
    all_res = {}

if len(all_res) == 0:
    for tbn in all_files:
        tbn = os.path.basename(tbn)
        if tbn in test_basenames:
            print(f"Skipping {tbn}")
            continue

        all_res[tbn] = {}
        for take_this in allowed_basenames:
            fn = os.path.join(folder, tbn, take_this)
            doc = webanno_tsv_read_file(fn)
            for annotation in doc.annotations:
                if annotation.layer == "webanno.custom.Connettivo":
                    sentence_text = " ".join(t.text for t in doc.annotation_sentences(annotation))
                    field_text = " ".join([t.text.lower() for t in annotation.tokens])
                    if field_text in connettivi_conversion:
                        field_text = connettivi_conversion[field_text]

                    this_index = f"{annotation.tokens[0].start}-{annotation.tokens[-1].end}"
                    if annotation.field == "CategoriaPDTB" or annotation.field == "Connettivo":
                        if this_index not in all_res[tbn]:
                            all_res[tbn][this_index] = {}
                        all_res[tbn][this_index]["text"] = field_text
                        all_res[tbn][this_index]["sentence"] = sentence_text

                        # Hoping that annotations do not span multiple sentences
                        all_res[tbn][this_index]["sentence_index"] = annotation.tokens[0].sentence_idx

                        if take_this not in all_res[tbn][this_index]:
                            all_res[tbn][this_index][take_this] = {}
                        all_res[tbn][this_index][take_this][annotation.field] = annotation.label

    with open("all-res-backup.pickle", "wb") as fd:
        print("Saving all-res-backup.pickle")
        pickle.dump(all_res, fd)

# print all_res with indentation
# import json
# print(json.dumps(all_res, indent=4))

# print all cases in which there is only one annotation for a particular span
# for tbn in all_res:
#     for span in all_res[tbn]:
#         if len(all_res[tbn][span]) == 4:
#             print(tbn, span, all_res[tbn][span])

features = {}

agreements = 0
disagreements = 0

ordered_files = list(all_res.keys())

for tbn in ordered_files:
    features[tbn] = set()
    for span in all_res[tbn]:
        if len(all_res[tbn][span]) == 4:
            disagreements += 1
        if len(all_res[tbn][span]) == 5:
            if all_res[tbn][span][allowed_basenames[0]] == all_res[tbn][span][allowed_basenames[1]]:
                conn_feat = "unk"
                pdtb_feat = "unk"
                if "Connettivo" in all_res[tbn][span][allowed_basenames[0]]:
                    conn_feat = all_res[tbn][span][allowed_basenames[0]]["Connettivo"]
                if "CategoriaPDTB" in all_res[tbn][span][allowed_basenames[0]]:
                    pdtb_feat = all_res[tbn][span][allowed_basenames[0]]["CategoriaPDTB"]
                feature_name = f"{all_res[tbn][span]['text']}-{conn_feat}-{pdtb_feat}"
                features[tbn].add(feature_name)
                agreements += 1
            else:
                disagreements += 1

mlb = MultiLabelBinarizer()
feature_matrix = mlb.fit_transform(features.values())

print(agreements, disagreements)


def split_into_blocks(lst, block_size=20):
    for i in range(0, len(lst), block_size):
        yield lst[i:i + block_size]


def collect_examples(train_index, ordered_files, all_res, allowed_basenames):
    examples = {}
    for t_index in train_index:
        for interval in all_res[ordered_files[t_index]]:
            if len(all_res[ordered_files[t_index]][interval]) != 5:
                continue
            if all_res[ordered_files[t_index]][interval][allowed_basenames[0]]['Connettivo'] != \
                    all_res[ordered_files[t_index]][interval][allowed_basenames[1]]['Connettivo']:
                continue
            t_value = all_res[ordered_files[t_index]][interval][allowed_basenames[0]]['Connettivo']
            cat_pdtb = None
            if t_value == "true":
                try:
                    if all_res[ordered_files[t_index]][interval][allowed_basenames[0]]['CategoriaPDTB'] != \
                            all_res[ordered_files[t_index]][interval][allowed_basenames[1]]['CategoriaPDTB']:
                        continue
                except:
                    continue
                cat_pdtb = all_res[ordered_files[t_index]][interval][allowed_basenames[0]]['CategoriaPDTB']
            text = all_res[ordered_files[t_index]][interval]['text']
            if text not in examples:
                examples[text] = {}
            if t_value not in examples[text]:
                examples[text][t_value] = []
            examples[text][t_value].append((all_res[ordered_files[t_index]][interval]['sentence'], cat_pdtb, t_index))
    return examples


mskf = MultilabelStratifiedShuffleSplit(n_splits=1, test_size=0.25, random_state=random_state)
train_examples = test_examples = None
for train_index, test_index in mskf.split(ordered_files, feature_matrix):
    print("TRAIN:", train_index, "TEST:", test_index)

    test_examples = collect_examples(test_index, ordered_files, all_res, allowed_basenames)
    train_examples = collect_examples(train_index, ordered_files, all_res, allowed_basenames)

    # for test_word in test_examples:
    #     if test_word not in train_examples:
    #         print(test_word)

if not train_examples:
    exit()
if not test_examples:
    exit()

exit()

fw = open(output_file, "w")

for word in test_examples:

    count = {}
    if word in train_examples:
        for s in train_examples[word].get("true", []):
            if s[1] not in count:
                count[s[1]] = 0
            count[s[1]] += 1
        # if len(train_examples[word]) == 1 and "false" in train_examples[word]:
        #     continue
        # if "true" in train_examples[word]:
        #     for s in train_examples[word]["true"]:
        #         if s[1] not in count:
        #             count[s[1]] = 0
        #         count[s[1]] += 1
        #     if len(count.keys()) == 1 and len(train_examples[word]) == 1:
        #         continue
        falses = len(train_examples[word].get("false", []))
        if falses:
            count['no_pdtb'] = falses

    if len(count.keys()) == 1:
        # Non c'è ambiguità
        continue

    example_text = ""
    if word in train_examples:
        for type in count:
            if type == "no_pdtb":
                continue
            parts = type.split(":")
            type_text = f"In queste frasi, l'espressione \"{word}\" è usata come connettivo {parts[0]} nella sottocategoria {parts[1]}."
            type_text += "\n"

            num_examples = 0
            for t in train_examples[word]["true"]:
                if t[1] != type:
                    continue
                num_examples += 1
                if num_examples > max_examples_for_type:
                    break
                type_text += "\n* " + t[0]
            type_text += "\n\n"
            example_text += type_text

        if "false" in train_examples[word]:
            type_text = f"In queste frasi, l'espressione \"{word}\" non è usata come connettivo."
            type_text += "\n"
            for t in train_examples[word]["false"][:max_examples_for_type]:
                type_text += "\n* " + t[0]
            type_text += "\n\n"
            example_text += type_text

    if example_text:
        example_text = f"Di seguito, troverai alcune frasi in cui l'espressione \"{word}\" è utilizzata o meno come connettivo.\n\n" + example_text

    frasi = []
    results = []
    llm_results = []
    for t in test_examples[word].get("true", []):
        frasi.append(f"* {t[0]}")
        results.append(t[1])
    for t in test_examples[word].get("false", []):
        frasi.append(f"* {t[0]}")
        results.append("false")

    combined = list(zip(frasi, results))
    random.seed(random_state)
    random.shuffle(combined)
    frasi, results = zip(*combined)

    index = 0
    for this_frasi in split_into_blocks(frasi, max_requests):
        print(f"{word} - {index} - {len(frasi)}")
        this_results = results[index:index + len(this_frasi)]
        index += len(this_frasi)

        frasi_text = "\n".join(this_frasi)

        num_loops = 0
        while True:
            if short_prompt:
                prompt = f"""
Concentriamoci sull'espressione "{word}".

{example_text}

Per ciascuna delle seguenti frasi, indica se l'espressione "{word}" ha funzione di connettivo e, in caso affermativo, la tipologia e la sotto-categoria. Se "{word}" non è usato come connettivo, scrivi "Non è un connettivo".
Non darmi altre informazioni né motivazioni, solo la risposta.

{frasi_text}

Come risposta, forniscimi un elenco puntato in cui ogni punto corrisponde a una delle frasi appena scritte.
In tutto ci devono essere {len(this_frasi)} punti.
                """
            else:
                prompt = f"""
In linguistica, ci sono alcuni connettivi detti COMPARISON, che hanno tre sotto-categorie: contrast, similarity, concession.
* Contrast: at least two differences between Arg1 and Arg2 are highlighted (es. al contrario, bensì).
* Similarity: one or more similarities between Arg1 and Arg2 are highlighted with respect to what each argument predicates as a whole or to some entities it mentions (es. allo stesso modo).
* Concession: a causal relation expected on the basis of one argument is cancelled or denied by the situation described in the other (es. prototypically tuttavia).

Altri connettivi sono di tipo TEMPORAL e possono avere due categorie: Synchronous e Asynchronous.
* Synchronous: some degree of temporal overlap between the events described (es. typically mentre, quando).
* Asynchronous: one event is described as preceding the other (es. typically prima che/di, dopo).

Ci sono poi i connettivi di tipo CONTINGENCY, che possono essere: Cause, Condition, Negative, Purpose.
* Cause: situations described in Arg1 and Arg2 are causally influenced but are not in a conditional relation (es. typically perché, quindi).
* Condition: one argument presents a situation as unrealized (the antecedent), which (when realized) would lead to the situation described by the other argument (the consequent) (es. typically se, purché).
* Negative condition: one argument (the antecedent) describes a situation presented as unrealized, which if it doesn’t occur, would lead to the situation described by the other argument (the consequent) (es. typically altrimenti, a meno che).
* Purpose: one argument presents an action that an AGENT undertakes with the purpose of the GOAL conveyed by the other argument being achieved (es. typically affinché).

Esistono anche i connettivi di tipo EXPANSION, che possono essere: Conjunction, Disjunction, Equivalence, Instantiation.
* Conjunction: both arguments bear the same relation to some other situation evoked in the discourse. It indicates that the two arguments make the same contribution with respect to that situation or contribute to it together. It differs from most other relations in that the arguments don’t directly relate to each other, but to this other situation (es. prototypically e, in più at the start of a sentence).
* Disjunction: two arguments are presented as alternatives, with either one or both holding. As with Conjunction, Disjunction is used when both its arguments bear the same relation to some other situation evoked in the discourse, making a similar contribution with respect to that situation. While the arguments also relate to each other as alternatives (with one or both holding), they also both relate in the same way to this other situation (es. typically o, oppure).
* Equivalence: both arguments are taken to describe the same situation, but from different perspectives (es. typically cioè).
* Instantiation: one argument describes a situation as holding in a set of circumstances, while the other argument describes one or more of those circumstances (es. typically ad/per esempio).

Infine, alcune congiunzioni o avverbi non sono considerati connettivi.
* Non vanno considerati connettivi elementi che, pur essendo parole grammaticali, invariabili, non indicano relazioni logico-argomentative: si pensi paradigmaticamente agli introduttori delle subordinate completive (che, di ecc.) e a quelli delle subordinate relative.
* Non vanno considerate connettivi quelle espressioni che, pur essendo associate a una relazione logico-argomentativa, sono morfologicamente variabili: da ciò discende che, per questo fatto, la conseguenza è che, la causa? ecc. In quest'ultimo caso, si può parlare di para-connettivi.

Concentriamoci ora sull'espressione "{word}".

{example_text}

Per ciascuna delle seguenti frasi, indica se l'espressione "{word}" ha funzione di connettivo e, in caso affermativo, la tipologia e la sotto-categoria. Se "{word}" non è usato come connettivo, scrivi "Non è un connettivo".
Non darmi altre informazioni né motivazioni, solo la risposta.

{frasi_text}

Come risposta, forniscimi un elenco puntato in cui ogni punto corrisponde a una delle frasi appena scritte.
In tutto ci devono essere {len(this_frasi)} punti.
                """

            try:
                if test:
                    responses = this_results
                    break
                else:
                    chat_response = client.chat.completions.create(
                        temperature=temperature,
                        model=model,
                        messages=[
                            {"role": "user", "content": prompt},
                        ]
                    )
                    response = chat_response.choices[0].message.content
                    responses = [line for line in response.splitlines() if line.strip()]

                    if len(this_results) == len(responses) or num_loops > max_loops:
                        if len(this_results) > len(responses):
                            responses += ["Non è un connettivo"] * (len(this_results) - len(responses))
                        if len(this_results) < len(responses):
                            responses = responses[:len(this_results)]
                        break

                print("Sizes mismatch, retrying")
            except:
                print("Error in connection, retrying")

            num_loops += 1

        for i in range(len(this_results)):
            fw.write(f"{word}\t{responses[i]}\t{this_results[i]}\t{this_frasi[i]}\n")
            # print(word, responses[i], this_results[i], this_frasi[i])

        time.sleep(pause)

fw.close()

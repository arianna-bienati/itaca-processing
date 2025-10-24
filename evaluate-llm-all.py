import pandas as pd
from collections import Counter
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, classification_report
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import os

map = {
    "congiunzione": "expansion:conjunction",
    "conclusivo": "comparison:conclusion",
    "causa": "contingency:cause",
    "avversativo": "comparison:contrast",
    "coordinazione": "expansion:conjunction",
    "coordinante": "expansion:conjunction",
    "coordinativo": "expansion:conjunction",
}
possible_results = {
    "comparison": {"contrast", "similarity", "concession"},
    "temporal": {"synchronous", "asynchronous"},
    "contingency": {"cause", "negative", "condition", "purpose"},
    "expansion": {"conjunction", "disjunction", "equivalence", "instantiation"},
}

abstention_label = "false"
threshold = 0
figsize = (48, 40)

def shorten_res(original_result):
    if ":" in original_result:
        parts = original_result.split(":")
        return f"{parts[0][:3]}:{parts[1][:3]}"
    else:
        return original_result[:7]

for l in possible_results.keys():
    for o in possible_results[l]:
        map[o] = f"{l}:{o}"

summary_index = 0
for llm in ["llama", "openai"]:
    for prompt in ["long", "short"]:
        print(f"Running evaluation: {llm} with {prompt} prompt")

        lists = []
        word_list = []
        gold_results = []
        for i in range(3):
            collect_gold = True
            if i > 0:
                collect_gold = False
            this_list = []
            filename = f"output-{llm}-temp_0.5-{prompt}-{i + 1}.txt"
            filename = os.path.join("txt-output", filename)
            df = pd.read_csv(filename, delimiter="\t")
            for index, row in df.iterrows():
                word = row.iloc[0].lower()
                word_list.append(row.iloc[0].lower())
                if collect_gold:
                    gold_results.append(f"{word}-{shorten_res(row.iloc[2].lower())}")
                result = row.iloc[1].lower()
                formatted_result = None
                if "non è un connettivo" in result:
                    formatted_result = "false"
                else:
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

                this_list.append(f"{word}-{shorten_res(formatted_result)}")

            lists.append(this_list)

        final_results = []
        expr_final_results = {}
        for i in range(len(lists[0])):
            find_max = Counter([l[i] for l in lists])
            final_results.append(find_max.most_common(1)[0][0])

        # experiments = {
        #     "standard": (gold_results, final_results)
        # }
        #
        # print(experiments)
        # break

        print(f"\nResults for {llm}-{prompt} experiment:")
        missing_labels = set(np.unique(gold_results)) - set(np.unique(final_results))
        if missing_labels:
            print(f"⚠️ Warning: These labels exist in ground truth but were never predicted: {missing_labels}")

        example_counter = Counter(gold_results)
        labels_to_remove = []
        for label, count in example_counter.items():
            if count < threshold:
                labels_to_remove.append(label)

        labels = np.unique(gold_results + final_results)  # Ensures all labels are considered

        filtered_gold = []
        filtered_pred = []

        for g, p in zip(gold_results, final_results):
            if g != abstention_label and p != abstention_label:
                filtered_gold.append(g)
                filtered_pred.append(p)

        labels = [label for label in labels if label not in labels_to_remove]
        conf_matrix = confusion_matrix(gold_results, final_results, labels=labels)

        # Print Confusion Matrix
        # print("\nConfusion Matrix:")
        # print(conf_matrix)

        conf_df = pd.DataFrame(conf_matrix, index=labels, columns=labels)
        # print("\nConfusion Matrix:")
        # print(conf_df)

        plt.figure(figsize=figsize)
        cmap = plt.cm.YlGnBu
        newcolors = cmap(np.linspace(0, 1, 256))
        newcolors[0, :] = np.array([0.9, 0.9, 0.9, 1])  # light grey for zeros
        newcmp = mcolors.ListedColormap(newcolors)
        # sns.heatmap(confusion_matrix, annot=True, cmap=newcmp, fmt="d")
        sns.heatmap(conf_df, annot=True, fmt="d", cmap=newcmp, xticklabels=labels, yticklabels=labels)

        plt.xlabel("Predicted Labels")
        plt.ylabel("True Labels")
        plt.title(f"Confusion Matrix ({llm}-{prompt})")
        plt.xticks(rotation=45)
        plt.yticks(rotation=45)
        plt.show()


import pandas as pd
from collections import Counter
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, classification_report
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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
limit = 10
problematic_expressions = {"e", "per"}

def shorten_res(original_result):
    if ":" in original_result:
        parts = original_result.split(":")
        return f"{parts[0][:3]}:{parts[1][:3]}"
    else:
        return original_result[:7]

for l in possible_results.keys():
    for o in possible_results[l]:
        map[o] = f"{l}:{o}"

summary_df = pd.DataFrame(columns=["Label", "Precision", "Recall", "F1"])

summary_index = 0
for llm in ["llama", "openai"]:
    for prompt in ["long", "short"]:
        print(f"Running evaluation: {llm} with {prompt} prompt")

        lists = []
        word_list = []
        gold_results = []
        expr_gold_results = {}
        for word in problematic_expressions:
            if word.lower() not in expr_gold_results:
                expr_gold_results[word.lower()] = []
        for i in range(3):
            collect_gold = True
            if i > 0:
                collect_gold = False
            this_list = []
            filename = f"output-{llm}-temp_0.5-{prompt}-{i + 1}.txt"
            df = pd.read_csv(filename, delimiter="\t")
            for index, row in df.iterrows():
                word_list.append(row.iloc[0].lower())
                if collect_gold:
                    for word in problematic_expressions:
                        if word.lower() == row.iloc[0].lower():
                            expr_gold_results[word.lower()].append(shorten_res(row.iloc[2].lower()))
                    gold_results.append(shorten_res(row.iloc[2].lower()))
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

                this_list.append(shorten_res(formatted_result))

            lists.append(this_list)

        final_results = []
        expr_final_results = {}
        for word in problematic_expressions:
            if word.lower() not in expr_final_results:
                expr_final_results[word.lower()] = []
        for i in range(len(lists[0])):
            find_max = Counter([l[i] for l in lists])
            for word in problematic_expressions:
                if word.lower() == word_list[i]:
                    expr_final_results[word.lower()].append(find_max.most_common(1)[0][0])
            final_results.append(find_max.most_common(1)[0][0])

        experiments = {
            "standard": (gold_results, final_results)
        }
        for word in problematic_expressions:
            experiments[word.lower()] = (expr_gold_results[word.lower()], expr_final_results[word.lower()])

        for exp_name, (gold_results, final_results) in experiments.items():
            print(f"\nResults for {exp_name} experiment:")
            missing_labels = set(np.unique(gold_results)) - set(np.unique(final_results))
            if missing_labels:
                print(f"⚠️ Warning: These labels exist in ground truth but were never predicted: {missing_labels}")

            example_counter = Counter(gold_results)
            labels_to_remove = []
            for label, count in example_counter.items():
                if count < limit:
                    labels_to_remove.append(label)

            labels = np.unique(gold_results + final_results)  # Ensures all labels are considered

            precision = precision_score(gold_results, final_results, labels=labels, average='macro', zero_division=0)
            recall = recall_score(gold_results, final_results, labels=labels, average='macro', zero_division=0)
            f1 = f1_score(gold_results, final_results, labels=labels, average='macro', zero_division=0)
            # precision = precision_score(gold_results, final_results, average='macro', zero_division=0)
            # recall = recall_score(gold_results, final_results, average='macro', zero_division=0)
            # f1 = f1_score(gold_results, final_results, average='macro', zero_division=0)
            print(f"Precision: {precision:.4f}")
            print(f"Recall: {recall:.4f}")
            print(f"F1-score: {f1:.4f}")

            summary_df.loc[summary_index] = [f"{llm}-{prompt} - {exp_name}", precision, recall, f1]
            summary_index += 1

            filtered_gold = []
            filtered_pred = []

            for g, p in zip(gold_results, final_results):
                if g != abstention_label and p != abstention_label:
                    filtered_gold.append(g)
                    filtered_pred.append(p)

            # Compute new metrics after removing abstention cases
            if filtered_gold:  # Ensure there are remaining samples to evaluate
                new_labels = np.unique(filtered_gold + filtered_pred)  # Ensure labels are consistent
                precision = precision_score(filtered_gold, filtered_pred, labels=new_labels, average='macro', zero_division=0)
                recall = recall_score(filtered_gold, filtered_pred, labels=new_labels, average='macro', zero_division=0)
                f1 = f1_score(filtered_gold, filtered_pred, labels=new_labels, average='macro', zero_division=0)
            else:
                precision, recall, f1 = 0.0, 0.0, 0.0  # If everything is abstention, metrics are undefined

            print(f"Precision (excluding abstentions): {precision:.4f}")
            print(f"Recall (excluding abstentions): {recall:.4f}")
            print(f"F1-score (excluding abstentions): {f1:.4f}")

            # summary_df.loc[summary_index] = [f"{llm}-{prompt}-abs - {exp_name}", precision, recall, f1]
            # summary_index += 1

            # labels = np.unique(gold_results)  # Get unique class labels
            if exp_name == "standard":
                labels = [label for label in labels if label not in labels_to_remove]
            conf_matrix = confusion_matrix(gold_results, final_results, labels=labels)

            # Print Confusion Matrix
            # print("\nConfusion Matrix:")
            # print(conf_matrix)

            conf_df = pd.DataFrame(conf_matrix, index=labels, columns=labels)
            print("\nConfusion Matrix:")
            print(conf_df)

            plt.figure(figsize=(10, 8))
            sns.heatmap(conf_df, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)

            plt.xlabel("Predicted Labels")
            plt.ylabel("True Labels")
            plt.title(f"Confusion Matrix ({llm}-{prompt} - {exp_name})")
            plt.xticks(rotation=45)
            plt.yticks(rotation=45)
            plt.show()

            # Print Classification Report
            print("\nClassification Report:")
            print(classification_report(gold_results, final_results, zero_division=0))

print("\nSummary:")
print(summary_df)

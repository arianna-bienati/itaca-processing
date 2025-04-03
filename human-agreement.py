import glob
import os
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from itaca.webanno_tsv import webanno_tsv_read_file

skip_files = {"AC20PA_BAZ14M.tsv", "AC20PA_MOH28R.tsv", "AL07BN_BAS27F.tsv", "AL07BN_BAS28S.tsv",
                  "AL07BN_BIA21M.tsv"}
allowed_basenames = ["arianna.bienati@eurac.edu.tsv", "mariachiara.pascucci@phd.unipi.it.tsv"]
folder = "dataset/annotation"

results = {}
for basename in allowed_basenames:
    results[basename] = {}

for d in glob.glob(os.path.join(folder, "*")):

    # Check that d is a directory
    if not os.path.isdir(d):
        continue

    ann_file_name = os.path.basename(d)
    if ann_file_name in skip_files:
        continue

    # List all tsv files in the directory
    for f in glob.glob(os.path.join(d, "*.tsv")):
        # Check that f is a file
        if not os.path.isfile(f):
            continue

        # Get the basename of the file
        bn = os.path.basename(f)
        if not bn in allowed_basenames:
            continue

        doc = webanno_tsv_read_file(f)
        for annotation in doc.annotations:
            if annotation.layer == "webanno.custom.Connettivo":
                ann_id = f"{ann_file_name}-{annotation.tokens[0].sentence_idx}-{annotation.tokens[0].start}"
                if annotation.field == "CategoriaPDTB" and annotation.label != "*":
                    results[bn][ann_id] = annotation.label
                if annotation.field == "Connettivo" and annotation.label == "false":
                    if ann_id not in results[bn]:
                        results[bn][ann_id] = annotation.label

# Assuming `results` is your dictionary with two annotators
annotator_1 = allowed_basenames[0]
annotator_2 = allowed_basenames[1]

# Ensure both annotators have the same keys
all_keys = set(results[annotator_1].keys()).union(set(results[annotator_2].keys()))
for key in all_keys:
    if key not in results[annotator_1]:
        results[annotator_1][key] = "false"
    if key not in results[annotator_2]:
        results[annotator_2][key] = "false"

# Create a DataFrame for the confusion matrix
data = {
    annotator_1: [results[annotator_1][key] for key in all_keys],
    annotator_2: [results[annotator_2][key] for key in all_keys]
}
df = pd.DataFrame(data)

# Filter out labels that appear less than 10 times
label_counts = df.apply(pd.Series.value_counts).fillna(0).sum(axis=1)
labels_to_keep = label_counts[label_counts >= 10].index
df = df[df[annotator_1].isin(labels_to_keep) & df[annotator_2].isin(labels_to_keep)]

# Create the confusion matrix
confusion_matrix = pd.crosstab(df[annotator_1], df[annotator_2])

# Draw the heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(confusion_matrix, annot=True, cmap="YlGnBu", fmt="d")
plt.title("Comparison of human annotations", fontsize=16)
plt.xlabel(annotator_2, fontsize=14)
plt.ylabel(annotator_1, fontsize=14)
plt.tight_layout()  # Adjust the layout to make sure everything fits
plt.show()
import glob
import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np

from itaca.webanno_tsv import webanno_tsv_read_file

skip_files = {"AC20PA_BAZ14M.tsv", "AC20PA_MOH28R.tsv", "AL07BN_BAS27F.tsv", "AL07BN_BAS28S.tsv",
                  "AL07BN_BIA21M.tsv"}
allowed_basenames = ["arianna.bienati@eurac.edu.tsv", "mariachiara.pascucci@phd.unipi.it.tsv"]
folder = "dataset/annotation"

merge_text_labels = False
threshold = 10
figsize = (24, 20)

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
                text = annotation.text.lower()
                ann_id = f"{ann_file_name}-{annotation.tokens[0].sentence_idx}-{annotation.tokens[0].start}"
                if annotation.field == "CategoriaPDTB" and annotation.label != "*":
                    results[bn][ann_id] = (text, annotation.label)
                if annotation.field == "Connettivo" and annotation.label == "false":
                    if ann_id not in results[bn]:
                        results[bn][ann_id] = (text, annotation.label)

# Assuming `results` is your dictionary with two annotators
annotator_1 = allowed_basenames[0]
annotator_2 = allowed_basenames[1]

# Ensure both annotators have the same keys
all_keys = set(results[annotator_1].keys()).union(set(results[annotator_2].keys()))
for key in all_keys:
    if key not in results[annotator_1]:
        results[annotator_1][key] = ("", "false")
    if key not in results[annotator_2]:
        results[annotator_2][key] = ("", "false")

# Create a DataFrame for the confusion matrix
if merge_text_labels:
    data = {
        annotator_1: ["-".join(results[annotator_1][key]) for key in all_keys],
        annotator_2: ["-".join(results[annotator_2][key]) for key in all_keys]
    }
else:
    data = {
        annotator_1: [results[annotator_1][key][1] for key in all_keys],
        annotator_2: [results[annotator_2][key][1] for key in all_keys]
    }
df = pd.DataFrame(data)

# Filter out labels that appear less than 10 times
label_counts = df.apply(pd.Series.value_counts).fillna(0).sum(axis=1)
labels_to_keep = label_counts[label_counts >= threshold].index
df = df[df[annotator_1].isin(labels_to_keep) & df[annotator_2].isin(labels_to_keep)]

# Create the confusion matrix
confusion_matrix = pd.crosstab(df[annotator_1], df[annotator_2])
plt.figure(figsize=figsize)

# Case 1: Basic heatmap
# sns.heatmap(confusion_matrix, annot=True, cmap="YlGnBu", fmt="d")

# Case 2: Heatmap with masked zeros
# mask = confusion_matrix == 0  # Mask out zeros
# sns.heatmap(confusion_matrix, annot=True, cmap="YlGnBu", fmt="d", mask=mask)
# plt.imshow(mask, cmap='Greys', interpolation='none', alpha=0.3)  # overlay if you like

# Case 3: Define the colormap
cmap = plt.cm.YlGnBu
newcolors = cmap(np.linspace(0, 1, 256))
newcolors[0, :] = np.array([0.9, 0.9, 0.9, 1])  # light grey for zeros
newcmp = mcolors.ListedColormap(newcolors)
ax = sns.heatmap(confusion_matrix, annot=True, cmap=newcmp, fmt="d", annot_kws={"size": 18})

ax.tick_params(axis='x', labelsize=18)
ax.tick_params(axis='y', labelsize=18)

plt.title("Comparison of human annotations", fontsize=28)
plt.xlabel("")
plt.ylabel("")
plt.tight_layout()  # Adjust the layout to make sure everything fits
#plt.show()
plt.savefig("img/human-iaa.png")
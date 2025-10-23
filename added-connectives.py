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
initial_name = "INITIAL_CAS.tsv"
folder = "dataset/annotation"

original_connectives = set()
annotated_connectives = set()

def collect_connectives(f, initial=False):
    doc = webanno_tsv_read_file(f)
    ret = set()
    for annotation in doc.annotations:
        if annotation.layer == "webanno.custom.Connettivo":
            text = annotation.text.lower()
            if initial:
                ret.add(text)
            else:
                if annotation.field == "CategoriaPDTB" and annotation.label != "*":
                    ret.add(text)
                if annotation.field == "Connettivo" and annotation.label == "false":
                    ret.add(text)
    return ret

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

        if bn == initial_name:
            original_connectives.update(collect_connectives(f, True))
        else:
            if not bn in allowed_basenames:
                continue
            annotated_connectives.update(collect_connectives(f))

print(original_connectives)
print(annotated_connectives)
print(original_connectives - annotated_connectives)
print(annotated_connectives - original_connectives)

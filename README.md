# itaca-processing

This is a companion repository containing data and scripts for the work "Theoretical implications of automated discourse parsing in student writing" proposed for publication in the 2025 IJCoL Guest Edited Special Edition on "Bridging Theoretical Linguistics and Automated Language Processing".

## What it contains

In the repository you can find:

* `annotation_guidelines` contains:
    * the annotation guidelines used for the manual annotation of the evaluation sample as `README.md`
    * the report of misalignments after the first 5 documents used for training (`20250210_report_agreement.tsv`). A preliminary analysis of disagreements is available in `20250210_report_agreement.md`
    * Krippendorff alpha for each text for both connective detection and sense classification tasks  `20250307_iaa_kripp_inc_connective.txt` and `semantics.txt` files.
    * the presentation held at WS3 at the Congresso Internazionale SLI 2023(`Bienati_Frey_Aprosio_Facchinelli_2023_applicazione-delle-risorse_final_cut.pdf`).

* `dataset`:
    * `annotation`: contains all 40 manually annotated texts for the evaluation sample. In each folder, you can find annotations by Arianna Bienati and Mariachiara Pascucci and `INITIAL_CAS.tsv` contains the initial pre-annotated files.
    * `curation`: contains all 40 curated documents. Curated files have been jointly produced by Arianna Bienati and Mariachiara Pascucci.

* `img`: contains heatmaps comparing models outputs and human annotated labels.

* `txt-output`: contains the models' responses to experimental prompts.

* `itaca`: contains scripts used for the pre-processing of the itaca corpus.
    * `iaa.py`: calculates Cohen's kappa for all layers that have been manually annotated in the original ITACA corpus (not considered in this analysis).
    * `preprocess.py`: processes text files of the ITACA corpus. It uses TINT to analyze the content of each file, extracting linguistic features and generating annotations based on defined criteria. Relevant for our analysis is the connective pre-processing. Annotations are formatted in TSV format to be re-imported into Inception.
    * `webanno_tsv.py` and `webanno_tsv_custom.py`: (custom) library to handle the WebAnno TSV format.

* `agreement.py`: calculates agreement (Cohen's kappa) among human annotators and models' outputs
* `evaluate.py`: computes evaluation metrics such as precision, recall, and F1-score for each combination of LLM (gpt4o-llama 3.3 70b) and prompt (long-short). It visualizes the confusion matrix using a heatmap to provide insights into the model's performance across different classes.
* `human-agreement.py`: processes annotation data from TSV files in `dataset/annotation`, comparing the annotations made by the two different annotators. It visualizes the results in a heatmap, providing a visual comparison of human agreements and disagreements.
* `parse-files-1.py` / `parse-files-2.py`: prompts language models to generate responses about the presence and sense of connectives in test sentences, based on collected examples from the training data. The first one is related to prompt the LLM sentences grouped by connective candidates, the second one send the whole text to the LLM.

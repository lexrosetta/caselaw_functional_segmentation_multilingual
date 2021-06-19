from collections import Counter
import csv
import itertools
import os
from pathlib import Path
from utils import update_doc_layout


PWD = Path()
DIR_DATA = PWD/'data'
EXCLUDED = ('gloss_export_raw', 'czech-pdt-ud-2.5-191206.udpipe',
            'Germany-DE-1', 'Italy-IT-1', 'Poland-PL-1', 'United_States-EN-2')
CSV_NAMES = ('annotator-1.csv', 'annotator-2.csv')

L0_OoS = 'L0 Out of Scope'
L0_H = 'L0 Heading'
L1_BG = 'L1 Background'
L1_A = 'L1 Analysis'
L2_IS = 'L2 Introductory Summary'
L2_OUT = 'L2 Outcome'
NM = 'Not Marked'
TYPES = (L0_OoS, L0_H, L1_BG, L1_A, L2_IS, L2_OUT, NM)
TYPES_CROSS = [f'{t_1}-{t_2}' for t_1, t_2 in itertools.product(TYPES, TYPES)]


def build_doc2annotations(annotator_csv, annotations_dict):
    with open(annotator_csv, newline='') as csv_f:
        annotation_reader = csv.reader(csv_f, delimiter=',', quotechar='"')
        next(annotation_reader)  # Skip header
        for annotation in annotation_reader:
            doc = annotation[1]  # Document
            if doc not in annotations_dict:
                annotations_dict[doc] = []
            annotations_dict[doc].append({
                'type': annotation[0],
                'start': int(annotation[2]),
                'end': int(annotation[3])
            })


for dataset_name in os.listdir(DIR_DATA):
    if dataset_name in EXCLUDED:
        continue
    print(f'Working on {dataset_name}.')
    country, lang, mod = dataset_name.split('-')
    annotators_dict = {'annotator-1': {}, 'annotator-2': {}}
    for i, csv_name in enumerate(CSV_NAMES, start=1):
        annotator_csv = DIR_DATA / dataset_name / csv_name
        annotations_dict = annotators_dict[f'annotator-{i}']
        build_doc2annotations(annotator_csv, annotations_dict)
    annotations_dict_1 = annotators_dict['annotator-1']
    annotations_dict_2 = annotators_dict['annotator-2']
    with open(DIR_DATA / dataset_name / f'ia_agreement.csv', 'w',
              newline='', encoding='utf-8') as csv_f:
        dataset_writer = csv.writer(csv_f, delimiter=',', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
        dataset_writer.writerow(['Document'] + TYPES_CROSS)
        for doc_name, annotations_1 in annotations_dict_1.items():
            with open(DIR_DATA / dataset_name / 'texts' / doc_name,
                      encoding='utf-8') as txt_f:
                txt = txt_f.read()
            annotations_2 = annotations_dict_2[doc_name]
            out_of_scopes_1 = [a for a in annotations_1 if a['type'] == L0_OoS]
            headings_1 = [a for a in annotations_1 if a['type'] == L0_H]
            backgrounds_1 = [a for a in annotations_1 if a['type'] == L1_BG]
            analyses_1 = [a for a in annotations_1 if a['type'] == L1_A]
            intro_summaries_1 = [a for a in annotations_1 if a['type'] == L2_IS]
            outcomes_1 = [a for a in annotations_1 if a['type'] == L2_OUT]
            out_of_scopes_2 = [a for a in annotations_2 if a['type'] == L0_OoS]
            headings_2 = [a for a in annotations_2 if a['type'] == L0_H]
            backgrounds_2 = [a for a in annotations_2 if a['type'] == L1_BG]
            analyses_2 = [a for a in annotations_2 if a['type'] == L1_A]
            intro_summaries_2 = [a for a in annotations_2 if a['type'] == L2_IS]
            outcomes_2 = [a for a in annotations_2 if a['type'] == L2_OUT]
            doc_layout_1 = [NM] * len(txt)
            doc_layout_2 = [NM] * len(txt)
            doc_layout_1 = update_doc_layout(doc_layout_1, out_of_scopes_1)
            doc_layout_1 = update_doc_layout(doc_layout_1, backgrounds_1)
            doc_layout_1 = update_doc_layout(doc_layout_1, analyses_1)
            doc_layout_1 = update_doc_layout(doc_layout_1, intro_summaries_1)
            doc_layout_1 = update_doc_layout(doc_layout_1, outcomes_1)
            doc_layout_1 = update_doc_layout(doc_layout_1, headings_1)
            doc_layout_2 = update_doc_layout(doc_layout_2, out_of_scopes_2)
            doc_layout_2 = update_doc_layout(doc_layout_2, backgrounds_2)
            doc_layout_2 = update_doc_layout(doc_layout_2, analyses_2)
            doc_layout_2 = update_doc_layout(doc_layout_2, intro_summaries_2)
            doc_layout_2 = update_doc_layout(doc_layout_2, outcomes_2)
            doc_layout_2 = update_doc_layout(doc_layout_2, headings_2)
            doc_layout = [f'{c_1}-{c_2}' for c_1, c_2
                          in zip(doc_layout_1, doc_layout_2)]
            char_counts = Counter(doc_layout)

            dataset_writer.writerow(
                [doc_name] + [char_counts.get(t, 0) for t in TYPES_CROSS]
            )

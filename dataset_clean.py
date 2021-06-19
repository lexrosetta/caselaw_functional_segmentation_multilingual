import csv
import os
from pathlib import Path
import re


PWD = Path()
DIR_DATA = PWD/'data'
EXCLUDED = ('czech-pdt-ud-2.5-191206.udpipe',)
DIR_TEXTS_NAME = 'texts'

for dataset_name in os.listdir(DIR_DATA):
    if dataset_name in EXCLUDED:
        continue
    annotations_dict = {}
    for csv_name in os.listdir(DIR_DATA/dataset_name):
        if not csv_name.endswith('csv'):
            continue
        annotations_dict[csv_name[:-4]] = {}
        with open(DIR_DATA/dataset_name/csv_name, newline='') as csv_f:
            annotation_reader = csv.reader(csv_f, delimiter=',', quotechar='"')
            next(annotation_reader)  # Skip header
            for annotation in annotation_reader:
                doc = annotation[1]  # Document
                if doc not in annotations_dict[csv_name[:-4]]:
                    annotations_dict[csv_name[:-4]][doc] = []
                annotations_dict[csv_name[:-4]][doc].append({
                    'type': annotation[0],
                    'start': int(annotation[2]),
                    'end': int(annotation[3])
                })
    for annotator_id, annotator_data in annotations_dict.items():
        txt_dict = {}
        for txt_name in os.listdir(DIR_DATA / dataset_name / DIR_TEXTS_NAME):
            with open(DIR_DATA / dataset_name / DIR_TEXTS_NAME / txt_name,
                      encoding='utf-8') as txt_f:
                txt_content = txt_f.read()
            txt_dict[txt_name] = txt_content
        for doc_name, doc_txt in txt_dict.items():
            annotations = sorted(annotator_data.get(doc_name, []),
                                 key=lambda a: (a['start'], a['end']))
            removal_mask = [1] * len(annotations)

            for i, focused_annotation in enumerate(annotations):
                f_start = focused_annotation['start']
                f_end = focused_annotation['end']
                f_len = f_end - f_start
                f_type = focused_annotation['type']
                if f_type in ('L0 Out of Scope', 'L0 Heading'):
                    if removal_mask[i] == 0:
                        continue
                    txt_dict[doc_name] = txt_dict[doc_name][:f_start]\
                        + txt_dict[doc_name][f_end:]
                    for j, annotation in enumerate(annotations):
                        if removal_mask[j] == 0:
                            continue
                        a_start, a_end = annotation['start'], annotation['end']
                        if a_start >= f_start and a_end <= f_end:
                            removal_mask[j] = 0
                        elif a_start <= f_start and a_end <= f_start:
                            pass
                        elif a_start >= f_end and a_end >= f_end:
                            annotations[j]['start'] -= f_len
                            annotations[j]['end'] -= f_len
                        elif f_start < a_end <= f_end:
                            annotations[j]['end'] = f_start
                        elif f_start <= a_start < f_end:
                            annotations[j]['start'] = f_start
                            annotations[j]['end'] -= f_len
                        elif f_start >= a_start and f_end <= a_end:
                            annotations[j]['end'] -= f_len
            annotator_data[doc_name] = [a for a, rm
                                        in zip(annotations, removal_mask) if rm]

            # Fix missing Background under Introductory Summary.
            intro_summaries = [a for a in annotator_data[doc_name]
                               if a['type'] == 'L2 Introductory Summary']
            for intro_summary in intro_summaries:
                annotator_data[doc_name].append({
                    'start': intro_summary['start'],
                    'end': intro_summary['end'],
                    'type': 'L1 Background'
                })

            # Fix missing Analysis under Outcome.
            outcomes = [a for a in annotator_data[doc_name]
                        if a['type'] == 'L2 Outcome']
            for outcome in outcomes:
                annotator_data[doc_name].append({
                    'start': outcome['start'],
                    'end': outcome['end'],
                    'type': 'L1 Analysis'
                })

            # Collapse consecutive series of annotations into one.
            types_dict = {}
            for annotation in annotator_data[doc_name]:
                a_type = annotation['type']
                if a_type not in ('L1 Background', 'L1 Analysis', 'L2 Outcome'):
                    continue
                if a_type not in types_dict:
                    types_dict[a_type] = []
                types_dict[a_type].append(annotation)
            new_annotations = []
            for t_annotations in types_dict.values():
                t_annotations.sort(key=lambda a: (a['start'], a['end']))
                new_t_annotations = []
                for annotation in t_annotations:
                    if not new_t_annotations:
                        new_t_annotations.append(annotation)
                    else:
                        last_end = new_t_annotations[-1]['end']
                        start, end = annotation['start'], annotation['end']
                        if end > last_end:
                            if start <= last_end:
                                new_t_annotations[-1]['end'] = end
                            else:
                                sep = txt_dict[doc_name][last_end:start]
                                if re.match(r'^[^A-z]+$', sep):
                                    new_t_annotations[-1]['end'] = end
                                else:
                                    new_t_annotations.append(annotation)
                new_annotations.extend(new_t_annotations)
            annotator_data[doc_name] = new_annotations

        # Save the cleaned docs for each annotator
        cleaned_txt_dir = f'{DIR_TEXTS_NAME}-clean-{annotator_id}'
        os.makedirs(DIR_DATA/dataset_name/cleaned_txt_dir, exist_ok=True)
        for doc_name, doc_txt in txt_dict.items():
            with open(DIR_DATA/dataset_name/cleaned_txt_dir/doc_name, 'w',
                      encoding='utf-8') as txt_f:
                txt_f.write(doc_txt)

        # Save the cleaned annotations for each annotator
        with open(DIR_DATA/dataset_name/f'{annotator_id}-clean.csv', 'w',
                  newline='', encoding='utf-8') as csv_f:
            dataset_writer = csv.writer(csv_f, delimiter=',', quotechar='"',
                                        quoting=csv.QUOTE_MINIMAL)
            dataset_writer.writerow(('Type', 'Document', 'Start', 'End'))
            for doc_name, annotations in annotator_data.items():
                for annotation in annotations:
                    dataset_writer.writerow((annotation['type'],
                                             doc_name,
                                             annotation['start'],
                                             annotation['end']))

import csv
import os
from pathlib import Path
import re
from utils import load_spacy, update_doc_layout, MODELS_DICT


PWD = Path()
DIR_DATA = PWD/'data'
EXCLUDED = ('Czech_Republic-CZ-1', 'czech-pdt-ud-2.5-191206.udpipe')
L1_BG = 'L1 Background'
L1_A = 'L1 Analysis'
L2_OUT = 'L2 Outcome'


for dataset_name in os.listdir(DIR_DATA):
    if dataset_name in EXCLUDED:
        continue
    print(f'Working on {dataset_name}:')
    country, lang, mod = dataset_name.split('-')
    nlp = load_spacy(MODELS_DICT[lang])
    for csv_name in os.listdir(DIR_DATA / dataset_name):
        if not csv_name.endswith('clean.csv'):
            continue
        annotator_id = csv_name[:-10]
        print(f'  - {annotator_id}')
        annotations_dict = {}
        with open(DIR_DATA / dataset_name / csv_name, newline='') as csv_f:
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
        with open(DIR_DATA / dataset_name/f'{annotator_id}-ICAIL2021.csv', 'w',
                  newline='', encoding='utf-8') as csv_f:
            dataset_writer = csv.writer(csv_f, delimiter=',', quotechar='"',
                                        quoting=csv.QUOTE_MINIMAL)
            dataset_writer.writerow(('Type', 'Document', 'Ordering', 'Text'))
            for doc_name, annotations in annotations_dict.items():
                backgrounds = [a for a in annotations if a['type'] == L1_BG]
                analyses = [a for a in annotations if a['type'] == L1_A]
                outcomes = [a for a in annotations if a['type'] == L2_OUT]
                with open(DIR_DATA/dataset_name/f'texts-clean-{annotator_id}'/
                          doc_name, encoding='utf-8') as txt_f:
                    txt_content = txt_f.read()
                doc_layout = [None] * len(txt_content)
                doc_layout = update_doc_layout(doc_layout, backgrounds)
                doc_layout = update_doc_layout(doc_layout, analyses)
                doc_layout = update_doc_layout(doc_layout, outcomes)
                new_annotations = []
                curr_start, offset, curr_type = None, 0, 0
                for offset, char_type in enumerate(doc_layout):
                    if char_type != curr_type:
                        if curr_type and offset - curr_start > 0:
                            new_annotations.append({
                                'start': curr_start,
                                'end': offset,
                                'type': curr_type
                            })
                        curr_start = offset
                        curr_type = char_type
                if curr_type and offset - curr_start > 0:
                    new_annotations.append({
                        'start': curr_start,
                        'end': offset,
                        'type': curr_type
                    })
                sent_i = 0
                for annotation in new_annotations:
                    start, end = annotation['start'], annotation['end']
                    annotation_txt = txt_content[start:end]
                    a_type = annotation['type']
                    doc = nlp(annotation_txt)
                    sentences = []
                    for s in doc.sents:
                        sent = re.sub(r'\s+', ' ', s.text.replace('\n', ' ')).strip()
                        if not sentences or\
                                (re.match(r'.+[a-z]{3,}.+', sent)
                                 and re.match(r'[A-Z]', sent)
                                 and len(sent) > 20
                                 and re.match(r'.+[a-z]{3,}.+', sentences[-1])
                                 and len(sentences[-1]) > 20):
                            sentences.append(sent)
                        else:
                            sentences[-1] += ' ' + sent
                    if country == 'France':
                        new_sentences = []
                        for sent in sentences:
                            new_sentences.extend(
                                s.strip() for s in sent.split(';') if s
                            )
                        sentences = new_sentences
                    for sent in (s for s in sentences if s):
                        dataset_writer.writerow(
                            (a_type, doc_name, sent_i, sent))
                        sent_i += 1

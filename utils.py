import spacy
from spacy.cli import download
import spacy_udpipe


MODELS_DICT = {
    'EN': 'en_core_web_lg',
    'FR': 'fr_core_news_lg',
    'DE': 'de_core_news_lg',
    'IT': 'it_core_news_lg',
    'PL': 'pl_core_news_lg',
    'CZ': 'data/czech-pdt-ud-2.5-191206.udpipe'
}


def load_spacy(model_str):
    try:
        return spacy.load(model_str)
    except:
        try:
            download(model_str)
            return spacy.load(model_str)
        except:
            return spacy_udpipe.load_from_path(lang='cs', path=model_str)


def update_doc_layout(doc_layout, annotations):
    for annotation in annotations:
        start, end = annotation['start'], annotation['end']
        a_type = annotation['type']
        doc_layout[start:end] = [a_type] * (end - start)
    return doc_layout

import re
import sys
import os
import random
import lxml.etree as ET
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk import word_tokenize

from .utils import write_percent_progress
from .models import Paper, Author, Authorship, Coauthorship


STEMMER = SnowballStemmer("english")

SW = stopwords.words('english') + [',', ':', ';', '.', '(', ')',
                                   '{', '}', '?', "'", '"', '[',
                                   ']', 'the', 'in', 'we', '``',
                                   '=', 'x', 'n', '-1/2', 'n^',
                                   '<', '>', 'k', 'g', 'p', '\\leq',
                                   'm\\', "''", ]

BASE_URL = '{http://arxiv.org/OAI/arXiv/}'

class PaperLoader:

    def __init__(self, path, debug=-1, shuffle=False):
        self.EXP = re.compile(r'\$.*\$')
        self.STEMMER = SnowballStemmer("english")
        self.SW = stopwords.words('english') + [
            ',', ':', ';', '.', '(', ')',
            '{', '}', '?', "'", '"', '[',
            ']', 'the', 'in', 'we', '``',
            '=', 'x', 'n', '-1/2', 'n^',
            '<', '>', 'k', 'g', 'p', '\\leq',
            'm\\', "''", ]

        self.BASE_URL = '{http://arxiv.org/OAI/arXiv/}'

        self.data_path = path
        self.filenames = []

    def papers_authors_in_db(self) -> None:
        all_files, total = self.list_all_files_and_prep()
        for i in range(total):
            if i%50 == 0:
                write_percent_progress(i, total)
            self.get_paper_authors_from_filename(all_files[i], max_len=15)
        write_percent_progress(total, total)

    def list_all_files_and_prep(self):
        list_of_files = list_all_file(self.data_path)
        all_files = []

        for filename in list_of_files:
            if filename.endswith('xml'):
                all_files.append(filename)

        if self.shuffle:
            random.shuffle(all_files)

        if self.debug > 0:
            all_files = all_files[:debug]

        total = len(all_files)

        return all_files, total
    
def list_all_files_and_prep(path, debug=None, shuffle=False):
    list_of_files = list_all_file(path)
    all_files = []

    for filename in list_of_files:
        if filename.endswith('xml'):
            all_files.append(filename)

    if shuffle:
        random.shuffle(all_files)

    if debug is not None:
        all_files = all_files[:debug]

    total = len(all_files)

    return all_files, total


def papers_authors_in_db(path: str, debug=None,
                         shuffle=False):
    all_files, total = list_all_files_and_prep(path, debug, shuffle)
    sys.stdout.write("Percent achieved: 0.00%")
    for i in range(total):
        if i%50 == 0:
            sys.stdout.write("\rPercent achieved: {0:.2f}%  ".format(100*i/total))

        get_paper_authors_from_filename(all_files[i], max_len=15)

    sys.stdout.write("\rPercent achieved: 100.00%\n")


def create_paper(doi, title, abstract, date, categories):
    tokens = [STEMMER.stem(w.lower()) for w in word_tokenize(abstract)
              if w.lower() not in SW and not w.isdigit() and len(w) >= 2 and not
              w.startswith("'")]

    if len(tokens) <= 5:
        return None, None

    abstract_clean = preprocess_abstract(abstract)

    p = Paper.objects.get_or_create(title=title, abstract=abstract_clean, doi=doi,
                                    categories=categories, date=date, tokens=tokens)

    return p

def decompose_authors(raw):
    """ Create author objects from raw strings."""
    authors = []

    for xml_auth in raw:
        authors.append(Author.objects.get_or_create(
            keyname=helper(xml_auth.find(BASE_URL + 'keyname')),
            forenames=helper(xml_auth.find(BASE_URL + 'forenames')),
            affiliation=helper(xml_auth.find(BASE_URL + 'affiliation'))
        )[0])

    return authors


def get_paper_authors_from_filename(filename: str, max_len=None):
    content = open(filename)
    element = ET.parse(content)

    raw_authors = element.find(BASE_URL + 'authors')

    if Paper.objects.filter(doi=helper(element.find(BASE_URL + 'id'))).exists():
        return

    p, new = create_paper(helper(element.find(BASE_URL + 'id')),
                          helper(element.find(BASE_URL + 'title')),
                          helper(element.find(BASE_URL + 'abstract')),
                          helper(element.find(BASE_URL + 'created')),
                          helper(element.find(BASE_URL + 'categories'), '').split())
    if not new:
        return

    if p is None:
        return
    
    authors = decompose_authors(raw_authors)

    create_authorships(authors, p)

def create_authorships(authors, paper):
    authorships = []
    for auth in authors:
        authorships.append(Authorship.objects.get_or_create(aid=auth, pid=paper))


def helper(elem: ET.Element, opt=None):
    """Ensure that we return None when the element is empty."""
    if hasattr(elem, 'text'):
        return elem.text if elem.text is not None else ''

    return '' if opt is None else opt

def listdir_nodot(path):
    return [item for item in os.listdir(path=path) if not item.startswith('.')]

def list_all_file(path):
    all_files = []

    for direct1 in listdir_nodot(path=path):
        cur_path1 = os.path.join(path, direct1)

        for direct2 in listdir_nodot(path=cur_path1):
            cur_path2 = os.path.join(cur_path1, direct2)

            for direct3 in listdir_nodot(path=cur_path2):
                cur_path3 = os.path.join(cur_path2, direct3)

                for direct4 in listdir_nodot(path=cur_path3):
                    cur_path4 = os.path.join(cur_path3, direct4)

                    for filename in listdir_nodot(path=cur_path4):
                        all_files.append(os.path.join(cur_path4, filename))
    return all_files

def preprocess_abstract(abstract: str):
    abstract_clean = abstract.replace("\n", " ").strip().replace(
        "  ", " ").replace(
            "  ", " ").replace(
                "\"", "").replace("\'", "")
    return abstract_clean


def prep_temp_file():
    with open('tmp.txt', 'w') as f:
        for paper in Paper.objects.all():
            f.write(' '.join(paper.tokens) + '\n')

def build_model():
    model = ftext.train_unsupervised('tmp.txt', 'skipgram', epoch=20, lr=0.1)
    model.save_model('model.bin')
    os.remove('tmp.txt')
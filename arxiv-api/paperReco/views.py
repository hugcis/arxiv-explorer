import os
import pickle
import sys

import ot
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from django.http import HttpResponse, Http404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from sklearn.metrics.pairwise import euclidean_distances

from  .initiate import papers_authors_in_db
from .models import Paper, Author
from .serializers import (AuthorSerializer,
                          PaperSerializer,
                          PaperWithAuthors,
                          PaperWithAuthorsSerializer)

def get_tfidf() -> TfidfVectorizer:
    """ This function either loads a serialized (pickled) representation of
    a TF-IDF vectorizer trained on all words from the abstracts of all papers
    if it exists, or creates it and saves it.
    TODO: Implement a refresh funcitonality to update the vectorizer as papers
    are added
    """
    if 'vectorizer.pkl' in os.listdir():
        return pickle.load(open('vectorizer.pkl', 'rb'))
    else:
        tfidf = TfidfVectorizer(ngram_range=(1,2), max_features=500000)
        tfidf.fit([' '.join(paper.tokens) for paper in Paper.objects.all()])
        pickle.dump(tfidf, open('vectorizer.pkl', 'wb'))

        return tfidf

# Load the TF-IDF vectorizer in memory for efficiency in response time
TFIDF = get_tfidf()

class PaperPagination(PageNumberPagination):
    """ The pagination class for returning the results.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20

class AuthorsList(generics.ListAPIView):
    """ API view returning a list of authors.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class AuthorsDetails(generics.RetrieveAPIView):
    """ API view returning a single author.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class PapersList(generics.ListAPIView):
    """ API view returning a list of papers.
    """
    queryset = Paper.objects.all()
    serializer_class = PaperSerializer
    pagination_class = PaperPagination

class PapersDetails(generics.RetrieveAPIView):
    """ API view returning a single paper.
    """
    queryset = Paper.objects.all()
    serializer_class = PaperSerializer

class LatestPapersDetails(generics.ListAPIView):
    """ API view returning the latest papers.
    """
    queryset = Paper.objects.all()
    serializer_class = PaperWithAuthorsSerializer
    pagination_class = PaperPagination

    def list(self, request: Request) -> Response:
        categories = request.GET.get('categories')
        if categories is not None:
            categories = categories.split(',')

        keywords = request.GET.get('keywords')
        if keywords is not None:
            keywords = keywords.split(',')

        base_queryset = self.get_queryset()
        if categories is not None:
            for category in categories:
                base_queryset = base_queryset.filter(categories__contains=[category])

        if keywords is not None:
            for word in keywords:
                base_queryset = base_queryset.filter(abstract__icontains=word)

        queryset = self.paginate_queryset(base_queryset.order_by('-date'))

        serializer = self.get_serializer(
            [PaperWithAuthors(paper, paper.authorship_set.all()) for paper in queryset], 
            many=True
        )

        return self.get_paginated_response(serializer.data)


class PapersDetailsByDOI(generics.RetrieveAPIView):
    """ API view returning a single paper from its doi.
    """
    queryset = Paper.objects.all()
    serializer_class = PaperSerializer
    lookup_field = 'doi'


class PaperNeighbors(APIView):
    def get(self, request, doi):
        
        phrases = []
        dates = []
        dois = {}

        main_paper = Paper.objects.get(doi=doi)

        index = 0 
        main_date = main_paper.date
        for n, paper in enumerate(Paper.objects.filter(
            date__year__gte=main_date.year-1).exclude(
                date__year__gt=main_date.year + 1)):

            phrases.append(' '.join(paper.tokens))
            dates.append(paper.date)
            dois[n] = paper.doi

            if paper.doi == doi:
                index = n

        #TFIDF = TfidfVectorizer()
        matrix = TFIDF.transform(phrases)
        dot = np.dot(matrix[index, :], matrix.T).toarray().reshape(-1)*date_decay(
            np.array([(main_date - d).days for d in dates]))

        sorted_indexes = np.argsort(-dot)[:10]
        sorted_dois = [dois[i] for i in sorted_indexes]

        results = []

        for doi in sorted_dois:
            results.append(Paper.objects.get(doi=doi))

        serializer = PaperSerializer(
            results,
            many=True
        )
        return Response(serializer.data)
        # vocab = pickle.load(open('vocab.pkl', 'rb'))
        # log_count_all = np.log(sum(vocab.values()))

        # for word in vocab:
        #     vocab[word] = log_count_all - np.log(vocab[word])

        # main_paper = Paper.objects.get(doi=doi)
        # tokens_set = set(main_paper.tokens)

        # other_papers = Paper.objects.all()
        # length = other_papers.count()

        # dictionary = pickle.load(open('dictionary.pkl', 'rb'))
        # word_vectors = np.load('embed.npy')

        # paper_dist = []

        # for i, other in enumerate(other_papers):
        #     if i%50 == 0 :
        #         sys.stdout.write("\r{:.2f}% Done    ".format(100*i/length))
        #     arr_main, arr_other, union_idx = compute_support_arrays(main_paper.tokens,
        #                                                             other.tokens,
        #                                                             tokens_set, vocab)
        #     dists = euclidean_distances(get_word_vector(union_idx, dictionary, word_vectors))
        #     distance = ot.emd2(arr_main, arr_other, dists)
        #     paper_dist.append((other, distance))


        # serializer = PaperSerializer(
        #     [i[0] for i in sorted(paper_dist, key=lambda x: x[1])[:10]],
        #     many=True
        # )
        # return Response(serializer.data)
    

def helper(txt, txt_dict, vocab):
    for word in txt:
        if word in txt_dict:
            txt_dict[word] += 1
        else:
            txt_dict[word] = 1

    
    for word in txt_dict:
        txt_dict[word] = txt_dict[word]*vocab[word]

    return txt_dict

def get_word_vector(index, dictionary, word_vectors):
    access = np.array([dictionary[i] for i in index])
    return word_vectors[access, :]

def compute_support_arrays(txt1, txt2, word1, vocab):
    dictio = word1.union(set(txt2))
    vocab = dict(zip(dictio, range(len(dictio))))
    txt1_dict = {}
    txt2_dict = {}
    
    txt1_dict = helper(txt1, txt1_dict, vocab)
    txt2_dict = helper(txt2, txt2_dict, vocab)
    
    union_idx = np.array(list(dictio))

    txt1_arr = np.zeros_like(union_idx, dtype=np.int)
    txt1_arr[list(set([vocab[i] for i in txt1]))] = np.array(list(txt1_dict.values()))
    
    txt2_arr = np.zeros_like(union_idx, dtype=np.int)
    txt2_arr[list(set([vocab[i] for i in txt2]))] = np.array(list(txt2_dict.values()))
    
    return txt1_arr/txt1_arr.sum(), txt2_arr/txt2_arr.sum(), union_idx


def date_decay(arr):
    return np.exp(-(arr**2/1825**2))

def DBFill(request):
    print("Filling DB")
    papers_authors_in_db('../data')
    return HttpResponse()

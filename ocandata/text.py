import pandas as pd
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from rank_bm25 import BM25Okapi

stemmer = PorterStemmer()


def get_language(language: str):
    if language:
        language = language.lower()
        if language == 'french' or language == 'fr' or language.startswith('fran'):
            return 'French'


def stem(string: str):
    return stemmer.stem(string)


def preprocess(string: str):
    string = string.lower()
    return [stem(word) for word in word_tokenize(string)]


class Bm25Index:

    def __init__(self, column):
        column = column.fillna('').astype(str).apply(preprocess)
        self.bm25 = BM25Okapi(column.tolist())

    def get_scores(self, sentence, n=10):
        tokenized_query = preprocess(sentence)
        doc_scores = self.bm25.get_scores(tokenized_query)
        top_indices = (-doc_scores).argsort()[:n]
        top_scores = doc_scores[top_indices]
        return top_indices, top_scores

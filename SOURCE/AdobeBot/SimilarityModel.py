#
import os
from gensim import corpora, models, similarities
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import datetime
import requests
import json
import logging

def similarity_matrix(docs, model=None):
    start_time = datetime.datetime.now()
    dim = len(docs)
    matrix = np.zeros((dim, dim))
    for i, doc in enumerate(docs):
        train_set = docs[:i] + docs[i + 1:]
        index = model(train_set)
        sims = index.similarity(doc)
        for doc_id, sim in sims:
            if doc_id >= i:
                doc_id += 1
            matrix[i, doc_id] = sim
    end_time = datetime.datetime.now()
    print('Training started: {0}'.format(start_time))
    print('Training complete: {0}'.format(end_time))
    print('Time spent training: {0}'.format(end_time - start_time))
    return matrix


# Classes/helpers for topic modelling
class BaseModel(object):
    """Base TFIDF model. Take a corpus of documents, clean, and
       then create a dictionary, MmCorpus. Implements similarity query method."""

    def __init__(self, documents, directory='models', filename='output'):
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.dict_path = '{0}/{1}.dict'.format(directory, filename)
        self.corpus_path = '{0}/{1}.mm'.format(directory, filename)
        texts = process_documents(documents)
        dictionary = corpora.Dictionary(texts)
        dictionary.save(self.dict_path)
        bows = [dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(self.corpus_path, bows)

    def similarity(self, document):
        dictionary = corpora.Dictionary.load(self.dict_path)
        vec_bow = dictionary.doc2bow(document.lower().split())
        vec_lsi = self.model[vec_bow]
        sims = self.index[vec_lsi]
        return sorted(list(enumerate(sims)), key=lambda x: x[1], reverse=True)

    def transform(self):
        corpus = corpora.MmCorpus(self.corpus_path)
        return self.model[corpus_tfidf]


class TFIDFModel(BaseModel):
    """TFIDModel."""

    def __init__(self, documents, directory='models', filename='output'):
        super(TFIDFModel, self).__init__(
            documents, directory='models', filename='output')
        self.tfidf_path = '{0}/{1}.model'.format(directory, filename)
        corpus = corpora.MmCorpus(self.corpus_path)
        self.model = models.TfidfModel(corpus)
        self.index = similarities.MatrixSimilarity(self.model[corpus])


class LSIModel(BaseModel):
    """LSI model."""

    def __init__(self, documents, directory='models', filename='output', num_topics=2):
        super(LSIModel, self).__init__(
            documents, directory='models', filename='output')
        dictionary = corpora.Dictionary.load(self.dict_path)
        corpus = corpora.MmCorpus(self.corpus_path)
        self.model = models.LsiModel(corpus, id2word=dictionary,
                                     num_topics=num_topics)
        self.index = similarities.MatrixSimilarity(self.model[corpus])


class LDAModel(BaseModel):
    """LDA Model."""

    def __init__(self, documents, directory='models', filename='output', num_topics=2):
        super(LDAModel, self).__init__(
            documents, directory='models', filename='output')
        dictionary = corpora.Dictionary.load(self.dict_path)
        corpus = corpora.MmCorpus(self.corpus_path)
        self.model = models.LdaModel(
            corpus, id2word=dictionary, num_topics=num_topics)
        self.index = similarities.MatrixSimilarity(self.model[corpus])


class LSITFIDFModel(TFIDFModel):
    """TFIDFLS model wrapped with LSI model."""

    def __init__(self, documents, directory='models', filename='output', num_topics=2):
        super(LSITFIDFModel, self).__init__(
            documents, directory='models', filename='output')
        dictionary = corpora.Dictionary.load(self.dict_path)
        corpus = corpora.MmCorpus(self.corpus_path)
        corpus_tfidf = self.model[corpus]
        self.model = models.LsiModel(corpus_tfidf, id2word=dictionary,
                                     num_topics=num_topics)
        self.index = similarities.MatrixSimilarity(self.model[corpus_tfidf])

    def transform(self):
        corpus = corpora.MmCorpus(self.corpus_path)
        tdidf = models.TfidfModel.load(self.tfidf_path)
        corpus_tfidf = tdidf[corpus]
        return self.model[corpus_tfidf]


def process_documents(documents):
    """Remove stopwords, tokenize by document, use TextBlob to clean
       punctuation, then remove words that only occur once in the corpus."""
    stpwrds = stopwords.words('english')
    tokenizer = RegexpTokenizer(r'\w+')
    texts = [[w for w in tokenizer.tokenize(doc.lower()) if w not in stpwrds]
             for doc in documents]
    all_tokens = sum(texts, [])
    tokens_once = set(
        w for w in set(all_tokens) if all_tokens.count(w) == 1
    )
    return [[w for w in text if w not in tokens_once]
            for text in texts]

import itertools
import pickle
import string

import numpy as np
import pandas as pd
from multiprocessing.pool import ThreadPool as Pool
from nltk import PorterStemmer, word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from BM25 import BM25
import tabulate


def preProcess(text, stopword_set, stemmer):
    cleaned_text = text.translate(str.maketrans('', '', '!"#$%&\'()*+,.<=>?@[]^`{|}~' + u'\xa0'))
    cleaned_text = cleaned_text.lower()
    cleaned_text = cleaned_text.translate(str.maketrans(string.whitespace, ' ' * len(string.whitespace), ''))

    tokenized_text = word_tokenize(cleaned_text)
    sw_removed_text = [word for word in tokenized_text if word not in stopword_set]
    sw_removed_text = [word for word in sw_removed_text if len(word) > 2]
    stemmed_text = ' '.join([stemmer.stem(w) for w in sw_removed_text])

    return stemmed_text

dataset = pd.read_csv('../resource/anime.csv')
stopword_set = set(stopwords.words())
stemmer = PorterStemmer()
pool = Pool(8)

cleaned_name = pool.starmap(preProcess, zip(dataset.Name, itertools.repeat(stopword_set), itertools.repeat(stemmer)))
cleaned_genres = pool.starmap(preProcess, zip(dataset.Genres, itertools.repeat(stopword_set), itertools.repeat(stemmer)))
cleaned_engName = pool.starmap(preProcess, zip(dataset.English_name, itertools.repeat(stopword_set), itertools.repeat(stemmer)))
cleaned_premiered = pool.starmap(preProcess, zip(dataset.Premiered, itertools.repeat(stopword_set), itertools.repeat(stemmer)))
cleaned_licensors = pool.starmap(preProcess, zip(dataset.Licensors, itertools.repeat(stopword_set), itertools.repeat(stemmer)))
cleaned_studios = pool.starmap(preProcess, zip(dataset.Studios, itertools.repeat(stopword_set), itertools.repeat(stemmer)))

data_texts = pd.DataFrame([cleaned_name, cleaned_engName, cleaned_genres, cleaned_premiered, cleaned_licensors, cleaned_studios], index=['name', 'eng_name', 'genres', 'premiered', 'licensors', 'studios']).T
# data_texts = pd.DataFrame([cleaned_name, cleaned_engName+cleaned_genres+cleaned_premiered+cleaned_licensors+cleaned_studios], index=['title', 'describtion']).T

pickle.dump(dataset, open('../resource/anime.pkl', 'wb'))
vectorizer = TfidfVectorizer(ngram_range=(1, 1))
bm25 = BM25(vectorizer)
bm25.fit(cleaned_name)
pickle.dump(bm25, open('../resource/BM25SearchByName.pkl', 'wb'))
# score = bm25.transform('full metal alchemist')
# rank = np.argsort(score)[::-1]
# print(dataset.iloc[rank[:5]].to_markdown())


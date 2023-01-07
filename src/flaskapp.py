import string
import numpy as np
from flask import Flask, request
from nltk import PorterStemmer, word_tokenize
import pickle


def preProcess(text, stopword_set, stemmer):
    cleaned_text = text.translate(str.maketrans('', '', '!"#$%&\'()*+,.<=>?@[]^`{|}~' + u'\xa0'))
    cleaned_text = cleaned_text.lower()
    cleaned_text = cleaned_text.translate(str.maketrans(string.whitespace, ' ' * len(string.whitespace), ''))

    tokenized_text = word_tokenize(cleaned_text)
    sw_removed_text = [word for word in tokenized_text if word not in stopword_set]
    sw_removed_text = [word for word in sw_removed_text if len(word) > 2]
    stemmed_text = ' '.join([stemmer.stem(w) for w in sw_removed_text])

    return stemmed_text


app = Flask(__name__)
app.vecterizer = pickle.load(open('../resource/BM25SearchByName.pkl', 'rb'))
app.animeInfo = pickle.load(open('../resource/anime.pkl', 'rb'))


@app.route('/SerachByName', methods=['GET'])
def FlaskSearhByName():
    response_object = {'status': 'success'}
    argList = request.args.to_dict(flat=False)
    query_term = argList['query'][0]
    score = app.vecterizer.transform(query_term)
    rank = np.argsort(score)[::-1]
    response_object = app.animeInfo.iloc[rank[:10]].to_json()
    return response_object


if __name__ == '__main__':
    app.run(debug=True)

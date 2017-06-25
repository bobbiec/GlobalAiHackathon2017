#!/usr/bin/env python3
import requests
import json
import pickle
import nltk.tokenize.punkt as pkt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from .actionRequired.train import features

API_URL = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment"
API_KEY = "REPLACEME"

# Preserve newlines in tokenization
# From https://stackoverflow.com/questions/33139531/preserve-empty-lines-with-nltks-punkt-tokenizer
class CustomLanguageVars(pkt.PunktLanguageVars):
    _period_context_fmt = r"""
        \S*                          # some word material
        %(SentEndChars)s             # a potential sentence ending
        \s*                       #  <-- THIS is what I changed
        (?=(?P<after_tok>
            %(NonWord)s              # either other punctuation
            |
            (?P<next_tok>\S+)     #  <-- Normally you would have \s+ here
        ))"""

def getSentiment(text, language="en"):
    ct = pkt.PunktSentenceTokenizer(lang_vars=CustomLanguageVars())
    sentences = ct.tokenize(text)
    # sentences = [sentence.strip() for sentence in sentences if sentence != ""]

    documents = []
    for i, sentence in enumerate(sentences):
        print(sentence)
        documents.append({"language":language, "id": str(i),"text": sentence})

    r = requests.post(API_URL,
                      json={"documents": documents},
                      headers={"Ocp-Apim-Subscription-Key": API_KEY,
                               "content-type": "application/json"})

    if r.status_code != 200:
        print("Something went wrong: %s" % r.text)
        return ([r.text], [0])

    results = json.loads(r.text)

    scores = [None] * len(sentences)
    for tup in results["documents"]:
        scores[int(tup["id"])] = tup["score"]
    return zip(sentences, scores)

def nltkAdjust(sentiment, weight=0.5):
    result = []
    sid = SentimentIntensityAnalyzer()
    for sentence, score in sentiment:
        ss = sid.polarity_scores(sentence)
        oldScore = (score-0.5) * 2
        newScore = weight*(ss["compound"]) + (1-weight)*(oldScore)
        result.append((sentence, newScore))
    # result.sort(key=lambda x: x[1])
    return result

def getClassifier(pickled="classifier.pickle"):
    with open(pickled, "rb") as f:
        classifier = pickle.load(f)
    return classifier

def filterActionItems(classifier, sentences):
    return [s[0] for s in sentences if classifier.classify(features(s[0]))]

def demo(text, nltk=False):
    # Sentiment Analysis
    sentences, scores = getSentiment(text)
    print(sentimentToString(sentences, scores, nltk))

    # Action items
    print("The following sentences look like action items: ")
    print("\n".join(filterActionItems(getClassifier(), sentences)))

if __name__ == "__main__":
    demo("This is an example sentence which is neutral. \
          Wow, this new text analysis program is amazing! \
          I'm disgusted by how poorly organized this hackathon is. \
          Let me know what you think of my project.", True)

#!/usr/bin/env python3
import requests
import json
import pickle
from nltk.tokenize import sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from .actionRequired.train import features

API_URL = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment"
API_KEY = "REPLACEME"

def getSentiment(text, language="en"):
    sentences = sent_tokenize(text)
    sentences = [sentence.strip() for sentence in sentences if sentence != ""]

    documents = []
    for i, sentence in enumerate(sentences):
        documents.append({"language":language, "id": str(i),"text": sentence})

    r = requests.post(API_URL,
                      json={"documents": documents},
                      headers={"Ocp-Apim-Subscription-Key": API_KEY,
                               "content-type": "application/json"})

    if r.status_code != 200:
        print("Something went wrong: %s" % r.text)
        return ([r.text], ["N/A"])

    results = json.loads(r.text)

    scores = [None] * len(sentences)
    for tup in results["documents"]:
        scores[int(tup["id"])] = tup["score"]
    return (sentences, scores)

def sentimentToList(sentences, scores, use_nltk=False):
    temp = []
    results = [(sentence, score) for (sentence, score) in zip(sentences, scores)]
    results.sort(key=lambda x: x[1])
    sid = SentimentIntensityAnalyzer()
    for r in results:
        temp.append("{0:.2f} | {1}".format(r[1], r[0][:70]))
        if use_nltk:
            ss = sid.polarity_scores(r[0])
            for key in ss: # Normalize to same as Azure scale
                ss[key] = ss[key]/2 + 0.5
            temp.append("{0:.2f} | neg: {1:.2f}, neu: {2:.2f}, pos: {3:.2f}".format(
                   ss["compound"], ss["neg"], ss["neu"], ss["pos"]))
        temp.append("")
    return temp

def getClassifier(pickled="classifier.pickle"):
    with open(pickled, "rb") as f:
        classifier = pickle.load(f)
    return classifier

def filterActionItems(classifier, sentences):
    return [s for s in sentences if classifier.classify(features(s))]

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

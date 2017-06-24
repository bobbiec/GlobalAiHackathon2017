#!/usr/bin/env python3
import requests
import json
import pickle
from nltk.tokenize import sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from actionRequired.train import features

"""
Dependencies (pip):
- requests
- json
- nltk (use nltk.download() to install)
    - punkt
    - subjectivity
    - vader_lexicon
"""

API_URL = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment"
API_KEY = "REPLACEME"

sqsp = """
Hi Bobbie,

My name is Susan and I'm the Campus Recruiting Lead at Squarespace. Frank Angulo informed me your calls with him and his team went well! I would like to connect with you regarding next steps. Do you have time for a quick call tomorrow afternoon?

Please provide me your availabilities and the best number to reach you.

Looking forward to speaking with you soon!

Best,
"""

usds = """
The United States Digital Service (USDS), the startup within The White House, will be coming to New York, July 27th, from 6-9pm ET for a private, invite only event that will highlight the many ways we are currently redesigning and rebuilding government services through different demonstrations of projects, lightning talks, and roundtable conversations. I would love for you to attend!

If you’d like to be included, please send me a confirmation by Friday, June 30th, and I will be sure to get an invite to you in the coming weeks!

Also, there are a ton of fun articles about our work floating around but this is one of my favorites about the USDS report to Congress: https://medium.com/the-u-s-digital-service/the-u-s-digital-service-2016-report-to-congress-ebf518e08bf6#.dw3r0xaeq

And here's the latest inspiring clip about us: https://youtu.be/aGe5rEDv3g8
"""

navyseal = """
What the fuck did you just fucking say about me, you little bitch? I’ll have you know I graduated top of my class in the Navy Seals, and I’ve been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills.

I am trained in gorilla warfare and I’m the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words.

You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You’re fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that’s just with my bare hands.

Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little “clever” comment was about to bring down upon you, maybe you would have held your fucking tongue.

But you couldn’t, you didn’t, and now you’re paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it.

You’re fucking dead, kiddo.
"""

def getSentiment(sentences, language="en"):
    documents = []
    for i, sentence in enumerate(sentences):
        documents.append({"language":language, "id": str(i),"text": sentence})


    r = requests.post(API_URL,
                      json={"documents": documents},
                      headers={"Ocp-Apim-Subscription-Key": API_KEY,
                                    "content-type": "application/json"})
    if r.status_code != 200:
        print("Something went wrong: %s" % r.text)
        return None

    results = json.loads(r.text)

    scores = [None] * len(sentences)
    for tup in results["documents"]:
        scores[int(tup["id"])] = tup["score"]
    return scores

def demo(text, nltk=False):
    sentences = sent_tokenize(text)
    sentences = [sentence.strip() for sentence in sentences if sentence != ""] # Remove empty sentences

    # Sentiment Analysis
    scores = getSentiment(sentences)
    results = [(sentence, score) for (sentence, score) in zip(sentences, scores)]
    results.sort(key=lambda x: x[1])
    sid = SentimentIntensityAnalyzer()
    for r in results:
        print("{0:.2f} | {1}".format(r[1], r[0][:70]))
        if nltk:
            ss = sid.polarity_scores(r[0])
            for key in ss: # Normalize to same as Azure scale
                ss[key] = ss[key]/2 + 0.5
            print("{0:.2f} | neg: {1:.2f}, neu: {2:.2f}, pos: {3:.2f}".format(
                   ss["compound"], ss["neg"], ss["neu"], ss["pos"]))
        print()

    # Action items
    with open("actionRequired/classifier.pickle", "rb") as f:
        classifier = pickle.load(f)

    actionItems = [s for s in sentences if classifier.classify(features(s))]
    print("The following sentences look like action items: ")
    print("\n".join(actionItems))


print("USDS email: ")
demo(usds, nltk=True)
#
# print("The Navy SEAL copypasta: ")
# demo(navyseal)

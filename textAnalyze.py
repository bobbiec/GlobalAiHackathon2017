import requests
import json
from nltk.tokenize import sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

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

subra = """
I write to inform you that after four rewarding and productive years as part of this community, I will be stepping down as president of Carnegie Mellon University on June 30. My wife Mary and I have reflected on the long-term commitment needed to implement the university’s strategic plan, and we feel Carnegie Mellon would be best served now by a president who is ready to make that extended commitment to generating resources and guiding the university toward reaching these objectives.

I am proud of what we have achieved together during this time. Through a year-long effort touching all parts of campus and beyond, we created the strategic plan that is already resulting in concrete progress. Together we have put renewed emphasis on student access, including the creation of Presidential Scholarships and Fellowships, providing financial aid to undergraduates and graduate students. We have seen the historic expansion of campus, including the opening of Scott Hall, the Cohon University Center addition, the Hamburg Hall addition, and the debt-free financing of the David A. Tepper Quadrangle. I am proud to see the growing commitment to excellence across the university’s fields and endeavors, led by our outstanding faculty, staff and students, and our renewed commitment to diversity and inclusion.

Mary and I have immensely enjoyed the time we have spent with students at all stages in their CMU education, in a variety of venues. We commend you for your outstanding work, and wish you all the best as you pursue your careers and lives. We also wish to extend our thanks to the outstanding faculty, staff, alumni, parents, academic leaders, administrative leaders, trustees, friends and the philanthropic leaders, especially in Pittsburgh’s vibrant foundation community, who contribute to CMU’s excellence.

I knew long before I came here that Carnegie Mellon is a special place, and it has been an unforgettable experience for Mary and me to join this community and work with so many of you. Even as we depart for new opportunities, we will always take CMU with us.
"""

navyseal = """
What the fuck did you just fucking say about me, you little bitch? I’ll have you know I graduated top of my class in the Navy Seals, and I’ve been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills.

I am trained in gorilla warfare and I’m the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words.

You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You’re fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that’s just with my bare hands.

Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little “clever” comment was about to bring down upon you, maybe you would have held your fucking tongue.

But you couldn’t, you didn’t, and now you’re paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it.

You’re fucking dead, kiddo.
"""

def getSentiment(text, language="en"):
    # Microsoft Azure sucks
    sentences = sent_tokenize(text)
    sentences = [sentence.strip() for sentence in sentences if sentence != ""] # Remove empty sentences
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
    return sentences, scores

def demo(text, nltk=False):
    sentences, scores = getSentiment(text)
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

print("Subra Suresh's goodbye email: ")
demo(subra)

print("The Navy SEAL copypasta: ")
demo(navyseal)

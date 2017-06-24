# Adapted from http://www.nltk.org/book/ch06.html

from collections import Counter
import nltk
from nltk.util import ngrams
import random

def features(sentence):
    tokens = sentence.split()
    result =  Counter(tokens) \
            + Counter(nltk.ngrams(tokens, 2, pad_left=True, pad_right=True))

    result["SENTENCE_LENGTH"] = len(tokens)
    return result

# Example code for training and development below
# with open("clean_data/intent_neg") as neg, open("clean_data/intent_pos") as pos:
#     text = [(sentence, False) for sentence in neg] + \
#            [(sentence, True) for sentence in pos]
#
# featureset = [(features(sentence), label) for (sentence, label) in text]
# classifier = nltk.NaiveBayesClassifier.train(featureset)
#
# random.shuffle(text)
#
# train = text[:1500]
# dev = text[1500:2500]
# test = text[2500:]
#
# train_set = [(features(sentence), label) for (sentence, label) in train]
# dev_set = [(features(sentence), label) for (sentence, label) in dev]
# test_set = [(features(sentence), label) for (sentence, label) in test]
#
# # classifier = nltk.NaiveBayesClassifier.train(train_set)
# accuracy = nltk.classify.accuracy(classifier, test_set)
# print("Accuracy:", accuracy)
#
# errors = []
# for i, (sentence, actual) in enumerate(dev):
#     guess = classifier.classify(features(sentence))
#     if guess != actual:
#         errors.append((guess, actual, sentence))
#     else:
#         print(i)
#
# lastresult = (None, None)
# for (guess, actual, sentence) in sorted(errors, key=lambda x: (x[0], len(x[2]))):
#     if (guess, actual) != lastresult:
#         print("\n\n\n", guess, actual, ": ")
#         lastresult = (guess, actual)
#     print(sentence, end = "")

# Requires maxent_ne_chunker and averaged_perceptron_tagger (from nltk.download)
# Original dataset from https://github.com/Charlie9/enron_intent_dataset_verified.git
from nltk import word_tokenize, pos_tag, ne_chunk

def namedEntityReplace(sentence):
    chunked = ne_chunk(pos_tag(word_tokenize(sentence)), binary=True)
    words = [leaf[0] if type(leaf[0]) == str else "NAMED_ENTITY" for leaf in chunked]
    new = " ".join(words)
    return new

def cleanFile(infile, outfile):
    with open(infile) as f1:
        results = [namedEntityReplace(line) for line in f1]
        with open(outfile, "w") as f2:
            f2.write("\n".join(results))

# Example use
# cleanFile("original_data/intent_pos", "clean_data/intent_pos")

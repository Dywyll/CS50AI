import sys

import nltk

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to" | "until"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NON_TERMINALS = """
S -> NP VP | S Conj S | NP VP Conj VP | S P
AP -> Adj | Adj AP
NP -> N | Det NP | AP NP | N PP
PP -> P NP | P S
VP -> V | V NP | V NP PP | V PP | VP Adv | Adv VP
"""

grammar = nltk.CFG.fromstring(NON_TERMINALS + TERMINALS)

parser = nltk.ChartParser(grammar)


def main():
    # If file name specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()
    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)

        return

    if not trees:
        print("Could not parse sentence.")

        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun phrase chunks:")

        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert sentence to a list of its words.
    Converting all characters to lowercase and removing any word that doesn't contain at least one letter.
    """

    # Return words which have at least one letter in the tokenized lowercase words
    return [word for word in nltk.word_tokenize(sentence.lower()) if any(char.isalpha() for char in word)]


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    """

    chunks = list()

    for node in tree:
        # If label is NP and no subtrees has NP label
        if node.label() == 'NP' and not list(node.subtrees(lambda x: x.label() == 'NP' and x != node)):
            chunks.append(node)
        # If label is S, call function recursively and add result to `chunks`
        elif node.label() == 'S':
            chunks += np_chunk(node)

    return chunks


if __name__ == "__main__":
    main()

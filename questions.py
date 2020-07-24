import math
import os
import string
import sys

import nltk

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])

    file_words = {
        filename: tokenize(files[filename]) for filename in files
    }

    file_idf_values = compute_idf_values(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idf_values, FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()

    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)

                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idf_values = compute_idf_values(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idf_values, SENTENCE_MATCHES)

    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name,
    return a dictionary mapping the filename of each file inside that directory to the file's contents as a string.
    """

    # For each file, open and set its read content to the corresponding file key
    return {
        file: open(os.path.join(directory, file), encoding='utf-8').read() for file in os.listdir(directory)
    }


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the words in that document, in order.
    """

    # For each word in the tokenized lowercase document, filter out punctuations and English stopwords
    return [
        word for word in nltk.word_tokenize(document.lower())
        if not all(char in string.punctuation for char in word) and word not in nltk.corpus.stopwords.words('english')
    ]


def compute_idf_values(documents):
    """
    Given a dictionary of documents that maps names of documents to a list of words,
    return a dictionary that maps words to their IDF values.
    """

    counts = dict()

    for words in documents.values():
        visited = set()

        for word in words:
            if word not in visited:
                visited.add(word)

                try:
                    counts[word] += 1
                except KeyError:
                    counts[word] = 1

    return {
        word: math.log(len(documents) / counts[word]) for word in counts.keys()
    }


def top_files(query, files, idf_values, n):
    """
    Given a query, a dictionary mapping names of files to a list of their words,
    and a dictionary mapping words to their IDF values,
    return a list of the filenames of the `n` top files that match the query, ranked according to TF-IDF.
    """

    result = dict()

    for file in files.keys():
        result[file] = 0

        for word in query:
            result[file] += files[file].count(word) * idf_values[word]

    return [key for key, value in sorted(result.items(), key=lambda item: item[1], reverse=True)][:n]


def top_sentences(query, sentences, idf_values, n):
    """
    Given a a set of words, a dictionary mapping sentences to a list of their words,
    and a dictionary mapping words to their IDF values, return a list of the `n` top sentences that match the query,
    ranked according to IDF.
    """

    ranks = list()

    for sentence, words in sentences.items():
        values = [sentence, 0, 0]

        for word in query:
            if word in words:
                values[1] += idf_values[word]

                values[2] += words.count(word) / len(words)

        ranks.append(values)

    return [
        sentence for sentence, measure, density in sorted(ranks, key=lambda item: (item[1], item[2]), reverse=True)
    ][:n]


if __name__ == "__main__":
    main()

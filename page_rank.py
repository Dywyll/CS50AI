import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python page_rank.py corpus")

    corpus = crawl(sys.argv[1])

    ranks = sample_page_rank(corpus, DAMPING, SAMPLES)

    print(f"Results from sampling ({SAMPLES} samples):")

    for page in sorted(ranks):
        print(f"    {page}: {ranks[page]:.4f}")

    ranks = iterate_page_rank(corpus, DAMPING)

    print(f"Results from iteration:")

    for page in sorted(ranks):
        print(f"    {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages. Return a dictionary where each key is a page,
    and values are a list of all other pages in the corpus that are linked to by the page.
    """

    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue

        with open(os.path.join(directory, filename)) as f:
            contents = f.read()

            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)

            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next, given a current page.
    With probability `damping_factor`, choose a link at random linked to by `page`.
    With probability `1 - damping_factor`, choose a link at random chosen from all pages in the corpus.
    """

    result = dict()

    # If the current page has not outgoing links, probability distribution is equal
    if not page:
        div = 1 / len(corpus)

        for i in corpus.keys():
            result[i] = div

        return result

    # Otherwise, proceed with normal calculations
    initial = damping_factor / len(corpus[page])

    for i in corpus[page]:
        result[i] = initial

    additional = (1 - damping_factor) / len(corpus)

    for i in corpus.keys():
        try:
            result[i] += additional
        except KeyError:
            result[i] = additional

    return result


def sample_page_rank(corpus, damping_factor, n):
    """
    Return values for each page by sampling `n` pages according to transition model, starting with a page at random.
    Return a dictionary where keys are page names, and values are their estimated value (a value between 0 and 1).
    All values should sum to 1.
    """

    counts = {page: 0 for page in corpus.keys()}

    page = random.choice(list(corpus.keys()))

    for i in range(1, n):
        counts[page] += 1

        page_transition_model = transition_model(corpus, page, damping_factor)

        page = random.choices(list(page_transition_model.keys()), list(page_transition_model.values()))[0]

    return {key: value / n for key, value in counts.items()}


def iterate_page_rank(corpus, damping_factor):
    """
    Return values for each page by iteratively updating PageRank values until convergence.
    Return a dictionary where keys are page names, and values are their estimated value (a value between 0 and 1).
    All values should sum to 1.
    """

    previous = {key: 1 / len(corpus) for key in corpus.keys()}

    reversed_ = {key: set() for key in corpus.keys()}

    random_ = (1 - damping_factor) / len(corpus)

    for key, value in corpus.items():
        for page in value:
            reversed_[page].add(key)

    while True:
        next_ = dict()

        for key, value in previous.items():
            temp = 0.0

            for page in reversed_[key]:
                temp += previous[page] / len(corpus[page])

            next_[key] = random_ + damping_factor * temp

        total = sum(next_.values())

        next_ = {key: value / total for key, value in next_.items()}

        if all([(abs(next_[key] - value) <= 0.0001) for key, value in sorted(previous.items())]):
            break

        previous = next_

    return previous


if __name__ == "__main__":
    main()

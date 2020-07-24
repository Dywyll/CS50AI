import csv
import itertools
import sys

PS = {
    # Unconditional probabilities for having gene
    'gene': {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },
    'trait': {
        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },
        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },
        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },
    # Mutation probability
    'mutation': 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")

    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            'gene': {
                2: 0,
                1: 0,
                0: 0
            },
            'trait': {
                True: 0,
                False: 0
            }
        } for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)

    for have_trait in power_set(names):
        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and people[person]["trait"] != (person in have_trait))
            for person in names
        )

        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in power_set(names):
            for two_genes in power_set(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)

                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")

        for field in probabilities[person]:
            print(f"    {field.capitalize()}:")

            for value in probabilities[person][field]:
                p = probabilities[person][field][value]

                print(f"        {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    """

    data = dict()

    with open(filename) as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = row["name"]

            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (
                    True if row["trait"] == "1" else
                    False if row["trait"] == "0" else None
                )
            }

    return data


def power_set(s):
    """
    Return a list of all possible subsets of set s.
    """

    s = list(s)

    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.
    """

    cumulative = 1

    for person in people:
        mom = people[person]['mother']
        dad = people[person]['father']

        if person in one_gene:
            if mom is None and dad is None:
                prob = PS['gene'][1]
            else:
                first = .5 if mom in one_gene else 1 - PS['mutation'] if mom in two_genes else PS['mutation']

                first *= .5 if dad in one_gene else PS['mutation'] if dad in two_genes else 1 - PS['mutation']

                second = .5 if mom in one_gene else PS['mutation'] if mom in two_genes else 1 - PS['mutation']

                second *= .5 if dad in one_gene else 1 - PS['mutation'] if dad in two_genes else PS['mutation']

                prob = first + second

            prob *= PS['trait'][1][person in have_trait]
        elif person in two_genes:
            if mom is None and dad is None:
                prob = PS['gene'][2]
            else:
                prob = .5 if mom in one_gene else 1 - PS['mutation'] if mom in two_genes else PS['mutation']

                prob *= .5 if dad in one_gene else 1 - PS['mutation'] if dad in two_genes else PS['mutation']

            prob *= PS['trait'][2][person in have_trait]
        else:
            if mom is None and dad is None:
                prob = PS['gene'][0]
            else:
                prob = .5 if mom in one_gene else 1 - PS['mutation'] if mom in two_genes else PS['mutation']

                prob *= .5 if dad in one_gene else 1 - PS['mutation'] if dad in two_genes else PS['mutation']

            prob *= PS['trait'][0][person in have_trait]

        cumulative *= prob

    return cumulative


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    """

    for person in probabilities:
        probabilities[person]['gene'][1 if person in one_gene else 2 if person in two_genes else 0] += p

        probabilities[person]['trait'][person in have_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution is normalized.
    """

    for person in probabilities:
        gene_total = 0

        for i in range(3):
            gene_total += probabilities[person]['gene'][i]

        for i in range(3):
            probabilities[person]['gene'][i] /= gene_total

        trait_total = probabilities[person]['trait'][True] + probabilities[person]['trait'][False]

        probabilities[person]['trait'][True] /= trait_total
        probabilities[person]['trait'][False] /= trait_total


if __name__ == "__main__":
    main()

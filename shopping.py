import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])

    x_train, x_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(x_train, y_train)

    predictions = model.predict(x_test)

    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of evidence lists and a list of labels.
    Return a tuple (evidence, labels).
    """

    evidence, labels = list(), list()

    with open(filename, 'r') as f:
        reader = list(csv.DictReader(f))

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        floats = [
            'Administrative_Duration', 'Informational_Duration', 'ProductRelated_Duration', 'BounceRates', 'ExitRates',
            'PageValues', 'SpecialDay'
        ]

        integers = [
            'Administrative', 'Informational', 'ProductRelated', 'OperatingSystems', 'Browser', 'Region', 'TrafficType'
        ]

        # Iterating through the rows
        for row in reader:
            # Converting fields values to int
            for field in integers:
                row[field] = int(row[field])

            # Converting fields values to float
            for field in floats:
                row[field] = float(row[field])

            # Converting month to int
            row['Month'] = months.index(row['Month'])

            # Converting visitor type to int
            row['VisitorType'] = 1 if row['VisitorType'] == 'Returning_Visitor' else 0

            # Converting weekend field value to int
            row['Weekend'] = 1 if row['Weekend'] == 'TRUE' else 0

            # Adding list of values to evidence list except for the last field
            evidence.append(list(row.values())[:-1])

            # Adding last field value to label
            labels.append(1 if row['Revenue'] == 'TRUE' else 0)

    return evidence, labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a fitted k-nearest neighbor model trained on the data.
    """

    neigh = KNeighborsClassifier(1)

    neigh.fit(evidence, labels)

    return neigh


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels, return a tuple (sensitivity, specificity).
    """

    # Dictionary to keep how many true positive and true negative values were found on the labels and predictions
    data = {
        'positive': {
            'labels': 0,
            'predictions': 0
        },
        'negative': {
            'labels': 0,
            'predictions': 0
        }
    }

    # For values in labels check if it's true positive or negative and increment in data dictionary accordingly
    for i in range(len(labels)):
        if labels[i] == 1:
            data['positive']['labels'] += 1
            data['positive']['predictions'] += predictions[i]
        else:
            data['negative']['labels'] += 1
            data['negative']['predictions'] += 1 - predictions[i]

    # Return a tuple containing results from each division
    # First value represents sensitivity, second value represents specificity
    return (
        data['positive']['predictions'] / data['positive']['labels'],
        data['negative']['predictions'] / data['negative']['labels']
    )


if __name__ == "__main__":
    main()

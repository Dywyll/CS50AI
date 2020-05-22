import os
import sys

import cv2
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():
    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit('Usage: python traffic.py data [model.h5]')

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)

    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test, y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]

        model.save(filename)

        print(f'Model saved to {filename}.')


def load_data(data_dir):
    """
    Load image data from directory.
    """

    images, labels = list(), list()

    for folder in os.listdir(data_dir):
        directory = os.path.join(data_dir, folder)

        if os.path.isdir(directory):
            for file in os.listdir(directory):
                img = cv2.imread(os.path.join(directory, file), cv2.IMREAD_COLOR)

                img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT), interpolation=cv2.INTER_AREA)

                images.append(img)

                labels.append(int(folder))

    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model.
    """

    model = tf.keras.models.Sequential(
        [
            # Convolution
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)),
            # Pooling
            tf.keras.layers.MaxPool2D((3, 3)),
            # Flattening
            tf.keras.layers.Flatten(),
            # Hidden layer with dropout
            tf.keras.layers.Dense(NUM_CATEGORIES * 32, 'relu'),
            tf.keras.layers.Dropout(0.5),
            # More hidden layers
            tf.keras.layers.Dense(NUM_CATEGORIES * 16, 'relu'),
            tf.keras.layers.Dense(NUM_CATEGORIES * 8, 'relu'),
            # Output layer
            tf.keras.layers.Dense(NUM_CATEGORIES, 'softmax')
        ]
    )

    # Compile model for training
    model.compile('adam', 'categorical_crossentropy', ['accuracy'])

    return model


if __name__ == "__main__":
    main()

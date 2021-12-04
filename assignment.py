
import tensorflow as tf
import numpy as np
from preprocessing import get_data
from preprocessing import get_labels
from preprocessing import get_next_batch

class Model(tf.keras.Model):
    def __init__(self):
        """
        NEED TO EDIT THIS
        """
        super(Model, self).__init__()

        self.batch_size = 18
        self.num_teams = 126
        self.learning_rate = tf.keras.optimizers.Adam(.001)
        self.num_epochs = 10
        self.hidden_size = 100

        self.layer1 = tf.keras.layers.Dense(self.hidden_size,activation='relu')
        self.layer2 = tf.keras.layers.Dense(self.hidden_size, activation='relu')
        self.layer3 = tf.keras.layers.Dense(1)


    def call(self, inputs):
        """
        Completed the forward pass through the network, obtaining logits
        :param inputs: shape of (num_teams, 27)
        :return: logits - a matrix of shape (num_inputs, 1)
        """
        return self.layer3(self.layer2(self.layer1(inputs)))

    def loss(self, logits, labels):
        """
        Here we calculate loss by comparing the logits, calculated in the call function with the labels
        :param logits: shape of (num_teams, 1)
        :param labels: shape of (num_teams, 1)
        :return: loss - a Tensor with a single entry
        """
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels, logits))
        return loss

    def accuracy(self, logits, labels):
        """
        NEED TO FILL IN
        """
        pass


def train(model, train_inputs, train_labels):
    '''
    This function is where we complete the training of our model, using training inputs and training labels.
    Batch the inputs, and complete the forward pass to obtain probabilities.
    Then we complete gradient descent and use the loss to update trainable variables correctly
    :param model: the initialized model to use for the forward
    pass and backward pass
    :param train_inputs: train inputs (all inputs to use for training), dim of [num_teams, 27]
    :param train_labels: train labels (all labels to use for training), dim of [num_teams, 1]
    :return: None
    '''

    # Need to shuffle inputs and labels here using index

    for i in range(model.batch_size):
        batched_inputs, batched_labels = get_next_batch(train_inputs, train_labels, model.batch_size, i)
        probs = model.call(batched_inputs.astype(np.float))

        with tf.GradientTape() as tape:
            batch_loss = model.loss(probs, batched_labels)
            gradients = tape.gradient(batch_loss, model.trainable_variables)
            model.learning_rate.apply_gradients(zip(gradients, model.trainable_variables))
        print(i)

    pass


def test(model, test_inputs, test_labels):
    """
    NEED TO FILL IN
    """
    pass


def main():
    '''
    This function is where we initialize our model, call our functions from preprocessing to obtain data and labels
    , and run training and testing functions to obtain a numerical level of accuracy.
    :return: None
    '''

    train_and_test_data = get_data(
        'data/recruiting_rankings_2014.csv',
        'data/recruiting_rankings_2015.csv',
        'data/recruiting_rankings_2016.csv',
        'data/recruiting_rankings_2017.csv',
        'data/team_records_2014.csv',
        'data/team_records_2015.csv',
        'data/team_records_2016.csv',
        'data/team_records_2017.csv',
        'data/returning_production_2018.csv')

    train_labels = (get_labels('data/expected_wins_2018.csv','data/team_talent_2018.csv','data/predicted_points_added_2018.csv',2018))
    test_labels = get_labels('data/expected_wins_2019.csv','data/team_talent_2019.csv','data/predicted_points_added_2019.csv',2019)

    # Making sure we only include teams that are in all three sets
    #print(train_and_test_data.columns)
    #print(train_labels.columns)
    train_labels = train_labels[train_labels['team'].isin(train_and_test_data['team'])]
    train_and_test_data = train_and_test_data[train_and_test_data['team'].isin(train_labels['team'])]
    test_labels = test_labels[test_labels['team'].isin(train_and_test_data['team'])]

    # Preprocessing training labels to be a [num_examples, 1] shape
    conference_list = (train_labels['conference'].unique())
    train_labels = train_labels.replace(conference_list, list(range(len(conference_list))))
    processed_labels = np.asarray(train_labels)
    processed_train_labels = np.prod(np.delete(processed_labels, 0, 1), 1)

    # Preprocessing test labels to be a [num_examples, 1] shape
    conference_list = (test_labels['conference'].unique())
    test_labels = test_labels.replace(conference_list, list(range(len(conference_list))))
    processed_labels = np.asarray(test_labels)
    processed_test_labels = np.prod(np.delete(processed_labels, 0, 1), 1)

    # For now, using the same data for training and testing, just different labels
    # We can change this later, just wanted to set up forward network
    model = Model()
    #for i in range(model.num_epochs):
    train(model, np.asarray(train_and_test_data), processed_train_labels)

if __name__ == '__main__':
    main()

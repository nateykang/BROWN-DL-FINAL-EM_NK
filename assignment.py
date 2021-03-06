from __future__ import absolute_import
import tensorflow as tf
import numpy as np
from preprocessing import get_data
from preprocessing import get_labels
from preprocessing import get_next_batch


class Model(tf.keras.Model):
    def __init__(self):
        """
        We initialize a tf.keras.Model here and its parameters. It specifies hidden_sizes and batch_size,
        as well as the number of epochs. We also initialize the trainable parameters (in this case, 3 Dense
        layers) and any other model specifications.
        """
        super(Model, self).__init__()

        self.batch_size = 18
        self.num_teams = 126
        self.learning_rate = tf.keras.optimizers.Adam(.001)
        self.num_epochs = 20
        self.hidden_size_1 = 500
        self.hidden_size_2 = 200
        self.num_games = 15
        self.num_data_points = 27

        self.layer1 = tf.keras.layers.Dense(self.hidden_size_1, activation='relu')
        self.layer2 = tf.keras.layers.Dense(self.hidden_size_2, activation='relu')
        self.layer3 = tf.keras.layers.Dense(15)

    def call(self, inputs):
        """
        Completes the forward pass through the network, obtaining logits
        :param inputs: shape of (batch_size, num_data_points)
        :return: logits - a matrix of shape (batch_size, hidden_size)
        """
        logits = self.layer3(self.layer2(self.layer1(inputs)))
        return logits

    def loss(self, logits, labels):
        """
        Here we calculate loss by comparing the logits, calculated in the call function with the labels
        We use the following loss function because our logits have not had softmax already applied
        :param logits: shape of (batch_size, hidden_size)
        :param labels: shape of (num_teams, 1)
        :return: loss - a Tensor with a single entry
        """
        one_hot = tf.one_hot(labels, self.num_games)
        all_loss = tf.nn.softmax_cross_entropy_with_logits(tf.reshape
                                                           (one_hot, [self.batch_size, self.num_games]), logits)
        loss = tf.reduce_mean(all_loss)
        return loss

    def accuracy(self, logits, labels):
        """
        We calculate the accuracy of the logits predictions here using prediction accuracy
        :param logits: shape of (batch_size, hidden_size)
        :param labels: shape of (num_teams, 1)
        :return accuracy: A single float representing the proportion of teams whose expected win was guessed correctly
        """
        predictions_logits = tf.cast(tf.argmax(logits, 1), dtype=tf.int64)
        predictions_labels = tf.cast(tf.reshape(labels, [-1]), dtype=tf.int64)
        correct_predictions = tf.equal(predictions_logits, predictions_labels)
        return tf.reduce_mean(tf.cast(correct_predictions, tf.float32))


def train(model, train_inputs, train_labels):
    """
    This function is where we complete the training of our model, using training inputs and training labels.
    Batch the inputs, and complete the forward pass to obtain probabilities.
    Then we complete gradient descent and use the loss to update trainable variables correctly
    :param model: the initialized model to use for the forward
    pass and backward pass
    :param train_inputs: train inputs (all inputs to use for training), dim of [num_teams, num_data_points]
    :param train_labels: train labels (all labels to use for training), dim of [num_teams, 2]
    :return: avg_acc: a float representing average accuracy over all batches in the epoch
    """

    acc = []
    # Need to shuffle inputs and labels here using index
    indices_list = list(range(0, model.num_teams))
    shuffled_indices = tf.random.shuffle(indices_list)
    inputs_shuffled = train_inputs[shuffled_indices][:]
    labels_shuffled = train_labels[shuffled_indices]

    inputs_shuffled = inputs_shuffled[:, 1:]
    labels_shuffled = labels_shuffled[:, 1:]

    for i in range(np.int(model.num_teams/model.batch_size)):
        batched_inputs, batched_labels = get_next_batch(inputs_shuffled, labels_shuffled, model.batch_size, i)
        with tf.GradientTape() as tape:
            probs = model.call(batched_inputs.astype(np.float))
            batch_loss = model.loss(probs, batched_labels)
            gradients = tape.gradient(batch_loss, model.trainable_variables)
            model.learning_rate.apply_gradients(zip(gradients, model.trainable_variables))
            acc.append(model.accuracy(probs, batched_labels))

    return np.mean(acc)


def test(model, test_inputs, test_labels):
    """
    This function is where we complete the testing of our model, using testing inputs and testing labels.
    Batch the inputs, and complete the forward pass to obtain probabilities.
    Calculate accuracy comparing the logits to the labels
    :param model: the initialized model to use for the forward pass
    :param test_inputs: test inputs, dim of [num_teams, num_data_points]
    :param test_labels: test labels, dim of [num_teams, 2]
    :return: avg_acc: a float representing average accuracy over all batches in the epoch
    """
    acc = []

    indices_list = list(range(0, model.num_teams))
    shuffled_indices = tf.random.shuffle(indices_list)
    inputs_shuffled = test_inputs[shuffled_indices][:]
    labels_shuffled = test_labels[shuffled_indices]

    inputs_shuffled = inputs_shuffled[:, 1:]
    labels_shuffled = labels_shuffled[:, 1:]

    for i in range(np.int(model.num_teams / model.batch_size)):
        batched_inputs, batched_labels = get_next_batch(inputs_shuffled, labels_shuffled, model.batch_size, i)
        probs = model.call(batched_inputs.astype(np.float))
        acc.append(model.accuracy(probs, batched_labels))

    final_accuracy = np.mean(acc)

    return final_accuracy


def main():
    """
    This function is where we initialize our model, call our functions from preprocessing to obtain data and labels
    , and run training and testing functions to obtain a numerical level of accuracy.
    :return: None
    """
    train_data = get_data(
        'data/recruiting_rankings_2014.csv',
        'data/recruiting_rankings_2015.csv',
        'data/recruiting_rankings_2016.csv',
        'data/recruiting_rankings_2017.csv',
        'data/team_records_2014.csv',
        'data/team_records_2015.csv',
        'data/team_records_2016.csv',
        'data/team_records_2017.csv',
        'data/returning_production_2018.csv',
        bool_tr2014=True)

    test_data = get_data(
        'data/recruiting_rankings_2015.csv',
        'data/recruiting_rankings_2016.csv',
        'data/recruiting_rankings_2017.csv',
        'data/recruiting_rankings_2018.csv',
        'data/team_records_2015.csv',
        'data/team_records_2016.csv',
        'data/team_records_2017.csv',
        'data/team_records_2018.csv',
        'data/returning_production_2019.csv',
        False)

    train_labels = get_labels('data/expected_wins_2018.csv', 'data/team_talent_2018.csv',
                              'data/predicted_points_added_2018.csv')
    test_labels = get_labels('data/expected_wins_2019.csv', 'data/team_talent_2019.csv',
                             'data/predicted_points_added_2019.csv')

    # Making sure we only include teams that are in all three sets
    train_labels = train_labels[train_labels['team'].isin(train_data['team'])]
    train_data = train_data[train_data['team'].isin(train_labels['team'])]
    test_labels = test_labels[test_labels['team'].isin(test_data['team'])]
    test_data = test_data[test_data['team'].isin(test_labels['team'])]

    # Converting teams to numbers
    teams_list_train = train_labels['team'].unique()
    teams_index_train = list(range(len(teams_list_train)))
    train_labels = train_labels.replace(teams_list_train, teams_index_train)
    train_data = train_data.replace(teams_list_train, teams_index_train)
    train_data = train_data.sort_values(by='team')

    teams_list_test = test_labels['team'].unique()
    teams_index_test = list(range(len(teams_list_test)))
    test_labels = test_labels.replace(teams_list_test, teams_index_test)
    test_data = test_data.replace(teams_list_test, teams_index_test)
    test_data = test_data.sort_values(by='team')

    # Preprocessing training and testing labels to be a [num_examples, 2] shape
    conference_list = (train_labels['conference'].unique())
    conference_index = list(range(len(conference_list)))

    train_labels = train_labels.replace(conference_list, conference_index)
    processed_train_labels = np.asarray(train_labels)
    test_labels = test_labels.replace(conference_list, conference_index)
    processed_test_labels = np.asarray(test_labels)

    teams_for_train_labels = np.asarray(train_labels['team'])
    processed_train_labels = np.column_stack((teams_for_train_labels, processed_train_labels[:, 5]))

    teams_for_test_labels = np.asarray(test_labels['team'])
    processed_test_labels = np.column_stack((teams_for_test_labels, processed_test_labels[:, 5]))

    # Preprocessing input data to be in the correct order
    train_data_array = np.asarray(train_data)
    train_data_array[:, [1, 0]] = train_data_array[:, [0, 1]]

    test_data_array = np.asarray(test_data)
    test_data_array[:, [1, 0]] = test_data_array[:, [0, 1]]

    model = Model()
    for i in range(model.num_epochs):
        accuracy = train(model, train_data_array, processed_train_labels)
        print(accuracy)

    final_accuracy = test(model, test_data_array, processed_test_labels)
    print(final_accuracy)


if __name__ == '__main__':
    main()

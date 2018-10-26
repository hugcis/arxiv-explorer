import sys 
import math
import pickle
import random
import collections
import tensorflow as tf
import numpy as np

from .models import Paper



VOCABULARY_SIZE = 300000
batch_size = 100
embedding_size = 150  
skip_window = 2       
num_skips = 4         
num_sampled = 64

valid_size = 5    
valid_window = 100  


def tokenizer_and_build_dataset(pap_query_set, n_words, min_len=5):
    all_len = 0
    count = [['UNK', -1]]
    vocab_counter = collections.Counter()

    length = pap_query_set.count()
    print("{} papers to check !".format(length))

    for i, paper in enumerate(pap_query_set):
        if i % 50 == 0: 
            write_percent_progress(i, length)

        tok_len = len(paper.tokens)
        if tok_len >= min_len: # Remove too short abtracts from the list

            vocab_counter.update(paper.tokens)

            all_len += tok_len
    write_percent_progress(length, length)

    print("Saving vocabulary.")
    pickle.dump(vocab_counter, open('vocab.pkl', 'wb'))
    print("Vocabulary saved.\n\n")

    print("{} words in all papers".format(all_len))
 
    count.extend(vocab_counter.most_common(n_words - 1))

    print("Counter finished, working on dictionary")

    dictionary = dict()
    for word, _ in count:
        dictionary[word] = len(dictionary)

    data = []
    unk_count = 0

    print("Looping through papers again, building data")
    for i, paper in enumerate(pap_query_set):
        if i % 50 == 0:
            write_percent_progress(i, length)

        tok_len = len(paper.tokens)
        
        if tok_len >= min_len: # Remove too short abtracts from the list
            for word in paper.tokens:
                index = dictionary.get(word, 0)
                if index == 0:  # dictionary['UNK']
                    unk_count += 1
                data.append(index)
    write_percent_progress(length, length)
    
    count[0][1] = unk_count
    reversed_dictionary = dict(zip(dictionary.values(), dictionary.keys()))

    return data, count, dictionary, reversed_dictionary

def generate_batch(data, batch_size, num_skips, skip_window, data_index=0):
    assert batch_size % num_skips == 0
    assert num_skips <= 2 * skip_window
    batch = np.ndarray(shape=(batch_size), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    span = 2 * skip_window + 1  # [ skip_window target skip_window ]
    buffer = collections.deque(maxlen=span)

    if data_index + span > len(data):
        data_index = 0
    buffer.extend(data[data_index:data_index + span])
    data_index += span

    for i in range(batch_size // num_skips):
        context_words = [w for w in range(span) if w != skip_window]
        words_to_use = random.sample(context_words, num_skips)

        for j, context_word in enumerate(words_to_use):
            batch[i * num_skips + j] = buffer[skip_window]
            labels[i * num_skips + j, 0] = buffer[context_word]

        if data_index == len(data):
            buffer.extend(data[:span])
            data_index = span
        else:
            buffer.append(data[data_index])
        data_index += 1

    data_index = (data_index + len(data) - span) % len(data)
    return batch, labels, data_index

def build_model():
    (data, count, dictionary, 
     reversed_dictionary) = tokenizer_and_build_dataset(Paper.objects.all(), VOCABULARY_SIZE)

    print('Most common words (+UNK)', count[:5])
    print('Sample data', data[:10], [reversed_dictionary[i] for i in data[:10]])
    data_index = 0

    batch, labels, _ = generate_batch(data, batch_size=8, num_skips=2, skip_window=1)
    print("Sample batch")
    for i in range(8):
        print(batch[i], reversed_dictionary[batch[i]],
              '->', labels[i, 0], reversed_dictionary[labels[i, 0]])

    vocabulary_size = len(dictionary)
    valid_examples = np.random.choice(valid_window, valid_size, replace=False)


    graph = tf.Graph()

    with graph.as_default():

      # Input data.
        train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
        train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
        valid_dataset = tf.constant(valid_examples, dtype=tf.int32)

        with tf.device('/cpu:0'):
        # Look up embeddings for inputs.
            embeddings = tf.Variable(
                tf.random_uniform([vocabulary_size, embedding_size], -0.003, 0.003))
            embed = tf.nn.embedding_lookup(embeddings, train_inputs)

        # Construct the variables for the NCE loss
            nce_weights = tf.Variable(
                tf.truncated_normal([vocabulary_size, embedding_size],
                                    stddev=1.0 / math.sqrt(embedding_size)))
            nce_biases = tf.Variable(tf.zeros([vocabulary_size]))

        loss = tf.reduce_mean(
            tf.nn.nce_loss(weights=nce_weights,
                           biases=nce_biases,
                           labels=train_labels,
                           inputs=embed,
                           num_sampled=num_sampled,
                           num_classes=vocabulary_size))

        optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.01).minimize(loss)

        norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keepdims=True))
        normalized_embeddings = embeddings / norm
        valid_embeddings = tf.nn.embedding_lookup(
            normalized_embeddings, valid_dataset)
        similarity = tf.matmul(
            valid_embeddings, normalized_embeddings, transpose_b=True)

        # Add variable initializer.
        init = tf.global_variables_initializer()

    num_steps = 700001

    with tf.Session(graph=graph) as session:
        init.run()
        print('Initialized')

        average_loss = 0
        for step in range(num_steps):
            batch_inputs, batch_labels, data_index = generate_batch(
                data, batch_size, num_skips, skip_window, data_index)
            feed_dict = {train_inputs: batch_inputs, train_labels: batch_labels}

            _, loss_val = session.run([optimizer, loss], feed_dict=feed_dict)
            average_loss += loss_val

            if step % 20000 == 0:
                if step > 0:
                    average_loss /= 2000

                print('Average loss at step ', step, ': ', average_loss)
                average_loss = 0

            if step % 100000 == 0:
                sim = similarity.eval()
                for i in range(valid_size):
                    valid_word = reversed_dictionary[valid_examples[i]]
                    top_k = 8  # number of nearest neighbors
                    nearest = (-sim[i, :]).argsort()[1:top_k + 1]
                    log_str = 'Nearest to %s:' % valid_word
                    for k in range(top_k):
                        close_word = reversed_dictionary[nearest[k]]
                        log_str = '%s %s,' % (log_str, close_word)
                    print(log_str)
        final_embeddings = normalized_embeddings.eval()
    
    pickle.dump(dictionary, open('dictionary.pkl', 'wb'))
    np.save('embed.npy', final_embeddings)


def write_percent_progress(progress, total):
    sys.stdout.write("\rCheckpoint {:.2f}%    ".format(100*progress/total))
    sys.stdout.flush()
    if progress == total:
        sys.stdout.write("\n\n")
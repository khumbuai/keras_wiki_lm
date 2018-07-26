import os
import pickle

import keras.backend as K
import numpy as np
from keras.callbacks import EarlyStopping, ModelCheckpoint

from keras_lm.language_model.model import build_language_model
from keras_lm.preprocessing.batch_generators import BatchGenerator


def evaluate_model(model, word2idx, test_sentence, num_predictions=5):
    """
    Visual preidictions of the language model. The test_sentence is appended with num_predictions words,
    which are predicted as the next words from the model.
    :param str test_sentence:
    :param int num_predictions:
    :return: None
    """

    idx2word = {i:w for w,i in word2idx.items()}
    test_sentence = test_sentence.split()
    encoded_sentence = [word2idx[w] for w in test_sentence]

    for i in range(num_predictions):
        X = np.reshape(encoded_sentence, (1, len(encoded_sentence)))

        pred = model.predict(X)
        answer = np.argmax(pred, axis=2)

        predicted_idx = answer[0][-2]
        encoded_sentence.append(predicted_idx)

    print(' '.join([idx2word[i] for i in encoded_sentence]))




if __name__ == '__main__':
    os.environ["CUDA_VISIBLE_DEVICES"]="1"
    #check_fast_model_output()
    batch_size = 64
    valid_batch_size = 16
    seq_length = 50

    corpus = pickle.load(open('assets/wikitext-103/wikitext-103.corpus','rb'))

    train_gen = BatchGenerator(corpus.train, batch_size, 'normal', modify_seq_len=True).batch_gen(seq_length)
    valid_gen = BatchGenerator(corpus.valid, valid_batch_size, 'normal', modify_seq_len=True).batch_gen(seq_length)

    K.clear_session()
    num_words = len(corpus.word2idx) +1
    model = build_language_model(num_words, embedding_size=300, use_gpu=False)
    model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(lr=3e-4, beta_1=0.8, beta_2=0.99))

    model.summary()

    callbacks = [EarlyStopping(patience=5),
                 ModelCheckpoint('assets/language_model.hdf5', save_weights_only=True)]
    history = model.fit_generator(train_gen,
                             steps_per_epoch=len(corpus.train)//(seq_length * batch_size),
                             epochs=epochs,
                             validation_data=valid_gen,
                             validation_steps=len(corpus.valid)//(seq_length * batch_size),
                             callbacks=callbacks,
                             )


    evaluate_model(model,corpus.word2idx,'i feel sick and go to the ')

import math
from collections import defaultdict

import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
from selenium import webdriver
from bs4 import BeautifulSoup
import csv
from admin.common.models import ValueObject
import pandas as pd


class NaverMovie(object):
    def __init__(self):
        self.vo = ValueObject()
        self.vo.context = 'admin/myNLP/data/'
        self.k = 0.5

    def naver_process(self):
        n = NaverMovie()
        n.model_fit()
        n.classify('내 인생 최고의 영화')

    def classify(self, doc):
        return self.class0_probs(self.model_fit(), doc)

    def class0_probs(self, word_probs, doc):
        docwords = doc.split()
        log_prob_if_class0 = log_prob_if_class1 = 0.0
        for word, log_prob_if_class0, log_prob_if_class1 in word_probs:
            if word in docwords:
                log_prob_if_class0 += math.log(log_prob_if_class0)
                log_prob_if_class1 += math.log(log_prob_if_class1)
            else:
                log_prob_if_class0 += math.log(1.0 - log_prob_if_class0)
                log_prob_if_class1 += math.log(1.0 - log_prob_if_class1)
        prob_if_class0 = math.exp(log_prob_if_class0)
        prob_if_class1 = math.exp(log_prob_if_class1)
        return prob_if_class0 / (prob_if_class0 + prob_if_class1)

    def web_scraping(self):
        ctx = self.vo.context
        driver = webdriver.Chrome(f'{ctx}chromedriver')
        driver.get('https://movie.naver.com/movie/sdb/rank/rmovie.naver')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_divs = soup.find_all('div', attrs={'class', 'tit3'})
        products = [[div.a.string for div in all_divs]]
        with open(f'{ctx}naver_movie_dataset.csv', 'w', newline='', encoding='UTF-8') as f:
            wr = csv.writer(f)
            wr.writerows(products)
        driver.get('https://movie.naver.com/movie/point/af/list.naver')
        all_divs = soup.find_all('div', attrs={'class', 'tit3'})
        products = [[div.a.string for div in all_divs]]
        with open(f'{ctx}review_train.csv', 'w', newline='', encoding='UTF-8') as f:
            wr = csv.writer(f)
            wr.writerows(products)
        driver.close()

    def load_corpus(self, fname):
        corpus = pd.read_table(f'{self.vo.context}review_train.csv', sep=',', encoding='UTF-8')
        # print(f'type(corpus)::: {type(corpus)}')
        # print(f'corpus::: {corpus}')
        train_X = np.array(corpus)
        return train_X

    def count_words(self, train_X):
        # 카테고리 0 (긍정) 1 (부정)
        default_counts = defaultdict(lambda: [0, 0])
        for doc, point in train_X:
            if self.isNumber(doc) is False:
                words = doc.split()
                for word in words:
                    default_counts[word][0 if point > 3.5 else 1] += 1
        return dict(default_counts)

    def word_probs(self, counts, n_class0, n_class1, k):
        return [(w,
          (class0 + k) / (n_class0 + 2*k),
          (class1 + k) / (n_class1 + 2 * k),
          ) for w, (class0, class1) in counts.items()]

    def model_fit(self):
        ctx = self.vo.context
        # self.web_scraping()


        # print(f'word_counts ::: {counts}')
        '''
        '재밋었네요': [1, 0]
        '별로재미없다': [0, 1]
        '''
        n_class0 = len([1 for _, point in train_X if point > 3.5])
        n_class1 = len([train_X]) - n_class0
        k = 0.5
        word_prob =
        print(f'확률: {word_prob}')




    def isNumber(self, doc):
        try:
            float(doc)
            return True
        except ValueError:
            return False



class MyImdb(object):
    def __init__(self):
        self.vo = ValueObject()
        self.vo.context = 'admin/myNLP/data/'

    def decode_review(self, text,reverse_word_index):
        return ' '.join([reverse_word_index.get(i, '?') for i in text])

    def imdb_process(self):
        imdb = keras.datasets.imdb

        (train_X, train_Y), (test_X, test_Y) = imdb.load_data(num_words=10000)
        print(f'>>>>>{type(train_X)}')
        
        word_index = imdb.get_word_index()
        word_index = {k: (v + 3) for k, v in word_index.items()}
        word_index["<PAD>"] = 0
        word_index["<START>"] = 1
        word_index["<UNK>"] = 2 # Unknown
        word_index["<UNUSED>"] = 3
        train_X = keras.preprocessing.sequence.pad_sequences(train_X,
                                                             value=word_index['<PAD>'],
                                                             padding='post',
                                                             maxlen=256)
        test_X = keras.preprocessing.sequence.pad_sequences(test_X,
                                                             value=word_index['<PAD>'],
                                                             padding='post',
                                                             maxlen=256)
        vacab_size = 10000
        model = keras.Sequential()
        model.add(keras.layers.Embedding(vacab_size, 16, input_shape=(None,)))
        model.add(keras.layers.GlobalAvgPool1D())
        model.add(keras.layers.Dense(16, activation=tf.nn.relu))
        model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))
        model.compile(optimizer=tf.optimizers.Adam(), loss = 'binary_crossentropy', metrics=['acc'])
        x_val = train_X[:10000]
        partial_X_train = train_X[10000:]
        y_val = train_Y[:10000]
        partial_Y_train = train_Y[10000:]
        history = model.fit(partial_X_train, partial_Y_train, epochs=40, batch_size=512, validation_data=(x_val, y_val))
        result = model.evaluate(test_X, test_Y)
        print(f'정확도 ::: {result}')
        '''
        loss: 0.0880 - 
        acc: 0.9785 - 
        val_loss: 0.3153 - 
        val_acc: 0.8819
        '''
        history_dict = history.history
        history_dict.keys()
        acc = history_dict['acc']
        val_acc = history_dict['val_acc']
        # loss = history_dict['loss']
        # val_loss = history_dict['val_loss']
        epochs = range(1, len(acc) + 1)
        plt.plot(epochs, acc, 'bo', label='Training acc')
        plt.plot(epochs, val_acc, 'b', label='Validation acc')
        plt.title('Training and validation accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.savefig(f'{self.vo.context}imdb_nlp.png')




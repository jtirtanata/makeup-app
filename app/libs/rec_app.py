from keras.models import load_model
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import theano.tensor as T


USERS_LENGTH = 25
RATINGS_LENGTH = 843
LIKE = 1
DISLIKE = 0.1

basic_info = "brand_name, img_url, product_name, productid, product_url"

def loss_func(y_true, y_pred):
    temp = np.dot(y_true, y_pred)
    temp_true = y_true.nonzero_values()
    temp_pred = temp.nonzero_values()
    temp_pred = temp_pred / temp_true
    loss = T.mean((temp_pred - temp_true)**2)
    return loss

class Recommender:
    def __init__(self):
        self.offset = 0
        self.cnx = create_engine('postgresql://ubuntu:pinpass@34.205.76.95:5432/ubuntu')
        self.model = load_model('libs/data/rec/model.h5', {'loss_func' : loss_func})
        self.preferences = np.zeros(RATINGS_LENGTH)
        self.user_data = np.zeros(USERS_LENGTH)
        self.tried_products = set()
        self.suggestions = []


    def fetch_popular(self, n):
        qry = '''SELECT {} FROM product ORDER BY rev_count
         DESC limit {} OFFSET {}'''.format(basic_info, n, self.offset)
        selection = pd.read_sql_query(qry,self.cnx)
        self.offset += n
        return selection.to_json()

    def predict(self, likes, dislikes, users_data=None):
        self.tried_products = self.tried_products.union(likes + dislikes)
        for like in likes:
            if like <= RATINGS_LENGTH:
                self.preferences[like] = LIKE
        for dislike in dislikes:
            if dislike <= RATINGS_LENGTH:
                self.preferences[dislike] = DISLIKE
        pred = self.model.predict([self.user_data.reshape(1, -1),
            self.preferences.reshape(1, -1)])
        p_ids = list(enumerate(pred[0]))
        for p_id in self.tried_products:
            p_ids.pop(p_id)
        p_ids = sorted(p_ids, key=lambda x: x[1], reverse=False)
        p_ids = list(filter(lambda x: x[1] > 0.6, p_ids))
        self.suggestions = p_ids
        p_ids = [str(x[0]) for x in p_ids[:min(10, len(p_ids))]]
        p_ids = ','.join(p_ids)
        qry = """SELECT {} FROM product WHERE productid IN ({})""".format(basic_info, p_ids)
        selection = pd.read_sql_query(qry, self.cnx)
        return selection.to_json()



    def reset(self):
        self.offset = 0

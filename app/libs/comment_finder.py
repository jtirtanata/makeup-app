import pandas as pd
import pickle
from sklearn.metrics import pairwise
import numpy as np

class CommentFinder:
    def __init__(path='libs/data/rec'):
        self.comment_table = pd.read_pickle(path + 'comment_table.pkl')
        self.sentence_table = pd.read_pickle(path + 'df_sent.pkl')
        self.tf_vectorizer = pickle.load(open(path + 'tf_vectorizer.pkl', 'rb'))
        self.nmf = pickle.load(open(path + 'nmf.pkl', 'rb'))
        self.topic_probs = pickle.load(open(path + 'topic_probs.pkl', 'rb'))
        self.sent_length = self.topic_probs.shape[0]

    def find_comment_ids(self, productid):
        return self.comment_table[self.comment_table.productid == productid].columnid.values

    def create_topic_vector(self, question):
        tf_idf = self.tf_vectorizer.transform([question])
        topic_vector = self.nmf.transform(tf_idf)
        return topic_vector

    def get_sent_ids(self, c_ids):
        return self.sentence_table[(self.sentence_table.commentid.isin(c_ids)) \
         & (self.sentence_table.no_topic == False)].index.values

    def find_best_sentences(self, q_vector, c_ids, no_sent=3, window=2):
        sent_ids = self.get_sent_ids(c_ids)
        cur_probs = np.take(self.topic_probs, sent_ids, axis=0)
        cosine_dist = list(zip(sent_ids, pairwise.cosine_similarity(cur_probs, topic_vector).reshape(-1)))
        sorted_dist = sorted(cosine_dist, key=lambda x:x[1])
        sorted_keys = [x[0] for x in sorted_dist if x[1] != 0][:no_sent]
        self.find_sentences(sorted_keys, 2)

    def find_sentences(self, sent_ids, window):
        d = {}
        for sent_id in sent_ids:
            c_id = self.sentence_table.iloc[sent_id].commentid
            cur_df = self.sentence_table.iloc[max(0, sent_id-window):min(\
                sent_id+window + 1, self.sent_length), :]
            indexes = cur_df[cur_df.commentid == c_id].index.values
            if c_id in d:
                d[c_id] = (min(indexes[0], d[c_id][0]), max(indexes[-1],\
                 d[c_id][1]))
            else:
                d[c_id] = (indexes[0], indexes[-1])
        sentences = []
        for i, indexes in d.items():
            comments = self.sentence_table.iloc[indexes[0]:indexes[1] + 1, :]\
                .comment.values
            sentence = '. '.join([sent.capitalize() for sent in comments])
            sentences.append(sentence)
        return sentences

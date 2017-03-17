import flask
import numpy as np
import pandas as pd
import pickle
from libs import rec_app
from flask import url_for, render_template, redirect

rec = rec_app.Recommender()
# Initialize the app
app = flask.Flask(__name__, static_url_path='')
# Homepage
#
@app.route("/start")
def viz_page():
    """
    Homepage: serve our visualization page, awesome.html
    """
    return render_template("start.html")

@app.route("/popular", methods=["GET"])
def popular():
    pop = rec.fetch_popular(20)
    return pop

@app.route("/preferences", methods=["POST"])
def preferences():
    data = flask.request.json
    likes = [int(x) for x in data['likes']]
    dislikes = [int(x) for x in data['dislikes']]
    suggestions = rec.predict(likes, dislikes)
    return suggestions

# @app.route("/comments", methods=["POST"])
# def comments():
#     data = flask.request.json
#     columns = [i for i, x in enumerate(data["columns"].split(',')) if int(x) == 1]
#     column_names = set([name_dict[i] for i in columns])
#     reviews = recmodel.get_comments(data["url"], column_names, 5)
#     return flask.jsonify(reviews)

#--------- RUN WEB APP SERVER ------------#

# Start the app server on port 80
# (The default website port)
app.run(host='0.0.0.0')
app.run(debug=True)

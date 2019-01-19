import flask
from flask import Flask, Response
import pandas as pd
from io import StringIO
app = Flask(__name__)


from keras.models import load_model
clf = load_model('clf.h5')
clf._make_predict_function()  # GH#6462 @ keras-team/keras


def run_model(input_arr):
    """Predictor function."""
    # reshape the flat [0, 255]-entry list into a [0, 1]-entry grid, as desired by the CNN.
    input_arr = input_arr.reshape(input_arr.shape[0], 28, 28, 1).astype('float') / 255
    return clf.predict(input_arr).argmax(axis=1)


@app.route('/ping', methods=['GET'])
def ping():
    """
    Determine if the container is healthy by running a sample through the algorithm.
    """
    # we will return status ok if the model doesn't barf
    # but you can also insert slightly more sophisticated tests here
    health_check_arr = pd.read_csv("health-check-data.csv").values
    try:
        result = run_model(health_check_arr)
        return Response(response='{"status": "ok"}', status=200, mimetype='application/json')
    except:
        return Response(response='{"status": "error"}', status=500, mimetype='application/json')


@app.route('/invocations', methods=['POST'])
def predict():
    """
    Do an inference on a single batch of data.
    """
    if flask.request.content_type == 'text/csv':
        X_train = flask.request.data.decode('utf-8')
        X_train = pd.read_csv(StringIO(X_train), header=None).values
    else:
        return flask.Response(response='This predictor only supports CSV data', status=415, mimetype='text/plain')

    results = run_model(X_train)

    # format into a csv
    results_str = ",\n".join(results.astype('str'))

    # return
    return Response(response=results_str, status=200, mimetype='text/csv')

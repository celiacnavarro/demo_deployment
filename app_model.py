from flask import Flask, request, jsonify
import os
import pickle
from sklearn.model_selection import cross_val_score
import pandas as pd
import sqlite3


os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/")
def hello():
    return "Bienvenido a mi API del modelo advertising"

# 1. Endpoint que devuelva la predicción de los nuevos datos enviados mediante argumentos en la llamada
@app.route('/v1/predict', methods=['GET'])
def predict():
    model = pickle.load(open('../data/advertising_model','rb'))

    tv = request.args.get('tv', None)
    radio = request.args.get('radio', None)
    newspaper = request.args.get('newspaper', None)

    if tv is None or radio is None or newspaper is None:
        return "Missing args, the input values are needed to predict"
    else:
        prediction = model.predict([[tv,radio,newspaper]])
        return "The prediction of sales investing that amount of money in TV, radio and newspaper is: " + str(round(prediction[0],2)) + 'k €'
     
# 2. Endpoint para almacenar nuevos registros 
@app.route('/v1/ingest_data', methods=['POST'])
def ingest_data():
    tv = request.args.get('tv', None)
    radio = request.args.get('radio', None)
    newspaper = request.args.get('newspaper', None)
    sales = request.args.get('sales', None)

    if tv is None or radio is None or newspaper is None or sales is None:
        return "Missing args, the input values are needed"
    else:
        try: 
            connection = sqlite3.connect('advertising.db')
            cursor = connection.cursor()
            select = "INSERT INTO campañas (TV, radio, newspaper, sales) VALUES (?,?,?,?)" 
            cursor.execute(select, (tv,radio,newspaper,sales)).fetchall()
            connection.commit()
            result = cursor.execute('SELECT * FROM campañas').fetchall()
            return 'Data succesfully inserted into the database'
        except:
            return 'An error has occured'
    
# 3. Reentrenar de nuevo el modelo con los posibles nuevos registros que se recojan
@app.route('/v1/retrain', methods=['GET'])
def retrain():
    model = pickle.load(open('../data/advertising_model','rb'))
    connection = sqlite3.connect('advertising.db')
    df = pd.read_sql("SELECT * FROM campañas", connection)
    X_train = df[['TV', 'radio', 'newspaper']]
    y_train = df['sales']
    try : 
        model.fit(X_train, y_train)
        pickle.dump(model, open('retrained_model', 'wb'))
        return 'Model successfully retrained with the new data'
    except:
        'An error has occured'
app.run()
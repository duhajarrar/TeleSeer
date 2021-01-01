#import dump, load
#from sklearn import preprocessing
#from imblearn.over_sampling import SMOTE
#from xgboost import XGBClassifier
import flask
import numpy as np
import json
from datetime import date
import sqlite3
import pandas as pd
from flask import make_response
#from sklearn.preprocessing import StandardScaler
from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
import joblib

headers = {'Content-Type': 'text/html'}
app = flask.Flask(__name__)
app.config["DEBUG"] = False
#loaded_model=xgboost.Booster({'nthread': 4})
#loaded_model.load_model("tuned_xgb_smote.bin")
loaded_model=joblib.load('gb.bin')
#WV,141,415,330-8173,yes,yes,37,258.6,84,43.96,222,111,18.87,326.4,97,14.69,11.2,5,3.02,0 false
#KS,128,415,382-4657,no,yes,25,265.1,110,45.07,197.4,99,16.78,244.7,91,11.01,10,3,2.7,1 false
#IN,65,415,329-6603,no,no,0,129.1,137,21.95,228.5,83,19.42,208.8,111,9.4,12.7,6,3.43,4 true

# Load Model

#3168a2 dark blue
#6badef ligh blue
flag=0
def pred_vect(x): #columns
    vect = {}
    v= x.split(',')
    print("here2222")
    vect['state']=float(v[0])
    vect['account_length'] =float(v[1])
    vect['area_code']=float(v[2])
    vect['phone_number']=float(v[3])
    vect['international_plan']=float(v[4])
    vect['voice_mail_plan']=float(v[5])
    vect['number_vmail_messages']=float(v[6])
    vect['total_day_minutes'] =float(v[7])
    vect['total_day_calls']=float(v[8])
    vect['total_day_charge']=float(v[9])
    print("here3333")
    vect['total_eve_minutes']=float(v[10])
    vect['total_eve_calls']=float(v[11])
    vect['total_eve_charge']=float(v[12])
    vect['total_night_minutes'] =float(v[13])
    vect['total_night_calls']=float(v[14])
    vect['total_night_charge']=float(v[15])
    vect['total_intl_minutes']=float(v[16])
    vect['total_intl_calls']  =float(v[17])
    vect['total_intl_charge']=float(v[18])
    vect['customer_service_calls']=float(v[19])
    return vect
#User class for login
# login
app.secret_key = 'secretkey'
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=1, username='jawwal', password='jwl'))
users.append(User(id=2, username='Oredoo', password='or'))
users.append(User(id=3, username='TeleSeerTeam', password='teleTeam'))

app = Flask(__name__)

app.secret_key = 'somesecretkeythatonlyishouldknow'
@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


#route for login:
@app.route('/login.html', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            session['username']=user.username
            session['logged_in']=True
            #return render_template('API.html')
            churn=0
            non_churn=0
            churn,non_churn = get_counts(session['username'])
            #return render_template('/API.html',output='Prediction Output', churn=churn, non_churn=non_churn)
            return render_template('API.html')

        return render_template('login.html')

    return render_template('login.html')
def get_counts (partner):
    churn=0
    non_churn=0
    try:
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
    except:
        print("Debug: can't connect to database")
    else:
        print("Debug: connected to database")

    # Insert a row of data
    try:
        c.execute(f"select prediction_result,count(*) cnt from customer_tble  where partner= '{partner}'  group by prediction_result ")
    except:
        print("Debug: can't select group by")
    else:
        print("Debug: group by selected")

    rows = c.fetchall()

    for row in rows:
        print(row[0])

    for row in rows:
        if row[0]== 1:
            churn=row[1]
            print(f"churn= {churn}")
        elif row[0]== 0:
            non_churn=row[1]
            print(f"non_churn= {non_churn}")

    # Save (commit) the changes
    try:
        conn.commit()
        conn.close()
    except:
        print("Debug: can't close")
    else:
        print("Debug: DB closed")

    return churn,non_churn

def record_action(partner, date, is_churn):
    churn=0
    non_churn=0


    try:
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
    except:
        print("Debug: can't connect to database")
    else:
        print("Debug: connected to database")

    # Create table

    try:
        c.execute('''CREATE TABLE customer_tble (date date, partner text,prediction_result smallint)''')
    except:
        print("Debug: can't create the table ")
    else:
        print("Debug: table created ")

    # Insert a row of data
    print(f"INSERT INTO customer_tble  VALUES ('{date}','{partner}',{is_churn} )")
    try:
        c.execute(f"INSERT INTO customer_tble  VALUES ('{date}','{partner}',{is_churn} )")
    except:
        print("Debug: can't insert a record")
    else:
        print("Debug: record inserted")

    # Insert a row of data
    try:
        c.execute(f"select prediction_result,count(*) cnt from customer_tble  where partner= '{partner}'  group by prediction_result ")
    except:
        print("Debug: can't select group by")
    else:
        print("Debug: group by selected")

    rows = c.fetchall()

    for row in rows:
        print(row[0])

    for row in rows:
        if row[0]== 1:
            churn=row[1]
            print(f"churn= {churn}")
        elif row[0]== 0:
            non_churn=row[1]
            print(f"non_churn= {non_churn}")

    # Save (commit) the changes
    try:
        conn.commit()
        conn.close()
    except:
        print("Debug: can't close")
    else:
        print("Debug: DB closed")

    return churn,non_churn

# def home():

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def home():
    headers = {'Content-Type': 'text/html'}
    return make_response(render_template('index.html'),200,headers)



@app.route('/about.html', methods=['GET'])
def about():
    return render_template("about.html")

@app.route('/services.html', methods=['GET'])
def service():
    return render_template("services.html")

@app.route('/clients.html', methods=['GET'])
def clients():
    return render_template("clients.html")

@app.route('/API.html', methods=['Post','Get'])
def api():
    print("first API")
    if session['logged_in']==False:
        return redirect(url_for("login"))


    #return render_template('API.html')
    churn=0
    non_churn=0
    churn,non_churn = get_counts(session['username'])
    return render_template('API.html')
    #return render_template('API.html',output='Prediction Output', churn=churn, non_churn=non_churn)


# api
@app.route('/contact.html', methods=['GET'])
def contact():
    return render_template("contact.html")






@app.route('/API2.html', methods=['GET','POST'])

def predict_new_transaction():
    print("second API")
    if not g.user:
        return render_template("login.html")

    print('Debug: Chek API argument Exists ...')
    if 'pca_vs' in request.args :
        print("******************hhhhhhhhhhhhhhhhhhhhhhhh*******************")
        pca_vs = request.args['pca_vs']
        print(pca_vs)
        print("*******----------------------------------------")
    else:
        return "Error: No id field provided. Please specify an pca_vs."

    print('Debug: Fromat Input ...')
    p = pca_vs.split(",")
    print("*********************",len(pca_vs.split(",")),"****************************")
    print(p)
    churn=0
    non_churn=0
    output1=""
    prediction=""
    if len(p) == 20:
        print("here1")
        pca_vs_dic= pred_vect(pca_vs)
        print('Debug: Wright to JSON, DF ...')
        json1 = json.loads(json.dumps(pca_vs_dic))
        query_df = (pd.DataFrame([json1]))
        is_churn = 0
        print(query_df)
        print("try11111")
        print('Debug: Predict ...')
        print("*******", query_df.shape)
        #label_encoder=preprocessing.LabelEncoder()
        # query_df['state'] = label_encoder.fit_transform(query_df['state'])
        # query_df['international_plan'] = label_encoder.fit_transform(query_df['international_plan'])
        # query_df['voice_mail_plan'] = label_encoder.fit_transform(query_df['voice_mail_plan'])
        # query_df['phone_number'] = label_encoder.fit_transform(query_df['phone_number'])
        #
        # state_encoder = load('state_encoder.bin')
        # ip_encoder = load('ip_encoder.bin')
        # ph_encoder = load('pn_encoder.bin')
        # vmp_encoder = load('vmp_encoder.bin')
        # query_df['state'] = state_encoder.transform(query_df['state'])
        # query_df['international_plan'] = ip_encoder.transform(query_df['international_plan'])
        # query_df['voice_mail_plan'] = vmp_encoder.transform(query_df['voice_mail_plan'])
        # query_df['phone_number'] = ph_encoder.transform(query_df['phone_number'])
        # #query_df=query_df.sort_index()

        #sc = load('std_scaler.bin')
        #sc = preprocessing.StandardScaler()
        #query_df = sc.fit_transform(query_df)
        print(query_df)
        prediction =""
        #if  query_df.empty == False :
        print(type(loaded_model))
        prediction= loaded_model.predict(query_df)
        pp=prediction
        print("try222222")
        print('Debug: Print Prediction Output ...')
        print("****************")
        print(prediction)
        out_arr = np.array2string(prediction)
        print(out_arr)
        if out_arr=="[0]":
            print("hii")
            output1="The inserted customer is not Churn "
            is_churn=0
            churn,non_churn= record_action(session['username'],date.today(), is_churn)
            return render_template('API.html', output='Prediction Output', is_churn=output1)
        elif out_arr=="[1]":
            print("hiiii")
            output1="The inserted customer is Churn"
            is_churn=1
            churn,non_churn= record_action(session['username'],date.today(), is_churn)
            return render_template('API.html', output='Prediction Output', is_churn=output1)
        return render_template('API.html', output='Prediction Output', is_churn=output1)
    else:
        output1 = "The Input Should Be 20 Number Separated By Comma"
        churn, non_churn = get_counts(session['username'])
        #return render_template('API.html', output='Prediction Output', is_churn=output1, churn=churn, non_churn=non_churn)
        return render_template('API.html', output='Prediction Output', is_churn=output1)
    return render_template('API.html', output='Prediction Output', is_churn="nothing")

#needs to be tested
@app.route('/logout')
def logout():
    session.pop('username',None)
    g.user=None
    session['logged_in']=False
    return render_template('index.html')


if __name__=="__main__":
    app.run()
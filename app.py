import numpy as np
import pandas as pd
import pickle
from flask import Flask,request,jsonify,render_template, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import *
from random import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'
app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465     
app.config["MAIL_USERNAME"] = 'mailtesting063@gmail.com'  
app.config['MAIL_PASSWORD'] = 'weir jdwy vavc azsk'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True  
model = pickle.load(open('model.pkl','rb'))
bcrypt = Bcrypt(app)
mail = Mail(app)

otp = randint(000000,999999)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self,id,email,password,name):
        self.id = id
        self.name = name
        self.email = email
        self.password = password


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():

    if request.method == 'POST':
        id = randint(10000000, 99999999)
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        secured_pass = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(id=id,name=name,email=email,password=secured_pass)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/verify/'+new_user.email)

    return render_template('register.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user:
            if user.password == bcrypt.generate_password_hash(password).decode('utf-8'):
              session['email'] = user.email
            return redirect('/index')
        else:
            flash('Invalid Credentials. Try again')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/predict',methods=['GET','POST'])
def predict():
    if request.method=='POST':
        features = [x for x in request.form.values()]
        source_dict = {'Bangalore': 0, 'Chennai': 1, 'Delhi': 2, 'Kolkata': 3, 'Mumbai': 4}
        destination_dict = {'Bangalore':0,'Cochin':1,'Delhi':2,'Kolkata': 3,'Hyderabad':4,'New Delhi':5}
        airline_dict = {'IndiGo': 3, 'Air India': 1, 'Jet Airways': 4, 'SpiceJet': 8, 'Multiple carriers': 6, 'GoAir': 2, 'Vistara': 10, 'Air Asia': 0, 'Vistara Premium economy': 11, 'Jet Airways Business': 5, 'Multiple carriers Premium economy': 7, 'Trujet': 9}
        source_value = features[0]
        dest_value = features[1]
        date_value = features[2]
        airline_value = features[3]
        
        stops_value = int(features[4])   #<----------

        a= pd.Series(source_value)
        source = a.map(source_dict).values[0]   #<----------
        b= pd.Series(dest_value)
        destination = b.map(destination_dict).values[0] #<---------
        c= pd.Series(airline_value)
        airline = c.map(airline_dict).values[0]   #<----------

        day = int(pd.to_datetime(date_value, format="%Y-%m-%dT%H:%M").day)    #<----------------
        month = int(pd.to_datetime(date_value, format="%Y-%m-%dT%H:%M").month)  #<---------

        hour = int(pd.to_datetime(date_value, format ="%Y-%m-%dT%H:%M").hour)
        minute = int(pd.to_datetime(date_value, format ="%Y-%m-%dT%H:%M").minute)
           
        if  source==destination:
            return render_template('index.html',pred='Source and Destination City cannot be same. Please try again! ')
            
        else:
            pred_features = [np.array([day,month,stops_value,hour,minute,airline,source,destination])]
            prediction = model.predict(pred_features)

            if stops_value==0:
                output = round(prediction[0],0)

            else:
                output = round(prediction[0],0)-2000


            return render_template('index.html',pred='The Flight Fare for the given date is:-  INR {}'.format(output))
    else:
        return render_template('index.html')
    
@app.route('/index/logout',methods=['GET','POST'])
def logout():
    return render_template('login.html')

@app.route('/verify/<email>',methods = ["GET","POST"])  
def verify(email):  
    email = str(email)
      
    msg = Message('OTP',sender = 'mailtesting063@gmail.com', recipients = [email])  
    msg.body = str("Your otp to register on Flight Price Predictor is : "+str(otp))
    mail.send(msg)  
    return render_template('verify.html')  
 
@app.route('/validate',methods=["GET","POST"])  
def validate():  
    user_otp = request.form['otp']  
    if otp == int(user_otp):  
        return redirect('/login')   
    return "<h3>Invalid otp entered, Kindly, register again !!</h3>"  

if __name__=='__main__':
    app.run(debug=True)

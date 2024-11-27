import numpy as np
import pandas as pd
import pickle
from flask import Flask,request,render_template, redirect, session, flash, url_for,make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import *
from random import *
import string
from datetime import datetime, timedelta    
import random

app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)
app.secret_key = 'secret_key'
model = pickle.load(open('model.pkl','rb'))
bcrypt = Bcrypt(app)
mail = Mail(app)

otp = randint(000000,999999)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True) 

    def __init__(self,id,email,password,name, reset_token=None, reset_token_expiration=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.reset_token = reset_token
        self.reset_token_expiration = reset_token_expiration


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
        new_user = User(id=id,name=name,email=email,password=secured_pass,reset_token=None,reset_token_expiration=None)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/verify/'+new_user.email)

    return render_template('register.html')

@app.route('/index')
def index():
    if 'email' not in session:
        flash("Please log in to access this page.", "warning")
        return redirect('/login')
    return render_template('index.html')


@app.before_request
def prevent_cache():
    if 'email' not in session:
        response = make_response()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user:
            if bcrypt.check_password_hash(user.password, password):
                session['email'] = user.email
                flash('Login successful!', 'success')
                return redirect('/index')
            else:
                flash('Invalid password. Please try again.', 'danger')
                return render_template('login.html')
        else:
            flash('Email not found. Please try again.', 'danger')
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
    
    session.clear()
    flash("You have been logged out successfully.", "success")

    response = make_response(redirect('/login'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

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

@app.route('/forgot_password',methods=['GET','POST'])
def fp():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = generate_reset_token()
            expiration_time = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
            user.reset_token = token
            user.reset_token_expiration = expiration_time
            db.session.commit()

            reset_link = url_for('reset_password', token=token, _external=True)
            send_reset_email(email, reset_link)
            return "Check your email for the password reset link."
        else:
            return "Email not found."

    return render_template('forgot_password.html')

def generate_reset_token():
    return ''.join(random.choices( string.ascii_letters + string.digits, k=32))

def send_reset_email(to_email, reset_link):
    msg = Message('Password Reset Request', sender='mailtesting063@gmail.com', recipients=[to_email])
    msg.body = f'Click the following link to reset your password: {reset_link}'
    mail.send(msg)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if user:
        if datetime.utcnow() > user.reset_token_expiration:
            flash("This token has expired.", "danger")
            return redirect('/forgot_password')

        if request.method == 'POST':
            new_password = request.form['password']
            hashed_password = bcrypt.generate_password_hash(new_password)
            user.password = hashed_password
            user.reset_token = None
            user.reset_token_expiration = None
            db.session.commit()
            flash("Your password has been reset successfully.", "success")
            return redirect('/login')

        return render_template('reset_password.html', token=token)

    else:
        flash("Invalid or expired reset token.", "danger")
        return redirect('/forgot_password')
if __name__=='__main__':
    app.run(debug=True)
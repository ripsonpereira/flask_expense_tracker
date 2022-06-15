
from unicodedata import category
from flask import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import secrets
from sqlalchemy import extract
from datetime import datetime
from sqlalchemy import func

import matplotlib.pyplot as plt
plt.switch_backend('agg')



secret = secrets.token_urlsafe(32)


# from tabledef import *
engine = create_engine('mysql://root:''@localhost/flask_expense_tracker', echo=True)

Session = sessionmaker(bind=engine)
s = Session()


app=Flask(__name__)
app.secret_key = secret
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/flask_expense_tracker'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)

    

  


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    user = db.relationship('User',
        backref=db.backref('expenses', lazy=True))

 

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    user = db.relationship('User',
        backref=db.backref('incomes', lazy=True))
 


@app.route("/")
def home():
 
        return render_template("home.html")

@app.route("/login", methods=['POST','GET'])
def login():

    if request.method=='POST':
        engine = create_engine('mysql://root:''@localhost/flask_expense_tracker', echo=True)

        Session = sessionmaker(bind=engine)
        s = Session()
       
        email=str(request.form['email'])
        password=str(request.form['password'])

     
        query = s.query(User).filter(User.email.in_([email]), User.password.in_([password]) )
        result = query.first()
       
        if result:
            session['logged_in'] = True
            session["login_message"]="logged in successfully"
            
            query = s.query(User).with_entities(User.id,User.username).filter(User.email.like(email))
            result=query.first()
            user_id=int(result[0])
            username=result[1]

            session['user_id']=user_id
            session['username']=username

           
            return menu()
        else:
            flash('wrong password or email!')
            return home()
    # print("notin")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

@app.route("/register" ,methods=['POST',"GET"])
def register():
    # if request.method=="get":
    #     return render_template("register.html")
    if request.method=='POST':
        
        name=str(request.form['username'])
        Email=str(request.form['email'])
        password=str(request.form['password'])
        u=User(username=name, email=Email, password=password)
        db.session.add(u)
        db.session.commit()
        session["message"]="registeration successful"
        return login()
    
    return render_template("register.html")

@app.route("/add_expense",methods=['POST','GET'])
def add_expense():
    if session['logged_in']==True:
        if request.method=='GET':
    
                return render_template("add_expense.html")
        elif request.method=='POST':
            
            category=str(request.form["expense"])
            print(category)
            amount=int(request.form["amount"])
            e=Expense(category=category, amount=amount,user_id=session["user_id"])
            db.session.add(e)
            db.session.commit()
            session["expense_message"]="Expense added"
            return menu()
    else:
        session["login_message"]="please login"
        return login()

@app.route("/add_income",methods=['POST','GET'])
def add_income():
    
    if session['logged_in']==True:
        if request.method=='GET':
                return render_template("add_income.html")
        if request.method=='POST':
            source=str(request.form["source"])
            amount=int(request.form["amount"])
            i=Income(source=source, amount=amount,user_id=session["user_id"])
            db.session.add(i)
            db.session.commit()
            session["Income_message"]="Income added"
            return redirect (url_for("menu"))

@app.route("/menu")
def menu():
    if session["logged_in"]==True:
        engine = create_engine('mysql://root:''@localhost/flask_expense_tracker', echo=True)

        Session = sessionmaker(bind=engine)
        s = Session()
        d = datetime.now()

        month=d.strftime("%m")
        year=d.year
        print(month,year)
        

        month_expense=s.query(Expense).with_entities(Expense.category,Expense.amount).filter(Expense.user_id.like(session["user_id"])).filter(extract('year',Expense.date)==year).filter(extract('month',Expense.date)).all()
        month_income=s.query(Income).with_entities(Income.source,Income.amount).filter(Income.user_id.like(session["user_id"])).filter(extract('year',Income.date)==year).filter(extract('month',Income.date)).all()
        print(month_expense)
        print(month_income)
        # month_expense=s.query(Expense).with_entities(Expense.category,Expense.amount).filter(Expense.user_id.like(session["user_id"])).filter(extract('year',Expense.date)==year).filter(extract('month',Expense.date)).all()
        expense_distribution = s.query(Expense).with_entities(func.sum(Expense.amount).label("sum"), Expense.category).group_by(Expense.category).filter(Expense.user_id.like(session["user_id"])).filter(extract('year',Expense.date)==year).filter(extract('month',Expense.date)).all()
        print(expense_distribution)
        amount=[int(i[0]) for i in expense_distribution]
        category=[i[1] for i in expense_distribution]
        e=sum(amount)
        earned=sum([int(i[1]) for i in month_income])

        print(amount,category)
        plt.clf()
        fig = plt.figure(figsize = (6, 4))
        plt.pie(amount,labels=category,
        autopct='%1.1f%%', pctdistance=0.85)
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig = plt.gcf()
        
        # Adding Circle in Pie chart
        fig.gca().add_artist(centre_circle)
        plt.savefig('static/images/expense.png',transparent=True)
        plt.clf()
        fig = plt.figure(figsize = (6, 4))
        plt.bar(category,amount,color ='maroon',
        width = 0.4)
        plt.savefig('static/images/expense1.png',transparent=True)
  
       
        return render_template("menu.html",income=month_income,expense=month_expense,amount=amount,category=category,e=e,earned=earned)



    

if __name__=="__main__":
    
    app.run(debug=True)
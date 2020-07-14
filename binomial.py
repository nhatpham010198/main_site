
import numpy as np
import math
from datetime import datetime
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy



#binding the instance to a very specific Flask application:
app = Flask(__name__) #create an instance
 #create an instance
# URI format 'SQLALCHEMY_DATABASE_URI' and 'sqlite:///test.db' go together
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tired.db'
# app1.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tired2.db'

db = SQLAlchemy(app)
# db1 = SQLAlchemy(app1)

# you can declare a model/data base
class table1(db.Model):
    __tablename__ = 'table1'
    id = db.Column(db.Integer, primary_key=True)
    a = db.Column(db.Float)
    b = db.Column(db.Float)
    c = db.Column(db.Float)
    d = db.Column(db.Float)
    e = db.Column(db.Float)



class table2(db.Model):
    __tablename__ = 'table2'
    id = db.Column(db.Integer, primary_key=True)
    a = db.Column(db.Float)
    b = db.Column(db.Float)
    c = db.Column(db.Float)
    d = db.Column(db.Float)
    e = db.Column(db.Float)

class table3(db.Model):
    __tablename__ = 'table3'
    id = db.Column(db.Integer, primary_key=True)
    a = db.Column(db.Float)
    b = db.Column(db.Float)
    c = db.Column(db.Float)
    d = db.Column(db.Float)
    e = db.Column(db.Float)
db.create_all()
db.session.commit()

# The index function will pass the entries to the show_entries.html template and
# return the rendered one:
#determine what url to where results of the functions are shown.
#route('/') means the url is localhost:5000. route('/home') means the url is localhost:5000/home/

## lattice price
def price(p_0, n, u, d):

    price_lattice = [[0 for _ in range(n+1)] for _ in range(n+1)]
    price_lattice[n][0] = p_0
    for i in range(1,n+1):
        price_lattice[n][i] = price_lattice[n][i-1] * d
    for period in range(1, n + 1):
        for state in range(n, n - period, -1):
            price_lattice[state-1][period] = price_lattice[state][period] * u**2
    return(np.array(price_lattice))

## vanila option
def vanila_option(p_0, n, v, r, s, country, R, T, cp):
    import math
    import numpy as np
    if cp not in [1,-1]:
        raise ValueError('CP should be either 1 (if call) or 0 (if put) ')

    u = math.exp(v*math.sqrt(T/n))
    d = 1/u
    discount = math.exp(r*T/n)
    q = (math.exp((r-R)*T/n)-d)/(u-d)
#     print(u,d,discount,q)
    price_lattice = price(p_0, n, u, d)
    valuation = [[0 for _ in range(n+1)] for _ in range(n+1)]
    stock = [[0 for _ in range(n+1)] for _ in range(n+1)]
    cash = [[0 for _ in range(n+1)] for _ in range(n+1)]

    if country == 'EU':
        for state in range(n+1):
            valuation[state][n] = round(max(cp*(price_lattice[state][n] - s), 0),2)
        for period in range(n-1, -1, -1):
            for state in range(n, n - period - 1, -1):
                valuation[state][period] = round(((1-q)*valuation[state][period+1] + q*valuation[state-1][period+1])/discount,2)

                upside_return = valuation[state-1][period+1]
                downside_return = valuation[state][period+1]
                stock[state][period] = round((upside_return-downside_return)/(price_lattice[state][period]*(u-d)),2)
                cash[state][period] = round((upside_return*d-downside_return*u)/(discount*(d-u)),2)
        return(valuation[n][0], valuation, stock, cash)


    elif country == 'US':
        for state in range(n+1):
            valuation[state][n] = round(max(cp*(price_lattice[state][n] - s), 0),2)
        for period in range(n-1, -1, -1):
            for state in range(n, n - period - 1, -1):
                valuation[state][period] = round(max(max(cp*(price_lattice[state][period] - s),0),
                                               ((1-q)*valuation[state][period+1] + q*valuation[state-1][period+1])/discount),2)

                upside_return = valuation[state-1][period+1]
                downside_return = valuation[state][period+1]
                stock[state][period] = round((upside_return-downside_return)/(price_lattice[state][period]*(u-d)),2)
                cash[state][period] = round((upside_return*d-downside_return*u)/(discount*(d-u)),2)

                if valuation[state][period] == max(cp*(price_lattice[state][period] - s),0):
                    exercise = [period,state]

        # print('Exercise the US option at period', exercise[0])

        return(valuation[n][0], valuation, stock, cash)

    else:
        raise ValueError('country should be either US or EU')

@app.route('/', methods=['POST', 'GET'])
def index():
    #request.method: method of the action
    # request is a class imported above
    if request.method == 'POST':
        option_p_0 = float(request.form.get('p_0'))
        option_n = int(request.form.get('n'))
        option_v = float(request.form.get('v'))
        option_r = float(request.form.get('r'))
        option_s = float(request.form.get('s'))
        option_country = str(request.form.get('country'))
        option_c = float(request.form.get('c'))
        option_T = float(request.form.get('T'))
        option_cp = int(request.form.get('cp'))
        # option_cp = 1 if typeoption == "Call" else -1



        # price = vanila_option(option_p_0, option_n, option_v, option_r, option_s, option_country, option_c, option_T, option_cp)[0]
        _, price, stock, cash  = vanila_option(option_p_0, option_n, option_v, option_r, option_s, option_country, option_c, option_T, option_cp)
        # price = sum([option_p_0, option_n, option_v, option_r, option_s, option_c, option_T, option_cp])
        # pass information in the content section (saved as task_content) as new item named new_task
        # round_price = round(price, 2)
        # new_option = NP(p_0 = option_p_0, n = option_n, v = option_v, r = option_r, s = option_s, country = option_country,
        # c = option_c, T = option_T, cp = option_cp, valuation = price, round_valuation = round_price)


        #add new_task to the database (db table)
        # without session and commit, we have to do it mannually (declare new entries
        # and type these commands to add new entries to the table)
        return (render_template('a.html', prices = price, stocks = stock, cash = cash,
                                          option_p_0=option_p_0, option_n=option_n, option_v=option_v,option_r=option_r,
                                          option_s=option_s, option_country=option_country, option_c=option_c,
                                          option_T=option_T, option_cp=option_cp )) #render a template, and show all value assigned to 'tasks' variable

        try:
            for a,b,c,d,e in cash:
                row = table3(a=a,b=b,c=c,d=d,e=e)
                db.session.add(row)

            for a,b,c,d,e in stock:
                row = table2(a=a,b=b,c=c,d=d,e=e)
                db.session.add(row)

            for a,b,c,d,e in price:
                row = table1(a=a,b=b,c=c,d=d,e=e)
                db.session.add(row)

            db.session.commit()


            # return redirect('/')

        except:
            return 'There was an issue adding your task'

    #if GET, return all item in the table
    else:
        prices = table1.query[-5:]
        stocks = table2.query[-5:]
        cash = table3.query[-5:]


        return (render_template('machine.html', prices = prices, stocks = stocks, cash = cash))

if __name__ == "__main__":
    app.run(debug=True)

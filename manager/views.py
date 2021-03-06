from django.shortcuts import render, redirect
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import *
import plotly
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
import requests
import pandas as pd
import numpy as np
from .forms import *
from django.contrib import messages
from .keys import ALPHAVANTAGE_API_KEY
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import plotly.express as px
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go

df = pd.read_csv("manager\digital_currency_list.csv")
names = df.iloc[:, 1].values


# Create your views here.
def home(request):
    # put_historical_data()
    return render(request, 'homepage.html')


def logoutUser(request):
    logout(request)
    return redirect('login')


def loginUser(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            name = request.POST.get('username')
            pwd = request.POST.get('password')
            user = authenticate(request, username=name, password=pwd)
            if user is not None:
                login(request, user)
                return redirect('home')
    messages.success(request, f'Login successful!')
    return render(request, 'login.html')


def registerUser(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    prior = Stocks.objects.filter(user=request.user)
    context={
        'stocks':prior,
    }
    return render(request, 'dashboard.html',context)

@login_required
def buy(request):
    global coin_data
    global name, amt, total_coins, total_money
    search=request.POST.get('search')
    if request.method == 'POST' and search is not None:
        try:
            match = df[df['currency name'] == request.POST.get('search')]
            name = request.POST.get('search')
            coin_data = pd.read_csv(r"manager\crypto_data" + "\\" + match.iloc[0, 0] + ".csv")
            #color_discrete_map = { 'Open': 'rgb(255,0,0)'}
            fig = px.line(coin_data, x="Date", y=coin_data.columns[1:2], width=1050, height=500)
            graph1 = plotly.offline.plot(fig, auto_open=False, output_type="div")
            fig = px.line(coin_data, x="Date", y=coin_data.columns[5:],width=1050, height=500)
            graph2 = plotly.offline.plot(fig, auto_open=False, output_type="div")
            fig = px.line(coin_data, x="Date", y=coin_data.columns[2:3],width=1050, height=500)
            graph3 = plotly.offline.plot(fig, auto_open=False, output_type="div")
            fig = px.line(coin_data, x="Date", y=coin_data.columns[3:4],width=1050, height=500)
            graph4 = plotly.offline.plot(fig, auto_open=False, output_type="div")
            fig = px.line(coin_data, x="Date", y=coin_data.columns[4:5],width=1050, height=500)
            graph5 = plotly.offline.plot(fig, auto_open=False, output_type="div")
            context = {"graph": [graph1,graph2,graph3,graph4,graph5]}
            return render(request, 'buy.html', context)
        except:
            context = {"err": "Currency not found!"}
            return render(request, 'buy.html', context)
    else:
        if request.method == 'POST':
            amt= int(request.POST.get('buyform'))
            per_coin_price = coin_data.iloc[0,1]
            print(coin_data)
            print(per_coin_price)
            total_coins = round(amt/per_coin_price)
            total_money = 100000
            context = {"amt": amt,"total_coins":total_coins,"name": name,
                       "date":date.today(),"total_money": total_money, "pcp":per_coin_price }

            return render(request, 'buyform.html', context)
    return render(request, 'buy.html')

@login_required
def goal(request):
    # put_historical_data()
    return render(request, 'goal.html')


def put_historical_data():
    df = pd.read_csv("manager\digital_currency_list.csv")
    codes = df.iloc[:, 0].values
    for code in codes:
        df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        url_crypto = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={code}&market=INR&apikey={ALPHAVANTAGE_API_KEY}"
        r = requests.get(url_crypto)
        data = r.json()
        try:
            counter = 0
            for days, values in data.get("Time Series (Digital Currency Daily)").items():
                li = [days]
                li.extend([values['1a. open (INR)'], values['2a. high (INR)'], values['3a. low (INR)'],
                           values['4a. close (INR)'], values['5. volume']])
                df.loc[counter] = li
                counter += 1
            df.to_csv(r"manager\crypto_data" + "\\" + code + ".csv", index=False)
        except:
            pass
@login_required
def buyform(request):
    
    if request.method == 'POST':
        print(name)
        prior = Stocks.objects.filter(user=request.user).filter(name=name)
        if len(prior) == 1:
            for crypto in prior:
                print('Prior',crypto.user,crypto.name,crypto.total_coins_bought)
                crypto.total_coins_bought += total_coins
                crypto.total_money_invested += amt
                crypto.total_money_now -= amt
                print(crypto.user, crypto.name, crypto.total_coins_bought)
                crypto.save()
                
        else:
            stock = Stocks(
                user = request.user,
                name = name,
                dob=date.today(),
                total_coins_bought = total_coins,
                total_money_invested = amt,
                total_money_now = total_money
            )
            stock.save()
            print("Stock saved")
            messages.success(request, f'Purchase successfull')
    prior = Stocks.objects.filter(user=request.user)
    context={
        'stocks':prior,
    }
    return render(request, 'dashboard.html',context)

    
@login_required
def sell(request,name):
    global name_sell, total_coins_sell, per_coin_price_sell, amt_sell
    print(name)
    name_sell = name
    match = df[df['currency name'] == name]
    data = pd.read_csv(r"manager\crypto_data" + "\\" + match.iloc[0, 0] + ".csv")
    fig = px.line(data, x="Date", y=data.columns[1:2], width=1050, height=500)
    graph1 = plotly.offline.plot(fig, auto_open=False, output_type="div")
    fig = px.line(data, x="Date", y=data.columns[5:],width=1050, height=500)
    graph2 = plotly.offline.plot(fig, auto_open=False, output_type="div")
    fig = px.line(data, x="Date", y=data.columns[2:3],width=1050, height=500)
    graph3 = plotly.offline.plot(fig, auto_open=False, output_type="div")
    fig = px.line(data, x="Date", y=data.columns[3:4],width=1050, height=500)
    graph4 = plotly.offline.plot(fig, auto_open=False, output_type="div")
    fig = px.line(data, x="Date", y=data.columns[4:5],width=1050, height=500)
    graph5 = plotly.offline.plot(fig, auto_open=False, output_type="div")
    context = {"graph": [graph1,graph2,graph3,graph4,graph5]}
    

    if request.method == 'POST':
        total_coins_sell = int(request.POST.get('sellform'))
        prior = Stocks.objects.filter(user=request.user).get(name=name_sell)
        if total_coins_sell > prior.total_coins_bought:
            messages.info(request, 'Invalid number of coins. Please enter coins that you currently have !')
            # We can show total coins user has here to improve UX
            return render(request, 'sell.html')
        per_coin_price_sell = data.iloc[0, 1]

        amt_sell = round(total_coins_sell * per_coin_price_sell)
        # total_money = 100000
        context = {"amt": amt_sell, "total_coins": total_coins_sell, "name": name,
                   "date": date.today(), "pcp": per_coin_price_sell}

        return render(request, 'sellform.html', context)

    return render(request, 'sell.html', context)

@login_required
def sellform(request):
    print('Hello sell')
    if request.method == 'POST':
        print(name_sell)
        crypto = Stocks.objects.filter(user=request.user).get(name=name_sell)
        if crypto.total_coins_bought - total_coins_sell == 0:
            crypto.delete()
        else:
            print('Prior', crypto.user, crypto.name, crypto.total_coins_bought)
            crypto.total_coins_bought -= total_coins_sell
            crypto.total_money_invested -= amt_sell
            crypto.total_money_now -= amt_sell
            crypto.save()
            print(crypto.user, crypto.name, crypto.total_coins_bought)
            print("Stock sold")
            messages.success(request, f'Sold successfully!')
    prior = Stocks.objects.filter(user=request.user)
    context={
        'stocks':prior,
    }
    return render(request, 'dashboard.html',context)

@login_required
def goal(request):
    if request.method=="POST":
        returns = int(request.POST.get('returns'))
        tp = int(request.POST.get('time'))
        print(date.today())
        six_months = str(date.today() + relativedelta(weeks=-tp))
        print(six_months)
        l=[]
        for i in os.listdir(r"manager\crypto_data"):
            t=pd.read_csv(r"manager\crypto_data" + "\\" + i)
            if len(t[t.Date==six_months].Open.values)>0:
                m=t[t.Date==six_months].Open.values[0]
                print(m)
                current=t.iloc[0,1]
                if ((current-m)/m)*100>=returns:
                    l.append(df[df['currency code']==i[:-4]]['currency name'].values[0])
        context={'stocks':[x for x in l if " " not in x]}
        print(context)
        return render(request,'list.html',context)
    return render(request, 'goal.html')

@login_required
def goalbuy(request,name1):
    global amt, total_coins, total_money

    global name
    search=request.POST.get('search')
    name=name1
    if request.method == 'POST' and search is None:
        match = df[df['currency name'] == name1]
        print(match,name1)        
        coin_data = pd.read_csv(r"manager\crypto_data" + "\\" + match.iloc[0, 0] + ".csv")
    
        amt= int(request.POST.get('buyform'))
        per_coin_price = coin_data.iloc[0,1]
        print(coin_data)
        print(per_coin_price)
        total_coins = round(amt/per_coin_price)
        total_money = 100000
        context = {"amt": amt,"total_coins":total_coins,"name": name1,
                    "date":date.today(),"total_money": total_money, "pcp":per_coin_price }
        print("babaaaaaaaaaa")
        return render(request, 'buyform.html', context)
    else: 
        if search is None:
            search=name1
        try:
            match = df[df['currency name'] == search]
            print(match,search)        
            coin_data = pd.read_csv(r"manager\crypto_data" + "\\" + match.iloc[0, 0] + ".csv")
            match = df[df['currency name'] == request.POST.get('search')]
            fig = px.line(coin_data, x="Date", y=coin_data.columns[1:2], width=1050, height=500)
            graph1 = plotly.offline.plot(fig, auto_open=False, output_type="div")
            fig = px.line(coin_data, x="Date", y=coin_data.columns[5:],width=1050, height=500)
            graph2 = plotly.offline.plot(fig, auto_open=False, output_type="div")
            fig = px.line(coin_data, x="Date", y=coin_data.columns[2:3],width=1050, height=500)
            graph3 = plotly.offline.plot(fig, auto_open=False, output_type="div")
            fig = px.line(coin_data, x="Date", y=coin_data.columns[3:4],width=1050, height=500)
            graph4 = plotly.offline.plot(fig, auto_open=False, output_type="div")
            fig = px.line(coin_data, x="Date", y=coin_data.columns[4:5],width=1050, height=500)
            graph5 = plotly.offline.plot(fig, auto_open=False, output_type="div")
            context = {"graph": [graph1,graph2,graph3,graph4,graph5]}
        except:
            context = {"err": "Currency not found!"}
        return render(request, 'buy.html', context)



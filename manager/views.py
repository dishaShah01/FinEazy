from django.shortcuts import render, redirect
from datetime import date
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
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import plotly.express as px

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


def dashboard(request):
    return render(request, 'dashboard.html')


def buy(request):
    global coin_data
    global name, amt, total_coins, total_money
    search=request.POST.get('search')
    if request.method == 'POST' and search is not None:
        match = df[df['currency name'] == request.POST.get('search')]
        name = request.POST.get('search')
        coin_data = pd.read_csv(r"manager\crypto_data" + "\\" + match.iloc[0, 0] + ".csv")
        fig = px.line(coin_data, x="Date", y=coin_data.columns[1:])
        graph = plotly.offline.plot(fig, auto_open=False, output_type="div")
        context = {"graph": graph}
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

def buyform(request):
    print('Hello')
    if request.method == 'POST':
        print(name)
        prior = Stocks.objects.filter(user=request.user).filter(name=name)
        if len(prior) == 1:
            for crypto in prior:
                print('Prior',crypto.user,crypto.name,crypto.total_coins_bought)
                crypto.total_coins_bought += total_coins
                crypto.total_money_invested += amt
                crypto.total_money_now -= amt
                crypto.save()
                print(crypto.user, crypto.name, crypto.total_coins_bought)
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
    return render(request, 'dashboard.html')
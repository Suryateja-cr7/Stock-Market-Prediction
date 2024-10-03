import bs4 as bs
from collections import Counter
import datetime as dt
import numpy as np
import os
import pandas as pd
import pandas_datareader.data as web
import pickle
import requests
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')
from sklearn import svm, neighbors
from sklearn.model_selection import train_test_split  
from sklearn.ensemble import VotingClassifier,RandomForestClassifier

def save_sp500_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text,'lxml')
    table = soup.find('table',{'class':'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker.strip())
    
    with open("sp500tickers.pickle","wb") as f:
        pickle.dump(tickers,f)
    
    print(tickers)
    return tickers

# save_sp500_tickers()

def get_data_from_yahoo(reload_sp500=False):

    with open("sp500tickers.pickle","rb") as f:
        tickers =pickle.load(f)

    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')

    start = dt.datetime(2020,1,1)
    end = dt.datetime(2023,11,12)

    for ticker in tickers:
        print(ticker)
        if not os.path.exists("stock_dfs/{}.csv".format(ticker)):
            df = yf.download(ticker,start,end)
            df.to_csv("stock_dfs/{}.csv".format(ticker))     
        else:
            print("already have")

get_data_from_yahoo()   
 
def compile_data():
    with open("sp500tickers.pickle","rb") as f:
        tickers = pickle.load(f)
    main_df=pd.DataFrame()
    for count,ticker in enumerate(tickers):
        df = pd.read_csv("stock_dfs/{}.csv".format(ticker))
        df.set_index('Date',inplace=True)
        df.rename(columns={'Adj Close':ticker},inplace=True)
        df.drop(['Open','High','Low','Close','Volume'],axis=1,inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df=main_df.join(df,how='outer')
        
        if count % 10 == 0:
            print(count)
    main_df.to_csv('sp500_joined_closes.csv')

compile_data()
def visulaize_data():
    df = pd.read_csv('sp500_joined_closes.csv')
    #df['AAPL\n'].plot()
    #plt.show()
    df1=df
    # Assuming your DataFrame is named 'df'
    df1 = df1.drop(['Date'], axis=1)

# Reset the index after dropping rows
    df1.reset_index(drop=True, inplace=True)

    #df1=df1.drop(['Date'],axis=1,inplace=True)
    df_corr = df1.corr()
    print(df_corr.head())

# visulaize_data()

def process_data_for_labels(ticker):
    h_days = 7
    df = pd.read_csv('sp500_joined_closes.csv',index_col=0)
    print(df.head())
    tickers=df.columns.values.tolist()
    df.fillna(0,inplace=True)
    for i in range(1,h_days+1):
        df['{}_{}d'.format(ticker,i)] = (df[ticker].shift(-i)-df[ticker])/df[ticker]
    #df = df.drop(['Date'], axis=1,inplace=True)

# Reset the index after dropping rows
    #df.reset_index(drop=True, inplace=True)
    df.fillna(0,inplace=True)
    print(df.head())
    return tickers,df

# process_data_for_labels('ABBV')

def buy_sell_hold(*args):
    cols = [c for c in args]
    x = 0.02
    for col in cols:
        if col > x:
            return 1
        if col < -x:
            return -1
    return 0

def extract_requirements(ticker):
    tickers,df = process_data_for_labels(ticker)
    df['{}_target'.format(ticker)] = list(map(buy_sell_hold, df['{}_1d'.format(ticker)], df['{}_2d'.format(ticker)], df['{}_3d'.format(ticker)], df['{}_4d'.format(ticker)], df['{}_5d'.format(ticker)], df['{}_6d'.format(ticker)], df['{}_7d'.format(ticker)]))
    #df['{}_target'.format(ticker)] = list(map(buy_sell_hold,df['{}_1d'.format(ticker)],df['{}_2d'.format(ticker)],df['{}_3d'.format(ticker),df['{}_4d'.format(ticker)]],df['{}_5d'.format(ticker)],df['{}_6d'.format(ticker)],df['{}_7d'.format(ticker)]))
    vals = df['{}_target'.format(ticker)].values.tolist()
    str_vals = [str(i) for i in vals]
    print('Data Spread:',Counter(str_vals))
    df.fillna(0,inplace=True)
    df = df.replace([np.inf,-np.inf],np.nan)
    df.dropna(inplace=True)

    df_vals = df[[ticker for ticker in tickers]].pct_change()
    df_vals = df_vals.replace([np.inf,-np.inf],0)
    df_vals.fillna(0,inplace=True)
    
    X = df_vals.values
    y=df['{}_target'.format(ticker)].values
    print(X)
    return X,y,df

#extract_requirements('XOM')
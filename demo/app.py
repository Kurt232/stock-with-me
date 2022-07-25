# -*- coding: utf-8 -*-
"""
---------------------------------------------------------
    File Name :         app                             
    Description :       flask echo server
    Author :            Karl                             
    Date :              2022-07-23                          
---------------------------------------------------------
    Change Activity :   2022-07-23
    
--------------------------------------------------------- 
"""
from flask import Flask, jsonify
from flask_socketio import SocketIO
from keras.models import load_model
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import re
from wordcloud import WordCloud
from wordcloud import ImageColorGenerator
from wordcloud import STOPWORDS
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
import base64
import io
import PIL.ExifTags
import PIL.Image
import PIL.ImageOps
import cv2
import warnings
warnings.filterwarnings("ignore")
import sklearn 
import datetime
import math
from datetime import datetime
from matplotlib import style
import pandas_datareader.data as pdr
from sklearn import datasets,linear_model,model_selection
from sklearn.model_selection import train_test_split
from sklearn import preprocessing,svm,tree
import sklearn.svm as svm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')  # 可以跨域了

def getInformation(stockName):

    wd = webdriver.Chrome(r'C:\Users\nnn\Downloads\chromedriver_win32\chromedriver.exe')
    #   爬虫需要安装浏览器引擎(https://chromedriver.storage.googleapis.com/index.html)并将上面read的地址改成自己储存的位置
    wd.implicitly_wait(5)  # 最长等待时间

    titleList = []
    summaryList = []
    linkList = []

    ##  Google搜索股票
    wd.get("https://www.google.com/?gl=us&hl=en&gws_rd=cr&pws=0")
    inputElement = wd.find_element(By.XPATH,"//input[@class = 'gLFyf gsfi']") #寻找搜索框元素
    inputElement.send_keys(stockName) #输入搜索内容
    enterElement = wd.find_element(By.XPATH,"//input[@class = 'gNO89b']").click()#输入回车
    newsElement = wd.find_element(By.XPATH,"//div[@class = 'MUFPAc']//a[text()='News']").click()#限定在“新闻”内
    ##  获取每页新闻及摘要
    for i in range(5):
        informationList = wd.find_elements(By.XPATH,"//div[@role = 'heading']")
        for information in informationList:
            title = information.text
            titleList += [title]
            try:
                summary = information.find_element(By.XPATH,".//following-sibling::div[1]").text
                summaryList += [summary]
                link = information.find_element(By.XPATH,"./parent::div[1]/parent::div[1]/parent::a[1]").get_attribute('href')
                linkList += [link]
            except:
                continue
        next = wd.find_element(By.XPATH,"//td[@class = 'YyVfkd']//following-sibling::td[1]").click()   

    wd.close()   
    return [titleList,summaryList,linkList]

def translate(senti):
    if int(senti) == 0:
        print('positive')
    elif int(senti) == 1:
        print('neutral')
    else :
        print('negative')

def sentiment_ana(message, tokenizer, md2):
    seq = tokenizer.texts_to_sequences(message)
    padded = pad_sequences(seq, maxlen=50, dtype='int32', value=0)
    pred = md2.predict(padded)
    labels = ['0','1','2']

    return np.argmax(pred)

def cleanText(text):
    if text == None:
        return ' '
    text = re.sub(r'\|\|\|', r' ', text) 
    text = re.sub(r'http\S+', r'<URL>', text)
    text = text.lower()
    text = text.replace('x', '')
    return text

def predictStock(stockName):
    ##通过雅虎获取股票信息
    yahoo = pdr.DataReader(stockName,start = "2020",end = "2023",data_source = "yahoo")
    yahoo_close = yahoo["Close"]
    ##空值处理
    forecast = 'Close'
    yahoo.fillna(value=-99999, inplace=True)
    forecast_out = int(math.ceil(0.03 * len(yahoo)))#调整预测天数
    ##获取X和y
    yahoo['label'] = yahoo[forecast].shift(-forecast_out)
    X = np.array(yahoo.drop(['label'], 1))
    X = preprocessing.scale(X)
    X_late = X[-forecast_out:]
    X = X[:-forecast_out]
    yahoo.dropna(inplace=True)
    y = np.array(yahoo['label'])
    yahooLinear = yahoo.copy()
    yahooSvm = yahoo.copy()
    yahooTree = yahoo.copy()
    ##线性模型
    X_train, X_test, y_train ,y_test = model_selection.train_test_split(X,y,test_size=0.3)
    model_linear = linear_model.LinearRegression()
    model_linear.fit(X_train,y_train)
    forecast_set = model_linear.predict(X_late)
    style.use('ggplot')
    yahooLinear['Forecast']=np.nan
    last_date = yahooLinear.iloc[-1].name
    last_unix = last_date.timestamp()
    one_day = 86400
    next_unix = last_unix + one_day

    for i in forecast_set:
        next_date = datetime.fromtimestamp(next_unix)
        next_unix += 86400
        yahooLinear.loc[next_date] = [np.nan for _ in range(len(yahooLinear.columns)-1)]+[i]
    yahooLinear['Close'].plot()
    yahooLinear['Forecast'].plot()
    plt.savefig('./linear_model.png')
    
    ##支持向量机模型
    X_train, X_test, y_train ,y_test = model_selection.train_test_split(X,y,test_size=0.3)
    model_svm = svm.SVC(C=10,kernel='rbf')
    model_svm.fit(X_train,y_train.astype('int'))
    forecast_set = model_svm.predict(X_late)
    style.use('ggplot')
    yahooSvm['Forecast']=np.nan
    last_date = yahooSvm.iloc[-1].name
    last_unix = last_date.timestamp()
    one_day = 86400
    next_unix = last_unix + one_day
    for i in forecast_set:
        next_date = datetime.fromtimestamp(next_unix)
        next_unix += 86400
        yahooSvm.loc[next_date] = [np.nan for _ in range(len(yahooSvm.columns)-1)]+[i]
    yahooSvm['Close'].plot()
    yahooSvm['Forecast'].plot()
    plt.savefig('./svm_model.png')
    
    ##决策树模型
    X_train, X_test, y_train ,y_test = model_selection.train_test_split(X,y,test_size=0.3)
    model_tree = tree.DecisionTreeClassifier(criterion="gini")
    model_tree.fit(X_train,y_train.astype('int'))
    forecast_set = model_tree.predict(X_late)
    style.use('ggplot')
    yahooTree['Forecast']=np.nan
    last_date = yahooTree.iloc[-1].name
    last_unix = last_date.timestamp()
    one_day = 86400
    next_unix = last_unix + one_day
    for i in forecast_set:
        next_date = datetime.fromtimestamp(next_unix)
        next_unix += 86400
        yahooTree.loc[next_date] = [np.nan for _ in range(len(yahooTree.columns)-1)]+[i]
    yahooTree['Close'].plot()
    yahooTree['Forecast'].plot()
    plt.savefig('./decisiontree_model.png')

def ack():
    print('message was received!')

@socketio.on('connection')
def handle_connection():
    print('build connection')

@socketio.on('require_stock')
def handle_require_data(stockName):
    print('received message: ' + stockName)
    # there is handle InPut to return
    # 并发都无所谓
    # socketio.emit('response_data', handle(data)) data: str

    df = pd.read_csv('all-data.csv',delimiter=',',encoding='latin-1')
    df = df.rename(columns={'neutral':'sentiment','According to Gran , the company has no plans to move all production to Russia , although that is where the company is growing .':'Message'})
    md2 = load_model('saved.h5')
    tokenizer = Tokenizer(num_words=500000, split=' ', filters='!"#$%&()*+,-./:;<=>?@[\]^_`{|}~', lower=True)
    tokenizer.fit_on_texts(df['Message'].values)

    [t, s, l] = getInformation(stockName)

    data = pd.DataFrame([t, s, l])
    data = data.T
    data = data.rename(columns={0:'Title',1:'Message'})
    data.insert(loc=1, column='RawMessage', value=data['Message'])
    data['Message'] = data['Message'].apply(cleanText)

    positive=0
    negative=0
    neutral=0
    temp_sentiment = []

    for index,row in data.iterrows():
        sentiment = sentiment_ana([row['Message']], tokenizer, md2)
        if sentiment == 0:
            positive += 1
        elif sentiment == 2:
            negative += 1
        else :
            neutral += 1
        temp_sentiment.append(sentiment)

    data.insert(loc=0, column='sentiment', value=temp_sentiment)
    #   data是包含所有新闻内容的类型为DataFrame的对象
    #   positive， neutral，negative是各自新闻的总数

    data["mytext_new"] = data['Message'].str.lower().str.replace('[^\w\s]','')
    new_df = data.mytext_new.str.split(expand=True).stack().value_counts().reset_index()
    new_df.columns = ['Word', 'Frequency'] 
    dict1 = dict(zip(new_df['Word'],new_df['Frequency']))

    text = " ".join(i for i in data.Message)
    stopwords = set(STOPWORDS)
    stopwords = ['.','..','...', stockName.lower()] + list(STOPWORDS)

    for stopword in stopwords:
        if stopword in dict1 :
            dict1.pop(stopword)
    word_cloud = WordCloud(stopwords=stopwords, background_color="white")
    word_cloud.generate_from_frequencies(dict1)

    plt.figure( figsize=(15,10))
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig('./wordcloud.png')

    data = data.drop('Message', axis='columns')
    data['sentiment'] = data.sentiment.map(lambda x: "success" if x == 0 else ("info" if x == 1 else "danger"))
    predictStock(stockName)

    info = dict()
    info['positive'] = positive
    info['negative'] = negative
    data2 = data.to_dict('records')
    info['news'] = data2

    wordcloud_file = "wordcloud.png"
    with open(wordcloud_file,"rb") as f:
        wordcloud_image = f.read()
        wordcloud_Data = base64.b64encode(wordcloud_image).decode("utf-8")
    info['wordcloud'] = wordcloud_Data

    linear_model_file = "linear_model.png"
    with open(linear_model_file,"rb") as f:
        linear_model_image = f.read()
        linear_model_Data = base64.b64encode(linear_model_image).decode("utf-8")
    info['linear_model'] = linear_model_Data

    svm_model_file = "svm_model.png"
    with open(svm_model_file,"rb") as f:
        svm_model_image = f.read()
        svm_model_Data = base64.b64encode(svm_model_image).decode("utf-8")
    info['svm_model'] = svm_model_Data

    decisiontree_model_file = "decisiontree_model.png"
    with open(decisiontree_model_file,"rb") as f:
        decisiontree_model_image = f.read()
        decisiontree_model_Data = base64.b64encode(decisiontree_model_image).decode("utf-8")
    info['decisiontree_model'] = decisiontree_model_Data

    info_json = json.dumps(info)
    socketio.emit('info: ', info_json, callback=ack)

if __name__ == "__main__":
    socketio.run(app, host='localhost', port=4321)

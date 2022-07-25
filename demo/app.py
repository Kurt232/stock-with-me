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

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')  # 可以跨域了

def getInformation(stockName):

    wd = webdriver.Chrome(r'C:\Users\nnn\Downloads\chromedriver_win32\chromedriver.exe')
    #   爬虫需要安装浏览器引擎(https://chromedriver.storage.googleapis.com/index.html)并将上面read的地址改成自己储存的位置
    wd.implicitly_wait(5)  # 最长等待时间

    titleList = []
    summaryList = []

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
            except:
                continue
        next = wd.find_element(By.XPATH,"//td[@class = 'YyVfkd']//following-sibling::td[1]").click()   
    return [titleList,summaryList]

def translate(senti):
    if int(senti) == 0:
        print('positive')
    elif int(senti) == 1:
        print('neutral')
    else :
        print('negative')

def sentiment_ana(message):
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

    [t, s] = getInformation(stockName)

    data = pd.DataFrame([t,s])
    data = data.T
    data = data.rename(columns={0:'Title',1:'Message'})
    data.insert(loc=1, column='RawMessage', value=data['Message'])
    data['Message'] = data['Message'].apply(cleanText)

    positive=0
    negative=0
    neutral=0
    temp_sentiment = []

    for index,row in data.iterrows():
        sentiment = sentiment_ana([row['Message']])
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
    data = data.drop('Message', axis='columns')

    info = dict()
    info['stockName'] = stockName
    info['positive'] = positive
    info['negative'] = negative
    info['neutral'] = neutral
    info['total'] = positive + negative + neutral
    data2 = data.to_dict('records')
    info['news'] = data2
    info_json = json.dumps(info)

    socketio.emit('info: ', info_json, callback=ack)

if __name__ == "__main__":
    socketio.run(app, host='localhost', port=4321)

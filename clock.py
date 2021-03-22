import sqlite3
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
import datetime
import random
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

sched = BlockingScheduler()


TOKEN = ""
URL = f'https://api.telegram.org/bot{TOKEN}/'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ''
#dev
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/lexus'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Userid(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, unique=True)

    def __init__(self, user_id):
        self.user_id = user_id

# @sched.scheduled_job('interval', minutes=1)
@sched.scheduled_job('cron', hour=20)
def send_stuff():
    ids = database_ids()
    print(ids)
    for i in ids:
        send_message(i, text="IDIOM OF THE DAY:")
        idioms = idioms_text()
        for idiom in idioms:
            send_message(i, text=idiom)
        send_message(i, text='MEMES OF THE DAY:')
        links = meme_img_links()
        for link in links:
            send_img(i, link)


def meme_img_links():
    # r = requests.get('https://cleanmemes.com/')
    # soup = BeautifulSoup(r.text, features='html.parser')
    # l = [x for x in soup.find_all('header', class_='entry-header')]
    # r = requests.get(l[1].h2.a.attrs['href'])
    date = str(datetime.datetime.now())[:10]

    r = requests.get('https://cleanmemes.com/%s/clean-memes-%s/'%(date.replace("-","/"), date[5:]+date[4]+date[:4]))
    if r.status_code != 404:
        soup = BeautifulSoup(r.text, features='html.parser')
        img_links = soup.find('p', class_='').findChildren('a')
        res = []
        for i in img_links:
            res.append(i['href'])
        return res
    else:
        current_year = int(str(datetime.datetime.now())[:4])
        days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28']
        months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        current_month = str(datetime.datetime.now())[5:7]
        last_month_index = months.index(current_month)-1
        date = "%s-%s-%s"%(current_year, months[last_month_index], random.choice(days))
        r = requests.get('https://cleanmemes.com/%s/clean-memes-%s/'%(date.replace("-","/"), date[5:]+date[4]+date[:4]))
        soup = BeautifulSoup(r.text, features='html.parser')
        img_links = soup.find('p', class_='').findChildren('a')
        res = []
        for i in img_links:
            res.append(i['href'])
        return res

def idioms_text():
    r = requests.get('https://www.theidioms.com/')
    soup = BeautifulSoup(r.text, features='html.parser')
    div = soup.find('div', class_='daily')
    div_link = div.p.a.attrs['href']
    r = requests.get(div_link)
    soup = BeautifulSoup(r.text, features='html.parser')
    article = soup.find('div', class_='article').findChildren('p', class_='')
    res = []
    for i in article:
        if len(i.getText())!=0:
            res.append(str(i.getText()))
    return res

def database_ids():
    ids = db.session.query(Userid)
    list_ids = []
    for id in ids:
        list_ids.append(int(id.user_id))
    return list_ids

def send_message(chat_id, text="hello"):
    url = URL + 'sendMessage'
    answer = {'chat_id':chat_id, 'text':text}
    r = requests.post(url, json=answer)
    return r.json()

def send_img(chat_id, photo):
    url = URL + 'sendPhoto'
    photo = {'chat_id':chat_id, 'photo':photo}
    r = requests.post(url, json=photo)
    return r.json()


sched.start()

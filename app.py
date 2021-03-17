from flask import Flask
#from flask_sslify import SSLify
from flask import request
from flask import jsonify
import requests
import json
from bs4 import BeautifulSoup
import datetime
import random
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

TOKEN = "1312582932:AAGKZ3wEZSo_9nzb_TDRPQl7aVhPPIaDCis"

app = Flask(__name__)
#sslify = SSLify(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://shodqieclttuev:65c28597be559e4bf896c9c3a41456ba4c94e74036af5269ea5a4e076e9da768@ec2-52-71-107-99.compute-1.amazonaws.com:5432/d8d4359m0f53dj'
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

#https://api.telegram.org/bot1312582932:AAGKZ3wEZSo_9nzb_TDRPQl7aVhPPIaDCis/setWebhook?url=https://v4h4.pythonanywhere.com/
#https://api.telegram.org/bot1312582932:AAGKZ3wEZSo_9nzb_TDRPQl7aVhPPIaDCis/setWebhook?url=https://ab2be63470db.ngrok.io/
@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        try:
            r = request.get_json()
            #write_json(r)
            chat_id = r['message']['chat']['id']
            message = r['message']['text']
            if message == '/start':
                #add_to_database(chat_id=str(chat_id))
                #if there isnt such user in database this code adds him/her to database
                # if db.session.query(Userid).filter(Userid.user_id == chat_id).count() == 0:
                #     data = Userid(user_id=chat_id)
                #     db.session.add(data)
                #     db.session.commit()
                data = db.session.query(Userid)
                counts = 0
                for d in data:
                    if d.user_id==str(chat_id):
                        counts+=1
                if counts==0:
                    add_data = Userid(user_id=chat_id)
                    db.session.add(add_data)
                    db.session.commit()
                send_message(chat_id, text="IDIOM OF THE DAY:")
                idioms = idioms_text()
                for idiom in idioms:
                    send_message(chat_id, text=idiom)
                send_message(chat_id, text='MEMES OF THE DAY:')
                links = meme_img_links()
                for link in links:
                    send_img(chat_id, link)
            else:
                send_message(chat_id, text=message)
        except KeyError:
            pass
        return jsonify(r)
    return "<h1>HELLO FROM BOT</h1>"

@app.route('/waker', methods=['POST','GET'])
def waker():
    return "<h1>THATS A WAKER</h1>"

URL = f'https://api.telegram.org/bot{TOKEN}/'

# def write_json(data, filename='answer.json'):
#     with open(filename, 'w') as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)


def add_to_database(chat_id):
    connection = sqlite3.connect("chat_ids.db")
    cursor = connection.cursor()
    cursor.execute('''INSERT OR IGNORE INTO USERS VALUES (NULL, %s)
    '''%(chat_id))
    connection.commit()
    connection.close()

def database_ids():
    connection = sqlite3.connect("chat_ids.db")
    cursor = connection.cursor()
    ids = cursor.execute('SELECT * FROM USERS').fetchall()
    list_ids = []
    for i in ids:
        list_ids.append(i[1])
    connection.commit()
    connection.close()
    return list_ids

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
        date = "%s-%s-%s"%(current_year-1, months[last_month_index], random.choice(days))
        r = requests.get('https://cleanmemes.com/%s/clean-memes-%s/'%(date.replace("-","/"), date[5:]+date[4]+date[:4]))
        soup = BeautifulSoup(r.text, features='html.parser')
        img_links = soup.find('p', class_='').findChildren('a')
        res = []
        for i in img_links:
            res.append(i['href'])
        return res


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

if __name__ == '__main__':
    app.debug = True
    app.run()

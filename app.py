from flask import Flask, request, render_template
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from datetime import datetime, timezone
import requests

app = Flask(__name__)
SQLALCHEMY_DATABASE_URL = 'sqlite:////tmp/weather.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
Base = declarative_base()
API_KEY = '7a1c45cb67aa9811d480c28f2c51dddf'


class City(Base):
    __tablename__ = 'City'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    def __repr__(self):
        return '<User %r>' % self.username


Base.metadata.drop_all(engine) #<--- to clear the database
Base.metadata.create_all(engine)


def get_weather(city):
    r = requests.get('https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(city, API_KEY))
    time_now = int(datetime.now(tz=timezone.utc).timestamp())
    day_time = get_daytime(time_now, r.json())
    dict_with_weather_info = {'degrees': int(json.loads(r.text)['main']['temp']) - 273,
                              'state': json.loads(r.text)['weather'][0]['main'],
                              'city': city,
                              'day_time': day_time}
    return dict_with_weather_info


def get_daytime(time, response):
    hr_gap = 1
    if response['sys']['sunrise'] < time <= response['sys']['sunset'] - 3600 * hr_gap:
        return "day"
    # if hr_gap before and after sunrise or hr_gap before after sunset
    elif response['sys']['sunrise'] - 3600 * hr_gap < time < response['sys']['sunrise'] + 3600 * hr_gap or \
            response['sys']['sunset'] - 3600 * hr_gap < time < response['sys']['sunset'] + 3600 * hr_gap:
        return "evening-morning"
    else:
        return "night"


@app.route('/')
def index():
    cities_weather = []
    for city in session.query(City).order_by(City.id):
        cities_weather.append(get_weather(city.name))
    return render_template("index.html", cities=cities_weather)


@app.route('/', methods=['POST'])
def add_city():
    new = request.form['city_name'].upper()
    city_already_there = False
    for city in session.query(City).order_by(City.id):
        if new == city.name:
            city_already_there = True

    if not city_already_there:
        new_city = City(name=new)
        session.add(new_city)
        session.commit()

    cities_weather = []
    for city in session.query(City).order_by(City.id):
        cities_weather.append(get_weather(city.name))

    return render_template('index.html', cities=cities_weather)


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()

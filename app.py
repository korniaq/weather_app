from flask import Flask
from flask import request
import sys
from flask import render_template
import requests
import json

app = Flask(__name__)
API_KEY = '7a1c45cb67aa9811d480c28f2c51dddf'


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        city = request.form['city_name'].upper()
        r = requests.get('https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(city, API_KEY))
        dict = json.loads(r.text)
        dict_with_weather_info = {'degrees': int(dict['main']['temp'])-273, 'state': dict['weather'][0]['main'], 'city': city}
        return render_template('index.html', weather=dict_with_weather_info)

    return render_template("index.html")


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()

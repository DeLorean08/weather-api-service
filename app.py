import os
import json
from dotenv import load_dotenv
import requests
from redis import Redis
from flask import Flask, render_template, request

app = Flask(__name__)
load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")


def get_redis_client() -> Redis:
    return Redis(
        host=REDIS_HOST,
        port=REDIS_PORT, 
        db=0, 
        decode_responses=True
    )

cache = get_redis_client()

@app.route("/", methods=['GET', 'POST'])
def main():
    city = request.args.get('city')
    if city:
        data = cache.get(city)
        if data:
            weather_data = json.loads(data)
            return render_template('index.html', weather_data=weather_data)
        else:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                cache.setex(city, 1800, json.dumps(data))
                print(data)
                return render_template('index.html', weather_data=data)
    return render_template('index.html')





if __name__ == '__main__':
    app.run(debug=True)

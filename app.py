import os
import json
from dotenv import load_dotenv
import requests
from redis import Redis
from flask import Flask, render_template, request
from datetime import datetime

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
    formated_time = datetime.now().strftime("%a, %d %b")
    city = request.args.get('city')
    if city:
        data = cache.get(city)
        if data:
            weather_data = json.loads(data)
            return render_template('index.html', weather_data=weather_data, current_date=formated_time)
        else:
            url = url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                forecast_items = []
                for item in data["list"]:
                    if "12:00:00" in item["dt_txt"]:
                        date_obj = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
                        item['display_date'] = date_obj.strftime("%d %b")
                        forecast_items.append(item)
                    if len(forecast_items) == 3: 
                        break
                weather_dict = {
                    "city": data['city']['name'],
                    "current": data["list"][0],
                    "forecast": forecast_items
                }
                cache.setex(city, 1800, json.dumps(weather_dict))
                return render_template('index.html', weather_data=weather_dict, current_date=formated_time)
            else:
                return render_template('index.html', error=True, invalid_city=city)
    return render_template('index.html', current_date=formated_time)





if __name__ == '__main__':
    app.run(debug=True)

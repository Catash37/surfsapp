from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import requests
import arrow

# Key for swell forecast API
key_API = "8e6bc43c-e89b-11ed-92e6-0242ac130002-8e6bc4a0-e89b-11ed-92e6-0242ac130002"

# Initialize the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///surfboards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
Bootstrap(app)

# Create dictionaries for each city
cities_coordinates = {
    'Sydney': {'lat': -33.8688, 'long': 151.209900},
    'Perth': {'lat': -31.9514, 'long': 115.8617},
    'Melbourne': {'lat': -37.8136, 'long': 144.9631},
    'Brisbane': {'lat': -27.4701, 'long': 153.0210},
    'Adelaide': {'lat': -34.9285, 'long': 138.6007},
    'Hobart': {'lat': -42.880554, 'long': 147.3249}
}


# Define the model
class Surfboard(db.Model):
    __tablename__ = 'surfboards'

    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    skill_level = db.Column(db.String(50), nullable=False)
    tail_shape = db.Column(db.String(50), nullable=False)

    SKILL_LEVELS = {
        'beginner': 0.70,
        'progressive': 0.55,
        'advanced': 0.4,
    }

    TAIL_SHAPES_INFO = {
         'allround': 'Squash tail: Great for all-around performance.',
        'control': 'Round tail: Offers smooth turns and better control.',
        'big': 'Pin tail: Ideal for big waves, provides excellent hold.',
        'small': 'Swallow tail: Enhances maneuverability in small waves.'
    }

    @classmethod
    def calculate_volume(cls, weight, skill_level):
        # Get skill factor based on selected skill level
        skill_factor = cls.SKILL_LEVELS.get(skill_level, 1.0)

        # Calculate volume based on weight and skill level
        volume = weight * skill_factor

        return volume

    @staticmethod
    def calc_length(skill_level, weight):
        if skill_level in ('beginner', 'progressive'):
            if weight <= 55:
                return "5'8 - 6'2"
            elif 55 < weight <= 72:
                return "5'10 - 6'4"
            elif 72 < weight <= 82:
                return "6'0 - 6'8"
            else:
                return "6'4 - 6'10"
        elif skill_level == 'advanced':
            if weight <= 55:
                return "5'4 - 6'0"
            elif 55 < weight <= 72:
                return "5'6 - 6'2"
            elif 72 < weight <= 82:
                return "5'8 - 6'4"
            else:
                return "5'10 - 6'6"

    @staticmethod
    def surfboard_shape_rec(height_swell):
        if height_swell <= 0.5:
            return "Fish/Groveler/Longboard"
        elif 0.6 <= height_swell <= 1.0:
            return "Fish/Shortboard"
        elif 1.1 <= height_swell <= 1.5:
            return "Shortboard"
        elif 1.6 <= height_swell <= 2.0:
            return "Shortboard/Performance Shortboard"
        elif 2.1 <= height_swell <= 2.5:
            return "Performance Shortboard/Step Up"
        elif 2.6 <= height_swell <= 3.5:
            return "Step Up"
        elif height_swell >= 3.6:
            return "Gun/Tow - Good luck :0"
        else:
            return 'Invalid parameters'

    @staticmethod
    def get_city_coordinates(city):
        return cities_coordinates.get(city, "Invalid Location")

    @staticmethod
    def swell(city_coordinates, key):
        lat = city_coordinates['lat']
        lng = city_coordinates['long']

        # Get first hour of today
        start = arrow.now().floor('day')

        # Get last hour of today
        end = arrow.now().ceil('day')

        response = requests.get(
            'https://api.stormglass.io/v2/weather/point',
            params={
                'lat': lat,
                'lng': lng,
                'params': ','.join(['waveHeight', 'waterTemperature']),
                'start': start.to('UTC').timestamp,  # Convert to UTC timestamp
                'end': end.to('UTC').timestamp  # Convert to UTC timestamp
            },
            headers={
                'Authorization': key
            }
        )

        json_data = response.json()

        # Get the first entry in the dictionary
        first_entry = json_data['hours'][0]

        # Extract the waveHeight
        height_swell = first_entry['waveHeight']['sg']

        return height_swell


# Define the form
class SurfboardForm(FlaskForm):
    weight = FloatField('Weight (kg)', validators=[DataRequired()])
    skill_level = SelectField('Skill Level', choices=[
        ('beginner', 'Beginner'),
        ('progressive', 'Progressive'),
        ('advanced', 'Advanced'),
    ], validators=[DataRequired()])
    tail_shape = SelectField('Tail Shape', choices=[
        ('allround', 'All Rounder'),
        ('control', 'More Control'),
        ('big', 'Ride Big Waves'),
        ('small', 'Ride Smaller Waves'),
    ], validators=[DataRequired()])
    city = SelectField('Location:', choices=[
        ('Sydney', 'Sydney'),
        ('Melbourne', 'Melbourne'),
        ('Perth', 'Perth'),
        ('Brisbane', 'Brisbane'),
        ('Adelaide', 'Adelaide'),
        ('Hobart', 'Hobart')
    ])


def get_weather_data(city):
    api_key = 'f3337f70ad27b09a847fe7856d3ceaaf'
    base_url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    return response.json()


# Define the route
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SurfboardForm()
    error = None
    if form.validate_on_submit():
        weight = form.weight.data
        skill_level = form.skill_level.data
        tail_shape = form.tail_shape.data
        city = form.city.data
        city_coordinates = Surfboard.get_city_coordinates(city)
        
        if city_coordinates == "Invalid Location":
            error = "Invalid location selected"
        else:
            original_volume = Surfboard.calculate_volume(weight, skill_level)
            volume_lower = original_volume - 2
            volume_upper = original_volume + 8
            length = Surfboard.calc_length(skill_level, weight)
            height_swell = Surfboard.swell(city_coordinates, key_API)
            tail_info = Surfboard.TAIL_SHAPES_INFO.get(tail_shape, 'Unknown tail shape')
            board_rec = Surfboard.surfboard_shape_rec(height_swell)
            wetsuit_thickness = None
            wax_type = None

            weather_data = get_weather_data(city)
            if weather_data.get('cod') != 200:  # Check if the response contains an error code
                error = weather_data.get('message', 'Error fetching weather data')
            else:
                weather = weather_data
                temperature = weather_data.get('main', {}).get('temp')
                if temperature is not None:
                    if temperature <15:
                        wetsuit_thickness = "5-6mm. It might be worth considering a drysuit if you're planning a long surf."
                        wax_type = "cold water wax"
                    elif 15<= temperature <=18:
                        wetsuit_thickness = "3-4mm. A full length wetsuit is advised."
                        wax_type = "cool water wax"
                    elif 18<= temperature <=24:
                        wetsuit_thickness = "3-4mm. A full length wetsuit is advised."
                        wax_type = "warm water wax"
                    else:
                        wetsuit_thickness = "1-2mm. A shorty or surf jacket should be fine."
                        wax_type = "tropical water wax"
        return render_template('result.html', volume_lower=volume_lower, volume_upper=volume_upper, tail_info=tail_info, length=length, weather=weather, error=error, wetsuit_thickness=wetsuit_thickness, wax_type=wax_type, board_rec=board_rec)
    return render_template('calculate.html', form=form)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

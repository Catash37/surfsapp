from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import requests

# Initialize the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///surfboards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
Bootstrap(app)

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

def get_weather_data(city):
    api_key = 'f3337f70ad27b09a847fe7856d3ceaaf'
    base_url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    print(response.url)  # Print the URL for debugging
    print(response.json())  # Print the JSON response for debugging
    return response.json()

# Define the route
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SurfboardForm()
    weather = None
    error = None
    if form.validate_on_submit():
        weight = form.weight.data
        skill_level = form.skill_level.data
        tail_shape = form.tail_shape.data
        city = request.form.get('city')
        original_volume = Surfboard.calculate_volume(weight, skill_level)
        volume_lower = original_volume - 2
        volume_upper = original_volume + 8

        tail_info = Surfboard.TAIL_SHAPES_INFO.get(tail_shape, 'Unknown tail shape')
        
        if city:
            weather_data = get_weather_data(city)
            if weather_data.get('cod') != 200:  # Check if the response contains an error code
                error = weather_data.get('message', 'Error fetching weather data')
            else:
                weather = weather_data

        return render_template('result.html', volume_lower=volume_lower, volume_upper=volume_upper, tail_info=tail_info, weather=weather, error=error)
    return render_template('calculate.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

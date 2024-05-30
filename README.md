# SurfsApp
SurfsApp is a Flask web application designed to provide surfboard recommendations based on user input regarding weight, skill level, tail shape preference, and location. Additionally, the app offers information on wetsuit thickness and wax type based on the temperature conditions in the user's city.

## Features

- Calculate the recommended volume and length of a surfboard based on weight and skill level.
- Provide information on the ideal tail shape based on the user's preference.
- Determine the suitability of different surfboard types based on the conditions in the user's city.
- Offer recommendations on wetsuit thickness and wax type according to temperature conditions.

## Technologies Used

- Flask: A micro web framework for Python used for building web applications.
- SQLAlchemy: A Python SQL toolkit and Object-Relational Mapping (ORM) library for interacting with databases.
- Flask-WTF: An extension for Flask that integrates with WTForms, a flexible forms validation and rendering library for Python.
- Bootstrap: A popular front-end framework for building responsive and mobile-first websites.
- Requests: A simple HTTP library for making requests in Python.
- StormGlass API: Provides surf forecast data such as wave height and water temperature.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your_username/SurfsApp.git
```

2. Navigate to the project directory:
```bash
cd SurfsApp
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask app:
```bash
python app.py
```

## Credits
SurfsApp was created by Peter Koncz, Zachary Raisin and Catherine Ashton.

Weather data is sourced from OpenWeather and Stormglass.io, and surfboard recommendations are based on industry standards and expertise.

## License
This project is licensed under the MIT License.


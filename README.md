# Netflix dashboard

Dashboard application that tries to gain insights about Netflix movies and TV shows by visualizing Netflix context [dataset](https://www.kaggle.com/shivamb/netflix-shows).

The application is available over [here](https://netflix-dashboard.herokuapp.com).

## Setup

1. Clone the repository `$ git clone git@github.com:armgabrielyan/netflix-dashboard.git`.
2. Change to the application directory `$ cd netflix-dashboard`
3. Install the required packages `$ pip install -r requirements.txt`.
4. To start the application, run `$ cd src && python app.py`. Alternatively, you can run it via gunicorn `$ sh -c 'cd ./src/ && gunicorn app:server'`.
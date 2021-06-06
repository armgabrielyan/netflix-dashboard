import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

netflix = pd.read_csv('../data/netflix_titles.csv')

type_data = netflix.groupby(['release_year', 'type'])[['show_id']] \
              .count() \
              .rename(columns = { 'show_id': 'count' }) \
              .reset_index()

rating_data = netflix.groupby(['release_year', 'rating'])[['show_id']] \
              .count() \
              .rename(columns = { 'show_id': 'count' }) \
              .reset_index()

def get_year_options():
    years = sorted(netflix['release_year'].unique())

    return [{'label': year, 'value': year } for year in years]

def get_rating_options():
    ratings = sorted(netflix['rating'].dropna().unique())

    return [{'label': rating, 'value': rating } for rating in ratings]

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])

server = app.server

app.layout = dbc.Container([
    html.Div([
        dbc.Row(
            dbc.Col(
                dcc.Graph(id = 'movie-tv-shows-count-bar-plot'),
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id = 'start-year-1',
                        options = get_year_options(),
                        value = '2001',
                        clearable = False,
                    ),
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id = 'end-year-1',
                        options = [],
                        value = '2021',
                        clearable = False,
                    ),
                ),
            ],
        ),
    ]),
    html.Div([
        dbc.Row(
            dbc.Col(
                dcc.Graph(id = 'rating-release_year-bar-plot'),
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id = 'start-year-2',
                        options = get_year_options(),
                        value = '2001',
                        clearable = False,
                    ),
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id = 'end-year-2',
                        options = [],
                        value = '2021',
                        clearable = False,
                    ),
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id = 'rating-dropdown',
                        options = get_rating_options(),
                        value=['TV-MA', 'R'],
                        multi = True,
                        clearable = False,
                    ),
                )
            ],
        ),
    ]),
])

@app.callback(
    Output('end-year-1', 'options'),
    Input('start-year-1', 'options'),
    Input('start-year-1', 'value'),
)
def set_cities_value(available_year_options, selected_year):
    start_index = available_year_options.index({'label': int(selected_year), 'value': int(selected_year) })

    return available_year_options[start_index:]

@app.callback(
    Output('movie-tv-shows-count-bar-plot', 'figure'),
    Input('start-year-1', 'value'),
    Input('end-year-1', 'value'),
)
def update_figure1(start_year, end_year):
    filtered_data = type_data[
        (type_data['release_year'] >= int(start_year)) & (type_data['release_year'] <= int(end_year))
    ]

    fig = px.bar(
        filtered_data,
        x = 'release_year',
        y = 'count',
        color = 'type',
        title = 'The number of movies and TV shows released over years',
        labels = {
            'release_year': 'Release year',
            'count': 'Count',
            'type': 'Type',
        },
    )
    fig.update_layout(barmode = 'group')

    return fig

@app.callback(
    Output('end-year-2', 'options'),
    Input('start-year-2', 'options'),
    Input('start-year-2', 'value'),
)
def set_cities_value(available_year_options, selected_year):
    start_index = available_year_options.index({'label': int(selected_year), 'value': int(selected_year) })

    return available_year_options[start_index:]

@app.callback(
    Output('rating-release_year-bar-plot', 'figure'),
    Input('start-year-2', 'value'),
    Input('end-year-2', 'value'),
    [dash.dependencies.Input('rating-dropdown', 'value')]
)
def update_figure2(start_year, end_year, ratings):
    filtered_data = rating_data[
        (rating_data['release_year'] >= int(start_year)) &
        (rating_data['release_year'] <= int(end_year)) &
        (rating_data['rating'].isin(ratings))
    ]

    fig = px.bar(
        filtered_data,
        x = 'release_year',
        y = 'count',
        color = 'rating',
        title = 'The number of cinematic works released over years based on rating',
        labels = {
            'release_year': 'Release year',
            'count': 'Count',
            'rating': 'Rating',
        },
    )
    fig.update_layout(barmode = 'group')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

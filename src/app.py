import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

netflix = pd.read_csv('../data/netflix_titles.csv')
netflix.columns = [
    'show_id',
    'cinematic_type',
    'title',
    'director',
    'cast',
    'country',
    'date_added',
    'release_year',
    'rating',
    'duration',
    'listed_in',
    'description',
]

def get_options(column):
    results = sorted(netflix[column].dropna().unique())

    return [{'label': result, 'value': result } for result in results]

def get_dropdown_label_from_value(dropdown_value, dropdown_options):
    dropdown_label = [x['label'] for x in dropdown_options if x['value'] == dropdown_value]

    return dropdown_label[0]

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])

server = app.server

app.layout = dbc.Container([
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
                        id = 'feature-dropdown',
                        options = [
                            { 'label': 'Cinematic type', 'value': 'cinematic_type' },
                            { 'label': 'Rating', 'value': 'rating' },
                        ],
                        value = 'cinematic_type',
                        clearable = False,
                    ),
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id = 'categories-dropdown',
                        multi = True,
                        clearable = False,
                    ),
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id = 'start-year',
                        options = get_options('release_year'),
                        value = '2001',
                        clearable = False,
                    ),
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id = 'end-year',
                        value = '2021',
                        clearable = False,
                    ),
                ),
            ],
        ),
    ]),
])

@app.callback(
    Output('end-year', 'options'),
    Input('start-year', 'options'),
    Input('start-year', 'value'),
)
def set_end_year(available_year_options, selected_year):
    start_index = available_year_options.index({'label': int(selected_year), 'value': int(selected_year) })

    return available_year_options[start_index:]

@app.callback(
    Output('categories-dropdown', 'options'),
    Input('feature-dropdown', 'value'),
)
def set_feature_category_options(feature):
    return get_options(feature)

@app.callback(
    Output('categories-dropdown', 'value'),
    Input('categories-dropdown', 'options'),
)
def set_feature_category_value(categories):
    return [categories[0]['value'], categories[1]['value']]

@app.callback(
    Output('rating-release_year-bar-plot', 'figure'),
    Input('feature-dropdown', 'value'),
    Input('feature-dropdown', 'options'),
    Input('start-year', 'value'),
    Input('end-year', 'value'),
    [dash.dependencies.Input('categories-dropdown', 'value')],
)
def update_barplot(feature_value, feature_options, start_year, end_year, categories):
    count_data = netflix.groupby(['release_year', feature_value])[['show_id']] \
              .count() \
              .rename(columns = { 'show_id': 'count' }) \
              .reset_index()

    filtered_data = count_data[
        (count_data['release_year'] >= int(start_year)) &
        (count_data['release_year'] <= int(end_year)) &
        (count_data[feature_value].isin(categories))
    ]

    feature_label = get_dropdown_label_from_value(feature_value, feature_options)

    fig = px.bar(
        filtered_data,
        x = 'release_year',
        y = 'count',
        color = feature_value,
        title = f'The number of cinematic works released over years based on {feature_label.lower()}',
        labels = {
            'release_year': 'Release year',
            'count': 'Count',
            feature_value: feature_label,
        },
    )
    fig.update_layout(barmode = 'group')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

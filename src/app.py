import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import itertools

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

country_codes = pd.read_csv('../data/wikipedia-iso-country-codes.csv')
country_codes = country_codes.rename(
    {
        'English short name lower case': 'Country',
        'Alpha-3 code': 'Code',
    },
    axis = 'columns',
).drop(columns = ['Alpha-2 code', 'Numeric code', 'ISO 3166-2'])

def get_options(column):
    results = sorted(netflix[column].dropna().unique())

    return [{'label': result, 'value': result } for result in results]

def get_dropdown_label_from_value(dropdown_value, dropdown_options):
    dropdown_label = [x['label'] for x in dropdown_options if x['value'] == dropdown_value]

    return dropdown_label[0]

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])

app.title = 'Netflix dashboard'

SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '16rem',
    'padding': '2rem 1rem',
    'background-color': '#f8f9fa',
}


CONTENT_STYLE = {
    'margin-left': '18rem',
    'margin-right': '2rem',
    'padding': '2rem 1rem',
}

server = app.server

sidebar = html.Div(
    [
        html.H3('Netflix dashboard'),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink('Geospatial distribution', href = '/', active = 'exact'),
                dbc.NavLink('Categorical features frequency', href = '/cat-feature-frequency', active = 'exact'),
                dbc.NavLink('Directors and actors insights', href = '/directors-actors-insights', active = 'exact'),
            ],
            vertical = True,
            pills = True,
        ),
    ],
    style = SIDEBAR_STYLE,
)

content = html.Div(id = 'page-content', style = CONTENT_STYLE)

app.layout = dbc.Container(
    [
        dcc.Location(id = 'url'),
        sidebar,
        content
    ],
    fluid = True,
)

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def render_page_content(pathname):
    if pathname == '/':
        controls = dbc.Card(
            [
                dbc.FormGroup(
                    [
                        dbc.Label('Start year'),
                        dcc.Dropdown(
                            id = 'start-year-geo',
                            options = get_options('release_year'),
                            value = '1925',
                            clearable = False,
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label('End year'),
                        dcc.Dropdown(
                            id = 'end-year-geo',
                            value = '2021',
                            clearable = False,
                        ),
                    ]
                ),
            ],
            body = True,
        )

        return dbc.Row(
            [
                dbc.Col(controls, md = 2),
                dbc.Col(dcc.Graph(id = 'geospatial-plot'), md = 10),
            ],
            align = 'center',
        )
    elif pathname == '/cat-feature-frequency':
        controls = dbc.Card(
            [
                dbc.FormGroup(
                    [
                        dbc.Label('Categorical feature'),
                        dcc.Dropdown(
                            id = 'feature-dropdown',
                            options = [
                                { 'label': 'Cinematic type', 'value': 'cinematic_type' },
                                { 'label': 'Rating', 'value': 'rating' },
                            ],
                            value = 'cinematic_type',
                            clearable = False,
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label('Categories'),
                        dcc.Dropdown(
                            id = 'categories-dropdown',
                            multi = True,
                            clearable = False,
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label('Start year'),
                        dcc.Dropdown(
                            id = 'start-year',
                            options = get_options('release_year'),
                            value = '2001',
                            clearable = False,
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label('End year'),
                        dcc.Dropdown(
                            id = 'end-year',
                            value = '2021',
                            clearable = False,
                        ),
                    ]
                ),
            ],
            body = True,
        )

        return dbc.Row(
            [
                dbc.Col(controls, md = 3),
                dbc.Col(dcc.Graph(id = 'cat-feature-release-year-bar-plot'), md = 9),
            ],
            align = 'center',
        )
    elif pathname == '/directors-actors-insights':
        controls = dbc.Card(
            [
                dbc.FormGroup(
                    [
                        dbc.Label('Column'),
                        dcc.Dropdown(
                            id = 'column-dropdown',
                            options = [
                                { 'label': 'Directors', 'value': 'director' },
                                { 'label': 'Actors', 'value': 'cast' },
                            ],
                            value = 'director',
                            clearable = False,
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label('Options'),
                        dcc.Dropdown(
                            id = 'column-options-dropdown',
                            options = [],
                            clearable = False,
                        ),
                    ]
                ),
            ],
            body = True,
        )

        return dbc.Row(
            [
                dbc.Col(controls, md = 3),
                dbc.Col(dcc.Graph(id = 'column-options-plot'), md = 9),
            ],
            align = 'center',
        )
    return dbc.Jumbotron(
        [
            html.H1('404: Not found', className = 'text-danger'),
            html.Hr(),
            html.P(f'The pathname {pathname} was not recognised...'),
        ]
    )

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
    category_values = list(map(lambda category: category['value'], categories))

    return category_values[:2]

@app.callback(
    Output('cat-feature-release-year-bar-plot', 'figure'),
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
        title = f'The freqency of Netflix content released over years based on {feature_label.lower()}',
        labels = {
            'release_year': 'Release year',
            'count': 'Count',
            feature_value: feature_label,
        },
    )
    fig.update_layout(barmode = 'group')

    return fig

@app.callback(
    Output('end-year-geo', 'options'),
    Input('start-year-geo', 'options'),
    Input('start-year-geo', 'value'),
)
def set_end_year(available_year_options, selected_year):
    start_index = available_year_options.index({'label': int(selected_year), 'value': int(selected_year) })

    return available_year_options[start_index:]

@app.callback(
    Output('geospatial-plot', 'figure'),
    Input('start-year-geo', 'value'),
    Input('end-year-geo', 'value'),
)
def update_geo_spatial_plot(start_year, end_year):
    columns_to_keep = list(netflix.columns)
    columns_to_keep.remove('country')

    filtered_data = netflix[(netflix['release_year'] >= int(start_year)) & (netflix['release_year'] <= int(end_year))]

    long_netflix = filtered_data.set_index(columns_to_keep).apply(lambda x: x.str.split(',').explode()).reset_index()
    long_netflix['country'] = long_netflix['country'].str.lstrip()

    country_frequency = pd.DataFrame(long_netflix['country'].value_counts()).reset_index()
    country_frequency.columns = ['Country', 'Frequency']

    location = pd.merge(
        country_frequency,
        country_codes[country_codes['Country'].isin(country_frequency['Country'])],
        how = 'left',
        on = ['Country'],
    )

    fig = px.choropleth(
        location,
        locations = 'Code',
        color = 'Frequency',
        hover_name = 'Country',
        title = 'The freqency of Netflix content released over years based on location',
        color_continuous_scale = px.colors.sequential.amp,
        width = 1200, height = 800
    )

    return fig

@app.callback(
    Output('column-options-dropdown', 'options'),
    Input('column-dropdown', 'value'),
)
def set_column_options(column):
    results = []

    if column == 'director':
        results = list(netflix['director'][~netflix['director'].isnull()])
    elif column == 'cast':
        lists_of_actors = list(netflix['cast'].apply(lambda x: x.split(', ') if isinstance(x, str) else []))

        chain = itertools.chain(*lists_of_actors)

        results = list(chain)

    return [{'label': result, 'value': result } for result in results]

@app.callback(
    Output('column-options-plot', 'figure'),
    Input('column-dropdown', 'value'),
    Input('column-options-dropdown', 'value'),
)
def update_column_options_barplot(column_value, option_value):
    filtered_data = netflix[(~netflix[column_value].isnull()) & (netflix[column_value].str.contains(option_value))]
    count_data = filtered_data.groupby(['release_year'])[['show_id']] \
            .count() \
            .rename(columns = { 'show_id': 'count' }) \
            .reset_index()

    fig = px.bar(
        count_data,
        x = 'release_year',
        y = 'count',
        title = f'The freqency of Netflix content particpated by {option_value} over years',
        labels = {
            'release_year': 'Release year',
            'count': 'Count',
        },
    )
    fig.update_layout(barmode = 'group')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

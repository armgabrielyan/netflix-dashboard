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
        html.H2('Sidebar', className='display-4'),
        html.Hr(),
        html.P(
            'A simple sidebar layout with navigation links', className='lead'
        ),
        dbc.Nav(
            [
                dbc.NavLink('Home', href = '/', active = 'exact'),
                dbc.NavLink('Page 1', href = '/page-1', active = 'exact'),
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
        return html.P('Home page')
    elif pathname == '/page-1':
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
                dbc.Col(controls, md = 4),
                dbc.Col(dcc.Graph(id = 'cat-feature-release-year-bar-plot'), md = 8),
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
    print('available_year_options', available_year_options)
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

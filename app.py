from dash import Dash, html, dcc, Input, Output, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


BS5 = 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css'
FONT = 'https://fonts.googleapis.com/css2?family=Poppins&display=swap'

newspapers_dataset = pd.read_excel('./filtered_analized_data.xlsx')
by_country = pd.read_csv('./by_country.csv')

country_keys = sorted(newspapers_dataset['country_key'].unique().tolist())
total_news_by_country = newspapers_dataset.groupby(by='country').count()[
    'title'].tolist()
news_genres = ['culture', 'economy', 'entertainment',
               'health', 'police', 'policy', 'science', 'society', 'sports',
               'tech', 'war', 'other']
news_genres.reverse()

app = Dash(
    __name__,
    title='Newspaper Analyzer',
    external_stylesheets=[BS5, FONT],
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True
)
app.css.config.serve_locally = True


@app.callback(
    Output('by-country-dataframe', 'data'),
    Input('date-picker', 'date'),
    Input('country-dropdown', 'value')
)
def dataframe_filter(date, country):
    """
    Function that filter data by country and date.
    """
    by_country = newspapers_dataset.query(
        f'country == "{country}" & scrape_date == "{date}"')
    return by_country.to_json(orient='split', date_format='iso')


def nav_bar():
    return html.Nav([
        html.Div([
            html.A('Newspaper Analytics',
                   href="/",
                   className='navbar-brand'
                   )
        ], className='container-fluid')
    ], className='navbar navbar-light bg-light glass-navbar')


def selector_card():
    # Converting dates into Pandas Timestamp for create a list
    # which contains days with no news in case it was necessary
    margin_of_dates = pd.date_range(newspapers_dataset['scrape_date'].min(),
                                    newspapers_dataset['scrape_date'].max()).tolist()
    enable_days = [i for i in newspapers_dataset['scrape_date'].unique()]
    disabled_days = [i for i in margin_of_dates if i not in enable_days]

    return dbc.Card([
        dbc.CardHeader(className='glass-card glass-card-header',
                       children='Selector', style={'font-size': '18px'}),
        dbc.CardBody([
            html.P(children='Filter by:',
                   style={'height': '15px'}
                   ),
            dcc.DatePickerSingle(
                min_date_allowed=newspapers_dataset['scrape_date'].min(),
                max_date_allowed=newspapers_dataset['scrape_date'].max(),
                disabled_days=disabled_days,
                calendar_orientation='vertical',
                first_day_of_week=1,
                date=newspapers_dataset['scrape_date'].max(),
                id='date-picker',
                className='selector',
                style={'z-index': '40'}
            ),
            dcc.Dropdown(
                options=by_country['country'].tolist(),
                placeholder="Select a country",
                value='Argentina',
                className='selector country-dropdown',
                id='country-dropdown',
                style={'z-index': '30'}
            ),
        ], class_name='selector',
            style={'z-index': '5'}
        )
    ], style={'background': 'rgba(255, 255, 255, 0)',
              'border': 'none',
              'padding-top': '10px',
              'padding-bottom': '10px',
              }
    )


@app.callback(
    Output('news-table', 'children'),
    Input('random-button', 'n_clicks')
)
def random_news_table(btn):
    if "n_clicks" == None:
        raise PreventUpdate
    else:
        news = newspapers_dataset.sample(1)
        temp = news[news_genres]
        genres = [i[0].capitalize() for i in temp.iteritems() if any(i[1])]
        value = 'Positive' if int(news['positive']) else 'Negative'
        link = news['link'].tolist()[0]

    table = [
        html.Table([
            html.Tbody([
                html.Tr([html.Td('News Title'), html.Td(news['title'])],
                        style={'height': '72px'}),
                html.Tr([html.Td('Genres'), html.Td(', '.join(genres))]),
                html.Tr([html.Td('Positivity'),
                        html.Td(value)]),
                html.Tr([html.Td('Newspaper'), html.Td(
                    news['newspaper'], className='td-100')]),
                html.Tr([html.Td('Country'), html.Td(news['country'])]),
                html.Tr([html.Td('Link'), html.Td(html.A("Link to news",
                                                         href=link,
                                                         target="_blank"))
                         ]),
            ])
        ], className='styled-table')
    ]
    return table


@app.callback(
    Output('pie-chart', 'figure'),
    Input('by-country-dataframe', 'data')
)
def pie_chart(dataframe):
    if not dataframe:
        raise PreventUpdate
    df = pd.read_json(dataframe, orient='split')
    by_country = df.groupby(by='country').sum().copy()
    by_country['total_news'] = len(df)
    by_country['negatives'] = by_country['total_news'] - by_country['positive']
    pos, neg = by_country['positive'].values[0], by_country['negatives'].values[0]
    fig = px.pie(
        values=[pos, neg],
        names=['Positives', 'Negatives'],
        color_discrete_sequence=['#03045e', '#0077b6']
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      xaxis_title=None,
                      yaxis_title=None,
                      showlegend=False,
                      paper_bgcolor='rgb(0,0,0,0)',
                      plot_bgcolor='rgb(0,0,0,0)')
    fig.update_traces(text=['Positive', 'Negative'],
                      hoverinfo='text',
                      selector=dict(type='pie'))

    return fig


@app.callback(
    Output('cat_bar_chart', 'figure'),
    Input('by-country-dataframe', 'data'),
)
def cat_bar_chart(dataframe):
    if not dataframe:
        raise PreventUpdate
    df = pd.read_json(dataframe, orient='split')
    df_by_positivity = df.groupby(by='positive').sum()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Negative',
                         y=news_genres,
                         x=df_by_positivity.iloc[0],
                         marker_color='#03045e',
                         orientation='h'))
    fig.add_trace(go.Bar(name='Positive',
                         y=news_genres,
                         x=df_by_positivity.iloc[1],
                         marker_color='#0077b6',
                         orientation='h'))
    fig.update_layout(barmode='stack',
                      margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      xaxis_title=None,
                      yaxis_title=None,
                      xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      legend=dict(bgcolor='rgba(0,0,0,0)', y=.92))
    fig.update_yaxes(linecolor='rgba(255, 255, 255, 0.2)', gridwidth=0)

    return fig


def posneg_world():
    hover = ['{}<br><br>{:.0f} of 100 news are positive'
             .format(i.country, i.positivity_rate_per100) for i in by_country.itertuples()]

    fig = go.Figure(go.Choropleth(locations=by_country['country_key'],
                                  locationmode='ISO-3',
                                  z=by_country['positivity_rate'],
                                  colorscale=['#03045e', '#caf0f8'],
                                  autocolorscale=False,
                                  hoverinfo='text',
                                  hovertext=hover,
                                  marker_line_color='white',
                                  colorbar_title='Positivity Rate',
                                  legendwidth=300
                                  ))
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      paper_bgcolor='rgba(0,0,0,0)',
                      geo=dict(bgcolor='rgba(0,0,0,0)'))
    fig.update_traces(colorbar=dict(orientation='h',
                                    yanchor='bottom',
                                    xanchor='center',
                                    y=-0.13, x=0.455,
                                    thickness=20,
                                    len=0.5
                                    ), selector=dict(type='choropleth'))
    return fig


def world_card():
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(['The map of Positivity'],
                               className='glass-card glass-card-header',
                               style={'font-size': '18px'}),
                dbc.CardBody([dcc.Graph(figure=posneg_world(),
                                        responsive=True)
                ], className='glass-card')
            ], style={'background': 'rgba(255, 255, 255, 0)',
                      'border': 'none'}
            )
        ], xs=12, sm=12, md=12, lg=6, xl=6
        )
    ], justify="center", align="center", className="h-50",
        style={'padding-bottom': '7px'}
    )


def bar_card():
    return dbc.Col([
        dbc.Card([
            dbc.CardHeader(['News by Genre'],
                           className='glass-card glass-card-header',
                           style={'font-size': '18px'}
                           ),
            dbc.CardBody(dcc.Graph(id='cat_bar_chart'),
                         className='glass-card')
        ], style={'background': 'rgba(255, 255, 255, 0)',
                  'border': 'none'}
        )
    ], xs=12, sm=12, md=12, lg=4, xl=4,
        style={'padding-top': '10px'}
    )


def pie_card():
    return dbc.Col([
        dbc.Card([
            dbc.CardHeader(['Positivity Pie Chart'],
                           className='glass-card glass-card-header',
                           style={'font-size': '18px'}),
            dbc.CardBody([dcc.Graph(id='pie-chart')],
                         className='glass-card')
        ], style={'background': 'rgba(255, 255, 255, 0)',
                  'border': 'none'}
        )
    ], xs=12, sm=12, md=12, lg=4, xl=4,
        style={'padding-top': '10px'}
    )


def table_news():
    return dbc.Card([
        dbc.CardHeader(['News Selector'],
                       className='glass-card glass-card-header',
                       style={'font-size': '18px'}
                       ),
        dbc.CardBody([
            html.Div(id='news-table'),
            html.Center(html.Button('Select a random News',
                                    id='random-button',
                                    className='btn btn-secondary button-random-news'
                                    ), style={'margin-top': '8px',
                                              'font-size': '15px'}
            )
        ], className='glass-card',
            style={'height': '281px'}
        )
    ], style={'background': 'rgba(255, 255, 255, 0)',
              'border': 'none'}
    )


app.layout = html.Div([
    dcc.Store(id='by-country-dataframe'),
    dbc.Container([
        nav_bar(),
        dbc.Row([
                dbc.Col([
                    selector_card(),
                    table_news()
                ]),
                bar_card(),
                pie_card()
                ], style={'margin-bottom': '10px'}
                ),
        world_card()
    ], fluid=True
    )
], className='glass-background'
)

if __name__ == '__main__':
    app.run_server(debug=True)

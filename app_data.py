from datetime import datetime as dt
import plotly.graph_objects as go
import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

df = pd.read_csv(r'C:\Users\oneta\Downloads\new-york-city-airbnb-open-data\AB_NYC_2019.csv')
df['last_review'] = pd.to_datetime(df['last_review'])

boroughs = df['neighbourhood_group'].unique()

mapbox_access_token = 'pk.eyJ1IjoicGF0b25lLWFudGhvbnkiLCJhIjoiY2s0aWsyZnpwMWxyaTNubzY2bG10dHF1YSJ9.J6X5nymCsrrJ0GPAU3wgHg'

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-40.7549, lat=73.9840),
        zoom=7,
    ),
)


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([

        html.Div([

            html.Div(
                "Created by Anthony Patone",
                style={
                    "text-align": "right",
                    "margin-top": "10px"
                }
            ),
            html.Label([
                html.A('Github Link', href='https://github.com/patone-anthony')
            ],
                style={
                    "text-align": "right",
                }
            ),


            html.H3(
                "New York City Airbnb Analytics Dashboard",
                style={
                    "margin-bottom": "30px",
                    "margin-top": "30px",
                    "text-align": "center",
                },
            ),
        ], className='row'),


        html.Div([
            html.Div([
                html.Div(['Filter the graphs using the selections below:'],
                         className="py-1 bold",
                         ),

                html.Div(['Borough:']),
                dcc.Dropdown(
                    id='borough_dropdown',
                    options=[
                        {'label': i, 'value': i} for i in boroughs
                    ],
                    value=boroughs,
                    multi=True,
                    style={
                        "margin-bottom": "15px",
                    },
                ),

                html.Div(['Last Review Date:']),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    min_date_allowed=df['last_review'].min(),
                    max_date_allowed=df['last_review'].max(),
                    start_date=df['last_review'].min(),
                    end_date=df['last_review'].max(),
                    style={
                        "margin-bottom": "15px",
                    },
                ),

                html.Div(['Room Type:']),
                dcc.Checklist(
                    id="room_checklist",
                    options=[
                        {'label': 'Private room', 'value': 'Private room'},
                        {'label': 'Entire home/apt', 'value': 'Entire home/apt'},
                        {'label': 'Shared room', 'value': 'Shared room'}
                    ],
                    value=['Private room', 'Entire home/apt', 'Shared room'],
                    style={
                        "margin-bottom": "15px",
                    },
                ),

                html.Div(['Price:']),
                dcc.RangeSlider(
                    id="price_rangeslider",
                    min=df['price'].min(),
                    max=df['price'].max(),
                    step=1,
                    value=[(df['price'].min()), df['price'].max()],
                    updatemode='drag',
                ),

                html.Div(
                    id='output-price_rangeslider',
                    style={
                        "margin-left": "20px",
                    },
                )

            ], className='three columns pretty_container'),

            html.Div([
                dcc.Graph(id='graph-all-apps'),
            ], className='nine columns pretty_container'),

        ], className='row flex-display'),


        html.Div([
            html.Div([
                dcc.Graph(id='geomap'),
            ], className='seven columns pretty_container'),

            html.Div([
                dcc.Graph(id='top_ten_graph'),
            ], className='five columns pretty_container'),

        ], className='row flex-display'),



    ],
        style={
            "width": "90%",
            "margin": "0 auto",
        }
    ),
],
    style={
        "margin": "0 auto",
    }
)


@app.callback(
    Output('output-price_rangeslider', 'children'),
    [Input('price_rangeslider', 'value')])
def update_output(value):
    min_value = value[0]
    max_value = value[1]
    return f'Min Price: ${min_value}, Max Price: ${max_value}'


@app.callback(
    Output('graph-all-apps', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('price_rangeslider', 'value'),
     Input('borough_dropdown', 'value'),
     Input('room_checklist', 'value')])
def update_figure(start_date, end_date, value, borough_values, room_values):
    min_price = value[0]
    max_price = value[1]
    filter_df = df[(df['last_review'] >= start_date) & (df['last_review'] <= end_date)]
    filter_df = filter_df[(filter_df['price'] >= min_price) & (filter_df['price'] <= max_price)]

    final_df = pd.DataFrame()

    for borough_value in borough_values:
        borough_filter = filter_df[filter_df['neighbourhood_group'] == borough_value]
        final_df = final_df.append(borough_filter)

    final_df1 = pd.DataFrame()

    for room_value in room_values:
        room_filter = final_df[final_df['room_type'] == room_value]
        final_df1 = final_df1.append(room_filter)

    fig = go.Figure()
    fig.add_trace(go.Histogram(histfunc="count",
                               x=final_df1['neighbourhood_group'],
                               # color='lifeExp'
                               ))
    return fig


@app.callback(
    Output('geomap', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('price_rangeslider', 'value'),
     Input('borough_dropdown', 'value'),
     Input('room_checklist', 'value')])
def goelocation_graph(start_date, end_date, value, borough_values, room_values):
    min_price = value[0]
    max_price = value[1]
    filter_df = df[(df['last_review'] >= start_date) & (df['last_review'] <= end_date)]
    filter_df = filter_df[(filter_df['price'] >= min_price) & (filter_df['price'] <= max_price)]

    final_df = pd.DataFrame()

    for borough_value in borough_values:
        borough_filter = filter_df[filter_df['neighbourhood_group'] == borough_value]
        final_df = final_df.append(borough_filter)

    final_df1 = pd.DataFrame()

    for room_value in room_values:
        room_filter = final_df[final_df['room_type'] == room_value]
        final_df1 = final_df1.append(room_filter)

    # final_df1.dropna()

    fig = go.Figure(go.Scattermapbox(
        lat=final_df1['latitude'],
        lon=final_df1['longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=9
        ),
        text=final_df1['name'],
    ))

    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, b=0, t=0),
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            style="light",
            center=go.layout.mapbox.Center(
                lat=40.7549,
                lon=-73.9840
            ),
            pitch=0,
            zoom=13,
        ),
    )

    return fig


@app.callback(
    Output('top_ten_graph', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('price_rangeslider', 'value'),
     Input('borough_dropdown', 'value'),
     Input('room_checklist', 'value')])
def top_ten(start_date, end_date, value, borough_values, room_values):
    min_price = value[0]
    max_price = value[1]
    filter_df = df[(df['last_review'] >= start_date) & (df['last_review'] <= end_date)]
    filter_df = filter_df[(filter_df['price'] >= min_price) & (filter_df['price'] <= max_price)]

    final_df = pd.DataFrame()

    for borough_value in borough_values:
        borough_filter = filter_df[filter_df['neighbourhood_group'] == borough_value]
        final_df = final_df.append(borough_filter)

    final_df1 = pd.DataFrame()

    for room_value in room_values:
        room_filter = final_df[final_df['room_type'] == room_value]
        final_df1 = final_df1.append(room_filter)

    final_df1.dropna()

    fig = go.Figure(go.Bar(
        x=df['neighbourhood'].value_counts()[:10].tolist(),
        y=df['neighbourhood'].value_counts()[:10].index.tolist(),
        orientation='h',
        marker={'color': df['neighbourhood'].value_counts()[:10].tolist(),
                'colorscale': 'Viridis'}))
    
    fig.update_layout(yaxis=dict(autorange="reversed"))

    return fig



if __name__ == '__main__':
    app.run_server(debug=True)


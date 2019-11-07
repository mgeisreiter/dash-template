import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import pandas as pd

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

import plotly as py

import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
########### Define a few variables ######

tabtitle = 'NYC Green Taxis'
sourceurl = 'https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page'
githublink = 'https://github.com/mgeisreiter/dash-template'

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

taxi = pd.read_csv('green_tripdata_2019-01.csv')
lookup = pd.read_csv('taxi+_zone_lookup.csv')
fp = 'geo_export_5741a122-d32a-497b-9ea7-73a4e2ea6bcb.shx'
map_df = gpd.read_file(fp)
df2 = pd.merge(taxi, lookup, left_on= 'PULocationID', right_on='LocationID', how = 'inner')
merged = pd.merge(df2, map_df, left_on= 'Borough', right_on='boro_name', how = 'inner')
merged = merged.drop(['boro_code', 'service_zone', 'Zone', 'congestion_surcharge','RatecodeID', 'store_and_fwd_flag', 'LocationID' , 'boro_name'], axis=1)
merged = merged.rename(columns={"shape_area": "PUshape_area", "shape_leng": "PUshape_leng", 'geometry':'PUgeometry', 'boro_code':'PUboro_code', 'Borough':'PUBorough'})
merged2 = pd.merge(merged, lookup, left_on= 'DOLocationID', right_on='LocationID', how = 'inner')
merged3 = pd.merge(merged2, map_df, left_on= 'Borough', right_on='boro_name', how = 'inner')
merged3 = merged3.drop(['boro_code', 'service_zone', 'Zone', 'LocationID','boro_name' ], axis=1)
merged3 = merged3.rename(columns={"shape_area": "DOshape_area", "shape_leng": "DOshape_leng", 'geometry':'DOgeometry', 'Borough':'DOBorough', 'total_amount': 'Avg Fare', 'trip_distance': 'Avg Distance', 'passenger_count':'Avg # Passengers'})
merged3['pu_datetime'] = pd.to_datetime(merged3['lpep_pickup_datetime'])
merged3['do_datetime'] = pd.to_datetime(merged3['lpep_dropoff_datetime'])
merged3=merged3[merged3['pu_datetime'].dt.year == 2019]
merged3['pu_date']=merged3['pu_datetime'].dt.date

pu_boroughs = ['Manhattan', 'Queens','Brooklyn', 'Bronx', 'Staten Island']
do_boroughs = ['Manhattan', 'Queens','Brooklyn', 'Bronx', 'Staten Island']
attributes  = ['Avg Fare', 'Avg Distance', 'Avg # Passengers']

def update_fig(pu_selected, do_selected, atr):
    new_df=merged3[(merged3['PUBorough']==pu_selected)&(merged3['DOBorough']==do_selected)]
    #new_df=merged3[merged3['DOBorough']=='Queens']
    mean = new_df.groupby('DOBorough')['Avg Fare'].mean()

    mydata4 = go.Scatter(x = new_df['pu_date'],
                    y=new_df.groupby('pu_date')['Avg Distance'].mean(),
                    marker = dict(color='#122A7F'),
                    name = 'Distance')
    mylayout = go.Layout(
                    title = 'Test',
                    xaxis = dict(title='Borough'),
                    yaxis = dict(title= 'Total Amount'))
    fig = go.Figure(data=[mydata4], layout = mylayout)
    return fig


def stats(pu_selected, do_selected):
     nl = 'x'
     new_df=merged3[(merged3['PUBorough']==pu_selected)&(merged3['DOBorough']==do_selected)]
     avg_fare = dict(new_df.groupby('PUBorough')['Avg Fare'].mean())
     avg_dist = dict(new_df.groupby('PUBorough')['Avg Distance'].mean())
     avg_pass = dict(new_df.groupby('PUBorough')['Avg # Passengers'].mean())
     text = (f'The average taxi trip from {pu_selected} to {do_selected} has the following values: ')
     text2 = (f'Avg Fare: {round(avg_fare[pu_selected],1)}')
     text3 = (f'Avg Distance: {round(avg_dist[pu_selected],1)}')
     text4 = (f'Avg # Passengers: {round(avg_pass[pu_selected],1)}')

     x = ['Stat', 'Value']
     y = [['Avg Fare', 'Avg Distance', 'Avg # Passengers'], [round(avg_fare[pu_selected],1), round(avg_dist[pu_selected],1), round(avg_pass[pu_selected],1)]]
     table = go.Figure(data=go.Table(header = dict(values = x), cells=dict(values = y)))

     return table

def barchart(attribute):
    boroughs = ['Manhattan', 'Queens','Brooklyn', 'Bronx', 'Staten Island']
    fig = go.Figure([go.Bar(x=boroughs, y = [1,2,3,4,5])])
    mylayout = go.Layout(
                    title = f'Avg Fare by Pickup Borough')
    return fig



########### Layout

app.layout = html.Div(children=[
    dcc.Tabs(id = 'tabs', children = [
        dcc.Tab(label = 'Taxi Trips by Borough', children = [
                html.H1('🚕 Green Taxi Trips in NYC 🚕'),
                html.Br(),
                html.Div([
                    html.Div([
                        html.H5('Select a pickup borough:'),
                        dcc.Dropdown(id='pu-location',
                                options=[{'label': i, 'value': i} for i in pu_boroughs],
                                value='Brooklyn',
                                style={'width': '5 00px'}),
                    ], className= 'six columns') ,
                    html.Div([
                        html.H5('Select a dropoff borough:'),
                        dcc.Dropdown(id='do-location',
                                options=[{'label': i, 'value': i} for i in do_boroughs],
                                value='Queens',
                                style={'width': '500px'}),
                    ], className = 'six columns'),
                ], className = 'twelve columns'),
                html.Br(),
                html.Div(id='stats_values', children=''),
                dcc.Graph(id='stats_table', figure = update_fig('Brooklyn', 'Queens', 'Avg Fare')),
                html.Br(),
                html.H5('Select an attribute to learn more about NYC taxi trips in January 2019 '),
                html.Div([
                    dcc.Dropdown(id='attribute',
                            options=[{'label': i, 'value': i} for i in attributes],
                            value='Avg Fare',
                            style={'width': '500px'})]),
                dcc.Graph(id='display-value', figure = stats('Brooklyn', 'Queens')),
                html.A('Code on Github', href=githublink),
                html.Br(),
                html.A("Data Source", href=sourceurl),
        ]),
        dcc.Tab(label = 'Taxi Trips by Attribute', children = [
                html.H1('🚕 Green Taxi Trips in NYC 🚕'),
                html.Br(),
                html.H5('Select an attribute to learn more about NYC taxi trips by Pickup and Dropoff Borough '),
                html.Div([
                    dcc.Dropdown(id='attribute2',
                            options=[{'label': i, 'value': i} for i in attributes],
                            value='Avg Fare',
                            style={'width': '500px'})]),
                dcc.Graph(id = 'barchart', figure = barchart('Avg Fare')),
                dcc.Graph(id = 'barchart2', figure = barchart('Avg Fare')),
                ]),
    ])
    ])

############ Callbacks
@app.callback(dash.dependencies.Output('display-value', 'figure'),
              [dash.dependencies.Input('pu-location', 'value'),
              dash.dependencies.Input('do-location', 'value'),
              dash.dependencies.Input('attribute', 'value')])
def update_fig(pu_selected, do_selected, atr):
    new_df=merged3[(merged3['PUBorough']==pu_selected)&(merged3['DOBorough']==do_selected)]
    new_df = new_df.sort_values(by='pu_date')
    mydata4 = go.Scatter(x = new_df['pu_date'].unique(),
                    y=new_df.groupby(['pu_date'])[atr].mean())
    mylayout = go.Layout(
                    title = f'{atr} for trips from {pu_selected} to {do_selected} in January 2019',
                    xaxis = dict(title='Date'),
                    yaxis = dict(title= atr))
    fig = go.Figure(data=[mydata4], layout = mylayout)
    return fig

@app.callback(dash.dependencies.Output('stats_table', 'figure'),
              [dash.dependencies.Input('pu-location', 'value'),
              dash.dependencies.Input('do-location', 'value')])
def stats(pu_selected, do_selected):
     new_df=merged3[(merged3['PUBorough']==pu_selected)&(merged3['DOBorough']==do_selected)]
     avg_fare = dict(new_df.groupby('PUBorough')['Avg Fare'].mean())
     avg_dist = dict(new_df.groupby('PUBorough')['Avg Distance'].mean())
     avg_pass = dict(new_df.groupby('PUBorough')['Avg # Passengers'].mean())
     x = ['Attribute', 'Value']
     y = [['Avg. Fare', 'Avg. Distance', 'Avg. # Passengers'], [round(avg_fare[pu_selected],1), round(avg_dist[pu_selected],1), round(avg_pass[pu_selected],1)]]
     table = go.Figure(data=go.Table(header = dict(values = x), cells=dict(values = y)))
     table.update_layout(height=300)
     return table

@app.callback(dash.dependencies.Output('stats_values', 'children'),
              [dash.dependencies.Input('pu-location', 'value'),
              dash.dependencies.Input('do-location', 'value')])
def stats(pu_selected, do_selected):
     text = (f'The average taxi trip from {pu_selected} to {do_selected} has the following attributes:')
     return text

@app.callback(dash.dependencies.Output('barchart', 'figure'),
              [dash.dependencies.Input('attribute2', 'value')])
def barchart(attribute):
    boroughs = ['Manhattan', 'Queens','Brooklyn', 'Bronx', 'Staten Island']
    fig = go.Figure([go.Bar(x=boroughs, y = merged3.groupby(['PUBorough'])[attribute].mean(), marker_color = '#197609')])
    fig.update_layout(
                    title = f'{attribute} by Pickup Borough')
    return fig

@app.callback(dash.dependencies.Output('barchart2', 'figure'),
              [dash.dependencies.Input('attribute2', 'value')])
def barchart(attribute):
    boroughs = ['Manhattan', 'Queens','Brooklyn', 'Bronx', 'Staten Island']
    fig = go.Figure([go.Bar(x=boroughs, y = merged3.groupby(['DOBorough'])[attribute].mean(), marker_color = '#8CE37D')])
    fig.update_layout(
                    title = f'{attribute} by Dropoff Borough')
    return fig


############ Deploy
if __name__ == '__main__':
    app.run_server(debug=True)

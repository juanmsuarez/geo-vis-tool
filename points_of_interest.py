import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
import plotly.express as px
import pandas as pd
from PIL import Image

# Constants
DATA_DIR = './data/'

MAPS_DIR = DATA_DIR + 'maps/'
ISLAND_SHAPE_PATH = MAPS_DIR + 'Kronos_Island.json'
CITY_SHAPE_PATH = MAPS_DIR + 'Abila.json'
CITY_BACKGROUND_PATH = MAPS_DIR + 'Abila.jpg'
CITY_BACKGROUND_LON = [24.82336, 24.91145]
CITY_BACKGROUND_LAT = [36.04530, 36.09468]

POI_DIR = DATA_DIR + 'poi/'
POI_PATH = POI_DIR + 'poi_{}.csv'
STOPPED_TIME_LABELS = {1: '1m', 15: '15m', 2 * 60: '2h', 4 * 60: '4h', 6 * 60: '6h'}

STYLESHEETS = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# Helpers
def read_shapefile(filepath):
    with open(filepath) as map_file:
        map_shape = json.load(map_file)
        return map_shape


# Plotly + Dash
def build_map_figure(island_shape, city_shape, points_of_interest):
    px.set_mapbox_access_token(open('.mapbox_token').read())
    fig = px.scatter_mapbox(points_of_interest, lat='lat', lon='lon',
                            color='car_id', color_discrete_sequence=px.colors.qualitative.Dark24)  # TODO: buscar mejor escala de color https://plotly.com/python/discrete-color/#color-sequences-in-plotly-express

    fig.update_layout(mapbox_style='white-bg',
                      mapbox_layers=[
                          {
                              'below': 'traces',
                              'sourcetype': 'image',
                              'source': Image.open(CITY_BACKGROUND_PATH),
                              'coordinates': [
                                  [CITY_BACKGROUND_LON[0], CITY_BACKGROUND_LAT[1]],
                                  [CITY_BACKGROUND_LON[1], CITY_BACKGROUND_LAT[1]],
                                  [CITY_BACKGROUND_LON[1], CITY_BACKGROUND_LAT[0]],
                                  [CITY_BACKGROUND_LON[0], CITY_BACKGROUND_LAT[0]]
                              ]
                          },
                          {
                              'below': 'traces',
                              'sourcetype': 'geojson',
                              'source': island_shape,
                              'type': 'line',
                          },
                          {
                              'below': 'traces',
                              'sourcetype': 'geojson',
                              'source': city_shape,
                              'type': 'line',
                              'line': {'width': 1},
                              'opacity': 0.5
                          }
                      ])

    return fig


def build_html_doc(app):
    app.layout = html.Div([
        html.H1("Puntos de interés"),

        dcc.Slider(
            id='stopped-time',
            min=1,
            max=6*60,
            step=None,
            marks=STOPPED_TIME_LABELS,
            value=15
        ),

        dcc.Graph(id='map', style={'height': '100vh'})
    ])


def set_callbacks(app):
    island_shape = read_shapefile(ISLAND_SHAPE_PATH)
    city_shape = read_shapefile(CITY_SHAPE_PATH)

    @app.callback(
        Output('map', 'figure'),
        Input('stopped-time', 'value'))
    def update_map(stopped_time):
        poi_path = POI_PATH.format(STOPPED_TIME_LABELS[stopped_time])
        points_of_interest = pd.read_csv(poi_path, names=['date', 'car_id', 'lat', 'lon'], dtype={'car_id': str})
        map_figure = build_map_figure(island_shape, city_shape, points_of_interest)
        return map_figure


def main():
    app = dash.Dash(__name__, external_stylesheets=STYLESHEETS)

    build_html_doc(app)
    set_callbacks(app)

    app.run_server(debug=True)


if __name__ == '__main__':
    main()

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
START_HOUR = 0
END_HOUR = 23

STYLESHEETS = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# Helpers
def read_shapefile(filepath):
    with open(filepath) as map_file:
        map_shape = json.load(map_file)
        return map_shape


# Plotly + Dash
def build_map_figure(points_of_interest):
    px.set_mapbox_access_token(open('.mapbox_token').read())

    island_shape = read_shapefile(ISLAND_SHAPE_PATH)  # TODO: avoid reload
    city_shape = read_shapefile(CITY_SHAPE_PATH)

    fig = px.scatter_mapbox(points_of_interest, lat='lat', lon='lon',
                            center={'lat': sum(CITY_BACKGROUND_LAT)/2, 'lon': sum(CITY_BACKGROUND_LON)/2}, zoom=13,
                            color='car_id', color_discrete_sequence=px.colors.qualitative.Dark24,
                            custom_data=points_of_interest[['car_id']])

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


def build_activity_figure(selected_points_of_interest):
    poi_path = POI_PATH.format(STOPPED_TIME_LABELS[1])
    points_of_interest = pd.read_csv(poi_path, names=['date', 'car_id', 'lat', 'lon'], dtype={'car_id': str})  # TODO: avoid reload
    dates_of_interest = pd.to_datetime(points_of_interest['date'])

    days = dates_of_interest.apply(lambda date: date.day)
    start_day, end_day = days.min().item(), days.max().item()  # TODO: avoid recalculation

    selected_dates_of_interest = pd.to_datetime(selected_points_of_interest['date'])

    days_of_interest, hours_of_interest, activity_frequency = [], [], []
    for hour in range(START_HOUR, END_HOUR + 1):
        for day in range(start_day, end_day + 1):
            days_of_interest.append(day)
            hours_of_interest.append(hour)
            cur_dates_mask = (selected_dates_of_interest.dt.day == day) & (selected_dates_of_interest.dt.hour == hour)
            freq = selected_dates_of_interest[cur_dates_mask].count()
            activity_frequency.append(freq)

    xaxes_ticks = END_HOUR - START_HOUR + 1
    yaxes_ticks = end_day - start_day + 1
    activity_figure = px.density_heatmap(x=hours_of_interest, y=days_of_interest, z=activity_frequency,
                                         labels={'x': 'Hour', 'y': 'Day of month'},
                                         nbinsx=xaxes_ticks, nbinsy=yaxes_ticks,
                                         color_continuous_scale=['#eeeeee', '#76cf63'])  # TODO constants
    activity_figure.update_xaxes(nticks=xaxes_ticks)
    activity_figure.update_yaxes(nticks=yaxes_ticks)

    return activity_figure


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

        dcc.Graph(id='map', style={'height': '90vh'}, figure={}),

        html.Div(id='activity-chart-div', children=[
            dcc.Graph(id='activity-chart', figure={})
        ])
    ])


def set_callbacks(app):
    @app.callback(
        Output('map', 'figure'),
        Output('map', 'clickData'),
        Input('stopped-time', 'value'))
    def update_map(stopped_time):
        poi_path = POI_PATH.format(STOPPED_TIME_LABELS[stopped_time])
        points_of_interest = pd.read_csv(poi_path, names=['date', 'car_id', 'lat', 'lon'], dtype={'car_id': str})  # TODO: avoid reload

        map_figure = build_map_figure(points_of_interest)
        return map_figure, None

    @app.callback(
        Output('activity-chart', 'figure'),
        Output('activity-chart-div', 'style'),
        Input('stopped-time', 'value'),
        Input('map', 'clickData'))
    def update_activity_chart(stopped_time, clicked_points):
        if not clicked_points:
            return dash.no_update, {'display': 'none'}

        poi_path = POI_PATH.format(STOPPED_TIME_LABELS[stopped_time])
        points_of_interest = pd.read_csv(poi_path, names=['date', 'car_id', 'lat', 'lon'], dtype={'car_id': str})  # TODO: avoid reload

        selected_car_id = clicked_points['points'][0]['customdata'][0]
        selected_points_of_interest = points_of_interest.loc[points_of_interest['car_id'] == selected_car_id]

        return build_activity_figure(selected_points_of_interest), {'display': 'block'}


def main():
    app = dash.Dash(__name__, external_stylesheets=STYLESHEETS)

    build_html_doc(app)
    set_callbacks(app)

    app.run_server(debug=True)


if __name__ == '__main__':
    main()

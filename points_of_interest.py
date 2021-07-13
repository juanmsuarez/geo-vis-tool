import json
import plotly.express as px
import pandas as pd

DATA_DIR = './data/'

MAPS_DIR = DATA_DIR + 'maps/'
ISLAND_PATH = MAPS_DIR + 'Kronos_Island.json'
CITY_PATH = MAPS_DIR + 'Abila.json'

POI_DIR = DATA_DIR + 'poi/'
POI_6H_PATH = POI_DIR + 'poi_6h.csv'


def read_shapefile(filepath):
    with open(filepath) as map_file:
        map_shape = json.load(map_file)
        return map_shape


def build_map_figure(island_shape, city_shape, points_of_interest):
    px.set_mapbox_access_token(open('.mapbox_token').read())
    fig = px.scatter_mapbox(points_of_interest, lat='lat', lon='lon',
                            color='car_id', color_discrete_sequence=px.colors.qualitative.Dark24)  # TODO: buscar mejor escala de color https://plotly.com/python/discrete-color/#color-sequences-in-plotly-express

    fig.update_layout(mapbox_style='white-bg',
        mapbox_layers=[
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
        }
    ])

    return fig


def main():
    island_shape = read_shapefile(ISLAND_PATH)
    city_shape = read_shapefile(CITY_PATH)
    points_of_interest = pd.read_csv(POI_6H_PATH, names=['date', 'car_id', 'lat', 'lon'], dtype={'car_id': str})

    fig = build_map_figure(island_shape, city_shape, points_of_interest)
    fig.show()


if __name__ == '__main__':
    main()

import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from urllib.request import urlopen

MAP_FILEPATH = './data/geospatial/Abila.json'


def read_map_shape():
    with open(MAP_FILEPATH) as map_file:
        map_shape = json.load(map_file)
        return map_shape


def build_map_figure(map_shape, data=pd.DataFrame()):
    #  TODO: cómo usar geojson=map_shape en px.scatter_geo?

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

        df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                         dtype={"fips": str})[:1]

        fig = px.choropleth(df, geojson=counties, locations='fips',
                            scope="usa",
                            )
        return fig


def main():
    map_shape = read_map_shape()
    fig = build_map_figure(map_shape)
    fig.show()


if __name__ == '__main__':
    main()

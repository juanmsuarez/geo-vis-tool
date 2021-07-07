"""
- Instalar geopandas en Windows es difícil y es poco robusto en cuanto al formato del shapefile
- Usamos en vez https://mapshaper.org/
"""

import geopandas as gpd
import sys


def main(argv):
    if len(argv) != 2:
        print("convert_to_geojson.py <inputfile> <outputfile>")
        sys.exit(2)

    input_path, output_path = argv

    geo_df = gpd.read_file(input_path)
    geo_df.to_file(output_path, driver="GeoJSON")


if __name__ == '__main__':
    main(sys.argv[1:])

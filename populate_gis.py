#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

import geopandas 
import osmnx as ox

from sqlalchemy import create_engine
from picos_psql_config import load_config

# Specify the name that is used to seach for the data
place_name = "Alameda"


# Get place boundary related to the place name as a geodataframe
gdf_area = ox.geocode_to_gdf(place_name)
config = load_config('database_gisdata.ini')
con_param = "postgresql://%s:%s@%s:5432/%s" % (config['user'] , config['password'], config['host'], config['database'] )
engine = create_engine(con_param)
gdf_area.to_postgis(place_name , engine)






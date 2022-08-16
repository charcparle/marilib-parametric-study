import plotly_express as px
import plotly.io as pio
import pandas as pd
import pickle
from datetime import datetime as dt
import os

from marilib.tools import units as unit
from marilib.aircraft_model.airplane import viewer as show
from marilib.aircraft_data.aircraft_description import Aircraft
from marilib.processes import assembly as run, initialization as init

#--------------------- import csv for airplane data sets ----------
csv_name = input("name of csv file: ./_summary/")
raw_df = pd.read_csv("./_summary/"+csv_name)
print(raw_df)
print("airplane data sets imported.")

#--------------------- start plotting charts ----------------------

#pio.renderers.default = "browser"
fig = px.scatter(raw_df, x='cabin.n_pax_ref', y='fuselage.length')
fig.show()
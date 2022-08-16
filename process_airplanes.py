import pandas as pd
import pickle
from datetime import datetime as dt
import os

from marilib.tools import units as unit
from marilib.aircraft_model.airplane import viewer as show
from marilib.aircraft_data.aircraft_description import Aircraft
from marilib.processes import assembly as run, initialization as init

input_dicts = []
filename_li = []
filename = ""
files = []
summary_df_all = pd.DataFrame()


for dirPath, dirNames, files in os.walk("./_airplane-data"):   #collect all designed airplanes
    for filename in files:
        if filename[-5:]==".dict":
            with open("./_airplane-data/"+filename, 'rb') as handle:
                aircraft_dict = pickle.loads(handle.read())
            input_dicts.append(aircraft_dict)   #store the data dictionary of all designed airplanes
            filename_li.append(filename)    #store the file names of all designed airplanes

for x in range(len(input_dicts)):   #iterate through all designed airplanes
    df_li = []
    input_dict = input_dicts[x]
    file_name = filename_li[x]
    summary_df_eachplane = pd.DataFrame({'file': [file_name]}).transpose()
    print(summary_df_eachplane)
    for k in input_dict['Aircraft']:    #iterate through the entire data dictionary in one airplane
        k_dict = input_dict['Aircraft'][k]
        kk_dict = dict()
        if type(k_dict) == dict:
            for key in k_dict:  # add key.parameter in the title for each sub-dictionary
                kk_dict[k + "." + key] = k_dict[key]
            dfk = pd.DataFrame.from_dict(kk_dict, orient='index')
        elif type(k_dict) == str:
            k_dict = k_dict
            dfk = pd.DataFrame({k: [k_dict]}).transpose()
        print("dfk.shape: ", k, " ", dfk.shape)
        df_li.append(dfk)
    print("len(df_li): ", len(df_li))
    for i in range(len(df_li)): #combine all sub-dictionary into one dictionary for one airplane
        print("i: ", i)
        summary_df_eachplane = summary_df_eachplane.append(df_li[i])
        print("summary_df_eachplane.shape: ", summary_df_eachplane.shape)
    summary_df_eachplane = summary_df_eachplane.transpose()
    summary_df_all = summary_df_all.append(summary_df_eachplane)

print(summary_df_all)

pd.DataFrame.to_csv(summary_df_all,"./_summary/summary_df_all_"+dt.now().strftime("%Y%m%d%H%M%S")+".csv")




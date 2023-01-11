
import pandas as pd
import os, sys
import numpy as np
import math

limit_rows = 5000

inputs = ['outside.csv', 'zimmer0-0.csv', 'zimmer0-1.csv', 'zimmer1.csv']

columns = ['System', 'Device', 'SensingDevice', 'Sensor', 'name', 'value', 'timestamp', 'location']

device_name = ['device_out', 'device_in_1','device_in_1', 'device_in_2']
device_type = ['aqara_multisensor_2', 'esp8266_1', 'esp8266_2', 'aqara_multisensor_1']
sensor_name = ['aqara_temp_2', 'ds18b20_1', 'ds18b20_2', 'aqara_temp_1']
name = ['t4', 't1', 't2', 't3']
location = ['outside', 'room1', 'room1', 'room2']
value_from = ['self', 'self', 'self', 'self']

processor = ['device_main', 'raspberry', '', '', 'processor']
processing_time = 5
system_name = 'MA TestSystem'

list_inputs = []

for filename in inputs:
    df = pd.read_csv(os.path.join(sys.path[0], filename), index_col=None, header=1, parse_dates=True, infer_datetime_format=True)
    list_inputs.append(df)

system = []
d_names = []
d_types = []
s_names = []
names = []
values = []
stamps = []
locations = []

for i, frames in enumerate(list_inputs):
    pre_value = 0
    for index, row in frames.iterrows():
        if index > (limit_rows / 8):
            break
        value = float(row.values[1])
        # clean errors which are already there (null and -128 values)
        if math.isnan(value):
            value = pre_value
        if value == -128:
            value = pre_value
        timestamp = pd.to_datetime(row.values[0])

        system.append(system_name)
        d_names.append(device_name[i])
        d_types.append(device_type[i])
        s_names.append(sensor_name[i])
        names.append(name[i])
        values.append(value)
        stamps.append(timestamp)
        locations.append(location[i])

        # adding processing data manually
        system.append(system_name)
        d_names.append(processor[0])
        d_types.append(processor[1])
        s_names.append(processor[2])
        names.append(processor[4])
        values.append(value)
        stamps.append(timestamp + pd.to_timedelta(processing_time, unit='s'))
        locations.append(location[i])

        pre_value = value

frame = pd.DataFrame(np.array([system, d_names, d_types, s_names, names, values, stamps, locations]).swapaxes(0,1), columns=columns)
frame = frame.sort_values(by='timestamp')
frame.to_csv(os.path.join(sys.path[0], 'iot-scenario-data.csv'), index=False)
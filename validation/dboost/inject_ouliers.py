import pandas as pd
import sys, os
import random
import numpy
from error_generator.strategies.switch_value.random_active_domain.random_active_domain import Random_Active_Domain
from error_generator.strategies.utilities.list_selected import List_selected
from error_generator.strategies.utilities.input_output import Read_Write
from error_generator.api.error_generator_api import Error_Generator

filename = "../../data/iot-scenario/raw-data/room0-0.csv"
filename_dirty = 'iot-dboost-dirty-2.csv'

ts = pd.read_csv(os.path.join(sys.path[0], filename), header=0)
ts.fillna(method='ffill', inplace=True)

max = numpy.max(ts['value']) * 1.5
min = numpy.min(ts['value']) * 0.5
errors = []

for i in range(0,85):
    rand = random.randint(0,8580)
    # generate random from 
    ts.at[rand, 'value'] = random.random() * (max - min) + min
    errors.append(rand)


ts.to_csv(os.path.join(sys.path[0], filename_dirty), index=False)
print(errors)

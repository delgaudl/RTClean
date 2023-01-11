import pandas as pd
import os, sys
import numpy as np

from pathlib import Path
from error_generator.strategies.typos.typo_butterfingers.typo_butterfingers import Typo_Butterfingers
from error_generator.strategies.typos.typo_keyboard.typo_keyboard import Typo_Keyboard
from error_generator.strategies.switch_value.Similar_based_active_domain.similar_based_active_domain import Similar_Based_Active_Domain
from error_generator.strategies.switch_value.random_active_domain.random_active_domain import Random_Active_Domain
from error_generator.strategies.noise.white_noise.white_noise import White_Noise
from error_generator.strategies.noise.gaussian_noise.gaussian_noise import Gaussian_Noise
from error_generator.strategies.missing_value.implicit_missing_value.implicit_missing_value import Implicit_Missing_Value
from error_generator.strategies.missing_value.explicit_missing_value.explicit_missing_value import Explicit_Missing_Value
from error_generator.strategies.utilities.list_selected import List_selected
from error_generator.strategies.utilities.input_output import Read_Write
from error_generator.strategies.word2vec.word2vec_nearest_neighbor.word2vec_nearest_neighbor import Word2vec_Nearest_Neighbor
from error_generator.api.error_generator_api import Error_Generator

filename = "iot-scenario-data.csv"
clean_path = "iot-scenario-clean.csv"
dirty_path = "iot-scenario-dirty.csv"
temp_path = "iot-scenario-temp.csv"

def saveCleanData(clean_path, df):
    if Path(clean_path).is_file():
        return
    data = []
    atttributes = df.columns.values
    for index, row in df.iterrows():
        for att in atttributes:
            data.append((index, att, row[att]))

    clean_frame = pd.DataFrame(np.array(data), columns=[
                               'tid', 'attribute', 'correct_val'])
    clean_frame.to_csv(os.path.join(sys.path[0], clean_path), index=False)


def injectErrorsAndSave(clean_path, dirty_path):
    methods = [
        # method, percentage, mute_columns
        (Typo_Butterfingers(), 5, [0, 2, 4, 6, 5, 7]),
        (Random_Active_Domain(), 5, [0, 1, 2, 3, 4, 6, 7]),
        (Explicit_Missing_Value(), 5, [6])
    ]
    
    for index, m in enumerate(methods):
        dataset, dataframe = Read_Write.read_csv_dataset(os.path.join(sys.path[0], temp_path if index != 0 else clean_path))
        mymethod = m[0]

        ds = Error_Generator().error_generator(
            method_gen=mymethod, selector=List_selected(), percentage=m[1], dataset=dataset, mute_column=m[2])

        # write to output
        Read_Write.write_csv_dataset(os.path.join(sys.path[0], temp_path if (index + 1) != len(methods) else dirty_path), ds)


df = pd.read_csv(os.path.join(sys.path[0], filename), index_col=None, header=0)

saveCleanData(clean_path, df)

injectErrorsAndSave(filename, dirty_path)

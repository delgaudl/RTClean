import pandas as pd
import os, sys
sys.path.append('../holoclean/')
sys.path.append('./parser/')
import math
import numpy as np

from dependencies import DeviceLinkDependency, CapabilityDependency, MonitoringDependency, LocalityDependency, TemporalDependency
from detect import Detector
from datetime import datetime


class OntologyDetector(Detector):
    """
    An error detector which detects errors in data with the help of the IoT Context Model
    """
    loader = None

    def __init__(self, name='OntologyDetector', loader=None):
        super(OntologyDetector, self).__init__(name)
        self.loader = loader

    def setup(self, dataset, env):
        self.ds = dataset
        self.env = env
        self.df = self.ds.get_raw_data()

    def getTemporalPredecessors(self, device):
        sensingDeviceName = 'sensing'
        predecessors = self.loader.queryTemporalPredecessors(device, sensingDeviceName)
        return [pre[sensingDeviceName] for pre in predecessors]

    def detect_noisy_cells(self):
        """
        detect_noisy_cells returns a pandas.DataFrame

        :return: pandas.DataFrame with columns:
            _tid_: entity ID
            attribute: attribute with possible erroneous value for this entityanze
        """
        attributes = self.ds.get_attributes()

        errors = []
        # error detection on each row itself
        for index, row in self.df.iterrows():
            # check for nan or null
            sensor_null = checkForNull(row['Sensor'])
            device_null = checkForNull(row['Device'])
            timestamp_null = checkForNull(row['timestamp'])
            location_null = checkForNull(row['location'])
            sensing_null = checkForNull(row['SensingDevice'])
            value_nan = checkForNaN(row['value'])

            # evaluate device-link dependency
            if not (sensor_null or device_null):
                dependency = DeviceLinkDependency(row['Sensor'], row['Device'])

                # check if dependency is present in context model
                if not dependency.evaluate(self.loader):
                    errors.append((index, 'Sensor'))
                    errors.append((index, 'Device'))
            
            # evaluate capability dependency
            if not (sensor_null or value_nan):
                metadataT = 'meta'
                metadataV = 'value'
                
                # get capabilities of specific sensor from context model
                capabilities = self.loader.querySensorCapabilities(row['Sensor'], metadataT, metadataV)
                dependency = CapabilityDependency(row['Sensor'], capabilities)

                # evaluate capability with given value
                if not dependency.evaluate(row['value']):
                    errors.append((index, 'value'))

            # evaluate monitoring dependency
            if not (device_null or timestamp_null):
                dependency = MonitoringDependency(row['Device'], 'value')

                # evaluated dependency at given timestamp with specific threshold
                if not dependency.evaluate(self.loader, row['timestamp']):
                    errors.append((index, 'value'))
            
            if not (timestamp_null or value_nan):
                time = datetime.fromisoformat(row['timestamp'])
                self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], utc=True)
                
                # evaluate locality dependency
                if not (sensing_null or location_null):
                    dependency = LocalityDependency(row['SensingDevice'], row['location'])

                    # get all nearby measurements
                    nearbys = dependency.getNearbys(self.loader)
                    if len(nearbys) != 0:
                        # get measurements of nearbys with in time range
                        nearby_rows = self.df.loc[self.df['SensingDevice'].isin(nearbys) & (self.df['timestamp'] >= dependency.getLowestTime(time)) & (self.df['timestamp'] <= dependency.getHighestTime(time))]
                        for i in range(len(nearby_rows)):
                            if not checkForNaN(nearby_rows.value.values[i]):
                                if not dependency.checkForOutlier(row['value'], nearby_rows.value.values[i]):
                                    errors.append((index, 'value'))
                                    
                # evaluate temporal dependency
                if not (device_null):
                    predecessors = self.getTemporalPredecessors(row['Device'])
                    dependency = TemporalDependency(row['Device'], predecessors)

                    if len(predecessors) != 0:
                        pre_rows = self.df.loc[self.df['Device'].isin(predecessors) & (self.df['timestamp'] <= time) & (self.df['timestamp'] >= dependency.getLowestTime(time))]
                        if len(pre_rows) > 0:
                            found = False
                            for i in range(len(pre_rows)):
                                if not checkForNaN(pre_rows.value.values[i]):
                                    if float(pre_rows.value.values[i]) == float(row['value']):
                                        found = True
                                        break
                                else:
                                    found = True
                                    break
                            if not found:
                                errors.append((index, 'timestamp'))
                
                self.df['timestamp'] = self.df['timestamp'].astype(str)

        unique_errors = np.unique(errors, axis=0)
        errors_df = pd.DataFrame(np.array(unique_errors), columns=['_tid_', 'attribute']).astype({'_tid_': 'int', 'attribute': 'str'})
        return errors_df

def checkForNull(value):
    if "nan" in value:
        return True
    return value == None or len(value) == 0

def checkForNaN(value):
    if "nan" in value:
        return True
    return math.isnan(float(value))

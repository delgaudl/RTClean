from datetime import timedelta

class Dependency:

    firstAttribute = None
    secondAttribute = None

    def __init__(self, firstAttribute, secondAttribute):
        self.firstAttribute = firstAttribute
        self.secondAttribute = secondAttribute


class DenialDependency(Dependency):

    def exportToString(self):
        return "t1&t2&EQ(t1.{0},t2.{0})&IQ(t1.{1},t2.{1})".format(self.firstAttribute, self.secondAttribute)


class MatchingDependency(Dependency):

    def exportToString(self):
        return "t1&t2&EQ(t1.{0},t2.{0})&EQ(t1.{1},t2.{1})".format(self.firstAttribute, self.secondAttribute)


class DeviceLinkDependency(Dependency):

    def evaluate(self, loader):
        return loader.hasSensorDeviceLink(self.firstAttribute, self.secondAttribute)


class TemporalDependency(Dependency):

    # static parameter for timeshift window
    PREDECESSOR_TIMESHIFT_THRESHOLD = 900 # in sec

    def getLowestTime(self, time):
        return time - timedelta(seconds=self.PREDECESSOR_TIMESHIFT_THRESHOLD)
    

class LocalityDependency(Dependency):

    # static parameter for timeshift window
    OUTLIER_TIMESHIFT_THRESHOLD = 900 # in sec
    OUTLIER_THRESHOLD = 3.3

    def checkForOutlier(self, value, value_sec):
        return abs(float(value) - float(value_sec)) < self.OUTLIER_THRESHOLD

    def getLowestTime(self, time):
        return time - timedelta(seconds=self.OUTLIER_TIMESHIFT_THRESHOLD / 2)

    def getHighestTime(self, time):
        return time + timedelta(seconds=self.OUTLIER_TIMESHIFT_THRESHOLD / 2)

    def getNearbys(self, loader):
        sensingDeviceName = 'sensingDevice'
        results = loader.queryNearbySensingDevices(self.secondAttribute, sensingDeviceName)
        result_strings = [row[sensingDeviceName].__str__() for row in results]
        return [sensing for sensing in result_strings if sensing != self.firstAttribute]


class MonitoringDependency(Dependency):

    # static parameter for monitoring threshold
    # future work: make adaptive to monitoring type
    MONITORING_THRESHOLD = 1.0
    
    def evaluate(self, loader, timestamp):
        monitor = loader.queryMonitoringDataAtTime(self.firstAttribute, timestamp, self.secondAttribute)
        if len(monitor) == 0:
            return True
        return monitor[0][self.secondAttribute] < self.MONITORING_THRESHOLD


class CapabilityDependency(Dependency):

    def evaluate(self, value):
        for cap in self.secondAttribute:
            if cap['meta'].toLowerCase() == 'minvalue':
                if value < cap['value']:
                    return False 
            elif cap['meta'].toLowerCase() == 'maxvalue':
                if value > cap['value']:
                    return False
            # future work: check more capabilities
        return True

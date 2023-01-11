from rdflib import Graph
from pyfuseki import FusekiQuery
from dependencies import DenialDependency, MatchingDependency
from query import Queries

class Loader:

    type = None

    def __init__(self, type=None):
        print("Preparing Ontology-Loader")
        self.type = type

    def escapeParameter(self, parameter):
        return parameter.replace("'", "")

    def querySubClasses(self, className, subclassName):
        """
        query all classes which have subclasses

        :param className: var to store key to access classes
        :param subclassName: var to store key to access subclasses

        :return: SPARQLResult containing key className and subclassName
        """
        return self.queryOntology(Queries.SUBCLASS.format(className, subclassName))

    def querySubSystems(self, className, subclassName, typeName, subtypeName):
        """
        query all systems or devices which have subsystems with specific type each

        :param className: var to store key to access classes
        :param subclassName: var to store key to access subclasses
        :param typeName: var to store key to access types
        :param subtypeName: var to store key to access types of subclasses

        :return: SPARQLResult containing key className, subclassName, typeName and subtypeName
        """
        return self.queryOntology(Queries.SUBSYSTEM.format(className, subclassName, typeName, subtypeName))

    def queryClassOfProperty(self, prefix, property, className):
        """
        query class with specific attribute

        :param prefix: prefix (namespace) of attribute
        :param property: name of attribute
        :param className: var to store key to access classes

        :return: SPARQLResult containing key className
        """
        prefix = self.escapeParameter(prefix)
        property = self.escapeParameter(property)
        return self.queryOntology(Queries.PROPERTY.format(className, prefix, property))

    def queryNearbySensingDevices(self, room, sensingDeviceName):
        """
        query sensing devices which are all in one room

        :param room: the room where the sensing devices are
        :param sensingDeviceName: var to store key to access sensing devices

        :return: SPARQLResult containing key sensingDeviceName
        """
        room = self.escapeParameter(room)
        return self.queryOntology(Queries.NEARBY.format(room, sensingDeviceName))

    def queryTemporalPredecessors(self, device, sensingDeviceName):
        """
        query temporal predecessors of one device

        :param device: the device of which the predecessors should be found
        :param sensingDeviceName: var to store key to access predecessor devices

        :return: SPARQLResult containing key sensingDeviceName
        """
        room = self.escapeParameter(device)
        return self.queryOntology(Queries.TEMPORAL.format(device, sensingDeviceName))

    def queryMonitoringDataAtTime(self, device, timestamp, valueName):
        """
        query last available monitor measurement of device at current timestamp

        :param device: the device of which the monitoring measurement should be found
        :param timestamp: at which timestamp the measurement should be taken
        :param valueName: var to store key to access the monitoring value

        :return: SPARQLResult containing key valueName. limit to 1 result
        """
        room = self.escapeParameter(device)
        timestamp = self.escapeParameter(timestamp)
        return self.queryOntology(Queries.MONITORING.format(device, timestamp, valueName))

    def querySensorCapabilities(self, sensor, metadataType, metadataValue):
        """
        query all capabilities of a specific sensor

        :param sensor: the sensor of which all capabilities should be found
        :param metadataType: var to store key to access the type of the capability
        :param metadataValue: var to store key to access the value of the capability

        :return: SPARQLResult containing key metadataType, metadataValue
        """
        sensor = self.escapeParameter(sensor)
        return self.queryOntology(Queries.CAPABILITIES.format(sensor, metadataType, metadataValue))

    def hasSensorDeviceLink(self, sensor, device):
        """
        True if device is linked with sensor. False if not

        :param sensor: the sensor which should be checked to be linked to the device
        :param device: the device which should be checked to be linked to the sensor
        :return: boolean if device is linked with sensor
        """
        sensor = self.escapeParameter(sensor)
        device = self.escapeParameter(device)
        return len(self.queryOntology(Queries.DEVICE_LINK.format(sensor, device))) > 0

    def writeDependenciesToFile(self, path, dependencies):
        """
        write matching dependencies and denial dependecies to file

        :param path: the path where the file should be written to
        :param dependencies: the dependencies as a list of strings
        """
        with open(path, 'w') as fp:
            for line in dependencies:
                fp.write("{}\n".format(line))

    def extractDependencies(self, output_file, columns, prefix):
        """
        extracting denial and matching dependencies from a ontology
        writing them to a file which is usable for HoloClean for error detection and repairing methods

        :param output_file: the path where the dependency file should be written to
        :param columns: the columns of the dataset
        :param prefix: the prefix (namespace) which is used in the ontology to describe attributes
        """
        listOfAllDependencies = []
        keyOfClass = 'className'
        keyOfSubclass = 'subclassName'
        keyOfType = 'typeName'
        keyOfSubtype = 'subtypeName'
        classPropertyMatching = dict()
        
        # extract all properties per class
        for property in columns:
            results = self.queryClassOfProperty(prefix, property, keyOfClass)
            for row in results:
                if row[keyOfClass] in classPropertyMatching:
                    classPropertyMatching[row[keyOfClass]].append(property)
                else:
                    classPropertyMatching[row[keyOfClass]] = [property]

        # Property Constraints
        for className in classPropertyMatching:
            listOfAllProperties = classPropertyMatching[className]
            for i in range(0, len(listOfAllProperties)):
                for j in range(0, len(listOfAllProperties)):
                    if i != j:
                        dependency = MatchingDependency(listOfAllProperties[i], listOfAllProperties[j])
                        listOfAllDependencies.append(dependency)

        # Subclass Constraints
        results = []
        if self.type == "iot-context-model":
            results = self.querySubSystems(keyOfClass, keyOfSubclass, keyOfType, keyOfSubtype)
        else:
            results = self.querySubClasses(keyOfClass, keyOfSubclass)
        for row in results:
            subclassName = row[keyOfSubtype].__str__().split('#')[1] if self.type == "iot-context-model" else row[keyOfSubclass]
            className = row[keyOfType].__str__().split('#')[1] if self.type == "iot-context-model" else row[keyOfClass]
            if len(classPropertyMatching) > 0:
                listOfAllPropertiesOfSubclass = classPropertyMatching[subclassName]
                listOfAllPropertiesOfParentclass = classPropertyMatching[className]
                for propertyOfSubclass in listOfAllPropertiesOfSubclass:
                    for propertyOfClass in listOfAllPropertiesOfParentclass:
                        dependency = DenialDependency(propertyOfClass, propertyOfSubclass)
                        listOfAllDependencies.append(dependency)
            elif className in columns and subclassName in columns:
                # no properties per class found -> create dependency from classname if in columns
                dependency = DenialDependency(className, subclassName)
                # prevent duplicates
                if not any(className == c.firstAttribute and subclassName == c.secondAttribute for c in listOfAllDependencies):
                    listOfAllDependencies.append(dependency)

        self.writeDependenciesToFile(output_file, [c.exportToString() for c in listOfAllDependencies])

class FileLoader(Loader):
    graph = None
    
    def __init__(self, path, format, type=None):
        super().__init__(type)
        self.graph = Graph()
        print('Parsing ontology from file')
        self.graph.parse(path, format=format)
    
    def queryOntology(self, query):
        return self.graph.query(query)

class DatabaseLoader(Loader):
    db = None

    def __init__(self, url, dataset, type=None):
        super().__init__(type)
        print('Connection with fuseki database will be established ...')
        self.db = FusekiQuery(url, dataset)
        print('Connection established.')
    
    def queryOntology(self, query):
        return self.db.run_sparql(query)

from enum import Enum

class Queries(str, Enum):
    SUBCLASS = """
            SELECT ?{0} ?{1}
            WHERE {{
                ?class a owl:Class .
                ?class rdfs:label ?{0} .
                ?class rdfs:subClassOf ?subclass .
                ?subclass owl:onClass ?name .
                ?name rdfs:label ?{1}
            }}
        """

    SUBSYSTEM = """
            SELECT ?{0} ?{1} ?{2} ?{3}
            WHERE {{
                ?class rdfs:label ?{0} .
                ?class rdf:type ?{2} .
                ?class ssn:hasSubsystem ?subclass .
                ?subclass rdfs:label ?{1} .
                ?subclass rdf:type ?{3}
            }}
        """

    PROPERTY = """
            SELECT ?{0}
            WHERE {{
                ?class a owl:Class .
                ?class rdfs:label ?{0} .
                ?class {1}:{2} ?property
            }}
        """

    NEARBY = """
        SELECT ?{1}
        WHERE {{
            ?device ssn:hasDeployment ?deployment .
            ?device rdfs:label ?{1} .
            ?deployment ssn:hasLocation ?location .
            ?location rdfs:label '{0}' .
        }}
    """

    TEMPORAL = """
        SELECT DISTINCT ?{1}
        WHERE {{
            ?device ssn:hasSubsystem ?actor .
            ?device rdfs:label '{0}' .
            ?attribute iot-lite:isActed ?actor .
            ?sensing iot-lite:isAssociatedWith ?attribute .
            ?sensing rdfs:label ?{1}
        }}
    """

    MONITORING = """
        SELECT ?{2} 
        WHERE {{
            ?monitor rdf:type ssn:Service .
            ?device iot-lite:exposedBy ?monitor .
            ?device rdfs:label '{0}' .
            ?monitor iot-context:hasMeasurement ?measurement .
            ?measurement iot-context:hasValue ?{2} .
            ?measurement iot-context:hasTimeStamp ?date .
            FILTER( ?date <= xsd:dateTime('{1}') )
        }}
        LIMIT 1
    """

    CAPABILITIES = """
        SELECT ?{1} ?{2} 
        WHERE {{
            ?sensor rdfs:label '{0}' .
            ?sensor ssn:hasMetadata ?meta .
            ?meta iot-lite:metadataType ?{1} .
            ?meta iot-lite:metadataValue ?{2} .
        }}
    """ 

    DEVICE_LINK = """
        SELECT *
        WHERE {{
            ?device rdfs:label '{1}' .
            ?device ssn:hasSubsystem ?sensing .
            ?sensor ssn:hasSensingDevice ?sensing .
            ?sensor rdfs:label '{0}'
        }}
    """
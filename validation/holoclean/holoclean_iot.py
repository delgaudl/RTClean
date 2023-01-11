import os, sys
sys.path.append('../holoclean/')
sys.path.append(os.path.join(os.path.dirname(__file__), '../../parser'))
import holoclean
from detect import NullDetector, ViolationDetector
from repair.featurize import *
from pathlib import Path
from parse import FileLoader, DatabaseLoader
from ontologydetector import OntologyDetector

# ontology file
ONTOLOGY_FILE_INPUT = './data/iot-scenario/iot-scenario.rdf'
ONTOLOG_FORMAT = 'turtle'
ONTOLOGY_ATTRIBUTES_PREFIX = 'iot-ins'

# (if no file is present) fuseki database connection
DB_URL = 'localhost:3030'
DB_DATASET_NAME = 'ontology'

# temp-path to store extracted data dependencies
DEPENDENCIES_OUTPUT = './data/iot-scenario/iot-dependencies.txt'

# setup a HoloClean session
hc = holoclean.HoloClean(
    db_name='holo',
    domain_thresh_1=0,
    domain_thresh_2=0,
    weak_label_thresh=0.99,
    max_domain=10000,
    cor_strength=0.6,
    nb_cor_strength=0.8,
    epochs=10,
    weight_decay=0.01,
    learning_rate=0.001,
    threads=1,
    batch_size=1,
    verbose=True,
    timeout=3*60000,
    feature_norm=False,
    weight_norm=False,
    print_fw=True
).session

hc.load_data('iot', './data/iot-scenario/error-injector/iot-scenario-dirty.csv')

# automatically extract dependencies from ontology stored as a file
loader = None
if Path(ONTOLOGY_FILE_INPUT).is_file():
    # Try to load ontology from file
    loader = FileLoader(ONTOLOGY_FILE_INPUT, ONTOLOG_FORMAT, type="iot-context-model")
else:
    # Try to connect to fuseki database
    loader = DatabaseLoader(DB_URL, DB_DATASET_NAME, type="iot-context-model")

if not Path(DEPENDENCIES_OUTPUT).is_file() and loader is not None:
    column_names = list(hc.ds.attr_to_idx.keys())
    loader.extractDependencies(DEPENDENCIES_OUTPUT, column_names, ONTOLOGY_ATTRIBUTES_PREFIX)

hc.load_dcs(DEPENDENCIES_OUTPUT)
hc.ds.set_constraints(hc.get_dcs())

# detect erroneous cells using these two detectors and add ontologydetector if available
detectors = [NullDetector(), ViolationDetector()]
if loader is not None:
    # currently very time intensive - can be further improved
    detectors.append(OntologyDetector(loader=loader))
hc.detect_errors(detectors)

# repair errors
hc.setup_domain()
featurizers = [
    InitAttrFeaturizer(),
    OccurAttrFeaturizer(),
    FreqFeaturizer(),
    ConstraintFeaturizer(),
]

hc.repair_errors(featurizers)

# evaluate the correctness of the results
hc.evaluate(fpath='./data/iot-scenario/error-injector/iot-scenario-clean.csv',
            tid_col='tid',
            attr_col='attribute',
            val_col='correct_val')

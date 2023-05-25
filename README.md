# RTClean

This is a prototypical implementation of a concept to extract dependencies from an ontology to improve existing error detection methods.
Those dependencies include new types upon existing _Denial Dependency_ and _Matching Dependency_:
* Device-Link Dependency
* Temporal Dependency
* Locality Dependency
* Monitoring Dependency
* Capability Dependency

## Structure of Repo

### data

Contains two datasets: _Hospital_ and _IoT_:
* _Hospital_ is a commonly used benchmark dataset from the US Health Service and already contains typos.
* _IoT_ is self-collected via a Smart Home Application with four temperature sensors. To inject errors use `inject.py`

### parser

* Definition of dependencies as python classes
* Definition of a ontology loader to parse from a file or a database
* Contains SPARQL Queries to extract dependencies from ontologies

### validation

Contains runnables to test data validation:

* Execution of HoloClean with Hospital dataset
* Execution of HoloClean with IoT dataset
* Execution of Raha with IoT dataset
* Injection of outliers in IoT dataset
* Execution of dBoost with outlier IoT dataset

## General

Ontologies are used to extract dependencies in the context of the data and find relations. These are evaluated for the usage in the further pipeline

### Error detection pipeline

The concept is implemented to work with [HoloClean](https://github.com/HoloClean/holoclean) and [Raha](https://github.com/BigDaMa/raha).
The HoloClean framework is enhanced with the extracted information to improve its error detection capabilities.

### Error Injection

*Hint:*
You need to build [error-generator](https://github.com/BigDaMa/error-generator). Change every occurences of "get_values()" to "values" since it is deprecated in pandas, but was not updated in this project.

### Run with HoloClean

*Hint:*
If you are running Python 3.8 and above you need to change all occurences of `time.clock()` to `time.time()`. This is a [known issue](https://github.com/HoloClean/holoclean/pull/110) of HoloClean.

## Installation Guide

This guide should give you an idea how to run this prototype. The following instructions show what to do to run the prototype with the Hospital dataset. 

1. Clone this repository
2. Clone [HoloClean](https://github.com/HoloClean/holoclean) to the same parent folder
3. See [Hints for HoloClean](#run-with-holoclean) and change the code accordingly
4. Setup HoloClean with [instructions from HoloClean-Repo](https://github.com/HoloClean/holoclean#readme). *Use Python 3.8 instead*
6. Start Postgres DB
7. You can try by executing `examples/holoclean_repair_example.py` in HoloClean's folder if the installation was successful
8. Install the python packages from the [requirements](#requirements)
9. To make sure the dependencies are extracted from the ontology (and not used from cache) delete `data/hospital-scenario/hospital-dependencies.txt`
10. Run `validation/holoclean/holoclean_hospital.py`
11. Results are printed to the console

The execution with the IoT dataset works analogously.

## Requirements

* Python (Version 3.8.x)
* rdflib
* pyfuseki
* pandas

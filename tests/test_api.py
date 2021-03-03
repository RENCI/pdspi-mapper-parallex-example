from tx.dateutils.utils import strtodate
import pdspi.pds_fhir_loader
import pdsphenotypemapping.clinical_feature
from tx.functional.either import Either, Right
from tx.parallex import run_python
import datetime
import json

timestamp = strtodate("2020-05-02T00:00:00Z")
pids = ["MickeyMouse"]
pid = pids[0]
json_in_dir = "./ptdata"
X = 10
Y = 10
study_start = strtodate("2010-01-01T00:00:00Z")
study_end = strtodate("2011-01-01T00:00:00Z")
resource_names = ["Patient", "Observation", "Condition", "MedicationRequest"]
age_unit = "year"


def test_age():
    fhir = pdspi.pds_fhir_loader.get_entries(json_in_dir=json_in_dir, pids=pids, resource_names=resource_names)
    patient = pdsphenotypemapping.clinical_feature.get_patient(patient_id=pid, fhir=fhir)
    age = pdsphenotypemapping.clinical_feature.age(unit=age_unit, timestamp=timestamp, patient=patient.value)
    assert age == Right({
        'certitude': 2,
        'how': {
            'birthDate': {
                'computed_from': {
                    'field': 'birthDate',
                    'resourceType': 'Patient'
                },
                'value': '1960-10-1'
            },
            'computed_from': ['request_timestamp', 'birthDate'],
            'request_timestamp': '2020-05-02'
        },
        'variableValue': {'unit': 'year', 'value': 59}
    })


def test_DOAC2():
    fhir = pdspi.pds_fhir_loader.get_entries(json_in_dir=json_in_dir, pids=pids, resource_names=resource_names)
    records = pdsphenotypemapping.clinical_feature.get_medication_request(patient_id=pid, fhir=fhir)
    interventions = pdsphenotypemapping.clinical_feature.DOAC2(start=study_start, end=study_end, records=records.value)
    assert isinstance(interventions, Right)
    assert len(interventions.value) == 4


def test_run():
    ret = run_python(3, "spec.py", "data.yaml")
    keys = {"0"}
    assert keys == set(ret.keys())
    for key in ret.keys():
        assert isinstance(ret[key], Right)

# -------------------------------------------------

import requests
import yaml
from pathlib import Path
from pdspi.pds_fhir_loader import get_entries
from pdsphenotypemapping.clinical_feature import get_patient_patient
import logging
from tempfile import mkdtemp
import os
import json
import shutil

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

json_headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

data_dir = Path(__file__).parent / "ptdata"

log.info(f"looking for fhir at {data_dir}")

resource_names = ["Patient", "MedicationRequest", "Condition", "Observation"]

input_dir = os.environ.get("INPUT_DIR")
output_dir = os.environ.get("OUTPUT_DIR")

def query(pids, timestamp, spec_name=None, lib_name=None, addarg=None, input_file=False, output_file=None):
    fhir = get_entries(json_in_dir=data_dir, pids=pids, resource_names=resource_names)
    if input_file:
        tmpdir = mkdtemp(dir=input_dir)
        tmpname = os.path.basename(tmpdir)
        for patient in fhir:
            patient_id = get_patient_patient(patient).value["id"]
            with open(os.path.join(tmpdir, patient_id + ".json"), "w") as f:
                json.dump(patient, f)
        fhir = {
            "$ref": tmpname
        }

    try:
        log.info(f"fhir = {fhir}")

        return requests.post(f"http://pdspi-mapper-parallex-example:8080/mapping", headers=json_headers, json={
            "data": fhir,
            "patientIds": pids,
            "settingsRequested": {
                "modelParameters": ([] if spec_name is None else [{
                    "id": "specName",
                    "parameterValue": {"value": spec_name}
                }]) + ([] if lib_name is None else [{
                    "id": "libraryPath",
                    "parameterValue": {"value": [lib_name]}
                }]) + ([] if output_file is None else [{
                    "id": "outputPath",
                    "parameterValue": {"value": output_file}
                }]) + ([] if addarg is None else [{
                    "id": "args",
                    "parameterValue": {"value": addarg}
                }]),
                "patientVariables": [
                    {"id":     "LOINC:2160-0"},
                    {"id":     "LOINC:82810-3"},
                    {"id":     "HP:0001892"},
                    {"id":     "HP:0000077"},
                    {"id":     "LOINC:45701-0"},
                    {"id":     "LOINC:LP212175-6"},
                    {"id":     "LOINC:64145-6"},
                    {"id":     "LOINC:85932-2"},
                    {"id":     "LOINC:54564-0"},
                    {"id":     "LOINC:LP128504-0"},
                    {"id":     "LOINC:54542-6"},
                    {"id":     "LOINC:LP172921-1"},
                    {"id":     "LOINC:30525-0"},
                    {"id":     "LOINC:54134-2"},
                    {"id":     "LOINC:54120-1"},
                    {"id":     "LOINC:21840-4"},
                    {"id":     "LOINC:56799-0"},
                    {"id":     "LOINC:8302-2"},
                    {"id":     "LOINC:29463-7"},
                    {"id":     "LOINC:39156-5"},
                    {"id":     "LOINC:LP21258-6"}
                ]
            },
            "timestamp": timestamp
        })
    finally:
        if input_file:
            shutil.rmtree(tmpdir)

def query2(pids, timestamp):
    fhir = get_entries(json_in_dir=data_dir, pids=pids, resource_names=resource_names)

    log.info(f"fhir = {fhir}")

    return requests.post(f"http://pdspi-mapper-parallex-example:8080/mapping", headers=json_headers, json={
        "data": fhir,
        "patientIds": pids,
        "settingsRequested": {
            "patientVariables": [
                {"id":     "LOINC:2160-0"},
                {"id":     "LOINC:82810-3"},
                {"id":     "HP:0001892"},
                {"id":     "HP:0000077"},
                {"id":     "LOINC:45701-0"},
                {"id":     "LOINC:LP212175-6"},
                {"id":     "LOINC:64145-6"},
                {"id":     "LOINC:85932-2"},
                {"id":     "LOINC:54564-0"},
                {"id":     "LOINC:LP128504-0"},
                {"id":     "LOINC:54542-6"},
                {"id":     "LOINC:LP172921-1"},
                {"id":     "LOINC:30525-0"},
                {"id":     "LOINC:54134-2"},
                {"id":     "LOINC:54120-1"},
                {"id":     "LOINC:21840-4"},
                {"id":     "LOINC:56799-0"},
                {"id":     "LOINC:8302-2"},
                {"id":     "LOINC:29463-7"},
                {"id":     "LOINC:39156-5"},
                {"id":     "LOINC:LP21258-6"}
            ]
        },
        "timestamp": timestamp
    })


def assert_result(res):
    assert len(res) == 1
    for p in res:
        assert "patientId" in p
        assert len(p["values"]) == 21
        for v in p["values"]:
            assert "id" in v
            assert "variableValue" in v

def test_api_spec():
    timestamp = "2020-05-02T00:00:00Z"
    pids = ["MickeyMouse"]

    result = query(pids, timestamp)
    log.info(result.content)
    assert result.status_code == 200
                
    assert_result(result.json())
    
def test_api_spec_data_from_file():
    timestamp = "2020-05-02T00:00:00Z"
    pids = ["MickeyMouse"]

    result = query(pids, timestamp, input_file=True)
    log.info(result.content)
    assert result.status_code == 200
                
    assert_result(result.json())
    
def test_api_spec_result_to_file():
    timestamp = "2020-05-02T00:00:00Z"
    pids = ["MickeyMouse"]

    output_file = "result.json"
    output_file_full_path = os.path.join(output_dir, output_file)
    try:
        result = query(pids, timestamp, output_file=output_file)

        assert result.status_code == 204

        with open(output_file_full_path) as outp:
            obj = json.load(outp)
        assert_result(obj)
    finally:
        os.remove(output_file_full_path)
    
def test_api_spec2():
    timestamp = "2020-05-02T00:00:00Z"
    pids = ["MickeyMouse"]

    result = query(pids, timestamp, spec_name="spec2.py")
    log.info(result.content)
    assert result.status_code == 200
                
    assert result.json() == [{
        "outcome": False
    }]

def test_api_spec3():
    timestamp = "2020-05-02T00:00:00Z"
    pids = ["MickeyMouse"]

    result = query(pids, timestamp, spec_name="spec3.py", lib_name="spec3")
    log.info(result.content)
    assert result.status_code == 200
                
    assert result.json() == [{
        "outcome": [1]
    }]

def test_api_spec4():
    timestamp = "2020-05-02T00:00:00Z"
    pids = ["MickeyMouse"]

    result = query2(pids, timestamp)
    log.info(result.content)
    assert result.status_code == 200
                
    assert_result(result.json())

def test_api_spec5():
    timestamp = "2020-05-02T00:00:00Z"
    pids = ["MickeyMouse"]

    result = query(pids, timestamp, spec_name="spec4.py")
    log.info(result.content)
    assert result.status_code == 200
                
    assert result.json() == [{
        "patientId": "MickeyMouse",
        "values": [
            {
                "id": "outcome",
                "variableValue": {
                    "value": False
                }
            }, {
                "id": "bmi_before",
                "variableValue": {
                    "value": None
                }
            }, {
                "id": "bmi_after",
                "variableValue": {
                    "value": None
                }
            }
        ]
    }]


def test_api_addarg():
    timestamp = "2020-05-02T00:00:00Z"
    pids = ["MickeyMouse"]

    result = query(pids, timestamp, spec_name="addarg.py", addarg={"t": "a"})
    log.info(result.content)
    assert result.status_code == 200
                
    assert result.json() == "a"

    

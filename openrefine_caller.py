# %%
from typing import Union, List

import requests
import re
import json
import io
import urllib.parse
import time

# %%
from requests import Response

PORJECT_NAME = "1234567890"


def get_csrf_token(port=3333):

    r = requests.get(f"http://localhost:{port}/command/core/get-csrf-token")
    return r.json()['token']

def create_project(input_csv, port=3333):

    token = get_csrf_token(port)
    options = {
        "project-name": " ".join(input_csv.split(".")),
        "project-file": open(input_csv)
    }

    params = {
        'csrf_token': token
    }
    r = requests.post("http://localhost:%s" % port + "/command/core/create-project-from-upload",
                      files=options, params=params)

    project_id = re.findall(r"\?project=(\d+)", r.url)[0]
    return project_id


# %%

def get_operation_json_string(country_tag: str, state_tag: str, city_tag: str) -> str:
    operations = [
        {'op': 'core/recon', 'engineConfig': {'facets': [], 'mode': 'row-based'}, 'columnName': country_tag,
         'config': {'mode': 'standard-service',
                    'service': 'https://tools.wmflabs.org/openrefine-wikidata/en/api',
                    'identifierSpace': 'http://www.wikidata.org/entity/',
                    'schemaSpace': 'http://www.wikidata.org/prop/direct/',
                    'type': {'id': 'Q3624078', 'name': 'sovereign state'}, 'autoMatch': True, 'columnDetails': [],
                    'limit': 0}, 'description': ('Reconcile cells in column %s to type Q3624078' % country_tag)},
        {
            "op": "core/recon-match-best-candidates",
            "engineConfig": {
                "facets": [
                    {
                        "type": "list",
                        "name": f"{country_tag}: judgment",
                        "expression": "forNonBlank(cell.recon.judgment, v, v, if(isNonBlank(value), \"(unreconciled)\", \"(blank)\"))",
                        "columnName": country_tag,
                        "invert": False,
                        "omitBlank": False,
                        "omitError": False,
                        "selection": [
                            {
                                "v": {
                                    "v": "none",
                                    "l": "none"
                                }
                            }
                        ],
                        "selectBlank": False,
                        "selectError": False
                    },
                    {
                        "type": "range",
                        "name": f"{country_tag}: best candidate's score",
                        "expression": "cell.recon.best.score",
                        "columnName": f"{country_tag}",
                        "from": 96,
                        "to": 101,
                        "selectNumeric": True,
                        "selectNonNumeric": True,
                        "selectBlank": True,
                        "selectError": True
                    }
                ],
                "mode": "row-based"
            },
            "columnName": f"{country_tag}",
            "description": "Match each cell to its best recon candidate in column Country"
        },
        {'op': 'core/recon', 'engineConfig': {'facets': [], 'mode': 'row-based'},
         'columnName': state_tag, 'config': {'mode': 'standard-service',
                                             'service': 'https://tools.wmflabs.org/openrefine-wikidata/en/api',
                                             'identifierSpace': 'http://www.wikidata.org/entity/',
                                             'schemaSpace': 'http://www.wikidata.org/prop/direct/',
                                             'type': {'id': 'Q10864048',
                                                      'name': 'first-level administrative country subdivision'},
                                             'autoMatch': True, 'columnDetails': [
                {'column': country_tag, 'propertyName': 'country', 'propertyID': 'P17'}], 'limit': 0},
         'description': 'Reconcile cells in column State or Province  (if applicable) to type Q10864048'},
        {
            "op": "core/recon-match-best-candidates",
            "engineConfig": {
                "facets": [
                    {
                        "type": "range",
                        "name": f"{state_tag}: best candidate's score",
                        "expression": "cell.recon.best.score",
                        "columnName": f"{state_tag}",
                        "from": 98,
                        "to": 101,
                        "selectNumeric": True,
                        "selectNonNumeric": True,
                        "selectBlank": True,
                        "selectError": True
                    }
                ],
                "mode": "row-based"
            },
            "columnName": f"{state_tag}",
            "description": f"Match each cell to its best recon candidate in column {state_tag}"
        },
        {'op': 'core/text-transform', 'engineConfig': {'facets': [
            {'type': 'list', 'name': '%s: judgment' % state_tag,
             'expression': 'forNonBlank(cell.recon.judgment, v, v, if(isNonBlank(value), "(unreconciled)", "(blank)"))',
             'columnName': state_tag, 'invert': False, 'omitBlank': False,
             'omitError': False, 'selection': [{'v': {'v': 'none', 'l': 'none'}}], 'selectBlank': False,
             'selectError': False}], 'mode': 'row-based'}, 'columnName': state_tag,
         'expression': '""', 'onError': 'keep-original', 'repeat': False, 'repeatCount': 10,
         'description': 'Text transform on cells in column State or Province  (if applicable) using expression ""'},
        {'op': 'core/recon', 'engineConfig': {'facets': [], 'mode': 'row-based'},
         'columnName': ('%s' % city_tag), 'config': {'mode': 'standard-service',
                                                     'service': 'https://tools.wmflabs.org/openrefine-wikidata/en/api',
                                                     'identifierSpace': 'http://www.wikidata.org/entity/',
                                                     'schemaSpace': 'http://www.wikidata.org/prop/direct/',
                                                     'type': {'id': 'Q7930989', 'name': 'city/town'},
                                                     'autoMatch': True, 'columnDetails': [
                {'column': ('%s' % country_tag), 'propertyName': 'country', 'propertyID': 'P17'}], 'limit': 0},
         'description': ('Reconcile cells in column %s to type Q7930989' % city_tag)},
        {
            "op": "core/recon-match-best-candidates",
            "engineConfig": {
                "facets": [
                    {
                        "type": "range",
                        "name": f"{city_tag}: best candidate's score",
                        "expression": "cell.recon.best.score",
                        "columnName": f"{city_tag}",
                        "from": 99,
                        "to": 101,
                        "selectNumeric": True,
                        "selectNonNumeric": True,
                        "selectBlank": True,
                        "selectError": True
                    }
                ],
                "mode": "row-based"
            },
            "columnName": f"{city_tag}",
            "description": f"Match each cell to its best recon candidate in column {city_tag}"
        },
        {'op': 'core/recon-mark-new-topics', 'engineConfig': {'facets': [
            {'type': 'list', 'name': ('%s: judgment' % city_tag),
             'expression': 'forNonBlank(cell.recon.judgment, v, v, if(isNonBlank(value), "(unreconciled)", "(blank)"))',
             'columnName': city_tag, 'invert': False, 'omitBlank': False, 'omitError': False,
             'selection': [{'v': {'v': 'none', 'l': 'none'}}], 'selectBlank': False, 'selectError': False}],
            'mode': 'row-based'},
         'columnName': city_tag, 'shareNewTopics': False,
         'description': (
                 'Mark to create new items for cells in column %s, one item for each cell' % city_tag)}]

    fo = io.StringIO()
    json.dump(operations, fo)
    return fo.getvalue()


# %% post our

def post_operation(project_id="2334308023768", port=3333,
                   payload="operations=%5B%7B%22op%22%3A%22core%2Frecon%22%2C%22engineConfig%22%3A%7B%22facets%22%3A%5B%5D%2C%22mode%22%3A%22row-based%22%7D%2C%22columnName%22%3A%22Country%22%2C%22config%22%3A%7B%22mode%22%3A%22standard-service%22%2C%22service%22%3A%22https%3A%2F%2Ftools.wmflabs.org%2Fopenrefine-wikidata%2Fen%2Fapi%22%2C%22identifierSpace%22%3A%22http%3A%2F%2Fwww.wikidata.org%2Fentity%2F%22%2C%22schemaSpace%22%3A%22http%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%22%2C%22type%22%3A%7B%22id%22%3A%22Q6256%22%2C%22name%22%3A%22country%22%7D%2C%22autoMatch%22%3Atrue%2C%22columnDetails%22%3A%5B%5D%2C%22limit%22%3A0%7D%2C%22description%22%3A%22Reconcile+cells+in+column+Country+to+type+Q6256%22%7D%2C%7B%22op%22%3A%22core%2Frecon-match-best-candidates%22%2C%22engineConfig%22%3A%7B%22facets%22%3A%5B%5D%2C%22mode%22%3A%22row-based%22%7D%2C%22columnName%22%3A%22Country%22%2C%22description%22%3A%22Match+each+cell+to+its+best+recon+candidate+in+column+Country%22%7D%5D&engine=%7B%22facets%22%3A%5B%5D%2C%22mode%22%3A%22row-based%22%7D"):

    csrf_token = get_csrf_token(port)
    url = "http://127.0.0.1:%s/command/core/apply-operations" % port
    querystring = {"project": project_id, "csrf_token": csrf_token}
    payload = payload
    headers = {
        'Connection': "keep-alive",
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Origin': ("http://127.0.0.1:%s" % port),
        'X-Requested-With': "XMLHttpRequest",
        'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
        'Sec-Fetch-Site': "same-origin",
        'Sec-Fetch-Mode': "cors",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,zh-TW;q=0.6,fr;q=0.5",
        'Cookie': "host=.butterfly",
        'Cache-Control': "no-cache",
        'Host': ("127.0.0.1:%s" % port),
        'Content-Length': "1024",
        'cache-control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

    return response.json()


# %% checking process



def get_processes(project_id_string="2334308023768", port="3333"):
    url = "http://127.0.0.1:%s/command/core/get-processes" % port

    querystring = {"project": project_id_string}

    headers = {
        'Connection': "keep-alive",
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'X-Requested-With': "XMLHttpRequest",
        'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,zh-TW;q=0.6,fr;q=0.5",
        'Cookie': "host=.butterfly",
        'Cache-Control': "no-cache",
        'Postman-Token': "57c0f128-2372-4488-bc74-75000fddb9e9,e1a36b54-2e99-4c7c-865c-94c4f5d7e113",
        'Host': ("127.0.0.1:%s" % port),
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()


# %% export
def export_rows(project_id: Union[int, str], port=3333) -> Response:
    data = {
        "engine": '{"facets":[],"mode":"row-based"}',
        'project': str(project_id),
        'format': 'csv'
    }

    response = requests.post("http://127.0.0.1:%s/command/core/export-rows" % port,
                             data=data)

    return response


# %% working

def openrefine_reconcile(input_csv: str, column_tags: List[List[str]],
                         output_csv="output.csv", port=3333, limit_time=3000, project_id=None):
    port_str = str(port)

    try:
        if project_id is None:
            project_id = create_project(input_csv)
            print(project_id)
        for country_tag, state_tag, city_tag in column_tags:
            operation_json = get_operation_json_string(country_tag, state_tag, city_tag)
            payload = (
                    "operations=" +
                    urllib.parse.quote(operation_json) +
                    "&engine=%7B%22facets%22%3A%5B%5D%2C%22mode%22%3A%22row-based%22%7D"
            )

            post_operation(project_id, port_str, payload)

            for i in range(limit_time):
                time.sleep(1)
                processing_json: dict = get_processes(project_id, port_str)
                print("Pending... (%d work pending)" % len(processing_json['processes']))
                if processing_json.get("processes") is None:
                    break
                elif len(processing_json["processes"]) == 0:
                    break

        exported = export_rows(project_id, port)

        if exported.status_code != 200:
            print("Cannot get the exported result")
        else:
            with open(output_csv, "wb") as f:
                f.write(exported.content)
            print("The normalized files has been outputted into %s" % output_csv)

        return project_id
    except Exception as e:
        raise e


# %%

if __name__ == '__main__':
    openrefine_reconcile("data/authors.csv", [
        ['Country', 'State', 'City (e.g.Brisbane)']
    ])

# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests to verify the endpoints for maintaining aysnchronous DRS callback requests.

Test-Suite to ensure that the /callbacks endpoint is working as expected.
"""
import copy
import requests
from http import HTTPStatus
import json

import pytest
from flask import current_app

from doc_api.models import Document
from doc_api.utils.logging import logger

PARAM_TEST_APIKEY = "?x-apikey={api_key}"
DOC_REC_PATH: str = "/api/v1/callbacks/document-records"
TEST_DOC_REC_LEGACY = {
    "accountId": "123456",
    "consumerDocumentId": "99990950",
    "consumerIdentifier": "108924",
    "documentType": "TRAN",
    "documentClass": "MHR"
}
TEST_DOC_REC_MODERN = {
    "accountId": "123456",
    "consumerDocumentId": "1099990950",
    "consumerIdentifier": "108924",
    "documentType": "TRAN",
    "documentClass": "MHR"
}
TEST_DOC_REC_INVALID = {
    "accountId": "123456",
    "consumerDocumentId": "99990950",
    "consumerIdentifier": "108924",
}
TEST_DOC_REC_BUSINESS_API = {
    "accountId": "business-api",
    "consumerDocumentId": "99980991",
    "consumerIdentifier": "BC1108924",
    "consumerFilingType": "annualReport",
    "consumerReferenceId": "1629808",
    "documentClass": "CORP"
}
TEST_DOC_REC_BUSINESS_API_WRAPPED = {
    "data": {
        "accountId": "business-api",
        "consumerDocumentId": None,
        "consumerIdentifier": "BC0223072",
        "consumerFilingType": "changeOfReceivers",
        "consumerReferenceId": 233834,
        "documentClass": "CORP"
    }
}


# testdata pattern is ({description}, {payload_json}, {has_key}, {author}, {status}, {ref_id})
TEST_CREATE_DATA = [
    ("Invalid no doc class type", TEST_DOC_REC_INVALID, True, "John Smith", HTTPStatus.BAD_REQUEST, None),
    ("Invalid no api key", TEST_DOC_REC_LEGACY, False, "John Smith", HTTPStatus.UNAUTHORIZED, None),
    ("Invalid bad api key", TEST_DOC_REC_LEGACY, False, "John Smith", HTTPStatus.UNAUTHORIZED, None),
    ("Valid legacy", TEST_DOC_REC_LEGACY, True, "John Smith", HTTPStatus.CREATED, None),
    ("Valid modern", TEST_DOC_REC_MODERN, True, "John Smith", HTTPStatus.CREATED, "9014005"),
    ("Valid business api", TEST_DOC_REC_BUSINESS_API, True, None, HTTPStatus.CREATED, None),
    ("Valid business api wrapped", TEST_DOC_REC_BUSINESS_API_WRAPPED, True, None, HTTPStatus.CREATED, None),
]
# testdata pattern is ({description}, {payload_json}, {status}, {update_doc_type}, {update_filing_type})
TEST_UPDATE_DATA = [
    ("Valid business api", TEST_DOC_REC_BUSINESS_API, HTTPStatus.CREATED, "ADDR", "changeOfAddress"),
]

@pytest.mark.parametrize("desc,payload_json,has_key,author,status,ref_id", TEST_CREATE_DATA)
def test_create_doc_rec(session, client, jwt, desc, payload_json, has_key, author, status, ref_id):
    """Assert that a post save new callback document record works as expected."""
    if is_ci_testing() or not current_app.config.get("SUBSCRIPTION_API_KEY"):
        return
    # setup
    headers = None   # {**kwargs, **{"Content-Type": "application/json"}}
    req_path = DOC_REC_PATH
    api_key = current_app.config.get("SUBSCRIPTION_API_KEY")
    if has_key and api_key:
        if desc == "Invalid bad api key":
            api_key += "JUNK"
        params = PARAM_TEST_APIKEY.format(api_key=api_key)
        req_path += params
    req_json = copy.deepcopy(payload_json)
    if author:
        req_json["author"] = author
    if ref_id:
        req_json["consumerReferenceId"] = ref_id
    # test
    payload = json.dumps(req_json).encode("utf-8")
    response = client.post(req_path, data=payload, headers=headers)
    # logger.info(response.json)

    # check
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        doc_json = response.json
        assert doc_json
        assert doc_json.get("documentServiceId")
        assert not doc_json.get("documentURL")
        if ref_id:
            assert doc_json.get("consumerReferenceId") == ref_id
        doc: Document = Document.find_by_doc_service_id(doc_json.get("documentServiceId"))
        assert doc
        doc_json = doc.json
        assert not doc_json.get("scanningInformation")
        if desc == "Valid business api wrapped":
            logger.info(doc_json)


@pytest.mark.parametrize("desc,payload_json,status,update_doc_type,update_filing_type", TEST_UPDATE_DATA)
def test_update_doc_rec(session, client, jwt, desc, payload_json, status, update_doc_type, update_filing_type):
    """Assert that a post save new callback document record, then update it, works as expected."""
    if is_ci_testing() or not current_app.config.get("SUBSCRIPTION_API_KEY"):
        return
    # setup
    headers = None   # {**kwargs, **{"Content-Type": "application/json"}}
    req_path = DOC_REC_PATH
    api_key = current_app.config.get("SUBSCRIPTION_API_KEY")
    params = PARAM_TEST_APIKEY.format(api_key=api_key)
    req_path += params
    req_json = copy.deepcopy(payload_json)
    # test
    payload = json.dumps(req_json).encode("utf-8")
    response = client.post(req_path, data=payload, headers=headers)
    # logger.info(response.json)

    # check
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        doc_json = response.json
        assert doc_json
        assert doc_json.get("documentServiceId")
        assert not doc_json.get("documentURL")
        doc: Document = Document.find_by_doc_service_id(doc_json.get("documentServiceId"))
        assert doc

    req_json["consumerFilingType"] = update_filing_type
    payload = json.dumps(req_json).encode("utf-8")
    response = client.post(req_path, data=payload, headers=headers)
    assert response.status_code == HTTPStatus.OK
    doc_json = response.json
    assert doc_json
    assert doc_json.get("documentType") == update_doc_type


def is_ci_testing() -> bool:
    """Check unit test environment: exclude pub/sub for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"


def get_test_colin(session, client, jwt):
    """Assert ."""
    if is_ci_testing() or not current_app.config.get("SUBSCRIPTION_API_KEY"):
        return
    # setup
    headers = None   # {**kwargs, **{"Content-Type": "application/json"}}
    headers_get_menu = {
        "Connection": "keep-alive",
        "Content-Type": "text/plain; charset=ISO-8859-1"
    }
    base_path = "https://www.corporateonline.gov.bc.ca/corporateonline/colin"
    get_menu_path = base_path + "/accesstransaction/menu.do?action=overview&filingTypeCode=RPRNT&from=main"
    overview_path = base_path + "/accesstransaction/menu.do"
    search_path = base_path + "/identcorp/searchCorp.do"
    receipt_path = base_path + "/reprint/report.do?action=receiptReport&check_token=no&historyIndex=1"
    # get_menu_path = "https://www.corporateonline.gov.bc.ca/"
    # logger.info(get_menu_path)
    # api_key = current_app.config.get("SUBSCRIPTION_API_KEY")
    #params = PARAM_TEST_APIKEY.format(api_key=api_key)
    #req_path += params
    #req_json = copy.deepcopy(payload_json)
    # test
    #payload = json.dumps(req_json).encode("utf-8")
    response = requests.get(get_menu_path, headers=headers_get_menu)
    # logger.info(response.text)
    cookie: str = response.cookies["JSESSIONID"]
    logger.info(f"cookie={cookie}")
    cookies = dict(JSESSIONID=cookie)
    overview_data = {
        "formType": "overview",
        "navigationAction": "next",
        "nextButton.x": 28,
        "nextButton.y": 13
    }
    response = requests.post(overview_path, headers=headers, data=overview_data, cookies=cookies)
    logger.info(f"overview status={response.status_code}")
    # with open("tests/unit/resources/colin_overview_response.txt", "w") as overview_file:
    #    overview_file.write(response.text)
    #    overview_file.close()
    search_data = {
        "defaultAction": "next",
        "formType": "search",
        "corpNum": "BC0659569",
        "password": "PROVIDE",
        "navigationAction": "next",
        "nextButton.x": 27,
        "nextButton.y": 7
    }
    response2 = requests.post(search_path, headers=headers, data=search_data, cookies=cookies)
    logger.info(f"search status={response2.status_code}")
    logger.info(response2.headers)
    # with open("tests/unit/resources/colin_search_response.txt", "w") as search_file:
    #    search_file.write(response2.text)
    #    search_file.close()
    response = requests.get(receipt_path, cookies=cookies)
    logger.info(f"receipt report status={response.status_code}")
    with open("tests/unit/resources/colin_receipt.pdf", "wb") as receipt_file:
        receipt_file.write(response.content)
        receipt_file.close()


def test_colin_file(session, client, jwt):
    """Assert ."""
    test_file: str = None
    with open("tests/unit/resources/colin-noa.html", "r") as data_file:
        test_file = data_file.read()
        data_file.close()
    search_base = "/reprint/report.do?action={report_type}Report&check_token=no&historyIndex={filing_index}"
    test_link = search_base.format(report_type="cert", filing_index="7")
    result = test_file.find(test_link)
    logger.info(f"search {test_link} find result={result}")
    index_first_filing_date = test_file.find("January 15, 2025 9:30 AM")
    index_first_report = test_file.find("historyIndex=0")
    logger.info(f"first filing date={index_first_filing_date} first report link={index_first_report}")

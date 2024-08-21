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

"""Tests to verify the endpoints for document searches.

Test-Suite to ensure that the /searches endpoint is working as expected.
"""
from http import HTTPStatus

import pytest
from flask import current_app

from doc_api.models import utils as model_utils, Document
from doc_api.models.type_tables import DocumentClasses, DocumentTypes
from doc_api.services.authz import BC_REGISTRY, STAFF_ROLE, COLIN_ROLE
from doc_api.utils.logging import logger

from tests.unit.services.utils import create_header, create_header_account


TEST_DATAFILE = 'tests/unit/services/unit_test.pdf'
MOCK_AUTH_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
STAFF_ROLES = [STAFF_ROLE, BC_REGISTRY]
INVALID_ROLES = [COLIN_ROLE]
DOC_CLASS1 = DocumentClasses.CORP.value
DOC_TYPE1 = DocumentTypes.CORP_MISC.value
TEST_DOC_ID = 'UT9999999'
TEST_CONSUMER_ID = 'UTBUS'
MEDIA_PDF = model_utils.CONTENT_TYPE_PDF
PARAMS1 = '?consumerIdentifier=UTBUS&consumerFilename=test.pdf&consumerFilingDate=2024-07-25' + \
    '&consumerScanDate=2024-05-01&consumerDocumentId=' + TEST_DOC_ID
PATH: str = '/api/v1/business/{doc_class}/{doc_type}' + PARAMS1
GET_PATH = '/api/v1/searches/{doc_class}'
PARAM_CONSUMER_ID = '?consumerIdentifier=' + TEST_CONSUMER_ID
PARAM_CONSUMER_ID_NONE = '?consumerIdentifier=XXXXXXX'
PARAM_DOC_SERVICE_ID = '?documentServiceId='
PARAM_CONSUMER_DOC_ID = '?consumerDocumentId=' + TEST_DOC_ID
PARAMS_DATE_INVALID = '?queryStartDate=2024-07-30'
PARAMS_DATE_VALID = '?queryStartDate=2023-07-30&queryEndDate=2023-07-30'
PARAMS_DATE_DOC_TYPE_VALID = '?queryStartDate=2023-07-30&queryEndDate=2024-03-30&documentType=' + DOC_TYPE1
PARAMS_DATE_CONS_ID_VALID = '?queryStartDate=2023-07-30&queryEndDate=2024-03-30&consumerIdentifier=' + TEST_CONSUMER_ID
PARAMS_DATE_ALL_VALID = '?queryStartDate=2023-07-30&queryEndDate=2024-03-30&consumerIdentifier=' + TEST_CONSUMER_ID + \
    '&documentType=' + DOC_TYPE1

# testdata pattern is ({description}, {params}, {roles}, {account}, {doc_class}, {status})
TEST_SEARCH_DATA = [
    ('Invalid doc class', PARAM_CONSUMER_ID, STAFF_ROLES, 'UT1234', 'JUNK', HTTPStatus.BAD_REQUEST),
    ('Invalid no params', None, STAFF_ROLES, 'UT1234', DOC_CLASS1, HTTPStatus.BAD_REQUEST),
    ('Invalid date params', PARAMS_DATE_INVALID, STAFF_ROLES, 'UT1234', DOC_CLASS1, HTTPStatus.BAD_REQUEST),
    ('Staff missing account', PARAM_CONSUMER_ID, STAFF_ROLES, None, DOC_CLASS1, HTTPStatus.BAD_REQUEST),
    ('Invalid role', PARAM_CONSUMER_ID, INVALID_ROLES, 'UT1234', DOC_CLASS1, HTTPStatus.UNAUTHORIZED),
    ('Valid date params', PARAMS_DATE_VALID, STAFF_ROLES, 'UT1234', DOC_CLASS1, HTTPStatus.NOT_FOUND),
    ('Valid date, type params', PARAMS_DATE_DOC_TYPE_VALID, STAFF_ROLES, 'UT1234', DOC_CLASS1, HTTPStatus.NOT_FOUND),
    ('Valid date, consumer_id params', PARAMS_DATE_CONS_ID_VALID, STAFF_ROLES, 'UT1234', DOC_CLASS1,
     HTTPStatus.NOT_FOUND),
    ('Valid date, type, consumer id params', PARAMS_DATE_ALL_VALID, STAFF_ROLES, 'UT1234', DOC_CLASS1,
     HTTPStatus.NOT_FOUND),
    ('Valid consumer ID no results', PARAM_CONSUMER_ID_NONE, STAFF_ROLES, 'UT1234', DOC_CLASS1, HTTPStatus.NOT_FOUND),
    ('Valid consumer ID', PARAM_CONSUMER_ID, STAFF_ROLES, 'UT1234', DOC_CLASS1, HTTPStatus.OK),
    ('Valid document ID', PARAM_CONSUMER_DOC_ID, STAFF_ROLES, 'UT1234', DOC_CLASS1, HTTPStatus.OK),
    ('Valid doc service ID', PARAM_DOC_SERVICE_ID, STAFF_ROLES, 'UT1234', DOC_CLASS1, HTTPStatus.OK)
]


@pytest.mark.parametrize('desc,params,roles,account,doc_class,status', TEST_SEARCH_DATA)
def test_searches(session, client, jwt, desc, params, roles, account, doc_class, status):
    """Assert that a documents search request works as expected."""
    # setup
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    req_path = GET_PATH.format(doc_class=doc_class)
    if params:
        req_path += params

    if status == HTTPStatus.OK:  # Create.
        raw_data = None
        with open(TEST_DATAFILE, 'rb') as data_file:
            raw_data = data_file.read()
            data_file.close()
        response = client.post('/api/v1/business/CORP/CORP_MISC' + PARAMS1,
                               data=raw_data,
                               headers=headers,
                               content_type=MEDIA_PDF)
        # logger.info(response.json)
        if desc == 'Valid doc service ID':
            resp_json = response.json
            req_path += resp_json.get('documentServiceId')
    # test
    response = client.get(req_path, headers=headers)

    # check
    # logger.info(response.json)
    assert response.status_code == status
    if response.status_code == HTTPStatus.OK:
        results_json = response.json
        assert results_json
        for doc_json in results_json:
            assert doc_json
            assert doc_json.get('documentServiceId')
            assert doc_json.get('documentURL')
            assert doc_json.get('documentClass') == doc_class

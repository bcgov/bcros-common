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
"""Test Suite to ensure the request utility functions are working as expected."""
import copy

import pytest

from doc_api.models import Document, DocumentRequest, DocumentScanning, User
from doc_api.models import utils as model_utils
from doc_api.models.type_tables import DocumentClasses, DocumentTypes, RequestTypes
from doc_api.resources import utils as resource_utils
from doc_api.resources.request_info import RequestInfo
from doc_api.services.abstract_storage_service import DocumentTypes as StorageDocTypes
from doc_api.utils.logging import logger

TEST_DATAFILE = "tests/unit/services/unit_test.pdf"
TEST_USER: User = User(username="testuser")
TEST_INFO: RequestInfo = RequestInfo(
    request_type=RequestTypes.ADD,
    request_path="path",
    doc_type=DocumentTypes.NR_MISC,
    doc_storage_type=StorageDocTypes.NR,
)
TEST_DOCUMENT = Document(
    id=200000000,
    document_service_id="UT9999999",
    document_type=DocumentTypes.PPR_MISC.value,
    document_class=DocumentClasses.PPR.value,
    add_ts=model_utils.now_ts(),
    consumer_document_id="T0000001",
    consumer_identifier="T0000002",
    consumer_filename="test.pdf",
    consumer_filing_date=model_utils.ts_from_iso_date_noon("2024-07-01"),
    description="Original",
)
TEST_TOKEN = {
    "username": "username_TEST1",
    "firstname": "given_name_TEST1",
    "lastname": "family_name_TEST1",
    "iss": "issuer_TEST1",
    "sub": "subject_TEST1",
    "idp_userid": "idp_userid_TEST1",
    "loginSource": "source_TEST1",
}
TEST_FILENAME = "updated_name.pdf"
DOC_SCAN = {
    "consumerDocumentId": "T0000002",
    "scanDateTime": "2024-07-01T19:00:00+00:00",
    "documentClass": "PPR",
    "accessionNumber": "AN-0001",
    "batchId": "1234",
    "author": "Jane Smith",
    "pageCount": 3,
}
UPDATE_DOC_SCAN = {
    "scanDateTime": "2024-08-15T19:00:00+00:00",
    "accessionNumber": "AN-0002",
    "batchId": "12345",
    "author": "Janet Smith",
    "pageCount": 4,
}
UPDATE_DOC = {
    "consumerDocumentId": "T0000002",
    "consumerFilename": "test-update.pdf",
    "consumerIdentifier": "CI-0000002",
    "documentType": "CORP_MISC",
    "documentClass": "CORP",
    "consumerFilingDateTime": "2024-08-01T19:00:00+00:00",
    "description": "Updated description of the document.",
}

# testdata pattern is ({req_type}, {req_path}, {doc_type}, {doc_storage_type}, {staff})
TEST_DATA_REQUEST_INFO = [
    (RequestTypes.ADD.value, "/CORP/CORP_MISC", DocumentTypes.CORP_MISC.value, StorageDocTypes.BUSINESS.value, True),
    (RequestTypes.GET.value, "/MHR_MISC", DocumentTypes.MHR_MISC.value, StorageDocTypes.MHR.value, False),
    (RequestTypes.REPLACE.value, "/NR_MISC", DocumentTypes.NR_MISC.value, StorageDocTypes.NR.value, True),
    (RequestTypes.UPDATE.value, "/PPR_MISC", DocumentTypes.PPR_MISC.value, StorageDocTypes.PPR.value, False),
]
# testdata pattern is ({doc_ts}, {doc_type}, {doc_service_id}, {content_type}, {doc_storage_type})
TEST_DATA_SAVE_STORAGE = [
    (
        "2024-09-01T19:00:00+00:00",
        DocumentTypes.CORP_MISC,
        "UT000001111",
        model_utils.CONTENT_TYPE_PDF,
        StorageDocTypes.BUSINESS,
    )
]
# testdata pattern is ({info}, {user}, {doc_id}, {account_id})
TEST_DATA_DOC_REQUEST = [(TEST_INFO, TEST_USER, 100, "UT1234")]
# testdata pattern is ({doc_class}, {start_offset}, {doc_type}, {cons_id}, {no_results})
TEST_DATA_DOC_DATES = [
    (None, 10, None, None, True),
    (DocumentClasses.CORP, 10, None, None, False),
    (DocumentClasses.CORP, 1, DocumentTypes.MHR_MISC, None, True),
    (DocumentClasses.CORP.value, 10, None, "UT000004", False),
    (DocumentClasses.CORP.value, 10, DocumentTypes.CORP_MISC.value, "UT000004", False),
]
# testdata pattern is ({doc_class}, {storage_type})
TEST_DATA_STORAGE_TYPES = [
    (DocumentClasses.CORP, StorageDocTypes.BUSINESS),
    (DocumentClasses.COOP, StorageDocTypes.BUSINESS),
    (DocumentClasses.FIRM, StorageDocTypes.BUSINESS),
    (DocumentClasses.OTHER, StorageDocTypes.BUSINESS),
    (DocumentClasses.SOCIETY, StorageDocTypes.BUSINESS),
    (DocumentClasses.MHR, StorageDocTypes.MHR),
    (DocumentClasses.NR, StorageDocTypes.NR),
    (DocumentClasses.PPR, StorageDocTypes.PPR),
]
# testdata pattern is ({document}, {token}, {doc_class}, {scan_info}, {update_scan_info}, {update_class_type})
TEST_UPDATE_DATA = [
    (TEST_DOCUMENT, TEST_TOKEN, DocumentClasses.PPR.value, None, None, True),
    (TEST_DOCUMENT, TEST_TOKEN, DocumentClasses.PPR.value, DOC_SCAN, None, False),
    (TEST_DOCUMENT, TEST_TOKEN, DocumentClasses.PPR.value, None, UPDATE_DOC_SCAN, False),
    (TEST_DOCUMENT, TEST_TOKEN, DocumentClasses.PPR.value, DOC_SCAN, UPDATE_DOC_SCAN, True)
]
# testdata pattern is ({document}, {token}, {filename})
TEST_REPLACE_DATA = [(TEST_DOCUMENT, TEST_TOKEN, TEST_FILENAME)]


@pytest.mark.parametrize("document,token,filename", TEST_REPLACE_DATA)
def test_save_replace(session, document, token, filename):
    """Assert that PUT request resource_utils.save_replace works as expected."""
    doc: Document = copy.deepcopy(document)
    doc.save()
    assert not doc.doc_storage_url
    info: RequestInfo = RequestInfo(RequestTypes.REPLACE.value, None, doc.document_type, None)
    info.account_id = "1234"
    info.consumer_filename = filename
    # info.document_class = doc_class
    raw_data = None
    with open(TEST_DATAFILE, "rb") as data_file:
        raw_data = data_file.read()
        data_file.close()
    result = resource_utils.save_replace(info, doc, token, raw_data)
    assert doc.doc_storage_url
    assert result.get("documentServiceId")
    assert result.get("createDateTime")
    assert result.get("documentType") == doc.document_type
    assert result.get("documentTypeDescription")
    assert result.get("documentClass")
    assert result.get("consumerDocumentId") == doc.consumer_document_id
    assert result.get("consumerIdentifier") == doc.consumer_identifier
    assert result.get("consumerFilename") == filename
    assert result.get("consumerFilingDateTime")
    assert result.get("documentURL")


@pytest.mark.parametrize("document,token,,doc_class,scan_info,update_scan_info,update_class_type", TEST_UPDATE_DATA)
def test_save_update(session, document, token, doc_class, scan_info,  update_scan_info, update_class_type):
    """Assert that patch request resource_utils.save_update works as expected."""
    doc: Document = copy.deepcopy(document)
    doc.save()
    if scan_info:
        scan_doc: DocumentScanning = DocumentScanning.create_from_json(scan_info,
                                                                       UPDATE_DOC.get("consumerDocumentId"),
                                                                       doc_class)
        scan_doc.id = 200000000
        scan_doc.save()
    info: RequestInfo = RequestInfo(RequestTypes.UPDATE.value, None, doc.document_type, None)
    request_data = copy.deepcopy(UPDATE_DOC)
    if not update_class_type:
        del request_data["documentType"]
        del request_data["documentClass"]
    if update_scan_info:
        request_data['scanningInformation'] = update_scan_info
    info.request_data = request_data
    info.account_id = "1234"
    info.document_class = doc_class
    info.consumer_doc_id = request_data.get("consumerDocumentId")
    info.consumer_identifier = request_data.get("consumerIdentifier")
    info.consumer_filename = request_data.get("consumerFilename")
    info.consumer_filedate = request_data.get("consumerFilingDateTime")
    info.description = request_data.get("description")
    result = resource_utils.save_update(info, doc, token)
    assert result.get("documentServiceId")
    assert result.get("createDateTime")
    assert result.get("documentTypeDescription")
    if update_class_type:
        assert result.get("documentType") == request_data.get("documentType")
        assert result.get("documentClass") == request_data.get("documentClass")
    else:
        assert result.get("documentType") == doc.document_type
        assert result.get("documentClass") == doc.document_class
    assert result.get("consumerDocumentId") == request_data.get("consumerDocumentId")
    assert result.get("consumerFilename") == request_data.get("consumerFilename")
    assert result.get("consumerIdentifier") == request_data.get("consumerIdentifier")
    assert result.get("description") == request_data.get("description")
    assert result.get("consumerFilingDateTime") == request_data.get("consumerFilingDateTime")
    assert not result.get("documentURL")
    if scan_info or update_scan_info:
        assert result.get("scanningInformation")
        scan_json = result.get("scanningInformation")
        if not update_scan_info:
            assert scan_json.get("scanDateTime") == scan_info.get("scanDateTime")
            assert scan_json.get("accessionNumber") == scan_info.get("accessionNumber")
            assert scan_json.get("batchId") == scan_info.get("batchId")
            assert scan_json.get("author") == scan_info.get("author")
            assert scan_json.get("pageCount") == scan_info.get("pageCount")
        else:
            assert scan_json.get("scanDateTime") == update_scan_info.get("scanDateTime")
            assert scan_json.get("accessionNumber") == update_scan_info.get("accessionNumber")
            assert scan_json.get("batchId") == update_scan_info.get("batchId")
            assert scan_json.get("author") == update_scan_info.get("author")
            assert scan_json.get("pageCount") == update_scan_info.get("pageCount")
    else:
        assert not result.get("scanningInformation")


@pytest.mark.parametrize("doc_class,start_offset,doc_type,cons_id,no_results", TEST_DATA_DOC_DATES)
def test_get_docs_by_dates(session, doc_class, start_offset, doc_type, cons_id, no_results):
    """Assert that get_docs_by_date_range works as expected."""
    info: RequestInfo = RequestInfo(RequestTypes.GET.value, None, doc_type, None)
    info.account_id = "1234"
    info.document_class = doc_class
    info.consumer_identifier = cons_id
    end = model_utils.now_ts()
    start = model_utils.date_offset(end.date(), start_offset)
    info.query_start_date = start.isoformat()
    info.query_end_date = end.isoformat()
    results = resource_utils.get_docs(info)
    if no_results:
        assert not results
    elif results:
        for result in results:
            assert result.get("documentServiceId")
            assert result.get("createDateTime")
            assert result.get("documentType")
            assert result.get("documentTypeDescription")
            assert result.get("documentClass")
            if doc_type:
                assert result.get("documentType") == doc_type
            if cons_id:
                assert result.get("consumerIdentifier") == cons_id
            assert not result.get("documentURL")


@pytest.mark.parametrize("info,user,doc_id,account_id", TEST_DATA_DOC_REQUEST)
def test_build_doc_request(session, info, user, doc_id, account_id):
    """Assert that building the document request model from the request works as expected."""
    info: RequestInfo = copy.deepcopy(info)
    info.staff = True
    info.account_id = account_id
    doc_request: DocumentRequest = resource_utils.build_doc_request(info, user, doc_id)
    assert doc_request
    assert doc_request.request_ts
    assert doc_request.document_id
    assert doc_request.account_id == account_id
    assert doc_request.document_id == doc_id
    assert doc_request.username == user.username
    assert doc_request.request_data


@pytest.mark.parametrize("req_type,req_path,doc_type,doc_storage_type,staff", TEST_DATA_REQUEST_INFO)
def test_request_info(session, req_type, req_path, doc_type, doc_storage_type, staff):
    """Assert that building the base request info works as expected."""
    info: RequestInfo = RequestInfo(req_type, req_path, doc_type, doc_storage_type)
    assert info.request_type == req_type
    assert info.request_path == req_path
    assert info.document_type == doc_type
    assert info.document_storage_type == doc_storage_type
    info.staff = staff
    info_json = info.json
    assert info_json.get("staff") == staff
    assert info_json.get("documentType") == doc_type
    assert "documentServiceId" in info_json
    assert "accept" in info_json
    assert "contentType" in info_json
    assert "consumerDocumentId" in info_json
    assert "consumerFilename" in info_json
    assert "consumerFilingDate" in info_json
    assert "consumerIdentifier" in info_json


@pytest.mark.parametrize("doc_ts,doc_type,doc_service_id,content_type,doc_storage_type", TEST_DATA_SAVE_STORAGE)
def test_save_doc_storage(session, doc_ts, doc_type, doc_service_id, content_type, doc_storage_type):
    """Assert that uploading a doc to document storage works as expected."""
    doc: Document = Document(
        add_ts=model_utils.ts_from_iso_format(doc_ts), document_type=doc_type, document_service_id=doc_service_id
    )
    info: RequestInfo = RequestInfo("ADD", "/business/CORP/CORP_MISC", doc_type, doc_storage_type)
    info.content_type = content_type
    raw_data = None
    with open(TEST_DATAFILE, "rb") as data_file:
        raw_data = data_file.read()
        data_file.close()
    doc_link = resource_utils.save_to_doc_storage(doc, info, raw_data)
    assert doc_link
    assert doc.doc_storage_url


@pytest.mark.parametrize("doc_class,storage_type", TEST_DATA_STORAGE_TYPES)
def test_get_storage_type(session, doc_class, storage_type):
    """Assert that get_docs_by_date_range works as expected."""
    test_type = resource_utils.get_doc_storage_type(doc_class)
    assert test_type == storage_type

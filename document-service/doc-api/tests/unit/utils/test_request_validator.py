# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Registration non-party validator tests."""
import copy

import pytest
from flask import current_app

from doc_api.models import DocumentScanning
from doc_api.models import utils as model_utils
from doc_api.models.type_tables import DocumentClasses, DocumentTypes, RequestTypes
from doc_api.resources.request_info import RequestInfo
from doc_api.utils import request_validator as validator
from doc_api.utils.logging import logger

# from registry_schemas import utils as schema_utils

REF_ID1 = "01234567890123456789012345678901234567890123456789"
REF_ID2 = "01234567890123456789012345678901234567890123456789X"
TEST_SCAN1 = {
    "scanDateTime": "2024-07-01",
    "accessionNumber": "AN-0001",
    "batchId": "1234",
    "author": "Jane Smith",
    "pageCount": 3
}
TEST_SCAN2 = {"accessionNumber": "AN-0001", "batchId": "1234", "author": "Jane Smith", "pageCount": 3}
TEST_SCAN3 = {
    "scanDateTime": "JUNK",
    "accessionNumber": "AN-0001",
    "batchId": "1234",
    "author": "Jane Smith",
    "pageCount": 3,
}
TEST_SCAN4 = {"pageCount": 1}
TEST_REMOVE = {
    "removed": True
}
DOC_ID_VALID_CHECKSUM = '63166035'
DOC_ID_INVALID_CHECKSUM = '63166034'
TEST_DOC1 = {
    "consumerDocumentId": "T0000001",
    "consumerFilename": "test.pdf",
    "consumerIdentifier": "T0000002",
    "documentType": "TRAN",
    "documentClass": "MHR",
    "consumerFilingDateTime": "2024-07-01T19:00:00+00:00",
    "description": "A meaningful description of the document.",
    "author": "John Smith",
    "consumerReferenceId": "9014001"
}
TEST_DOC_UPDATE1 = {"consumerFilename": "test.pdf"}
TEST_DOC_UPDATE2 = {"consumerFilename": "test-update.pdf"}
TEST_DOC_UPDATE3 = {"consumerIdentifier": "T0000002"}
TEST_DOC_UPDATE4 = {"consumerIdentifier": "UT0000003"}
TEST_DOC_UPDATE5 = {"documentType": "TRAN"}
TEST_DOC_UPDATE6 = {"documentType": "DEAT"}
TEST_DOC_UPDATE7 = {"description": "A meaningful description of the document."}
TEST_DOC_UPDATE8 = {"description": "UPDATED"}
TEST_DOC_UPDATE9 = {"author": "John Smith"}
TEST_DOC_UPDATE10 = {"author": "John David Smith"}

# test data pattern is ({description}, {valid}, {payload}, {new}, {cons_doc_id}, {doc_class}, {message_content})
TEST_DATA_SCANNING = [
    ("Valid new", True, TEST_SCAN1, True, "UT000001", DocumentClasses.CORP, None),
    ("Valid new minimal", True, TEST_SCAN4, True, "UT000001", DocumentClasses.CORP, None),
    ("Valid update", True, TEST_SCAN1, False, "UT000001", DocumentClasses.CORP, None),
    ("Valid update no date", True, TEST_SCAN2, False, "UT000001", DocumentClasses.CORP, None),
    ("Valid new no scan date", True, TEST_SCAN2, True, "UT000001", DocumentClasses.CORP, None),
    ("Invalid new no payload", False, None, True, "UT000001", DocumentClasses.CORP, validator.MISSING_SCAN_PAYLOAD),
    ("Invalid new no class", False, TEST_SCAN1, True, "UT000001", None, validator.MISSING_DOC_CLASS),
    ("Invalid new class", False, TEST_SCAN1, True, "UT000001", "JUNK", validator.INVALID_DOC_CLASS),
    ("Invalid new no doc id", False, TEST_SCAN1, True, None, DocumentClasses.CORP, validator.MISSING_SCAN_DOCUMENT_ID),
    ("Invalid new page count", False, TEST_SCAN1, True, "UT000001", DocumentClasses.CORP, validator.INVALID_PAGE_COUNT),
    ("Invalid update no payload", False, None, False, "UT000001", DocumentClasses.CORP, validator.MISSING_SCAN_PAYLOAD),
    ("Invalid update no class", False, TEST_SCAN1, False, "UT000001", None, validator.MISSING_DOC_CLASS),
    ("Invalid update class", False, TEST_SCAN1, False, "UT000001", "JUNK", validator.INVALID_DOC_CLASS),
    (
        "Invalid update no doc id",
        False,
        TEST_SCAN1,
        False,
        None,
        DocumentClasses.CORP,
        validator.MISSING_SCAN_DOCUMENT_ID,
    ),
    ("Invalid new exists", False, TEST_SCAN1, True, "UT000001", DocumentClasses.CORP, validator.INVALID_SCAN_EXISTS),
]
# test data pattern is ({description}, {valid}, {req_type}, {doc_type}, {content_type}, {doc_class}, {ref_id}, {message_content})
TEST_DATA_ADD = [
    (
        "Valid",
        True,
        RequestTypes.ADD,
        DocumentTypes.CORR,
        model_utils.CONTENT_TYPE_PDF,
        DocumentClasses.CORP,
        REF_ID1,
        None,
    ),
    (
        "Invalid missing doc type",
        False,
        RequestTypes.ADD,
        None,
        model_utils.CONTENT_TYPE_PDF,
        DocumentClasses.CORP,
        None,
        validator.MISSING_DOC_TYPE,
    ),
    (
        "Invalid doc type",
        False,
        RequestTypes.ADD,
        "JUNK",
        model_utils.CONTENT_TYPE_PDF,
        DocumentClasses.CORP,
        None,
        validator.INVALID_DOC_TYPE,
    ),
    (
        "Invalid doc class",
        False,
        RequestTypes.ADD,
        DocumentTypes.CORR,
        model_utils.CONTENT_TYPE_PDF,
        "JUNK",
        None,
        validator.INVALID_DOC_CLASS,
    ),
    (
        "Invalid missing content",
        False,
        RequestTypes.ADD,
        DocumentTypes.CORR,
        None,
        DocumentClasses.CORP,
        None,
        validator.MISSING_CONTENT_TYPE,
    ),
    (
        "Invalid content",
        False,
        RequestTypes.ADD,
        DocumentTypes.CORR,
        "XXXXX",
        DocumentClasses.CORP,
        None,
        validator.INVALID_CONTENT_TYPE,
    ),
    (
        "Invalid doc class - type",
        False,
        RequestTypes.ADD,
        DocumentTypes.TRAN,
        model_utils.CONTENT_TYPE_PDF,
        DocumentClasses.FIRM,
        None,
        validator.INVALID_DOC_CLASS_TYPE,
    ),
    (
        "Invalid consumer reference id",
        False,
        RequestTypes.ADD,
        DocumentTypes.CORR,
        model_utils.CONTENT_TYPE_PDF,
        DocumentClasses.CORP,
        REF_ID2,
        validator.INVALID_REFERENCE_ID,
    ),
    ("Valid no class", True, RequestTypes.ADD, DocumentTypes.TRAN, model_utils.CONTENT_TYPE_PDF, None, None, None),
]
# test data pattern is ({description}, {valid}, {filing_date}, {message_content})
TEST_DATA_ADD_DATES = [
    ("Valid no dates", True, None, None),
    ("Valid filing date", True, "2024-07-31", None),
    ("Invalid filing date", False, "January 12, 2022", validator.INVALID_FILING_DATE),
]
# test data pattern is ({description}, {valid}, {doc_class}, {doc_service_id},
# {doc_id}, {cons_id}, {start}, {end}, {message_content})
TEST_DATA_GET = [
    ("Valid service id", True, DocumentClasses.CORP, "1234", None, None, None, None, None),
    ("Valid doc id", True, DocumentClasses.CORP, None, "1234", None, None, None, None),
    ("Valid consumer id", True, DocumentClasses.CORP, None, None, "1234", None, None, None),
    ("Valid query dates", True, DocumentClasses.CORP, None, None, None, "2024-07-01", "2024-07-01", None),
    ("Invalid doc class", False, "XXXX", None, None, None, None, None, validator.INVALID_DOC_CLASS),
    ("Missing doc class", False, None, "1234", None, None, None, None, validator.MISSING_DOC_CLASS),
    ("Missing params", False, DocumentClasses.CORP, None, None, None, None, None, validator.MISSING_QUERY_PARAMS),
    (
        "Invalid query dates",
        False,
        DocumentClasses.CORP,
        None,
        None,
        None,
        "2024-07-01",
        None,
        validator.MISSING_DATE_PARAM,
    ),
    (
        "Invalid query dates",
        False,
        DocumentClasses.CORP,
        None,
        None,
        None,
        None,
        "2024-07-01",
        validator.MISSING_DATE_PARAM,
    ),
]
# test data pattern is ({description}, {valid}, {start_date}, {end_date}, {message_content})
TEST_DATA_SEARCH_DATES = [
    ("Valid no dates", True, None, None, None),
    ("Valid date range", True, "2024-07-31", "2024-07-31", None),
    ("Invalid date range", False, "2024-07-31", "2024-07-30", validator.INVALID_START_END_DATE),
    ("Invalid start date", False, "January 12, 2022", None, validator.INVALID_START_DATE),
    ("Invalid end date", False, None, "January 12, 2022", validator.INVALID_END_DATE),
]
# test data pattern is ({description},{valid},{doc_type},{cons_id},{filename},{filing_date},{desc},{ref_id},{message_content})
TEST_DATA_PATCH = [
    ("Valid doc type", True, "DEAT", None, None, None, None, REF_ID1, None),
    ("Valid removed", True, None, None, None, None, None, None, None),
    ("Valid consumer id", True, None, "BC0700000", None, None, None, None, None),
    ("Valid filename", True, None, None, "change_address.pdf", None, None, None, None),
    ("Valid filing date", True, None, None, None, "2024-07-31", None, None, None),
    ("Valid description", True, None, None, None, None, "Important description", None, None),
    ("Valid scanning change", True, None, None, None, None, None, None, None),
    ("Invalid no change", False, None, None, None, None, None, None, validator.MISSING_PATCH_PARAMS),
    ("Invalid no change scanning", False, None, None, None, None, None, None, validator.MISSING_PATCH_PARAMS),
    ("Invalid filing date", False, None, None, None, "January 12, 2022", None, None, validator.INVALID_FILING_DATE),
    ("Invalid ref id", False, None, None, None, None, None, REF_ID2, validator.INVALID_REFERENCE_ID),
    ("Invalid doc type", False, "ADDR", None, None, None, None, None,
     validator.INVALID_DOC_CLASS_TYPE.format(doc_type="ADDR", doc_class="MHR")),
]
# test data pattern is ({description}, {valid}, {payload}, {doc_type}, {content_type}, {doc_class}, {message_content})
TEST_DATA_REPLACE = [
    ("Valid", True, True, DocumentTypes.CORR, model_utils.CONTENT_TYPE_PDF, DocumentClasses.CORP, None),
    (
        "Invalid missing content",
        False,
        True,
        DocumentTypes.CORR,
        None,
        DocumentClasses.CORP,
        validator.MISSING_CONTENT_TYPE,
    ),
    (
        "Invalid content",
        False,
        True,
        DocumentTypes.CORR,
        "*/*",
        DocumentClasses.CORP,
        validator.INVALID_CONTENT_TYPE,
    ),
    (
        "Missing payload",
        False,
        False,
        DocumentTypes.CORR,
        model_utils.CONTENT_TYPE_PDF,
        DocumentClasses.FIRM,
        validator.MISSING_PAYLOAD,
    ),
]
# test data pattern is ({description}, {valid}, {doc_id})
TEST_DATA_DOC_ID_CHECKSUM = [
    ("Valid doc id", True, DOC_ID_VALID_CHECKSUM),
    ("Invalid doc id", False, DOC_ID_INVALID_CHECKSUM),
    ("Valid doc id skip", True, "0100000204")
]
# test data pattern is ({description}, {valid}, {prod_code}, {entity_id}, {event_id}, {rtype}, {name}, {fdate}, {message_content})
TEST_DATA_REPORT_CREATE = [
    ("Valid", True, None, "123455", "1234234", "FILING", "name.pdf", "2024-09-01T19:00:00+00:00", None),
    ("Valid product", True, "BUSINESS", "123455", "1234234", "FILING", "name.pdf", "2024-09-01T19:00:00+00:00", None),
    ("Invalid product", False, "XXX", "123455", "1234234", "FILING", "name.pdf", "2024-09-01T19:00:00+00:00",
     validator.INVALID_PRODUCT_CODE.format(product_code="XXX")),
    ("Invalid entity id", False, None, "1", "1234234", "FILING", "name.pdf", "2024-09-01T19:00:00+00:00",
     validator.INVALID_ENTITY_ID.format(entity_id="1")),
    ("Invalid event id", False, None, "12345", "junk", "FILING", "name.pdf", "2024-09-01T19:00:00+00:00",
     validator.INVALID_EVENT_ID.format(event_id="junk")),
    ("Invalid report type", False, None, "12345", "12345", "F", "name.pdf", "2024-09-01T19:00:00+00:00",
     validator.INVALID_REPORT_TYPE.format(report_type="F")),
    ("Invalid name", False, None, "12345", "12345", "FILING", ".pdf", "2024-09-01T19:00:00+00:00",
     validator.INVALID_FILENAME.format(filename=".pdf")),
    ("Invalid date", False, None, "12345", "12345", "FILING", "name.pdf", "January 1, 2010",
     validator.INVALID_FILING_DATE.format(param_date="January 1, 2010")),
]
# test data pattern is ({description}, {valid}, {rtype}, {name}, {fdate}, {message_content})
TEST_DATA_REPORT_UPDATE = [
    ("Valid", True, "FILING", "name.pdf", "2024-09-01T19:00:00+00:00", None),
    ("Invalid missing update", False, None, None, None, validator.INVALID_REPORT_UPDATE),
    ("Invalid missing update empty", False, "", "", "", validator.INVALID_REPORT_UPDATE),
    ("Invalid report type", False, "F", "name.pdf", "2024-09-01T19:00:00+00:00",
     validator.INVALID_REPORT_TYPE.format(report_type="F")),
    ("Invalid name", False, "FILING", ".pdf", "2024-09-01T19:00:00+00:00",
     validator.INVALID_FILENAME.format(filename=".pdf")),
    ("Invalid date", False, "FILING", "name.pdf", "January 1, 2010",
     validator.INVALID_FILING_DATE.format(param_date="January 1, 2010")),
]
# test data pattern is ({description}, {valid}, {doc_type}, {message_content})
TEST_DATA_DOC_TYPE = [
    ("Valid", True, "TRAN", None),
    ("Valid", True, "FNCH", None),
    ("Invalid", False, "MHR_MISC", validator.INVALID_DOC_TYPE),
    ("Inactive", False, "CLW", validator.INACTIVE_DOC_TYPE),
    ("Inactive", False, "DAT", validator.INACTIVE_DOC_TYPE),
    ("Inactive", False, "PRE", validator.INACTIVE_DOC_TYPE),
    ("Inactive", False, "MEM", validator.INACTIVE_DOC_TYPE),
    ("Inactive", False, "MHSP", validator.INACTIVE_DOC_TYPE),
]
# test data pattern is ({description}, {valid}, {doc_type}, {doc_class}, {message_content})
TEST_DATA_DOC_CLASS_TYPE = [
    ("Valid", True, "TRAN", "MHR", None),
    ("Invalid", False, "TRAN", "CORP", validator.INVALID_DOC_CLASS_TYPE),
    ("Invalid", False, "FNCH", "MHR", validator.INVALID_DOC_CLASS_TYPE),
    ("Invalid", False, "MEM", "MHR", validator.INVALID_DOC_CLASS_TYPE),
    ("Invalid", False, "DAT", "MHR", validator.INVALID_DOC_CLASS_TYPE),
    ("Invalid", False, "PRE", "MHR", validator.INVALID_DOC_CLASS_TYPE),
    ("Inactive", False, "CLW", "MHR", validator.INACTIVE_DOC_CLASS_TYPE),
    ("Inactive", False, "MHSP", "MHR", validator.INACTIVE_DOC_CLASS_TYPE),
    ("Inactive", False, "MEM", "PPR", validator.INACTIVE_DOC_CLASS_TYPE),
    ("Inactive", False, "DAT", "PPR", validator.INACTIVE_DOC_CLASS_TYPE),
    ("Inactive", False, "PRE", "CORP", validator.INACTIVE_DOC_CLASS_TYPE),
]
# test data pattern is ({description},{modified},{existing},{update})
TEST_DATA_SCAN_MODIFIED = [
    ("No info", False, None, None),
    ("No update", False, TEST_SCAN1, None),
    ("No existing", False, None, TEST_SCAN1),
    ("No change", False, TEST_SCAN1, TEST_SCAN1),
    ("Update accessionNumber", True, TEST_SCAN1, TEST_SCAN1),
    ("Update scanDateTime", True, TEST_SCAN1, TEST_SCAN1),
    ("Update batchId", True, TEST_SCAN1, TEST_SCAN1),
    ("Update author", True, TEST_SCAN1, TEST_SCAN1),
    ("Update pageCount", True, TEST_SCAN1, TEST_SCAN1),
]
# test data pattern is ({description},{modified},{existing},{update})
TEST_DATA_DOC_MODIFIED = [
    ("No update", False, TEST_DOC1, {}),
    ("No change", False, TEST_DOC1, TEST_DOC1),
    ("Filename no change", False, TEST_DOC1, TEST_DOC_UPDATE1),
    ("Filename change", True, TEST_DOC1, TEST_DOC_UPDATE2),
    ("Entity ID no change", False, TEST_DOC1, TEST_DOC_UPDATE3),
    ("Entity ID change", True, TEST_DOC1, TEST_DOC_UPDATE4),
    ("Doc type no change", False, TEST_DOC1, TEST_DOC_UPDATE5),
    ("Doc type change", True, TEST_DOC1, TEST_DOC_UPDATE6),
    ("Description no change", False, TEST_DOC1, TEST_DOC_UPDATE7),
    ("Description change", True, TEST_DOC1, TEST_DOC_UPDATE8),
    ("Author no change", False, TEST_DOC1, TEST_DOC_UPDATE9),
    ("Author change", True, TEST_DOC1, TEST_DOC_UPDATE10),
]


@pytest.mark.parametrize("desc,modified,existing,update", TEST_DATA_DOC_MODIFIED)
def test_validate_doc_modified(session, desc, modified, existing, update):
    """Assert that document record modified check works as expected."""
    info: RequestInfo = RequestInfo("UPDATE", None, existing.get("documentType"), None)
    info.document_class = existing.get("documentClass")
    if update:
        info.request_data = copy.deepcopy(update)
        info.consumer_doc_id = update.get("consumerDocumentId")
        info.consumer_filename = update.get("consumerFilename")
        info.consumer_filedate = update.get("consumerFilingDateTime")
        info.consumer_identifier = update.get("consumerIdentifer")
        info.consumer_reference_id = update.get("consumerReferenceId")
        info.description = update.get("description")
    else:
        info.request_data = {}
    if existing:
        info.request_data["existingDocument"] = copy.deepcopy(existing)
    test_modified = validator.is_document_modified(info)
    assert test_modified == modified


@pytest.mark.parametrize("desc,modified,existing,update", TEST_DATA_SCAN_MODIFIED)
def test_validate_scan_modified(session, desc, modified, existing, update):
    """Assert that the scanning record update check works as expected."""
    info: RequestInfo = RequestInfo(None, None, None, None)
    info.request_data = {}
    if existing:
        existing_doc = {
            "scanningInformation": copy.deepcopy(existing)
        }
        info.request_data["existingDocument"] = existing_doc
    if update:
        test_json = copy.deepcopy(update)
        if desc == "Update accessionNumber":
            test_json["accessionNumber"] = "TEST-12343"
        elif desc == "Update scanDateTime":
            test_json["scanDateTime"] = "2025-10-10"
        if desc == "Update batchId":
            test_json["batchId"] = "TEST1234"
        if desc == "Update author":
            test_json["author"] = "NEW TEST AUTHOR"
        if desc == "Update pageCount":
            test_json["pageCount"] = 91
        info.request_data["scanningInformation"] = test_json
    test_modified = validator.is_scanning_modified(info)
    assert test_modified == modified


@pytest.mark.parametrize("desc,valid,doc_type,doc_class,message_content", TEST_DATA_DOC_CLASS_TYPE)
def test_validate_doc_type_class(session, desc, valid, doc_type, doc_class, message_content):
    """Assert that document type validation validation works as expected."""
    info: RequestInfo = RequestInfo(None, None, doc_type, None)
    info.document_class = doc_class
    msg: str = validator.validate_class_type(info)
    if valid:
        assert not msg
    else:
        test_msg = message_content.format(doc_type=doc_type, doc_class=doc_class)
        assert test_msg == msg


@pytest.mark.parametrize("desc,valid,doc_type,message_content", TEST_DATA_DOC_TYPE)
def test_validate_doc_type(session, desc, valid, doc_type, message_content):
    """Assert that document type validation validation works as expected."""
    info: RequestInfo = RequestInfo(None, None, doc_type, None)
    msg: str = validator.validate_doc_type(info)
    if valid:
        assert not msg
    else:
        test_msg = message_content.format(doc_type=doc_type)
        assert test_msg == msg


@pytest.mark.parametrize("desc,valid,prod_code,entity_id,event_id,rtype,name,fdate,message_content", TEST_DATA_REPORT_CREATE)
def test_validate_report_create(session, desc, valid, prod_code, entity_id, event_id, rtype, name, fdate, message_content):
    """Assert that create report request validation works as expected."""
    # setup
    request_json = {
    }
    if prod_code:
        request_json["productCode"] = prod_code
    if entity_id:
        request_json["entityIdentifier"] = entity_id
    if event_id:
        request_json["requestEventIdentifier"] = event_id
    if rtype:
        request_json["reportType"] = rtype
    if name:
        request_json["name"] = name
    if fdate:
        request_json["datePublished"] = fdate
    error_msg = validator.validate_report_request(request_json, True)
    if valid:
        assert error_msg == ""
        assert request_json.get("eventIdentifier")
    else:
        assert error_msg != ""
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize("desc,valid,rtype,name,fdate,message_content", TEST_DATA_REPORT_UPDATE)
def test_validate_report_update(session, desc, valid, rtype, name, fdate, message_content):
    """Assert that the update report request validation works as expected."""
    # setup
    request_json = {

    }
    if rtype:
        request_json["reportType"] = rtype
    if name:
        request_json["name"] = name
    if fdate:
        request_json["datePublished"] = fdate
    error_msg = validator.validate_report_request(request_json, False)
    if valid:
        assert error_msg == ""
    else:
        assert error_msg != ""
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize("desc,valid,start_date,end_date,message_content", TEST_DATA_SEARCH_DATES)
def test_validate_search_dates(session, desc, valid, start_date, end_date, message_content):
    """Assert that new get request validation works as expected for scan and file dates."""
    # setup
    info: RequestInfo = RequestInfo(RequestTypes.GET, "NA", None, "NA")
    info.account_id = "NA"
    info.document_class = DocumentClasses.CORP
    if start_date:
        info.query_start_date = start_date
    if end_date:
        info.query_end_date = end_date
    if desc == "Valid no dates":
        info.document_service_id = "12343"

    error_msg = validator.validate_request(info)

    if valid:
        assert error_msg == ""
    else:
        assert error_msg != ""
        if message_content:
            err_msg: str = message_content
            if desc == "Invalid date range":
                err_msg = validator.INVALID_START_END_DATE.format(start_date=start_date, end_date=end_date)
            elif desc == "Invalid start date":
                err_msg = validator.INVALID_START_DATE.format(param_date=start_date)
            elif desc == "Invalid end date":
                err_msg = validator.INVALID_END_DATE.format(param_date=end_date)
            assert error_msg.find(err_msg) != -1


@pytest.mark.parametrize("desc,valid,filing_date,message_content", TEST_DATA_ADD_DATES)
def test_validate_add_dates(session, desc, valid, filing_date, message_content):
    """Assert that new add request validation works as expected for scan and file dates."""
    # setup
    info: RequestInfo = RequestInfo(RequestTypes.ADD, "NA", DocumentTypes.CORR, "NA")
    info.content_type = model_utils.CONTENT_TYPE_PDF
    info.account_id = "NA"
    info.document_class = DocumentClasses.CORP
    if filing_date:
        info.consumer_filedate = filing_date
    error_msg = validator.validate_request(info)
    if valid:
        assert error_msg == ""
    else:
        assert error_msg != ""
        if message_content:
            err_msg: str = message_content
            if desc == "Invalid filing date":
                err_msg = validator.INVALID_FILING_DATE.format(param_date=filing_date)
            assert error_msg.find(err_msg) != -1


@pytest.mark.parametrize("desc,valid,doc_class,service_id,doc_id,cons_id,start,end,message_content", TEST_DATA_GET)
def test_validate_get(session, desc, valid, doc_class, service_id, doc_id, cons_id, start, end, message_content):
    """Assert that get documents request validation works as expected."""
    # setup
    info: RequestInfo = RequestInfo(RequestTypes.GET.value, "NA", None, "NA")
    info.account_id = "NA"
    if doc_class:
        info.document_class = doc_class
    if service_id:
        info.document_service_id = service_id
    if doc_id:
        info.consumer_doc_id = doc_id
    if cons_id:
        info.consumer_identifier = cons_id
    if start:
        info.query_start_date = start
    if end:
        info.query_end_date = end

    error_msg = validator.validate_request(info)
    if valid:
        assert error_msg == ""
    else:
        assert error_msg != ""
        if message_content:
            err_msg: str = message_content
            if desc == "Invalid doc class":
                err_msg = validator.INVALID_DOC_CLASS.format(doc_class=doc_class)
            assert error_msg.find(err_msg) != -1


@pytest.mark.parametrize("desc,valid,req_type,doc_type,content_type,doc_class,ref_id,message_content", TEST_DATA_ADD)
def test_validate_add(session, desc, valid, req_type, doc_type, content_type, doc_class, ref_id, message_content):
    """Assert that new add request validation works as expected."""
    # setup
    info: RequestInfo = RequestInfo(req_type, "NA", doc_type, "NA")
    info.content_type = content_type
    info.account_id = "NA"
    if doc_class:
        info.document_class = doc_class
    if ref_id:
        info.consumer_reference_id = ref_id
    error_msg = validator.validate_request(info)
    if doc_type and not doc_class and not message_content:
        assert info.document_class
        if doc_type == DocumentTypes.TRAN.value:
            assert info.document_class == DocumentClasses.MHR.value
    if valid:
        assert error_msg == ""
    else:
        assert error_msg != ""
        if message_content:
            err_msg: str = message_content
            if desc == "Invalid doc type":
                err_msg = validator.INVALID_DOC_TYPE.format(doc_type=doc_type)
            elif desc == "Invalid doc class":
                err_msg = validator.INVALID_DOC_CLASS.format(doc_class=doc_class)
            elif desc == "Invalid content":
                err_msg = validator.INVALID_CONTENT_TYPE.format(content_type=content_type)
            elif desc == "Invalid doc class - type":
                err_msg = validator.INVALID_DOC_CLASS_TYPE.format(doc_class=doc_class, doc_type=doc_type)
            assert error_msg.find(err_msg) != -1


@pytest.mark.parametrize("desc,valid,doc_type,cons_id,filename,filing_date,description,ref_id,message_content", TEST_DATA_PATCH)
def test_validate_patch(session, desc, valid, doc_type, cons_id, filename, filing_date, description, ref_id, message_content):
    """Assert that patch request validation works as expected."""
    # setup
    info: RequestInfo = RequestInfo(RequestTypes.UPDATE, "NA", TEST_DOC1.get("documentType"), "NA")
    info.content_type = model_utils.CONTENT_TYPE_PDF
    info.account_id = "NA"
    info.document_class = TEST_DOC1.get("documentClass")
    if desc == "Valid removed":
        info.request_data = TEST_REMOVE
    else:
        info.request_data = {}
    info.request_data["existingDocument"] = copy.deepcopy(TEST_DOC1)
    if desc in ("Valid scanning change", "Invalid no change scanning"):
        info.request_data["existingDocument"]["scanningInformation"] = copy.deepcopy(TEST_SCAN1)
        info.request_data["scanningInformation"] = copy.deepcopy(TEST_SCAN1)
        if desc == "Valid scanning change":
            info.request_data["scanningInformation"]["pageCount"] = 1
    if doc_type:
        info.document_type = doc_type
        info.request_data["documentType"] = doc_type
    if cons_id:
        info.consumer_identifier = cons_id
        info.request_data["consumerIdentifier"] = cons_id
    if filename:
        info.consumer_filename = filename
        info.request_data["consumerFilename"] = filename
    if filing_date:
        info.consumer_filedate = filing_date
        info.request_data["consumerFilingDateTime"] = filing_date
    if description:
        info.description = description
        info.request_data["description"] = description
    if ref_id:
        info.consumer_reference_id = ref_id
        info.request_data["consumerReferenceId"] = ref_id

    error_msg = validator.validate_request(info)
    if valid:
        assert error_msg == ""
    else:
        assert error_msg != ""
        if message_content:
            err_msg: str = message_content
            if desc == "Invalid filing date":
                err_msg = validator.INVALID_FILING_DATE.format(param_date=filing_date)
            assert error_msg.find(err_msg) != -1


@pytest.mark.parametrize("desc,valid,has_payload,doc_type,content_type,doc_class,message_content", TEST_DATA_REPLACE)
def test_validate_replace(session, desc, valid, has_payload, doc_type, content_type, doc_class, message_content):
    """Assert that new put add/replace document request validation works as expected."""
    # setup
    info: RequestInfo = RequestInfo(RequestTypes.REPLACE, "NA", doc_type, "NA")
    info.content_type = content_type
    info.account_id = "NA"
    info.has_payload = has_payload
    info.document_class = doc_class
    error_msg = validator.validate_request(info)
    if doc_type and not doc_class and not message_content:
        assert info.document_class
        if doc_type == DocumentTypes.CORR:
            assert info.document_class == DocumentClasses.CORP.value
    if valid:
        assert error_msg == ""
    else:
        assert error_msg != ""
        if message_content:
            err_msg: str = message_content
            if desc == "Invalid content":
                err_msg = validator.INVALID_CONTENT_TYPE.format(content_type=content_type)
            assert error_msg.find(err_msg) != -1


@pytest.mark.parametrize("desc,valid,payload,is_new,cons_doc_id,doc_class,message_content", TEST_DATA_SCANNING)
def test_validate_scanning(session, desc, valid, payload, is_new, cons_doc_id, doc_class, message_content):
    """Assert that document scanning validation works as expected."""
    scan_json = None
    if payload:
        scan_json = copy.deepcopy(payload)
        if cons_doc_id:
            scan_json["consumerDocumentId"] = cons_doc_id
        if doc_class:
            scan_json["documentClass"] = doc_class
    if desc == "Invalid new exists":
        doc_scan: DocumentScanning = DocumentScanning.create_from_json(scan_json, cons_doc_id, doc_class)
        doc_scan.id = 200000000
        doc_scan.save()
    elif desc == "Invalid new page count":
        scan_json["pageCount"] = 0
    error_msg = validator.validate_scanning(scan_json, is_new)
    if valid:
        assert error_msg == ""
    else:
        assert error_msg != ""
        if message_content:
            err_msg: str = message_content
            if desc in ("Invalid new class", "Invalid update class"):
                err_msg = validator.INVALID_DOC_CLASS.format(doc_class=doc_class)
            elif is_new and desc == "Invalid new exists":
                err_msg = validator.INVALID_SCAN_EXISTS.format(doc_class=doc_class, cons_doc_id=cons_doc_id)
            assert error_msg.find(err_msg) != -1


@pytest.mark.parametrize("desc,valid,doc_id", TEST_DATA_DOC_ID_CHECKSUM)
def test_doc_id_checksum(session, desc, valid, doc_id):
    """Assert that the check digit algorithm doc id validation works as expected."""
    result = validator.checksum_valid(doc_id)
    assert valid == result

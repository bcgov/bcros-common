# Copyright © 2025 Province of British Columbia
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
"""This module executes all the job steps."""
import copy
import sys
from http import HTTPStatus

import psycopg2
import pymupdf
import requests
from bs4 import BeautifulSoup

from colin_report_migration.config import Config
from colin_report_migration.database import Database
from colin_report_migration.services.document_storage.storage_service import GoogleStorageService
from colin_report_migration.services.utils.exceptions import ScrapingException
from colin_report_migration.utils.logging import logger

REPORT_TYPE_CERT = "cert"
REPORT_TYPE_FILING = "filing"
REPORT_TYPE_NOA = "noa"
REPORT_TYPE_RECEIPT = "receipt"
STORAGE_DOC_NAME = "{report_date}/{corp_num}-{event_id}-{report_type}.pdf"
REPORT_PATH = "/reprint/report.do?action={report_type}Report&check_token=no&historyIndex={filing_index}"
HIST_REPORT_PATH = "/search/report.do?action={report_type}Report&check_token=no&historyIndex={filing_index}"
HIST_REPORT_PATH1 = "/search/report.do?action={report_type}Report&amp;check_token=no&amp;historyIndex={filing_index}"
SCRAPING_MENU_PATH = "/accesstransaction/menu.do?action=overview&filingTypeCode=RPRNT&from=main"
SCRAPING_OVERVIEW_PATH = "/accesstransaction/menu.do"
SCRAPING_SEARCH_PATH = "/identcorp/searchCorp.do"
SCRAPING_HEADERS_MENU = {"Connection": "keep-alive", "Content-Type": "text/plain; charset=ISO-8859-1"}
SCRAPING_OVERVIEW_DATA = {"formType": "overview", "navigationAction": "next", "nextButton.x": 28, "nextButton.y": 13}
SCRAPING_SEARCH_DATA = {
    "defaultAction": "next",
    "formType": "search",
    "corpNum": "",
    "password": "",
    "navigationAction": "next",
    "nextButton.x": 27,
    "nextButton.y": 7,
}
SCRAPING_SEARCH_HIST_DATA = {
    "_flowExecutionKey": "e1s1",
    "basicSearch": True,
    "individualSearch": False,
    "clientLettersSearch": False,
    "incorporationNumber": "",
    "basicStateType": "ACT",
    "basicCorporationTypes": "CFS",
    "advancedStateType": "ACT",
    "advancedCorporationTypes": "CFS",
    "findResults": "ALL",
    "_csrf": "",
}
HIST_PATH1 = (
    "/int/logon.cgi?flags=1000:1,0&TYPE=33554433&REALMOID=06-43462114-ead0-4da9-9bec-83e62afcabcd&GUID="
    + "&SMAUTHREASON=0&METHOD=GET&TARGET="
    + "https%3a%2f%2fwww%2ebcregistryallservices%2egov%2ebc%2eca%2fsofi%2flogin%2flogin%2ehtm"
)
HIST_PATH2 = "/preLogon.cgi"
HIST_PATH3 = "/int01/logon.fcc"
HIST_PATH4 = "/int01/private/postLogon.cgi"
SOFI_LOGIN_PATH = "/login/login.htm"
SOFI_START_PATH = "/sofi.htm?_flowId=search&_flowExecutionKey=e1s1"
HIST_SEARCH_PATH = "/login/search/searchAction.do?corpNum={corp_num}&_flowExecutionKey=e1s1"


def get_storage_name(filing_date: str, corp_num: str, event_id: int, report_type: str) -> str:
    """Get doc storage name for a legacy document record."""
    report_date: str = filing_date[:10].replace("-", "/")
    storage_name = STORAGE_DOC_NAME.format(
        report_date=report_date, corp_num=corp_num, event_id=event_id, report_type=report_type
    )
    return storage_name


def setup_historical(config: Config):
    """
    For companies in a historical state, set up the colin session before getting a company ledger history
    using SOFI searching.

    Args:
        config: Job configuration containing environment variables.
    """
    if not config.HIST_LOGIN_URL or not config.HIST_ID or not config.HIST_PASS or not config.SOFI_URL:
        logger.error("Status HIS but setup_historical not configured correctly: aborting.")
        return None
    url = config.HIST_LOGIN_URL + HIST_PATH1
    step: str = "Historical Logon 1 GET"
    try:
        session = requests.Session()
        response = session.get(url, timeout=(2, 10))
        if not response.ok:
            logger.error(f"setup_historical {step} error")
            raise ScrapingException(f"Scraping setup_historical {step} failed for url={url}.")
        step = "Historical Logon 2 POST"
        url = config.HIST_LOGIN_URL + HIST_PATH2
        payload = {"instance": "instance_int", "user": config.HIST_ID, "password": config.HIST_PASS}
        response = session.post(url, data=payload, timeout=(2, 10))
        if not response.ok:
            logger.error(f"setup_historical {step} error")
            raise ScrapingException(f"Scraping setup_historical {step} failed for url={url}.")
        step = "Historical Logon 3 POST"
        url = config.HIST_LOGIN_URL + HIST_PATH3
        payload = {
            "SMENC": "ISO-8859-1",
            "SMLOCALE": "US-EN",
            "target": "/clp-cgi/int01/private/postLogon.cgi",
            "smauthreason": "0",
            "smagentname": None,
            "user": config.HIST_ID,
            "password": config.HIST_PASS,
        }
        response = session.post(url, data=payload, timeout=(2, 10))
        if not response.ok:
            logger.error(f"setup_historical {step} error")
            raise ScrapingException(f"Scraping setup_historical {step} failed for url={url}.")
        step = "Historical Logon 4 GET"
        url = config.HIST_LOGIN_URL + HIST_PATH4
        response = session.get(url, timeout=(2, 10))
        if not response.ok:
            logger.error(f"setup_historical {step} error")
            raise ScrapingException(f"Scraping setup_historical {step} failed for url={url}.")
        step = "Historical SOFI login GET"
        url = config.SOFI_URL + SOFI_LOGIN_PATH
        response = session.get(url, timeout=(2, 10))
        if not response.ok:
            logger.error(f"setup_historical {step} error")
            raise ScrapingException(f"Scraping setup_historical {step} failed for url={url}.")
        # print(session.cookies.get_dict())
        return session
    except ScrapingException:
        raise
    except Exception as err:
        raise ScrapingException(f"Scraping setup_historical failed for step {step}. {err}") from err


def get_corp_filings_page(corp_num: str, corp_password: str, colin_url: str) -> dict:
    """COLIN UI screen scraping to retrieve filing history by corp num and password."""
    menu_url = colin_url + SCRAPING_MENU_PATH
    overview_url = colin_url + SCRAPING_OVERVIEW_PATH
    search_url = colin_url + SCRAPING_SEARCH_PATH
    step: str = "menu"
    try:
        response = requests.get(menu_url, headers=SCRAPING_HEADERS_MENU, timeout=(2, 10))
        if response.status_code != 200:
            logger.info("menu error")
            raise ScrapingException(f"Scraping get menu failed for url={menu_url}.")
        cookie: str = response.cookies["JSESSIONID"]
        cookies = {"JSESSIONID": cookie}
        step = "overview"
        response = requests.post(overview_url, data=SCRAPING_OVERVIEW_DATA, cookies=cookies, timeout=(2, 10))
        if response.status_code != 200:
            logger.info("overview error")
            raise ScrapingException(f"Scraping get overview failed for url={overview_url}.")
        search_data = copy.deepcopy(SCRAPING_SEARCH_DATA)
        search_data["corpNum"] = corp_num
        search_data["password"] = corp_password
        step = "search"
        response = requests.post(search_url, data=search_data, cookies=cookies, timeout=(2, 10))
        if response.status_code != 200:
            raise ScrapingException(f"Scraping get search failed for url={search_url}.")
        page_text = response.text
        filing_info: dict = {"colin_url": colin_url, "filings_page": page_text, "cookies": cookies}
        filing_info["no_reports"] = page_text.find("check_token=no&historyIndex=") < 1
        filing_info["active"] = True
        # logger.info(f"get_corp_filings_page length={len(response.text)}")
        return filing_info
    except ScrapingException:
        raise
    except Exception as err:
        raise ScrapingException(f"Scraping failed for step {step} corp num={corp_num}. {err}") from err


def get_corp_hist_filings_page(session, corp_num: str, colin_url: str, sofi_url: str) -> dict:
    """COLIN UI screen scraping to retrieve filing history by corp num for a historical company."""
    step: str = "SOFI search page GET"
    try:
        url: str = sofi_url + SOFI_START_PATH
        response = session.get(url, timeout=(2, 10))
        if not response.ok:
            logger.error(f"get_corp_hist_filings_page {step} response error")
            raise ScrapingException(f"Scraping get_corp_hist_filings_page {step} failed for url={url}.")
        step = "SOFI search corp num POST"
        search_data = copy.deepcopy(SCRAPING_SEARCH_HIST_DATA)
        search_data["incorporationNumber"] = corp_num
        # Extract required request token from the response header meta info.
        soup = BeautifulSoup(response.text, "html.parser")
        tag = soup.find("meta", attrs={"name": "_csrf"})
        search_data["_csrf"] = tag.get("content") if tag else ""
        response = session.post(url, data=search_data, timeout=(2, 10))
        if not response.ok:
            logger.error(f"get_corp_hist_filings_page {step} response error")
            raise ScrapingException(f"Scraping get_corp_hist_filings_page {step} failed for url={url}.")
        step = "COLIN search corp num GET"
        url = colin_url + HIST_SEARCH_PATH.format(corp_num=corp_num)
        response = session.get(url, timeout=(2, 10))
        if not response.ok:
            logger.error(f"get_corp_hist_filings_page {step} response error")
            raise ScrapingException(f"Scraping get_corp_hist_filings_page {step} failed for url={url}.")
        page_text = response.text
        filing_info: dict = {"colin_url": colin_url, "filings_page": page_text, "cookies": session.cookies.get_dict()}
        filing_info["no_reports"] = page_text.find("check_token=no&amp;historyIndex=") < 1
        filing_info["active"] = False
        return filing_info
    except ScrapingException:
        raise
    except Exception as err:
        raise ScrapingException(f"Scraping failed for step {step} corp num={corp_num}. {err}") from err


def has_report(filings_page: str, filing_index: int, report_type: str, active: bool = True) -> bool:
    """Determine if filing has a specific report by examining the company history page."""
    if active:
        test_report = REPORT_PATH.format(report_type=report_type, filing_index=filing_index) + "&"
        return filings_page.find(test_report) > 0
    test_report = HIST_REPORT_PATH1.format(report_type=report_type, filing_index=filing_index) + "&amp;"
    return filings_page.find(test_report) > 0


def is_stale_extract(filing_rows: list, filings_info: dict) -> bool:
    """Determine if the colin extract company history is stale: the screen scrape first filing is more recent."""
    if not filing_rows:
        return False
    filings_page = filings_info.get("filings_page")
    filing_row = filing_rows[0]
    expected_first_filing_date: str = str(filing_row[3])
    tz_first_filing_date: str = str(filing_row[4])
    index_first_filing_date = filings_page.find(expected_first_filing_date)
    index_tz_filing_date = filings_page.find(tz_first_filing_date)
    index_first_report = filings_page.find("Report&amp;check_token=no&amp;historyIndex=0")
    if index_first_report < 1:
        index_first_report = filings_page.find("Report&check_token=no&historyIndex=0")
    if index_first_report < 1:
        index_first_report = filings_page.find("historyIndex=0")
    return index_first_report < index_first_filing_date and index_first_report < index_tz_filing_date


def cleanup_pdf(pdf_data):
    """Remove request/retrieval date and time from the legacy report."""
    doc = pymupdf.Document(stream=pdf_data)
    page = doc[0]
    # Date and time text coordinates are well-known from unit testing. Coordinates should work for all dates.
    remove_rect = pymupdf.Rect(14.0, 39.0, 275.0, 53.0)
    page.add_redact_annot(remove_rect)
    page.apply_redactions()  # This permanently removes the content
    updated_pdf = doc.tobytes(garbage=3, clean=True, deflate=True, deflate_images=True, deflate_fonts=True)
    doc.close()
    return updated_pdf


def save_report(corp_num: str, report_type: str, filing_info: dict, result: dict) -> dict:
    """Save an individual report to doc storage and create a DRS app report record."""
    storage_name: str = get_storage_name(result.get("filing_date"), corp_num, result.get("event_id"), report_type)
    save_storage_key = report_type + "_storage_name"
    result[save_storage_key] = storage_name
    try:
        colin_url = filing_info.get("colin_url")
        filing_index: int = filing_info.get("filing_index")
        cookies: dict = filing_info.get("cookies")
        report_url = colin_url
        if filing_info.get("active", True):
            report_url += REPORT_PATH.format(report_type=report_type, filing_index=filing_index)
        else:
            report_url += HIST_REPORT_PATH.format(report_type=report_type, filing_index=filing_index)
        response = requests.get(report_url, cookies=cookies)
        if response.status_code == HTTPStatus.OK and response.text and response.text.find("Error") > 0:
            result["error_count"] = result.get("error_count") + 1
            result["error_message"] = result.get("error_message") + f"Report service error getting {storage_name}. "
            logger.error(f"Report service error trying to retrieve report for {storage_name}.")
        elif response.status_code == HTTPStatus.OK:
            pdf_data = response.content
            if report_type in (REPORT_TYPE_FILING, REPORT_TYPE_NOA):
                pdf_data = cleanup_pdf(pdf_data)
            GoogleStorageService.save_document(storage_name, pdf_data)
            Database.create_document_record(corp_num, storage_name, report_type.upper(), result)
            result["report_count"] = result.get("report_count") + 1
        else:
            result["error_count"] = result.get("error_count") + 1
            result["error_message"] = result.get("error_message") + f" {response.status_code} {response.text}"
    except Exception as err:
        result["error_count"] = result.get("error_count", 0) + 1
        result["error_message"] = result.get("error_message") + " " + str(err)
    return result


def migrate_filing(filing_row, corp_num: str, filing_info: dict) -> dict:
    """Migrage reports for a single filing."""
    result: dict = {"error_count": 0, "report_count": 0, "error_message": ""}
    try:
        result["filing_date"] = str(filing_row[0])
        result["event_id"] = int(filing_row[1])
        result["filing_type"] = str(filing_row[2])
        active: bool = filing_info.get("active", True)
        # logger.info(f"{result.get("event_id")} {result.get("filing_type")}")
        if has_report(filing_info.get("filings_page"), filing_info.get("filing_index"), REPORT_TYPE_RECEIPT, active):
            result = save_report(corp_num, REPORT_TYPE_RECEIPT, filing_info, result)
        if has_report(filing_info.get("filings_page"), filing_info.get("filing_index"), REPORT_TYPE_FILING, active):
            result = save_report(corp_num, REPORT_TYPE_FILING, filing_info, result)
        elif (
            result["filing_type"] == "CONVL"
            and str(filing_row[5]) == "P"
            and filing_row[6]
            and str(filing_row[6]) == "AR"
        ):
            result = save_report(corp_num, REPORT_TYPE_FILING, filing_info, result)
        if has_report(filing_info.get("filings_page"), filing_info.get("filing_index"), REPORT_TYPE_NOA, active):
            result = save_report(corp_num, REPORT_TYPE_NOA, filing_info, result)
        if has_report(filing_info.get("filings_page"), filing_info.get("filing_index"), REPORT_TYPE_CERT, active):
            result = save_report(corp_num, REPORT_TYPE_CERT, filing_info, result)
    except Exception as err:
        result["error_count"] = result.get("error_count") + 1
        result["error_message"] = str(err)
    return result


def migrate_filing_conversion_ar(filing_row, corp_num: str, filing_info: dict) -> dict:
    """Migrage a single conversion ledger AR filing report for a filing."""
    result: dict = {"error_count": 0, "report_count": 0, "error_message": ""}
    try:
        result["filing_date"] = str(filing_row[0])
        result["event_id"] = int(filing_row[1])
        result["filing_type"] = str(filing_row[2])
        result = save_report(corp_num, REPORT_TYPE_FILING, filing_info, result)
    except Exception as err:
        result["error_count"] = result.get("error_count") + 1
        result["error_message"] = str(err)
    return result


def migrate_reports(config: Config, rows: list):  # pylint: disable=too-many-locals
    """
    Migrate reports for each company in the rows list following the steps outlined in the job description.

    Args:
        config: Job configuration containing environment variables.
        rows: The business database mig_colin_reports table query results with the set of company identifiers.
    """
    total_error_count: int = 0
    total_report_count: int = 0
    corp_num: str = ""
    corp_count: int = 0
    filing_summary: dict
    historical_session = setup_historical(config) if rows and not config.ACTIVE else None
    if not config.ACTIVE and historical_session is None:
        return
    for row in rows:
        summary_json = []
        error_count: int = 0
        report_count: int = 0
        filing_info: dict = {}
        corp_count += 1
        try:
            corp_num = str(row[0])
            if config.ACTIVE:
                filing_info = get_corp_filings_page(corp_num, str(row[1]), config.COLIN_URL)
            else:
                filing_info = get_corp_hist_filings_page(
                    historical_session, corp_num, config.COLIN_URL, config.SOFI_URL
                )
            if filing_info.get("no_reports"):
                filing_summary = {
                    "skipped": True,
                    "warning_message": "No report links in filing history page. Company frozen?",
                }
                summary_json.append(filing_summary)
            else:
                filing_rows = Database.get_corp_filings(corp_num, None)
                if is_stale_extract(filing_rows, filing_info):
                    filing_summary = {
                        "skipped": True,
                        "warning_message": "STALE: page first report date more recent than query first filing date.",
                    }
                    summary_json.append(filing_summary)
                else:
                    filing_info["filing_index"] = 0
                    for filing_row in filing_rows:
                        filing_summary = migrate_filing(filing_row, corp_num, filing_info)
                        report_count += filing_summary.get("report_count", 0)
                        error_count += filing_summary.get("error_count", 0)
                        filing_info["filing_index"] = filing_info.get("filing_index") + 1
                        summary_json.append(filing_summary)
                    total_error_count += error_count
                    total_report_count += report_count
            Database.update_company_migration(corp_num, report_count, error_count, summary_json)
        except Exception as report_err:
            logger.error(f"Job {config.JOB_ID} unexpected error for corp_num={corp_num}: {report_err}")
            total_error_count += 1
        if corp_count % 15 == 0:
            logger.info(f"Job {config.JOB_ID} company migration count: {corp_count}")
    logger.info(f"Final counts companies={corp_count} errors={total_error_count} reports={total_report_count}.")


def migrate_recent_reports(config: Config, rows: list):  # pylint: disable=too-many-locals, too-many-branches
    """
    For companies where the reports have migrated but a filing was created after the last
    report migration, and the filing has outputs, migrate reports for each company recent filing in the rows list
    following the steps outlined in the job description.

    Args:
        config: Job configuration containing environment variables.
        rows: The business database mig_colin_reports table query results with the set of company identifiers
              as well as the migrated_ts and current report_count, error_count and migration_summary.
    """
    total_error_count: int = 0
    total_report_count: int = 0
    corp_num: str = ""
    corp_count: int = 0
    filing_summary: dict
    historical_session: dict = setup_historical(config) if rows and not config.ACTIVE else None
    if not config.ACTIVE and historical_session is None:
        return
    for row in rows:
        summary_json = []
        error_count: int = 0
        report_count: int = 0
        filing_info: dict = {}
        corp_count += 1
        try:
            corp_num = str(row[0])
            if config.ACTIVE:
                filing_info = get_corp_filings_page(corp_num, str(row[1]), config.COLIN_URL)
            else:
                filing_info = get_corp_hist_filings_page(
                    historical_session, corp_num, config.COLIN_URL, config.SOFI_URL + SOFI_START_PATH
                )
            if filing_info.get("no_reports"):
                filing_summary = {
                    "skipped": True,
                    "warning_message": "No report links in filing history page. Company state?",
                }
                summary_json.append(filing_summary)
            else:
                filing_rows = Database.get_corp_filings(corp_num, str(row[2]))
                if is_stale_extract(filing_rows, filing_info):
                    filing_summary = {
                        "skipped": True,
                        "warning_message": "STALE: page first report date more recent than query first filing date.",
                    }
                    summary_json.append(filing_summary)
                else:
                    filing_info["filing_index"] = 0
                    for filing_row in filing_rows:
                        filing_summary = migrate_filing(filing_row, corp_num, filing_info)
                        report_count += filing_summary.get("report_count", 0)
                        error_count += filing_summary.get("error_count", 0)
                        filing_info["filing_index"] = filing_info.get("filing_index") + 1
                        summary_json.append(filing_summary)
                    total_error_count += error_count
                    total_report_count += report_count
            report_count += int(row[3])
            error_count += int(row[4])
            summary_json.extend(list(row[5]))
            if summary_json and summary_json[0].get("warning_message"):
                Database.update_company_migration_no_ts(corp_num, report_count, error_count, summary_json)
            else:
                Database.update_company_migration(corp_num, report_count, error_count, summary_json)
        except Exception as report_err:
            logger.error(f"Job {config.JOB_ID} unexpected error for corp_num={corp_num}: {report_err}")
            total_error_count += 1
        if corp_count % 15 == 0:
            logger.info(f"Job {config.JOB_ID} company migration count: {corp_count}")
    logger.info(f"Final counts companies={corp_count} errors={total_error_count} reports={total_report_count}.")


def migrate_conversion_ar(config: Config, rows: list):
    """
    For companies where the reports have migrated and conversion ledger annual reports exist, as a patch one-time update
    migrate the missing conversion ledger annual report filing outputs.

    Args:
        config: Job configuration containing environment variables.
        rows: The business database mig_colin_reports table query results with the set of company identifiers
              as well as the migrated_ts and current report_count, error_count and migration_summary.
    """
    total_error_count: int = 0
    total_report_count: int = 0
    corp_num: str = ""
    corp_count: int = 0
    filing_summary: dict
    for row in rows:  # pylint: disable=too-many-nested-blocks
        summary_json = []
        error_count: int = 0
        report_count: int = 0
        corp_count += 1
        try:
            corp_num = str(row[0])
            filing_info: dict = get_corp_filings_page(corp_num, str(row[1]), config.COLIN_URL)
            if filing_info.get("no_reports"):
                filing_summary = {
                    "skipped": True,
                    "warning_message": "No report links in filing history page. Company state?",
                }
                summary_json.append(filing_summary)
            else:
                filing_rows = Database.get_corp_filings(corp_num)
                if is_stale_extract(filing_rows, filing_info):
                    filing_summary = {
                        "skipped": True,
                        "warning_message": "STALE: page first report date more recent than query first filing date.",
                    }
                    summary_json.append(filing_summary)
                else:
                    filing_info["filing_index"] = 0
                    for filing_row in filing_rows:
                        if (
                            str(filing_row[2]) == "CONVL"
                            and str(filing_row[5]) == "P"
                            and filing_row[6]
                            and str(filing_row[6]) == "AR"
                        ):
                            filing_summary = migrate_filing_conversion_ar(filing_row, corp_num, filing_info)
                            report_count += filing_summary.get("report_count", 0)
                            error_count += filing_summary.get("error_count", 0)
                            summary_json.append(filing_summary)
                        filing_info["filing_index"] = filing_info.get("filing_index") + 1
                    total_error_count += error_count
                    total_report_count += report_count
            report_count += int(row[3])
            error_count += int(row[4])
            summary_json.extend(list(row[5]))
            Database.update_company_migration_no_ts(corp_num, report_count, error_count, summary_json)
        except Exception as report_err:
            logger.error(f"Job {config.JOB_ID} convesion AR unexpected error for corp_num={corp_num}: {report_err}")
            total_error_count += 1
        if corp_count % 15 == 0:
            logger.info(f"Job {config.JOB_ID} company migration count: {corp_count}")
    logger.info(f"Final counts companies={corp_count} errors={total_error_count} reports={total_report_count}.")


def job(config: Config):
    """
    Execute the job:
        Run a business database mig_colin_reports query to get the company identifiers to migrate filing reports for.
        Depending on the job environment variable values, filter on job id, recognition year, and company state.
        The number of companies to migrate per job run can also be configured by env variable.
        If environment variable MIGRATION_UPDATE_PREVIOUS is True, only migrate reports for filings that were
        created since the last report migration for the company, excluding companies that have migrated.
        For each company:
            1. Screen scrape the colin application to get the report links.
            2. Query the business database colin_extract schema to get the company filing history.
            3. Match the query filing to the scraped history link reports.
            4. Retrieve each filing report using the scraped history link.
            5. Save the report to the DRS document storage business bucket.
            6. Insert a DRS application_reports table record in the DRS docs database.

    Args:
        config: Job configuration containing environment variables.

    Returns:
    """
    try:
        Database.init_app(config)
        rows = Database.get_job_corps(config)
        if config.UPDATE_PREVIOUS:
            migrate_recent_reports(config, rows)
        elif config.UPDATE_CONVERSION_AR:
            migrate_conversion_ar(config, rows)
        else:
            migrate_reports(config, rows)
    except (psycopg2.Error, Exception) as err:
        job_message: str = f"Run failed: {str(err)}."
        logger.error(job_message)
        sys.exit(1)  # Retry Job Task by exiting the process
    finally:
        # Clean up: Close the database cursor and connection
        Database.close_app()

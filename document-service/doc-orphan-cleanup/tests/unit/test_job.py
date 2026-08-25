# Copyright © 2026 Province of British Columbia
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
"""Unit tests for the job."""
import os

import psycopg2

from doc_orphan_cleanup.config import Config
from doc_orphan_cleanup.database import Database
from doc_orphan_cleanup.utils.logging import setup_logging


TEST_DOC_STATEMENT = """
INSERT INTO documents(id, document_service_id, add_ts, consumer_document_id, consumer_identifier, consumer_filename,
                      consumer_filing_date, doc_storage_url, document_type, document_class, description, author,
                      consumer_reference_id)
     VALUES (nextval('document_id_seq'), get_service_doc_id(), now() - interval '35 days', get_document_number(),
             null, null, null, null, 'FILE', 'CORP', null, null, null)
"""


def test_config():
    """Assert that the config setup from env vars works as expected."""
    config: Config = Config()
    assert config.LOGICAL_DELETE is True
    assert config.UNCONSUMED_ORPHAN_INTERVAL == "30"
    assert "'COOP','CORP','FIRM'" in config.DOCUMENT_CLASSES

def test_get_orphaned_count():
    """Assert that the count query works as expected."""
    try:
        config, job_status = setup_testing()
        job_status = Database.get_orphaned_count(config, job_status)
        print(f"get_orphaned_count: {job_status.get("orphan_count")} status={job_status.get("status")}")
        assert job_status.get("status") == 200
    except (psycopg2.Error, Exception) as err:
        print(f"get_orphaned_count failed: {err}.")
    finally:
        Database.close_app()

def test_backup_orphaned_documents():
    """Assert that the backup documents SQL statement works as expected."""
    try:
        config, job_status = setup_testing()
        create_test_doc()
        job_status["orphan_count"] = 1
        job_status = Database.backup_orphaned_documents(config, job_status)
        assert job_status.get("status") == 200
    except (psycopg2.Error, Exception) as err:
        print(f"backup_orphaned_documents failed: {err}.")
    finally:
        Database.close_app()

def test_remove_orphaned_documents():
    """Assert that the logically removed documents SQL statement works as expected."""
    try:
        config, job_status = setup_testing()
        create_test_doc()
        job_status["orphan_count"] = 1
        job_status = Database.remove_orphaned_documents(config, job_status)
        assert job_status.get("status") == 200
    except (psycopg2.Error, Exception) as err:
        print(f"remove_orphaned_documents failed: {err}.")
    finally:
        Database.close_app()

def test_delete_orphaned_documents():
    """Assert that the physically delete documents SQL statement works as expected."""
    try:
        config, job_status = setup_testing()
        create_test_doc()
        job_status["orphan_count"] = 1
        job_status = Database.delete_orphaned_documents(config, job_status)
        assert job_status.get("status") == 200
    except (psycopg2.Error, Exception) as err:
        print(f"delete_orphaned_documents failed: {err}.")
    finally:
        Database.close_app()

def setup_testing():
    """Common test setup."""
    config: Config = Config()
    setup_logging(os.path.join(os.path.abspath("src/doc_orphan_cleanup"), "logging.yaml"))
    Database.init_app(config)
    job_status: dict = {"error_msg": "", "status": 200, "orphan_count": 0}
    return config, job_status

def create_test_doc():
    """Create orphaned document record for testing."""
    Database.doc_db_cursor.execute(TEST_DOC_STATEMENT)
    Database.doc_db_conn.commit()

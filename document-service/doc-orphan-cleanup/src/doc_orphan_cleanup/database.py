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
"""All of the database connection and changes for the job are captured here.

Define SQL statements
Create database connections and cursors for the job.
Execute queries, updates, and inserts.
Close database connections and cursors on job completion.
"""
from contextlib import suppress

import psycopg2

from doc_orphan_cleanup.config import Config
from doc_orphan_cleanup.utils.logging import logger

QUERY_ORPHAN_COUNT: str = """
select count(d.id)
  from documents d
 where d.document_class in ({doc_classes})
   and d.consumer_document_id is not null
   and length(d.consumer_document_id) != 8
   and d.add_ts < now() - interval '{interval_days} days'
   and (d.consumer_reference_id is null or trim(d.consumer_reference_id) = '')
"""
BACKUP_STATEMENT = """
insert into orphaned_documents
(select d.*
   from documents d
  where d.document_class in ({doc_classes})
    and d.consumer_document_id is not null
    and length(d.consumer_document_id) != 8
    and d.add_ts < now() - interval '{interval_days} days'
    and (d.consumer_reference_id is null or trim(d.consumer_reference_id) = '')
)
"""
REMOVE_STATEMENT = """
update documents
   set document_type = 'DELETED', document_class = 'DELETED',
       description = document_type::text || ' ' || document_class::text,
       document_service_id = 'DEL-' || document_service_id,
       consumer_document_id = 'DEL-' || consumer_document_id,
       consumer_identifier = case when consumer_identifier is not null then 'DEL-' || consumer_identifier else null end
  where document_class in ({doc_classes})
    and consumer_document_id is not null
    and length(consumer_document_id) != 8
    and add_ts < now() - interval '{interval_days} days'
    and (consumer_reference_id is null or trim(consumer_reference_id) = '')
"""
DELETE_REQUEST_STATEMENT = """
delete
  from document_requests
 where document_id in (
 select d.id
   from documents d
  where d.document_class in ({doc_classes})
    and d.consumer_document_id is not null
    and length(d.consumer_document_id) != 8
    and d.add_ts < now() - interval '{interval_days} days'
    and (d.consumer_reference_id is null or trim(d.consumer_reference_id) = '')
)
"""
DELETE_STATEMENT = """
delete
  from documents
 where document_class in ({doc_classes})
   and consumer_document_id is not null
   and length(consumer_document_id) != 8
   and add_ts < now() - interval '{interval_days} days'
   and (consumer_reference_id is null or trim(consumer_reference_id) = '')
"""


class Database:  # pylint: disable=too-few-public-methods
    """Database object."""

    doc_db_conn: psycopg2.extensions.connection
    doc_db_cursor: psycopg2.extensions.cursor

    @staticmethod
    def init_app(config: Config):
        """Set up the job database connections and cursors."""
        logger.info("Job getting doc database connection and cursor.")
        Database.doc_db_conn = psycopg2.connect(dsn=config.DOC_DB_URI)
        Database.doc_db_cursor = Database.doc_db_conn.cursor()

    @staticmethod
    def close_app():
        """Close the database cursors and connections."""
        with suppress(Exception):
            Database.doc_db_cursor.close()
        with suppress(Exception):
            Database.doc_db_conn.close()

    @classmethod
    def get_orphaned_count(cls, config: Config, rec_json: dict) -> dict:
        """Get job count of DRS records orphaned since the last time the job ran."""
        interval_days: str = config.UNCONSUMED_ORPHAN_INTERVAL
        doc_classes: str = config.DOCUMENT_CLASSES
        query_statement: str = QUERY_ORPHAN_COUNT.format(interval_days=interval_days, doc_classes=doc_classes)
        logger.info(f"Executing query to get DRS orphan count:\n{query_statement}")
        try:
            Database.doc_db_cursor.execute(query_statement)
            drs_rows = Database.doc_db_cursor.fetchall()
            row = drs_rows[0]
            rec_json["orphan_count"] = int(row[0])
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error(f"get_orphaned_count failed: {db_exception}")
            rec_json["error_msg"] = rec_json.get("error_msg") + "Get_orphaned_count failed see log.\n"
            rec_json["status"] = 500
            rec_json["orphan_count"] = 0
        return rec_json

    @classmethod
    def backup_orphaned_documents(cls, config: Config, rec_json: dict) -> dict:
        """Save a copy of the orphaned document records in the orphaned_documents table."""
        if rec_json.get("status") != 200:
            logger.info("Skipping backup_orphaned_documents - error status:")
            return rec_json
        if rec_json.get("orphan_count", 0) < 1:
            logger.info("Skipping backup_orphaned_documents - no orphan records:")
            return rec_json
        interval_days: str = config.UNCONSUMED_ORPHAN_INTERVAL
        doc_classes: str = config.DOCUMENT_CLASSES
        sql_statement: str = BACKUP_STATEMENT.format(interval_days=interval_days, doc_classes=doc_classes)
        logger.info(f"Executing query to backup orphaned document records:\n{sql_statement}")
        try:
            Database.doc_db_cursor.execute(sql_statement)
            Database.doc_db_conn.commit()
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error(f"backup_orphaned_documents failed: {db_exception}")
            rec_json["error_msg"] = rec_json.get("error_msg") + "Backup_orphaned_documents failed see log.\n"
            rec_json["status"] = 500
            Database.doc_db_conn.rollback()
        return rec_json

    @classmethod
    def remove_orphaned_documents(cls, config: Config, rec_json: dict) -> dict:
        """Logically delete the orphaned document records so they are excluded from the DRS API (searching)."""
        if rec_json.get("status") != 200:
            logger.info("Skipping remove_orphaned_documents - error status:")
            return rec_json
        if rec_json.get("orphan_count", 0) < 1:
            logger.info("Skipping remove_orphaned_documents - no orphan records:")
            return rec_json
        interval_days: str = config.UNCONSUMED_ORPHAN_INTERVAL
        doc_classes: str = config.DOCUMENT_CLASSES
        sql_statement: str = REMOVE_STATEMENT.format(interval_days=interval_days, doc_classes=doc_classes)
        logger.info(f"Executing query to remove orphaned document records:\n{sql_statement}")
        try:
            Database.doc_db_cursor.execute(sql_statement)
            Database.doc_db_conn.commit()
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error(f"remove_orphaned_documents failed: {db_exception}")
            rec_json["error_msg"] = rec_json.get("error_msg") + "Remove_orphaned_documents failed see log.\n"
            rec_json["status"] = 500
            Database.doc_db_conn.rollback()
        return rec_json

    @classmethod
    def delete_orphaned_documents(cls, config: Config, rec_json: dict) -> dict:
        """Physically, permanently delete the orphaned document records from the database."""
        if rec_json.get("status") != 200:
            logger.info("Skipping delete_orphaned_documents - error status:")
            return rec_json
        if rec_json.get("orphan_count", 0) < 1:
            logger.info("Skipping delete_orphaned_documents - no orphan records:")
            return rec_json
        interval_days: str = config.UNCONSUMED_ORPHAN_INTERVAL
        doc_classes: str = config.DOCUMENT_CLASSES
        sql_statement: str = DELETE_REQUEST_STATEMENT.format(interval_days=interval_days, doc_classes=doc_classes)
        logger.info(f"Executing query to delete orphaned document request records:\n{sql_statement}")
        sql_statement2: str = DELETE_STATEMENT.format(interval_days=interval_days, doc_classes=doc_classes)
        logger.info(f"Executing query to delete orphaned document records:\n{sql_statement2}")
        try:
            Database.doc_db_cursor.execute(sql_statement)
            Database.doc_db_cursor.execute(sql_statement2)
            Database.doc_db_conn.commit()
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error(f"delete_orphaned_documents failed: {db_exception}")
            rec_json["error_msg"] = rec_json.get("error_msg") + "Delete_orphaned_documents failed see log.\n"
            rec_json["status"] = 500
            Database.doc_db_conn.rollback()
        return rec_json

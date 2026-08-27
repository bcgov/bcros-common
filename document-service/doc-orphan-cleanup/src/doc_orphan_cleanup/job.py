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
"""This module executes all the job steps."""
import sys

import psycopg2

from doc_orphan_cleanup.config import Config
from doc_orphan_cleanup.database import Database
from doc_orphan_cleanup.services.notify import Notify
from doc_orphan_cleanup.utils.logging import logger

JOB_MSG: str = "Job completed count={count}, status={status}, error message={error_msg}"


def delete_orphaned_records(config: Config, job_status: dict) -> dict:
    """
    Delete the orphaned record either physically or logically depending on the env var LOGICAL_DELETE.

    Args:
        config: Job configuration containing environment variables.
        job_status: Holds the running status success/errors for the job.
    """
    if config.LOGICAL_DELETE:
        job_status = Database.remove_orphaned_documents(config, job_status)
    else:
        job_status = Database.delete_orphaned_documents(config, job_status)
    return job_status


def job(config: Config):
    """
    Summary:
        Delete DRS documents created by consumer applications as drafts that are never used in a filing or registration.
        A copy of a deleted record is stored in the DRS database orphaned_documents table.
        Depending on the LOGICAL_DELETE environment variable, deletion is either permanent or logical.
        If permanent, the document record is deleted from the database.
        If logical, the document record is updated to marked as deleted. It is excluded from DRS API searching.

    Detail:
        1. Execute a query to get a count of orphaned records since the last tieme the job ran. Exit the job if the
           count is 0.
        2. If step 1 is successful and orphaned records exist, execute a insert statement to create a copy fo all
           document records to be deleted in the orphaned documents table.
        3. If step 2 is successful, execute statement(s) to delete the orphaned records.
           If LOGICAL_DELETE is true, mark the records as removed.
           If LOGICAL_DELETE is false, physically delete the records from the database.
        4. Optional. If the environment varialbe NOTIFY_CONFIG is configured send an email notification with the
           job run status.
        5. Log the job run status and exit.

    Args:
        config: Job configuration containing environment variables.

    Returns:
    """
    try:
        Database.init_app(config)
        job_status: dict = {"error_msg": "", "status": 200, "orphan_count": 0}
        job_status = Database.get_orphaned_count(config, job_status)
        job_status = Database.backup_orphaned_documents(config, job_status)
        job_status = delete_orphaned_records(config, job_status)
        msg: str = JOB_MSG.format(
            count=job_status.get("orphan_count"), status=job_status.get("status"), error_msg=job_status.get("error_msg")
        )
        logger.info(msg)
        notify_client: Notify = Notify(config)
        notify_client.send_status(job_status)
    except (psycopg2.Error, Exception) as err:
        job_message: str = f"Run failed: {err}."
        logger.error(job_message)
        sys.exit(1)  # Retry Job Task by exiting the process
    finally:
        # Clean up: Close the database cursor and connection
        Database.close_app()

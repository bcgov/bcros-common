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
"""This module contains the email notification service used by the job"""
import copy
import json
from http import HTTPStatus

import requests

from doc_orphan_cleanup.config import Config
from doc_orphan_cleanup.utils.logging import logger

EMAIL_DATA_TEMPLATE = {"recipients": "", "content": {"subject": "", "body": ""}}


class Notify:
    """Notify calls the GCNotify service to email the status of the job run."""

    def __init__(self, config: Config):
        """Create the notify service."""
        if config.NOTIFY_CONFIG != "":
            notify_config: dict = json.loads(config.NOTIFY_CONFIG)
            self.url: str = notify_config.get("url", "")
            self.recipients: str = notify_config.get("recipients", "")
            self.subject: str = notify_config.get("subject", "")
            self.body: str = notify_config.get("body", "")
            self.jwt = get_sa_token(config)
        else:
            self.url: str = ""
            self.recipients: str = ""
            self.subject: str = ""
            self.body: str = ""
            self.jwt = None

    def send_status(self, status_data: dict) -> HTTPStatus:
        """Send a job status email."""
        if self.url == "" or self.jwt is None:
            logger.info("Skipping job status email notification - not configured.")
            return HTTPStatus.OK

        body: str = self.body.format(
            orphan_count=status_data.get("orphan_count"),
            status=status_data.get("status"),
            error_msg=status_data.get("error_msg") if len(status_data.get("error_msg")) > 3 else "",
        )
        payload = copy.deepcopy(EMAIL_DATA_TEMPLATE)
        payload["recipients"] = self.recipients
        payload["content"]["subject"] = self.subject
        payload["content"]["body"] = body
        logger.info(f"Sending status email {payload}")
        self.send_email(payload)

    def send_email(self, payload: dict) -> HTTPStatus:
        """Create and send the email payload to the Notify service."""
        headers = {"Authorization": "Bearer " + self.jwt, "Content-Type": "application/json"}
        res = requests.post(url=self.url, headers=headers, json=payload, timeout=30.0)
        logger.info(f"Email sent to {self.url} response status code={res.status_code}")
        return res.status_code


def get_sa_token(config: Config):
    """Common notification service requires a Registries issued JWT. Request one from the OIDC service."""
    oidc_token_url = config.JWT_OIDC_TOKEN_URL
    client_id = config.ACCOUNT_SVC_CLIENT_ID
    client_secret = config.ACCOUNT_SVC_CLIENT_SECRET
    logger.info(f"Calling OIDC api to get token: URL = {oidc_token_url}, client_id={client_id}.")
    try:
        headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
        data = f"grant_type=client_credentials&scope=openid&client_id={client_id}&client_secret={client_secret}"
        response = requests.post(url=oidc_token_url, data=data, params=None, headers=headers, timeout=30.0)
        if not response or not response.ok:
            logger.info(f"Get SA token failed {response.status_code} {response.text}")
            return None
        response_json = json.loads(response.text)
        token = response_json["access_token"]
        logger.info("Have new sa token from OIDC.")
        return token
    except Exception as err:
        logger.error(f"get_sa_token error: {str(err)}")
        return None

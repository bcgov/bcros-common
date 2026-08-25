# Copyright © 2026 Province of British Columbia
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
"""The application common configuration."""
import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class BaseConfig:
    """Base configuration."""


class Config(BaseConfig):
    """Production configuration."""

    DB_USER = os.getenv("DOC_DATABASE_USERNAME", "")
    DB_PASSWORD = os.getenv("DOC_DATABASE_PASSWORD", "")
    DB_NAME = os.getenv("DOC_DATABASE_NAME", "")
    DB_HOST = os.getenv("DOC_DATABASE_HOST", "")
    DB_PORT = os.getenv("DOC_DATABASE_PORT", "5432")  # POSTGRESQL

    # POSTGRESQL DOC database
    if DB_UNIX_SOCKET := os.getenv("DOC_DATABASE_UNIX_SOCKET", None):
        DOC_DB_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?host={DB_UNIX_SOCKET}"
    else:
        DOC_DB_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    LOGICAL_DELETE: bool = bool(os.getenv("LOGICAL_DELETE", "True"))
    UNCONSUMED_ORPHAN_INTERVAL: str = os.getenv("UNCONSUMED_ORPHAN_INTERVAL", "30")
    DOCUMENT_CLASSES: str = "'" + os.getenv("DOCUMENT_ClASSES", "COOP,CORP,FIRM").replace(",", "','") + "'"
    NOTIFY_CONFIG: str = os.getenv("NOTIFY_CONFIG", "")
    JWT_OIDC_TOKEN_URL: str = os.getenv("JWT_OIDC_TOKEN_URL", "")
    ACCOUNT_SVC_CLIENT_ID: str = os.getenv("ACCOUNT_SVC_CLIENT_ID", "")
    ACCOUNT_SVC_CLIENT_SECRET: str = os.getenv("ACCOUNT_SVC_CLIENT_SECRET", "")

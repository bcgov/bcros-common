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
"""Common setup and fixtures for the pytest suite used by this service."""
import datetime
import os
from contextlib import contextmanager

import google.auth
import pytest
from google.api_core.exceptions import NotFound
from google.auth.credentials import AnonymousCredentials

from doc_api import create_app
from doc_api import jwt as _jwt
from doc_api.models import db as _db
from doc_api.services.document_storage import storage_service
from doc_api.services.gcp_auth import auth_service

from . import FROZEN_DATETIME

_FAKE_GCS: dict = {}
# Permanent fixture object the tests expect to find in every document bucket.
_FAKE_GCS_SEED_NAME = "unit_test/unit_test.pdf"
_FAKE_GCS_SEED_FILE = os.path.join(os.path.dirname(__file__), "unit", "services", "unit_test.pdf")


class _FakeBlob:
    """In-memory stand-in for google.cloud.storage.Blob."""

    def __init__(self, bucket_name: str, name: str):
        self.bucket_name = bucket_name
        self.name = name
        self.time_created = datetime.datetime.now(datetime.timezone.utc)

    def upload_from_string(self, data, content_type=None):  # pylint: disable=unused-argument
        _FAKE_GCS[(self.bucket_name, self.name)] = data if isinstance(data, bytes) else str(data).encode()

    def download_as_bytes(self):
        if (self.bucket_name, self.name) not in _FAKE_GCS and self.name == _FAKE_GCS_SEED_NAME:
            with open(_FAKE_GCS_SEED_FILE, "rb") as seed_file:
                _FAKE_GCS[(self.bucket_name, self.name)] = seed_file.read()
        if (self.bucket_name, self.name) not in _FAKE_GCS:
            raise NotFound(f"{self.bucket_name}/{self.name}")
        return _FAKE_GCS[(self.bucket_name, self.name)]

    def delete(self):
        _FAKE_GCS.pop((self.bucket_name, self.name), None)

    def generate_signed_url(self, **kwargs):  # pylint: disable=unused-argument
        return f"https://storage.googleapis.com/{self.bucket_name}/{self.name}?X-Goog-Signature=unit-test"


class _FakeBucket:
    """In-memory stand-in for google.cloud.storage.Bucket."""

    def __init__(self, name: str):
        self.name = name

    def blob(self, name: str):
        return _FakeBlob(self.name, name)

    def copy_blob(self, blob, destination_bucket, new_name=None):
        data = _FAKE_GCS.get((blob.bucket_name, blob.name), b"")
        _FAKE_GCS[(destination_bucket.name, new_name or blob.name)] = data
        return _FakeBlob(destination_bucket.name, new_name or blob.name)


class _FakeStorageClient:
    """In-memory stand-in for google.cloud.storage.Client."""

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        pass

    def bucket(self, name: str):
        return _FakeBucket(name)


class _FakeCredentials(AnonymousCredentials):
    """Placeholder application default credentials for keyless unit test runs."""

    def __init__(self):
        super().__init__()
        self.token = "unit-test-token"
        self.service_account_email = "unit-test@example.iam.gserviceaccount.com"

    def refresh(self, request):  # pylint: disable=unused-argument
        """Nothing to refresh."""


@pytest.fixture(scope="session", autouse=True)
def offline_gcp():
    """Without a GCP_AUTH_KEY (CI is keyless), keep tests off real Google Cloud APIs.

    Session scoped so it is in place before the app (and its Pub/Sub publisher) is created.
    Application default credentials return placeholder credentials, Cloud Storage is replaced
    with an in-memory fake, and no ID token is requested for the report service.
    With a GCP_AUTH_KEY set locally, the tests still run against the real services.
    """
    if os.getenv("GCP_AUTH_KEY"):
        yield
        return
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(google.auth, "default", lambda *args, **kwargs: (_FakeCredentials(), None))
        patch.setattr(storage_service.storage, "Client", _FakeStorageClient)
        patch.setattr(auth_service.google.oauth2.id_token, "fetch_id_token", lambda *args, **kwargs: None)
        yield


@contextmanager
def not_raises(exception):
    """Corallary to the pytest raises builtin.

    Assures that an exception is NOT thrown.
    """
    try:
        yield
    except exception:
        raise pytest.fail(f"DID RAISE {exception}")  # pylint: disable=raise-missing-from


# fixture to freeze utcnow to a fixed date-time
@pytest.fixture
def freeze_datetime_utcnow(monkeypatch):
    """Fixture to return a static time for utcnow()."""

    class _Datetime:
        @classmethod
        def utcnow(cls):
            """UTC NOW"""
            return FROZEN_DATETIME

    monkeypatch.setattr(datetime, "datetime", _Datetime)


@pytest.fixture(scope="session")
def app():
    """Return a session-wide application configured in TEST mode."""
    _app = create_app("unitTesting")

    with _app.app_context():
        yield _app


@pytest.fixture(scope="function")
def client(app):  # pylint: disable=redefined-outer-name
    """Return a session-wide Flask test client."""
    return app.test_client()


@pytest.fixture(scope="session")
def jwt():
    """Return a session-wide jwt manager."""
    return _jwt


@pytest.fixture(scope="session")
def db(app, request):  # pylint: disable=redefined-outer-name
    """Session-wide test database."""

    #    def teardown():
    #        _db.drop_all()

    #    _db.app = app

    #    _db.create_all()
    #    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope="function")
def session(db, request):  # pylint: disable=redefined-outer-name
    """Return a function-scoped session."""
    db.session.begin_nested()

    def commit():
        db.session.flush()

    # patch commit method
    old_commit = db.session.commit
    db.session.commit = commit

    def teardown():
        db.session.rollback()
        db.session.close()
        db.session.commit = old_commit

    request.addfinalizer(teardown)
    return db.session

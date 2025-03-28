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

"""Tests to assure the ops end-point.

Test-Suite to ensure that the /ops endpoint is working as expected.
"""

from unittest.mock import patch

from sqlalchemy import exc

from notify_api.models import db


def test_ops_healthz_success(session, client):  # pylint: disable=unused-argument
    """Assert that the service is healthy if it can successfully access the database."""
    rv = client.get("/ops/healthz")
    assert rv.status_code == 200  # noqa: PLR2004
    assert rv.json == {"message": "api is healthy"}


def test_ops_healthz_exception(session, client):  # pylint: disable=unused-argument
    """Assert that the service is healthy if it can successfully access the database."""
    with patch.object(db.session, "execute", side_effect=exc.SQLAlchemyError):
        rv = client.get("/ops/healthz")
        assert rv.status_code == 500  # noqa: PLR2004
        assert rv.json == {"message": "api is down"}
    with patch.object(db.session, "execute", side_effect=Exception):
        rv = client.get("/ops/healthz")
        assert rv.status_code == 500  # noqa: PLR2004
        assert rv.json == {"message": "api is down"}


def test_ops_readyz(client):
    """Asserts that the service is ready to serve."""
    rv = client.get("/ops/readyz")

    assert rv.status_code == 200  # noqa: PLR2004
    assert rv.json == {"message": "api is ready"}

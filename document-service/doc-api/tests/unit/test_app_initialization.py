# Copyright © 2024 Province of British Columbia
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
"""Tests for pg8000 graceful shutdown event listener."""
import sys
from unittest.mock import Mock, patch

import pytest

from doc_api import _setup_pg8000_graceful_shutdown


def _capturing_listens_for():
    """Return a (side_effect, captured_list) pair that records decorated functions."""
    captured = []

    def mock_listens_for(engine, event_name):
        def decorator(fn):
            captured.append(fn)
            return fn
        return decorator

    return mock_listens_for, captured


class TestSetupPg8000GracefulShutdown:
    """Tests for _setup_pg8000_graceful_shutdown."""

    def test_non_pg8000_engine_skips_listener(self):
        """Non-pg8000 engines do not register a connect event listener."""
        mock_engine = Mock()
        mock_engine.driver = "psycopg2"

        with patch("doc_api.event") as mock_event:
            _setup_pg8000_graceful_shutdown(mock_engine)
            mock_event.listens_for.assert_not_called()

    def test_pg8000_engine_registers_connect_listener(self):
        """pg8000 engines register exactly one 'connect' event listener."""
        mock_engine = Mock()
        mock_engine.driver = "pg8000"
        mock_listens_for, captured = _capturing_listens_for()

        with patch("doc_api.event") as mock_event:
            mock_event.listens_for.side_effect = mock_listens_for
            _setup_pg8000_graceful_shutdown(mock_engine)

        mock_event.listens_for.assert_called_once_with(mock_engine, "connect")
        assert len(captured) == 1

    def test_safe_close_calls_original_close_without_error(self):
        """safe_close delegates to the original close when no exception occurs."""
        mock_engine = Mock()
        mock_engine.driver = "pg8000"
        mock_listens_for, captured = _capturing_listens_for()

        with patch("doc_api.event") as mock_event:
            mock_event.listens_for.side_effect = mock_listens_for
            _setup_pg8000_graceful_shutdown(mock_engine)

        orig_close = Mock()
        mock_dbapi_conn = Mock()
        mock_dbapi_conn.close = orig_close

        captured[0](mock_dbapi_conn, Mock())
        mock_dbapi_conn.close()

        orig_close.assert_called_once()

    def test_safe_close_suppresses_pg8000_interface_error(self):
        """safe_close suppresses pg8000 InterfaceError raised on teardown."""
        from pg8000.exceptions import InterfaceError

        mock_engine = Mock()
        mock_engine.driver = "pg8000"
        mock_listens_for, captured = _capturing_listens_for()

        with patch("doc_api.event") as mock_event:
            mock_event.listens_for.side_effect = mock_listens_for
            _setup_pg8000_graceful_shutdown(mock_engine)

        orig_close = Mock(side_effect=InterfaceError("connection already closed"))
        mock_dbapi_conn = Mock()
        mock_dbapi_conn.close = orig_close

        captured[0](mock_dbapi_conn, Mock())

        # Must not propagate the InterfaceError
        mock_dbapi_conn.close()

    def test_safe_close_reraises_non_interface_errors(self):
        """safe_close re-raises exceptions that are not pg8000 InterfaceError."""
        mock_engine = Mock()
        mock_engine.driver = "pg8000"
        mock_listens_for, captured = _capturing_listens_for()

        with patch("doc_api.event") as mock_event:
            mock_event.listens_for.side_effect = mock_listens_for
            _setup_pg8000_graceful_shutdown(mock_engine)

        orig_close = Mock(side_effect=RuntimeError("unexpected failure"))
        mock_dbapi_conn = Mock()
        mock_dbapi_conn.close = orig_close

        captured[0](mock_dbapi_conn, Mock())

        with pytest.raises(RuntimeError, match="unexpected failure"):
            mock_dbapi_conn.close()

    def test_missing_pg8000_exceptions_module_is_handled(self):
        """ImportError from pg8000.exceptions is caught; safe_close still works."""
        mock_engine = Mock()
        mock_engine.driver = "pg8000"
        mock_listens_for, captured = _capturing_listens_for()

        with patch("doc_api.event") as mock_event:
            mock_event.listens_for.side_effect = mock_listens_for
            with patch.dict(sys.modules, {"pg8000.exceptions": None}):
                _setup_pg8000_graceful_shutdown(mock_engine)

        orig_close = Mock()
        mock_dbapi_conn = Mock()
        mock_dbapi_conn.close = orig_close

        captured[0](mock_dbapi_conn, Mock())
        mock_dbapi_conn.close()

        orig_close.assert_called_once()

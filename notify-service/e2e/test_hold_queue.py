"""E2E hold flags: simulate queue-emails / queue-sms being switched on and off.

ON  -> new notifications are stored as HELD (not published) and the resend job skips that channel.
OFF -> notifications send immediately and the resend job releases HELD notifications (any age).
"""

import base64
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
import json
from unittest.mock import patch

from conftest import BC_NOTIFY_SMS_TOPIC, SMTP_TOPIC
import pytest

from notify_api.models import Notification, NotificationHistory, db
from notify_api.services.flags import FeatureFlag
from notify_api.services.gcp_queue import queue
from notify_api.utils.enums import Role

# An inline image routes the email to SMTP, which completes without a provider callback.
EMAIL = (
    "/api/v1/notify",
    {
        "recipients": "held-recipient@gov.bc.ca",
        "requestBy": "e2e",
        "content": {"subject": "Held subject", "body": '<p>Hi</p><img src="cid:logo">'},
    },
    SMTP_TOPIC,
)
SMS = (
    "/api/v2/sms",
    {"recipients": "250-555-0199", "requestBy": "e2e", "body": "Held SMS"},
    BC_NOTIFY_SMS_TOPIC,
)
CHANNELS = [
    pytest.param(FeatureFlag.QUEUE_EMAILS, EMAIL, id="email"),
    pytest.param(FeatureFlag.QUEUE_SMS, SMS, id="sms"),
]


@pytest.fixture
def set_flag(feature_flags):
    """Switch a flag in the offline LaunchDarkly data source; hold flags are reset to off afterwards."""

    def _set(flag: FeatureFlag, value: bool):
        feature_flags.update(feature_flags.flag(str(flag)).variation_for_all(value))

    yield _set
    _set(FeatureFlag.QUEUE_EMAILS, False)
    _set(FeatureFlag.QUEUE_SMS, False)


def _capture_publish():
    published = []
    patcher = patch.object(
        queue,
        "publish",
        side_effect=lambda topic, payload, **_: published.append((topic, payload)),
    )
    return patcher, published


def _published_ids(published, topic=None) -> list[int]:
    return [
        json.loads(payload)["data"]["notificationId"]
        for published_topic, payload in published
        if topic is None or published_topic == topic
    ]


def _submit(api_client, auth_headers, request) -> tuple[dict, list]:
    path, body, _ = request
    patcher, published = _capture_publish()
    with patcher:
        response = api_client.post(path, json=body, headers=auth_headers(Role.SYSTEM.value))
    assert response.status_code == HTTPStatus.OK
    return response.json, published


def _resend(api_client, auth_headers) -> list:
    patcher, published = _capture_publish()
    with patcher:
        response = api_client.post("/api/v2/resend", json={}, headers=auth_headers(Role.SYSTEM.value))
    assert response.status_code == HTTPStatus.OK
    return published


def _age(api_app, notification_id: int, age: timedelta, status=None):
    with api_app.app_context():
        notification = db.session.get(Notification, notification_id)
        notification.request_date = datetime.now(UTC) - age
        if status:
            notification.status_code = status
        db.session.commit()


def _status(api_app, notification_id: int):
    with api_app.app_context():
        notification = db.session.get(Notification, notification_id)
        return notification.status_code if notification else None


@pytest.mark.parametrize(("flag", "request_data"), CHANNELS)
def test_flag_off_sends_immediately(api_app, api_client, auth_headers, set_flag, flag, request_data):
    set_flag(flag, False)

    body, published = _submit(api_client, auth_headers, request_data)

    assert body["notifyStatus"] == "QUEUED"
    assert _published_ids(published, request_data[2]) == [body["id"]]
    assert _status(api_app, body["id"]) == Notification.NotificationStatus.QUEUED


@pytest.mark.parametrize(("flag", "request_data"), CHANNELS)
def test_flag_on_holds_until_switched_off(api_app, api_client, auth_headers, set_flag, flag, request_data):
    topic = request_data[2]

    # ON: stored as HELD, nothing published, and the resend job leaves it alone.
    set_flag(flag, True)
    body, published = _submit(api_client, auth_headers, request_data)
    assert body["notifyStatus"] == "HELD"
    assert published == []

    notification_id = body["id"]
    # Older than the 48h resend window and the archive window: still held, never expired.
    _age(api_app, notification_id, timedelta(days=31))
    assert notification_id not in _published_ids(_resend(api_client, auth_headers))
    assert _status(api_app, notification_id) == Notification.NotificationStatus.HELD

    # OFF: the next resend run releases it regardless of age.
    set_flag(flag, False)
    assert notification_id in _published_ids(_resend(api_client, auth_headers), topic)
    with api_app.app_context():
        notification = db.session.get(Notification, notification_id)
        assert notification.status_code == Notification.NotificationStatus.QUEUED
        assert notification.retry_count == 1

    # Switching back ON holds new work only; the released notification is not held again.
    set_flag(flag, True)
    held_again, _ = _submit(api_client, auth_headers, request_data)
    assert held_again["notifyStatus"] == "HELD"
    assert _status(api_app, notification_id) == Notification.NotificationStatus.QUEUED


def test_released_email_is_delivered(api_app, api_client, auth_headers, delivery_smtp_client, set_flag):
    set_flag(FeatureFlag.QUEUE_EMAILS, True)
    body, _ = _submit(api_client, auth_headers, EMAIL)
    notification_id = body["id"]

    set_flag(FeatureFlag.QUEUE_EMAILS, False)
    published = _resend(api_client, auth_headers)
    payload = next(
        p for t, p in published if t == SMTP_TOPIC and json.loads(p)["data"]["notificationId"] == notification_id
    )

    envelope = {
        "subscription": "projects/e2e/subscriptions/smtp",
        "message": {"data": base64.b64encode(payload).decode()},
    }
    with patch("notify_delivery.services.providers.email_smtp.smtplib.SMTP") as smtp_class:
        smtp_server = smtp_class.return_value.__enter__.return_value
        push = delivery_smtp_client.post("/smtp/", json=envelope)

    assert push.status_code == HTTPStatus.OK
    smtp_server.sendmail.assert_called_once()
    assert _status(api_app, notification_id) is None
    with api_app.app_context():
        assert NotificationHistory.find_by_notification_id(notification_id).status_code == "SENT"


def test_hold_is_per_channel(api_app, api_client, auth_headers, set_flag):
    set_flag(FeatureFlag.QUEUE_EMAILS, True)

    email, _ = _submit(api_client, auth_headers, EMAIL)
    sms, sms_published = _submit(api_client, auth_headers, SMS)
    assert email["notifyStatus"] == "HELD"
    assert sms["notifyStatus"] == "QUEUED"
    assert _published_ids(sms_published) == [sms["id"]]

    # A failed SMS is still resent while email is held.
    _age(api_app, sms["id"], timedelta(hours=1), Notification.NotificationStatus.FAILURE)
    resent = _published_ids(_resend(api_client, auth_headers))
    assert sms["id"] in resent
    assert email["id"] not in resent


def test_both_flags_on_skip_resend_and_archive(api_app, api_client, auth_headers, set_flag):
    stale, _ = _submit(api_client, auth_headers, EMAIL)
    failed, _ = _submit(api_client, auth_headers, SMS)
    _age(api_app, stale["id"], timedelta(days=31))
    _age(api_app, failed["id"], timedelta(hours=1), Notification.NotificationStatus.FAILURE)

    set_flag(FeatureFlag.QUEUE_EMAILS, True)
    set_flag(FeatureFlag.QUEUE_SMS, True)
    assert _resend(api_client, auth_headers) == []
    assert _status(api_app, stale["id"]) == Notification.NotificationStatus.QUEUED
    assert _status(api_app, failed["id"]) == Notification.NotificationStatus.FAILURE

    set_flag(FeatureFlag.QUEUE_EMAILS, False)
    set_flag(FeatureFlag.QUEUE_SMS, False)
    assert failed["id"] in _published_ids(_resend(api_client, auth_headers))
    assert _status(api_app, stale["id"]) is None
    with api_app.app_context():
        assert NotificationHistory.find_by_notification_id(stale["id"]).status_code == "EXPIRED"

"""add HELD status

Revision ID: b72e0d5f8a31
Revises: a61d9c4e7f20
Create Date: 2026-11-04 00:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "b72e0d5f8a31"
down_revision = "a61d9c4e7f20"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "INSERT INTO notification_status VALUES("
        "'HELD', "
        "'Notification is held by the queue-emails/queue-sms flag and not yet sent', "
        "false)"
    )


def downgrade():
    op.execute("UPDATE notification SET status_code='QUEUED' WHERE status_code='HELD'")
    op.execute("DELETE FROM notification_status WHERE code='HELD'")

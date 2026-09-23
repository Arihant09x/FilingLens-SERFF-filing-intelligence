"""add extraction progress fields to documents"""

from alembic import op
import sqlalchemy as sa

revision = "0002_document_progress_fields"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    table_name = "documents"
    columns = [
        ("stage", sa.Column("stage", sa.String(length=64), nullable=True, server_default="queued")),
        ("message", sa.Column("message", sa.String(length=255), nullable=True)),
        ("job_id", sa.Column("job_id", sa.String(length=128), nullable=True)),
        ("attempt_count", sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0")),
        ("current_page", sa.Column("current_page", sa.Integer(), nullable=False, server_default="0")),
        ("total_pages", sa.Column("total_pages", sa.Integer(), nullable=True)),
        ("progress_percentage", sa.Column("progress_percentage", sa.Float(), nullable=False, server_default="0")),
        ("started_at", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True)),
        ("completed_at", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True)),
        ("last_progress_at", sa.Column("last_progress_at", sa.DateTime(timezone=True), nullable=True)),
        ("error_message", sa.Column("error_message", sa.String(length=500), nullable=True)),
    ]

    with op.batch_alter_table(table_name) as batch_op:
        for column_name, column in columns:
            if not _column_exists(bind, table_name, column_name):
                batch_op.add_column(column)


def downgrade() -> None:
    bind = op.get_bind()
    table_name = "documents"
    columns = [
        "error_message",
        "last_progress_at",
        "completed_at",
        "started_at",
        "progress_percentage",
        "total_pages",
        "current_page",
        "attempt_count",
        "job_id",
        "message",
        "stage",
    ]

    with op.batch_alter_table(table_name) as batch_op:
        for column_name in columns:
            if _column_exists(bind, table_name, column_name):
                batch_op.drop_column(column_name)

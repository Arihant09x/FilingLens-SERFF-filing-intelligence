"""create FilingLens tables"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("email", sa.String(320), nullable=False), sa.Column("hashed_password", sa.String(255), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("documents", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False), sa.Column("filename", sa.String(512), nullable=False), sa.Column("storage_key", sa.String(512), nullable=False), sa.Column("file_size", sa.Integer(), nullable=False), sa.Column("sha256", sa.String(64), nullable=False), sa.Column("page_count", sa.Integer()), sa.Column("status", sa.String(32), nullable=False), sa.Column("current_page", sa.Integer(), nullable=False), sa.Column("total_pages", sa.Integer()), sa.Column("progress_percentage", sa.Float(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_documents_user_id", "documents", ["user_id"])
    op.create_index("ix_documents_sha256", "documents", ["sha256"])
    op.create_index("ix_documents_status", "documents", ["status"])
    op.create_table("extraction_versions", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id"), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("strategy", sa.String(64), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("structured_data", sa.JSON(), nullable=False), sa.Column("confidence_summary", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_extraction_versions_document_id", "extraction_versions", ["document_id"])
    op.create_table("audit_events", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False), sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id")), sa.Column("event_type", sa.String(80), nullable=False), sa.Column("metadata", sa.JSON(), nullable=False), sa.Column("ip_address", sa.String(64)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_index("ix_extraction_versions_document_id", table_name="extraction_versions")
    op.drop_table("extraction_versions")
    op.drop_index("ix_documents_status", table_name="documents")
    op.drop_index("ix_documents_sha256", table_name="documents")
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
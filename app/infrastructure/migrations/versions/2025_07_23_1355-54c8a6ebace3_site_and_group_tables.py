"""Site and Group Tables

Revision ID: 54c8a6ebace3
Revises: a867097dafa8
Create Date: 2025-07-23 13:55:11.498280

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "54c8a6ebace3"
down_revision: str | None = "a867097dafa8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("group1", "group2", "group3", name="grouptypeenum"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_groups_id"), "groups", ["id"], unique=False)
    op.create_table(
        "sites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("country", sa.Enum("FR", "IT", name="countryenum"), nullable=False),
        sa.Column("installation_date", sa.Date(), nullable=False),
        sa.Column("max_power_megawatt", sa.Float(), nullable=False),
        sa.Column("min_power_megawatt", sa.Float(), nullable=False),
        sa.Column("useful_energy_at_1_megawatt", sa.Float(), nullable=True),
        sa.Column("efficiency", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sites_id"), "sites", ["id"], unique=False)
    op.create_table(
        "group_group",
        sa.Column("parent_group_id", sa.Integer(), nullable=False),
        sa.Column("child_group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["child_group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["parent_group_id"], ["groups.id"]),
        sa.PrimaryKeyConstraint("parent_group_id", "child_group_id"),
    )
    op.create_table(
        "site_group",
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"]),
        sa.PrimaryKeyConstraint("site_id", "group_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("site_group")
    op.drop_table("group_group")
    op.drop_index(op.f("ix_sites_id"), table_name="sites")
    op.drop_table("sites")
    op.drop_index(op.f("ix_groups_id"), table_name="groups")
    op.drop_table("groups")
    # ### end Alembic commands ###

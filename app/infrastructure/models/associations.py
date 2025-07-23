from infrastructure.db import Base
from sqlalchemy import Column, ForeignKey, Table

site_group_table = Table(
    "site_group",
    Base.metadata,
    Column("site_id", ForeignKey("sites.id"), primary_key=True),
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
)

group_group_table = Table(
    "group_group",
    Base.metadata,
    Column("parent_group_id", ForeignKey("groups.id"), primary_key=True),
    Column("child_group_id", ForeignKey("groups.id"), primary_key=True),
)

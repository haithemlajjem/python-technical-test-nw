import enum

from infrastructure.db import Base
from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship

from .associations import group_group_table, site_group_table


class GroupTypeEnum(str, enum.Enum):
    group1 = "group1"
    group2 = "group2"
    group3 = "group3"


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(GroupTypeEnum), nullable=False)

    sites = relationship(
        "Site",
        secondary=site_group_table,
        back_populates="groups",
        cascade="all, delete",
        lazy="selectin",  # <--- Eager load sites
    )

    child_groups = relationship(
        "Group",
        secondary=group_group_table,
        primaryjoin=id == group_group_table.c.parent_group_id,
        secondaryjoin=id == group_group_table.c.child_group_id,
        backref="parent_groups",
        cascade="all, delete",
        lazy="selectin",  # <--- Eager load child groups
    )

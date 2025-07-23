import enum

from infrastructure.db import Base
from sqlalchemy import Column, Date, Enum, Float, Integer, String
from sqlalchemy.orm import relationship

from .associations import site_group_table


class CountryEnum(str, enum.Enum):
    FR = "FR"
    DE = "DE"
    ES = "ES"
    IT = "IT"


class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(Enum(CountryEnum), nullable=False)
    installation_date = Column(Date, nullable=False)
    max_power_megawatt = Column(Float, nullable=False)
    min_power_megawatt = Column(Float, nullable=False)
    useful_energy_at_1_megawatt = Column(Float, nullable=True)
    efficiency = Column(Float, nullable=True)

    groups = relationship(
        "Group",
        secondary=site_group_table,
        back_populates="sites",
        lazy="selectin",  # Eager load groups
        cascade="all, delete",
    )

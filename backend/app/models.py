from sqlalchemy import Column, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from backend.app.db import Base


# Lookup table for age groups.
class AgeGroup(Base):
    __tablename__ = "age_group"

    age_group_id = Column(Integer, primary_key=True, index=True)
    age_bracket = Column(String(50), unique=True, nullable=False)

    # Relationship back to cancer incidence stats
    cancer_incidence_stats = relationship(
        "CancerIncidenceStat",
        back_populates="age_group",
    )

# Lookup table for cancer types.
class CancerType(Base):
    __tablename__ = "cancer_type"

    cancer_id = Column(Integer, primary_key=True, index=True)
    cancer_name = Column(String(255), unique=True, nullable=False)
    icd10_code = Column(String(20), nullable=True)

    # Relationship back to cancer incidence stats
    cancer_incidence_stats = relationship(
        "CancerIncidenceStat",
        back_populates="cancer_type",
    )


# Lookup table for sex values.
class Sex(Base):
    __tablename__ = "sex"

    sex_id = Column(Integer, primary_key=True, index=True)
    sex_label = Column(String(50), unique=True, nullable=False)

    # Relationship back to cancer incidence stats
    cancer_incidence_stats = relationship(
        "CancerIncidenceStat",
        back_populates="sex",
    )


# Main melanoma/cancer incidence statistics table.
# This table links to:
# - cancer_type
# - sex
# - age_groue
class CancerIncidenceStat(Base):
    __tablename__ = "cancer_incidence_stat"

    stat_id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    count = Column(Integer, nullable=True)
    incidence_rate = Column(Float, nullable=True)

    cancer_id = Column(Integer, ForeignKey("cancer_type.cancer_id"), nullable=True)
    sex_id = Column(Integer, ForeignKey("sex.sex_id"), nullable=True)
    age_group_id = Column(Integer, ForeignKey("age_group.age_group_id"), nullable=True)

    # Relationships to lookup tables
    cancer_type = relationship("CancerType", back_populates="cancer_incidence_stats")
    sex = relationship("Sex", back_populates="cancer_incidence_stats")
    age_group = relationship("AgeGroup", back_populates="cancer_incidence_stats")

# Lookup table for Australian states.
class State(Base):
    __tablename__ = "state"

    state_id = Column(Integer, primary_key=True, index=True)
    state_code = Column(String(10), unique=True, nullable=False)
    state_name = Column(String(100), nullable=False)

    # Relationship back to city
    cities = relationship("City", back_populates="state")

# City reference table with coordinates.
class City(Base):
    __tablename__ = "city"

    city_id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String(100), unique=True, nullable=False)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    state_id = Column(Integer, ForeignKey("state.state_id"), nullable=True)

    # Relationship to parent state
    state = relationship("State", back_populates="cities")

# Australia-wide yearly UV summary statistics table. This is the main table for the UV chart endpoint.
class UVIndexStat(Base):
    __tablename__ = "uv_index_stat"

    uv_stat_id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, unique=True, nullable=False, index=True)
    australian_uv_low = Column(Float, nullable=True)
    australian_uv_high = Column(Float, nullable=True)
    australian_uv_median = Column(Float, nullable=True)
from sqlalchemy.orm import Session

from backend.app import models

# Get all Australia-wide yearly UV summary rows.
def get_uv_year_summary(db: Session):
    return (
        db.query(models.UVIndexStat)
        .order_by(models.UVIndexStat.year.asc())
        .all()
    )

# Get melanoma incidence rows filtered by:
# - cancer name
# - sex label
# - age bracket
# - year range

def get_melanoma_incidence(
    db: Session,
    cancer_name: str,
    sex_label: str,
    age_bracket: str,
    year_from: int,
    year_to: int,
):
    return (
        db.query(models.CancerIncidenceStat)
        .join(models.CancerType, models.CancerIncidenceStat.cancer_id == models.CancerType.cancer_id)
        .join(models.Sex, models.CancerIncidenceStat.sex_id == models.Sex.sex_id)
        .join(models.AgeGroup, models.CancerIncidenceStat.age_group_id == models.AgeGroup.age_group_id)
        .filter(models.CancerType.cancer_name == cancer_name)
        .filter(models.Sex.sex_label == sex_label)
        .filter(models.AgeGroup.age_bracket == age_bracket)
        .filter(models.CancerIncidenceStat.year >= year_from)
        .filter(models.CancerIncidenceStat.year <= year_to)
        .order_by(models.CancerIncidenceStat.year.asc())
        .all()
    )

# Get all age-group dropdown options.
def get_age_groups(db: Session):
    return (
        db.query(models.AgeGroup)
        .order_by(models.AgeGroup.age_group_id.asc())
        .all()
    )
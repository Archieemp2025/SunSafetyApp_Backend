import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app import crud, schemas
from backend.app.db import get_db


# Basic logger for request validation and unexpected failures.
logger = logging.getLogger(__name__)


# Router for melanoma-related endpoints.-
router = APIRouter(
    prefix="/api/melanoma",
    tags=["Melanoma"],
)

# Allowed values for current MVP.
ALLOWED_SEX_VALUES = {"Persons", "Males", "Females"}

ALLOWED_AGE_BRACKETS = {
    "00-09",
    "10-19",
    "20-29",
    "30-39",
    "40-49",
    "50-59",
    "60-69",
    "70-79",
    "80-89",
    "90+",
}

# Return melanoma incidence rows filtered by:
# - sex
# - age_group
# - year range
# The cancer type is fixed to "Melanoma of the skin" because that is the current product scope for the frontend
@router.get("/incidence", response_model=List[schemas.MelanomaIncidenceResponse])
def get_melanoma_incidence(
    sex: str = Query(
        ...,
        min_length=1,
        max_length=50,
        description="Sex filter, for example: Persons",
    ),
    age_group: str = Query(
        ...,
        min_length=1,
        max_length=50,
        description="Age-group filter, for example: 20-29",
    ),
    year_from: int = Query(
        ...,
        ge=2007,
        le=2023,
        description="Start year for the incidence query",
    ),
    year_to: int = Query(
        ...,
        ge=2007,
        le=2023,
        description="End year for the incidence query",
    ),
    db: Session = Depends(get_db),
):
    # Validate supported sex values. This prevents unexpected values and keeps behavior predictable.-
    if sex not in ALLOWED_SEX_VALUES:
        logger.warning("Invalid sex filter received: %s", sex)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sex value. Allowed values: {sorted(ALLOWED_SEX_VALUES)}",
        )
    
    if age_group not in ALLOWED_AGE_BRACKETS:
        logger.warning("Invalid age_group filter received: %s", age_group)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid age_group value. Allowed values: {sorted(ALLOWED_AGE_BRACKETS)}",
        )
    
    # Validate year range ordering.
    if year_from > year_to:
        logger.warning(
            "Invalid year range received: year_from=%s, year_to=%s",
            year_from,
            year_to,
        )
        raise HTTPException(
            status_code=400,
            detail="year_from must be less than or equal to year_to.",
        )

    # Query the database for melanoma incidence rows.
    rows = crud.get_melanoma_incidence(
        db=db,
        cancer_name="Melanoma of the skin",
        sex_label=sex,
        age_bracket=age_group,
        year_from=year_from,
        year_to=year_to,
    )

    # Return a clean frontend-ready response shape.
    return [
        schemas.MelanomaIncidenceResponse(
            year=row.year,
            count=row.count,
        )
        for row in rows
    ]
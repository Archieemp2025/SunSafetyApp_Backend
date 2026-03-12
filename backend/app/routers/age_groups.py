from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app import crud, schemas
from backend.app.db import get_db

# Router for age-group related endpoints.
router = APIRouter(
    prefix="/api/age-groups",
    tags=["Age Groups"],
)

# Return all age-group options from the database.
@router.get("", response_model=List[schemas.AgeGroupResponse])
def get_age_groups(db: Session = Depends(get_db)):
    return crud.get_age_groups(db)
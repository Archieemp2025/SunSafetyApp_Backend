from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app import crud, schemas
from backend.app.db import get_db

# Router for UV-related endpoints.
router = APIRouter(
    prefix="/api/uv",
    tags=["UV"],
)

# Return all Australia-wide yearly UV summary rows.
@router.get("/year-summary", response_model=List[schemas.UVYearSummaryResponse])
def get_uv_year_summary(db: Session = Depends(get_db)):
    return crud.get_uv_year_summary(db)
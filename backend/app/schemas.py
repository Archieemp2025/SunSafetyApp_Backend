from typing import Optional

from pydantic import BaseModel, ConfigDict

# Response schema for a single Australia-wide yearly UV summary row.
class UVYearSummaryResponse(BaseModel):
    year: int
    australian_uv_low: Optional[float] = None
    australian_uv_high: Optional[float] = None
    australian_uv_median: Optional[float] = None

    # Allow Pydantic to read values directly from SQLAlchemy model objects
    model_config = ConfigDict(from_attributes=True)


# Response schema for a single melanoma incidence row.
class MelanomaIncidenceResponse(BaseModel):
    year: int
    count: Optional[int] = None

    # Allow Pydantic to read values directly from SQLAlchemy model objects
    model_config = ConfigDict(from_attributes=True)

# Response schema for myth-buster cards shown on the first page.
class MythBusterResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    tagline: Optional[str] = None

# Detailed response schema for a single myth-buster share view.
class MythBusterDetailResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    tagline: Optional[str] = None
    share_url: str

# Response schema for age-group dropdown options.
class AgeGroupResponse(BaseModel):
    age_group_id: int
    age_bracket: str

    # Allow Pydantic to read values directly from SQLAlchemy model objects
    model_config = ConfigDict(from_attributes=True)
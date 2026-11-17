from pydantic import BaseModel, Field
from datetime import datetime, timezone

class JobPosting(BaseModel):
    """
    Pydantic class that guarantees that what we kept from the job posting has the correct type and that required fields exists.
    """
    # Identification
    source: str = "af"
    source_id: str
    url: str | None = None
    title: str

    # Dates
    published: datetime | None = None
    last_published: datetime | None = None
    deadline: datetime | None = None
    removed: bool = False

    # Description
    description: str = ""

    # Employment conditions
    employment_type: str | None = None
    duration: str | None = None
    working_hours: str | None = None
    salary_type: str | None = None

    # Classification
    occupation: str | None = None

    # Employer
    employer: str | None = None
    municipality: str | None = None
    employer_url: str |None = None
    
    # Application
    apply_url: str | None = None

    # Metadata
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
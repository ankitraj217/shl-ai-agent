"""Internal catalog data models."""

from pydantic import BaseModel, Field


class Assessment(BaseModel):
    """Normalized SHL assessment catalog item."""

    entity_id: str
    name: str
    url: str
    description: str = ""
    job_levels: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    duration: str = ""
    remote: str = ""
    adaptive: str = ""
    search_text: str = ""

    @property
    def test_type(self) -> str:
        """Return the public test type string."""
        return ", ".join(self.categories) if self.categories else "Assessment"


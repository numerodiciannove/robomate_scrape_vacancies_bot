from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SiteConfig:
    base_url: str
    selectors: dict[str, str]


@dataclass
class CV:
    name: str
    age: Optional[int]
    skills: List[str]
    location: str
    education: bool
    additional_education_exists: bool
    languages_exist: bool
    additional_info: bool
    salary: Optional[int]
    url: str
    rating: int = 0

    def calculate_rating(self) -> None:
        """Calculate the rating of the CV based on its attributes."""
        rating = 0

        if self.age:
            if 25 <= self.age <= 35:
                rating += 2
            elif 36 <= self.age <= 45:
                rating += 1

        rating += len(self.skills) * 2

        if self.education:
            rating += 3

        if self.additional_education_exists:
            rating += 2

        if self.languages_exist:
            rating += 2

        if self.additional_info:
            rating += 1

        if self.salary:
            rating += 1

        self.rating = rating

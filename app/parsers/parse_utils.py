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
    languages_exist: bool = None
    additional_info: bool = None
    salary: Optional[int] = None
    url: str = None
    photo: str = None
    rating: int = 0

    def calculate_rating(self) -> None:
        """Calculate the rating of the CV based on its attributes."""
        rating = 0

        if self.age:
            if 25 <= self.age <= 35:
                rating += 3
            elif 36 <= self.age <= 45:
                rating += 2
            else:
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

        if self.photo:
            rating += 19

        self.rating = rating

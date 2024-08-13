from typing import List, Dict, Any
from attr import dataclass
import requests
import json
import re
from parse_utils import CV


@dataclass
class GenericApiScraper:
    base_url: str
    resumes_endpoint: str
    city_list_endpoint: str
    headers: dict
    experience_catigories: dict

    def _fetch_data(self, url, params=None) -> Any:
        if params:
            response = requests.post(url, headers=self.headers, data=json.dumps(params))
        else:
            response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Error fetching data: {response.status_code} - {response.text}"
            )

    def get_city_list(self) -> str:
        url = self.base_url + self.city_list_endpoint
        return self._fetch_data(url)

    def get_city_id_by_name(self, city_name: str) -> int:
        cities = self.get_city_list()
        key = "nameUkr"

        for city in cities:
            if city[key].lower() == city_name.lower():
                return int(city["id"])
        raise Exception(f"City '{city_name}' not found.")

    def get_resumes(
        self, position: str, city_name: str, experience_label=None
    ) -> None | Any:
        try:
            city_id = self.get_city_id_by_name(city_name)
        except Exception as e:
            print(f"An error occurred while getting city ID: {e}")
            return

        experience_ids = []

        if experience_label:
            experience_ids.append(self.experience_catigories.get(experience_label, "0"))

        url = self.base_url + self.resumes_endpoint
        
        params = {
            "page": 0,
            "period": "ThreeMonths",
            "sort": "Score",
            "searchType": "skills",
            "ukrainian": True,
            "SearchContext": "Main",
            "cityId": city_id,
            "experienceIds": experience_ids,
            "keyWords": position,
        }

        return self._fetch_data(url, params)

    def create_cv_from_resume(self, resume: Dict) -> CV:
        """Convert a resume dictionary to a CV dataclass instance."""

        def extract_age(age_str: str) -> int:
            match = re.search(r"\d+", age_str)
            return int(match.group()) if match else None

        def process_photo_url(photo_url: str) -> str:
            """Process photo URL and return None if the URL contains 'None'."""
            return photo_url if photo_url and "None" not in photo_url else None

        return CV(
            name=resume.get("fullName", "Unknown"),
            age=extract_age(resume.get("age", "")),
            location=resume.get("cityName", "Unknown"),
            skills=resume.get("skills", []),
            education=resume.get("education", False),
            additional_education_exists=resume.get(
                "additional_education_exists", False
            ),
            languages_exist=resume.get("languages_exist", False),
            photo=process_photo_url(resume.get("photo", "")),
            url=(resume.get("url", "No URL")).replace("/cv/", "/candidates/"),
        )

    def get_top_5_cv(self, resumes: List[Dict]) -> List[CV]:
        """Rank resumes based on CV attributes and return the top 5 as CV objects."""
        # Convert resumes to CV dataclass instances
        cv_list = [self.create_cv_from_resume(resume) for resume in resumes]

        # Calculate ratings for each CV
        for cv in cv_list:
            cv.calculate_rating()

        # Sort CVs by rating in descending order
        ranked_cvs = sorted(cv_list, key=lambda x: x.rating, reverse=True)

        # Return the top 5 resumes
        return ranked_cvs[: min(len(ranked_cvs), 5)]

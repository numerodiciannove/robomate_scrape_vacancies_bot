import requests
import json
from typing import List, Dict
import re
from app.parsers.parse_utils import CV 


class RabotaUaAPI:
    BASE_URL = "https://employer-api.rabota.ua/"
    RESUMES_ENDPOINT = "cvdb/resumes"
    CITY_LIST_ENDPOINT = "values/citylist"
    HEADERS = {
        'Content-Type': 'application/json',
    }

    EXPERIENCE_DICT = {
        "Без досвіду": "0",
        "До 1 року": "1",
        "Від 1 до 2 років": "2",
        "Від 2 до 5 років": "3",
        "Від 5 до 10 років": "4",
        "Більше 10 років": "5"
    }

    def _fetch_data(self, url, params=None):
        if params:
            response = requests.post(url, headers=self.HEADERS, data=json.dumps(params))
        else:
            response = requests.get(url, headers=self.HEADERS)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    def get_city_list(self):
        url = self.BASE_URL + self.CITY_LIST_ENDPOINT
        return self._fetch_data(url)

    def get_city_id_by_name(self, city_name: str):
        cities = self.get_city_list()
        key = 'nameUkr'
        
        for city in cities:
            if city[key].lower() == city_name.lower():
                return city['id']
        raise Exception(f"City '{city_name}' not found.")

    def get_resumes(self, position: str, city_name: str, experience_label=None):
        try:
            city_id = self.get_city_id_by_name(city_name)
        except Exception as e:
            print(f"An error occurred while getting city ID: {e}")
            return

        experience_ids = []
        if experience_label:
            experience_ids.append(self.EXPERIENCE_DICT.get(experience_label, "0"))

        url = self.BASE_URL + self.RESUMES_ENDPOINT
        params = {
            "page": 0,
            "period": "ThreeMonths",
            "sort": "UpdateDate",
            "searchType": "everywhere",
            "ukrainian": True,
            "cityId": city_id,
            "experienceIds": experience_ids,
            "keyWords": position
        }

        return self._fetch_data(url, params)
    
    def create_cv_from_resume(self, resume: Dict) -> CV:
        """Convert a resume dictionary to a CV dataclass instance."""
        
        def extract_age(age_str: str) -> int:
            # Используйте регулярное выражение для извлечения чисел из строки
            match = re.search(r'\d+', age_str)
            return int(match.group()) if match else None
        
        def process_photo_url(photo_url: str) -> str:
            """Process photo URL and return None if the URL contains 'None'."""
            return photo_url if photo_url and 'None' not in photo_url else None

        return CV(
            name=resume.get('fullName', 'Unknown'),
            age=extract_age(resume.get('age', '')),
            location=resume.get('cityName', 'Unknown'),
            skills=resume.get('skills', []),
            education=resume.get('education', False),
            additional_education_exists=resume.get('additional_education_exists', False),
            languages_exist=resume.get('languages_exist', False),
            photo=process_photo_url(resume.get('photo', '')),
            url=resume.get('url', 'No URL')
        )

    def rank_resumes(self, resumes: List[Dict]) -> List[CV]:
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

# Example usage:
if __name__ == "__main__":
    rabota_ua_api = RabotaUaAPI()
    
    position = "python Django"
    city_name = "Київ"
    experience_label = "Від 5 до 10 років"

    resumes_result = rabota_ua_api.get_resumes(position, city_name, experience_label)
    print(resumes_result)
    total_count = resumes_result.get("total")
    
    print(f"Total number of resumes: {total_count}")
    
    top_cvs = rabota_ua_api.rank_resumes(resumes_result.get('documents', []))
    print(top_cvs)

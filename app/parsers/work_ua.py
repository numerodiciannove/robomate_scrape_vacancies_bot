from dataclasses import dataclass
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote

WORK_UA_RESUMES_URL = "https://www.work.ua/resumes-"
EXPERIENCE_CATEGORIES = {
    "Без досвіду": 0,
    "До 1 року": 1,
    "Від 1 до 2 років": 164,
    "Від 2 до 5 років": 165,
    "Понад 5 років": 166,
}


@dataclass
class CV:
    name: str
    age: int
    skills: list[str]
    location: str
    education: bool
    additional_education_exists: bool
    languages_exist: bool
    additional_info: bool
    salary: int
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


class WorkUaScraper:
    CV_CARD_SELECTOR = (
        "div.card.card-hover.card-search.resume-link.card-visited.wordwrap"
    )
    NAME_SELECTOR = "h1.mt-0.mb-0"
    AGE_SELECTOR = "dl.dl-horizontal dt:-soup-contains('Вік:') + dd"
    LOCATION_SELECTOR = "dl.dl-horizontal dt:-soup-contains('Місто проживання:') + dd"
    SALARY_SELECTOR = "span.text-muted-print"
    SKILLS_SELECTOR = "ul.list-unstyled li span.ellipsis"
    EDUCATION_SELECTOR = "h2:-soup-contains('Освіта')"
    ADDITIONAL_EDUCATION_SELECTOR = (
        "h2:-soup-contains('Додаткова освіта та сертифікати')"
    )
    LANGUAGES_SELECTOR = "h2:-soup-contains('Знання мов')"
    ADDITIONAL_INFO_SELECTOR = "h2:-soup-contains('Додаткова інформація')"

    def __init__(
        self, position: str, location: str = None, experience: str = None
    ) -> None:
        self.position = position
        self.location = location
        self.experience = experience

    def create_url_from_query(self, page=1) -> str:
        """Generate the URL for a specific query."""
        base_url = WORK_UA_RESUMES_URL

        if self.position:
            position_encoded = quote(self.position)
            if self.location:
                location_encoded = quote(self.location)
                position_encoded += "+" + location_encoded
            base_url += f"{position_encoded}/"

        query_params = []

        if self.experience:
            experience_encoded = str(
                EXPERIENCE_CATEGORIES.get(self.experience, self.experience)
            )
            query_params.append(f"experience={experience_encoded}")

        if page > 1:
            query_params.append(f"page={page}")

        full_url = base_url + "?" + "&".join(query_params) if query_params else base_url
        return full_url

    async def fetch_page(self, session, url: str) -> str:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            print(f"Error fetching {url}: {e}")
            return ""

    async def extract_cv_urls(self, html: str) -> list[str]:
        try:
            soup = BeautifulSoup(html, "html.parser")
            product_cards = soup.select(self.CV_CARD_SELECTOR)
            return [
                f"https://www.work.ua{card.find('a')['href']}" for card in product_cards
            ]
        except Exception as e:
            print(f"Error extracting CV URLs: {e}")
            return []

    async def get_total_pages(self, session, url: str) -> int:
        html = await self.fetch_page(session, url)
        try:
            soup = BeautifulSoup(html, "html.parser")
            pagination = soup.select_one("ul.pagination.hidden-xs")
            if pagination:
                last_page_link = pagination.select("a")[-2]
                return int(last_page_link.get_text())
        except Exception as e:
            print(f"Error extracting total pages: {e}")
        return 1

    async def process_page_range(self, page_range: range) -> list[str]:
        async with aiohttp.ClientSession() as session:
            urls = []
            for page in page_range:
                url = self.create_url_from_query(page=page)
                html = await self.fetch_page(session, url)
                page_urls = await self.extract_cv_urls(html)
                urls.extend(page_urls)
            return urls

    async def get_all_cv_urls(self) -> list[str]:
        async with aiohttp.ClientSession() as session:
            first_page_url = self.create_url_from_query(page=1)
            total_pages = await self.get_total_pages(session, first_page_url)

        num_processes = min(os.cpu_count(), total_pages)
        page_ranges = [
            range(i, total_pages + 1, num_processes)
            for i in range(1, num_processes + 1)
        ]

        tasks = [self.process_page_range(page_range) for page_range in page_ranges]
        results = await asyncio.gather(*tasks)
        return [url for result in results for url in result]

    async def extract_cv_data(self, session, url: str) -> CV:
        html = await self.fetch_page(session, url)
        soup = BeautifulSoup(html, "html.parser")

        try:
            name = self.extract_text(soup, self.NAME_SELECTOR)
            age = self.extract_age(soup)
            location = self.extract_text(soup, self.LOCATION_SELECTOR)
            salary = self.extract_salary(soup)
            skills = self.extract_skills(soup)

            return CV(
                name=name,
                age=age,
                skills=skills,
                location=location,
                salary=salary,
                education=self.exists(soup, self.EDUCATION_SELECTOR),
                additional_education_exists=self.exists(
                    soup, self.ADDITIONAL_EDUCATION_SELECTOR
                ),
                additional_info=self.exists(soup, self.ADDITIONAL_INFO_SELECTOR),
                languages_exist=self.exists(soup, self.LANGUAGES_SELECTOR),
                url=url,
            )
        except Exception as e:
            print(f"Error extracting CV data from {url}: {e}")
            return CV(
                name="Unknown",
                age=None,
                skills=[],
                location="Unknown",
                education=False,
                additional_education_exists=False,
                languages_exist=False,
                additional_info=False,
                salary=None,
                url=url,
            )

    def extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        tag = soup.select_one(selector)
        return tag.get_text(strip=True) if tag else "Unknown"

    def extract_age(self, soup: BeautifulSoup) -> int:
        age_text = self.extract_text(soup, self.AGE_SELECTOR)
        if age_text and age_text.split()[0].isdigit():
            return int(age_text.split()[0])
        return None

    def extract_salary(self, soup: BeautifulSoup) -> int:
        salary_text = self.extract_text(soup, self.SALARY_SELECTOR)
        if salary_text:
            # Remove any non-digit characters
            salary_digits = "".join(filter(str.isdigit, salary_text))
            return int(salary_digits) if salary_digits else None
        return None

    def extract_skills(self, soup: BeautifulSoup) -> list[str]:
        return [
            tag.get_text(strip=True)
            for tag in soup.select(self.SKILLS_SELECTOR)
            if tag.get_text(strip=True)
        ]

    def exists(self, soup: BeautifulSoup, selector: str) -> bool:
        return soup.select_one(selector) is not None

    async def get_all_cv_data(self, cv_urls: list[str]) -> list[CV]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.extract_cv_data(session, url) for url in cv_urls]
            return await asyncio.gather(*tasks)

    def get_top_5_cv(self, cv_data: list[CV]) -> list[CV]:
        """Get the top 5 CVs based on their rating."""
        cv_data.sort(key=lambda x: x.rating, reverse=True)
        return cv_data[: min(len(cv_data), 5)]


if __name__ == "__main__":
    position = "Кухар"
    location = "Київ"
    experience = "Від 2 до 5 років"

    async def main() -> None:
        scraper = WorkUaScraper(
            position=position, location=location, experience=experience
        )
        urls = await scraper.get_all_cv_urls()
        cv_data = await scraper.get_all_cv_data(urls)
        for cv in cv_data:
            cv.calculate_rating()

        top_5_cv = scraper.get_top_5_cv(cv_data)
        for cv in top_5_cv:
            print(
                f"Name: {cv.name}, Rating: {cv.rating}, URL: {cv.url}, Age: {cv.age}, Salary: {cv.salary}"
            )

    asyncio.run(main())

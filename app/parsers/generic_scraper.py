from dataclasses import dataclass
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup

from typing import Callable, List, Optional
from parse_utils import SiteConfig, CV


class GenericScraper:
    def __init__(
        self,
        config: SiteConfig,
        experience_categories: dict[str, int],
        position: str,
        location: str = None,
        experience: str = None,
        url_generator = Callable
    ) -> None:
        self.config = config
        self.url_generator = url_generator
        self.experience_categories = experience_categories
        self.position = position
        self.location = location
        self.experience = experience

    def create_url_from_query(self, page: int = 1) -> str:
        """Generate the URL for a specific query with pagination."""
        url = self.url_generator(position=self.position, location=self.location, experience=self.experience, page=page)
        return url

    async def get_page_html(self, session, url: str) -> str:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            print(f"Error fetching {url}: {e}")
            return ""

    async def extract_cv_urls(self, html: str) -> List[str]:
        base_url = self.config.base_url.replace("-", "")
        try:
            soup = BeautifulSoup(html, "html.parser")
            cv_cards = soup.select(self.config.selectors["cv_card"])
            return [
                f"{base_url}{card.find('a')['href']}" for card in cv_cards
            ]
        except Exception as e:
            print(f"Error extracting CV URLs: {e}")
            return []

    async def get_total_pages(self, session, url: str) -> int:
        html = await self.get_page_html(session, url)
        try:
            soup = BeautifulSoup(html, "html.parser")
            pagination = soup.select_one(self.config.selectors["paginator"])
            if pagination:
                last_page_link = pagination.select("a")[-2]
                return int(last_page_link.get_text())
        except Exception as e:
            print(f"Error extracting total pages: {e}")
        return 1

    async def process_page_range(self, page_range: range) -> List[str]:
        async with aiohttp.ClientSession() as session:
            urls = []
            for page in page_range:
                url = self.create_url_from_query(page=page)
                html = await self.get_page_html(session, url)
                page_urls = await self.extract_cv_urls(html)
                urls.extend(page_urls)
            return urls

    async def get_all_cv_urls(self) -> List[str]:
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
        html = await self.get_page_html(session, url)
        soup = BeautifulSoup(html, "html.parser")

        try:
            name = self.extract_text(soup, self.config.selectors["name"])
            age = self.extract_age(soup)
            location = self.extract_text(soup, self.config.selectors["location"])
            salary = self.extract_salary(soup)
            skills = self.extract_skills(soup)

            return CV(
                name=name,
                age=age,
                skills=skills,
                location=location,
                salary=salary,
                education=self.exists(soup, self.config.selectors["education"]),
                additional_education_exists=self.exists(
                    soup, self.config.selectors["additional_education"]
                ),
                additional_info=self.exists(
                    soup, self.config.selectors["additional_info"]
                ),
                languages_exist=self.exists(soup, self.config.selectors["languages"]),
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

    def extract_age(self, soup: BeautifulSoup) -> Optional[int]:
        age_text = self.extract_text(soup, self.config.selectors["age"])
        if age_text and age_text.split()[0].isdigit():
            return int(age_text.split()[0])
        return None

    def extract_salary(self, soup: BeautifulSoup) -> Optional[int]:
        salary_text = self.extract_text(soup, self.config.selectors["salary"])
        if salary_text:
            # Remove any non-digit characters
            salary_digits = "".join(filter(str.isdigit, salary_text))
            return int(salary_digits) if salary_digits else None
        return None

    def extract_skills(self, soup: BeautifulSoup) -> List[str]:
        return [
            tag.get_text(strip=True)
            for tag in soup.select(self.config.selectors["skills"])
            if tag.get_text(strip=True)
        ]

    def exists(self, soup: BeautifulSoup, selector: str) -> bool:
        return soup.select_one(selector) is not None

    async def get_all_cv_data(self, cv_urls: List[str]) -> List[CV]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.extract_cv_data(session, url) for url in cv_urls]
            return await asyncio.gather(*tasks)

    def get_top_5_cv(self, cv_data: List[CV]) -> List[CV]:
        """Get the top 5 CVs based on their rating."""
        cv_data.sort(key=lambda x: x.rating, reverse=True)
        return cv_data[: min(len(cv_data), 5)]


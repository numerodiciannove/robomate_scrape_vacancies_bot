from dataclasses import dataclass, fields
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


QUOTE_FIELDS = [field.name for field in fields(CV)]


def create_url_from_query(position: str, location=None, experience=None, page=1) -> str:
    """Generate the URL for a specific query."""
    base_url = WORK_UA_RESUMES_URL

    if position:
        position_encoded = quote(position)
        if location:
            location_encoded = quote(location)
            position_encoded += "+" + location_encoded
        base_url += f"{position_encoded}/"

    query_params = []

    if experience:
        if isinstance(experience, list):
            experience_encoded = "+".join(
                str(EXPERIENCE_CATEGORIES.get(exp, exp)) for exp in experience
            )
        else:
            experience_encoded = str(EXPERIENCE_CATEGORIES.get(experience, experience))
        query_params.append(f"experience={experience_encoded}")

    if page > 1:
        query_params.append(f"page={page}")

    full_url = base_url
    if query_params:
        full_url += "?" + "&".join(query_params)

    return full_url


async def fetch_page(session, url) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def extract_cv_urls(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    product_cards = soup.select(
        "div.card.card-hover.card-search.resume-link.card-visited.wordwrap"
    )

    urls = []
    for card in product_cards:
        link_element = card.find("a")
        href = link_element["href"]
        if not href.startswith("http"):
            href = f"https://www.work.ua{href}"
        urls.append(href)

    return urls


async def get_total_pages(session, url) -> int:
    html = await fetch_page(session, url)
    soup = BeautifulSoup(html, "html.parser")
    pagination = soup.select_one("ul.pagination.hidden-xs")
    if pagination:
        last_page_link = pagination.select("a")[-2]
        return int(last_page_link.get_text())
    return 1


async def process_page_range(
    position: str, location: str, experience: list[str], page_range: range
) -> list[str]:
    urls = []
    async with aiohttp.ClientSession() as session:
        for page in page_range:
            url = create_url_from_query(
                position=position, location=location, experience=experience, page=page
            )
            html = await fetch_page(session, url)
            page_urls = await extract_cv_urls(html)
            urls.extend(page_urls)
    return urls


async def get_all_cv_urls(
    position: str, location: str = None, experience: str = None
) -> list[str]:
    async with aiohttp.ClientSession() as session:
        first_page_url = create_url_from_query(
            position=position, location=location, experience=experience, page=1
        )
        total_pages = await get_total_pages(session, first_page_url)

    num_processes = min(os.cpu_count(), total_pages)
    page_ranges = [
        range(i, total_pages + 1, num_processes) for i in range(1, num_processes + 1)
    ]

    tasks = [
        process_page_range(position, location, experience, page_range)
        for page_range in page_ranges
    ]
    results = await asyncio.gather(*tasks)

    all_urls = [url for result in results for url in result]
    return all_urls


async def extract_cv_data(session, url: str) -> CV:
    html = await fetch_page(session, url)
    soup = BeautifulSoup(html, "html.parser")

    # Extracting name
    name_tag = soup.select_one("h1.mt-0.mb-0")
    name = name_tag.get_text(strip=True) if name_tag else None

    # Extracting age
    age_tag = soup.select_one("dl.dl-horizontal dt:-soup-contains('Вік:') + dd")
    age_text = age_tag.get_text(strip=True) if age_tag else None
    age = (
        int(age_text.split()[0]) if age_text and age_text.split()[0].isdigit() else None
    )

    # Extracting location
    location_tag = soup.select_one(
        "dl.dl-horizontal dt:-soup-contains('Місто проживання:') + dd"
    )
    location = location_tag.get_text(strip=True) if location_tag else None

    # Extracting salary
    salary_tag = soup.select_one("span.text-muted-print")
    salary_text = salary_tag.get_text(strip=True) if salary_tag else None
    if salary_text:
        salary = int("".join(filter(str.isdigit, salary_text)))
    else:
        salary = None

    # Extracting skills
    skills = []
    skill_tags = soup.select("ul.list-unstyled li span.ellipsis")
    for tag in skill_tags:
        skill = tag.get_text(strip=True)
        if skill:
            skills.append(skill)

    # Check if education exists
    education_exists = soup.select_one("h2:-soup-contains('Освіта')") is not None

    # Check if additional education and certifications exists
    additional_education_exists = (
        soup.select_one("h2:-soup-contains('Додаткова освіта та сертифікати')")
        is not None
    )

    # Check if languages exists
    languages_exist = soup.select_one("h2:-soup-contains('Знання мов')") is not None

    # Check if additional info exists
    additional_info = (
        soup.select_one("h2:-soup-contains('Додаткова інформація')") is not None
    )

    return CV(
        name=name,
        age=age,
        skills=skills,
        location=location,
        salary=salary,
        education=education_exists,
        additional_education_exists=additional_education_exists,
        additional_info=additional_info,
        languages_exist=languages_exist,
        url=url,
    )


async def get_all_cv_data(cv_urls: list[str]) -> dict:
    async with aiohttp.ClientSession() as session:
        tasks = [extract_cv_data(session, url) for url in cv_urls]
        cv_data = await asyncio.gather(*tasks)
    return cv_data


if __name__ == "__main__":
    position = "graphic designer"
    location = "Вінниця"
    experience = "Від 2 до 5 років"

    async def main():
        urls = await get_all_cv_urls(
            position=position, location=location, experience=experience
        )
        cv_data = await get_all_cv_data(urls)
        print(cv_data)

    asyncio.run(main())

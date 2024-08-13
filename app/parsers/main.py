import asyncio
from typing import List, Callable
from parse_utils import CV
from generic_scraper import GenericScraper
from generic_api_scraper import GenericApiScraper
from site_configs.work_ua import (
    WORK_UA_CONFIG,
    WORK_UA_EXPERIENCE_CATEGORIES,
    work_ua_url_generator,
)
from site_configs.rabota_ua import (
    RABOTA_UA_BASE_URL,
    RABOTA_UA_RESUMES_ENDPOINT,
    RABOTA_UA_CITY_LIST_ENDPOINT,
    RABOTA_UA_HEADERS,
    RABOTA_UA_EXPERIENCE_DICT,
)


async def get_work_ua_top_5_cvs(
    position: str,
    location: str,
    experience: str,
    url_generator: Callable = work_ua_url_generator,
) -> List[CV]:
    """Fetch top 5 CVs from Work.ua based on position, location, and experience."""
    scraper = GenericScraper(
        config=WORK_UA_CONFIG,
        experience_categories=WORK_UA_EXPERIENCE_CATEGORIES,
        position=position,
        location=location,
        experience=experience,
        url_generator=url_generator,
    )
    urls = await scraper.get_all_cv_urls()
    cv_data = await scraper.get_all_cv_data(urls)
    for cv in cv_data:
        cv.calculate_rating()

    return scraper.get_top_5_cv(cv_data)


def get_rabota_ua_top_5_cvs(
    canditate_position: str,
    canditate_city: str,
    canditate_experience: str,
    base_api_url: str,
    resumes_endpoint: str,
    city_list_api_endpoint: str,
    headers: dict,
    experience_categories: dict,
) -> List[CV]:
    """Fetch top 5 CVs from Rabota.ua based on candidate's position, city, and experience."""
    rabota_ua_api = GenericApiScraper(
        base_url=base_api_url,
        resumes_endpoint=resumes_endpoint,
        city_list_endpoint=city_list_api_endpoint,
        headers=headers,
        experience_catigories=experience_categories,
    )

    resumes_result = rabota_ua_api.get_resumes(
        position=canditate_position,
        city_name=canditate_city,
        experience_label=canditate_experience,
    )

    top_5_cvs = rabota_ua_api.get_top_5_cv(resumes_result.get("documents", []))

    return top_5_cvs


async def test_parsers() -> None:
    position = "python"
    skills = "python Django"
    location = "Київ"
    experience = "Від 2 до 5 років"

    # Fetch top 5 CVs from Work.ua
    work_ua_top_5_cv = await get_work_ua_top_5_cvs(
        position=position,
        location=location,
        experience=experience,
        url_generator=work_ua_url_generator,
    )

    # Fetch top 5 CVs from Rabota.ua
    rabota_ua_top_5_cv = get_rabota_ua_top_5_cvs(
        canditate_position=skills,
        canditate_city=location,
        canditate_experience=experience,
        base_api_url=RABOTA_UA_BASE_URL,
        resumes_endpoint=RABOTA_UA_RESUMES_ENDPOINT,
        city_list_api_endpoint=RABOTA_UA_CITY_LIST_ENDPOINT,
        headers=RABOTA_UA_HEADERS,
        experience_categories=RABOTA_UA_EXPERIENCE_DICT,
    )

    print("\n\nWORK.UA TOP 5 --------->\n\n", work_ua_top_5_cv)
    print("\n\nRABOTA.UA TOP 5 --------->\n\n", rabota_ua_top_5_cv)


if __name__ == "__main__":
    asyncio.run(test_parsers())

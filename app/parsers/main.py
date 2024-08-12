import asyncio
from typing import List, Callable
from parse_utils import CV
from generic_scraper import GenericScraper
from site_configs.work_ua import WORK_UA_CONFIG, WORK_UA_EXPERIENCE_CATEGORIES, work_ua_url_generator

async def get_work_ua_top_5_cvs(position: str, location: str, experience: str, url_generator: Callable = work_ua_url_generator) -> List[CV]:
    '''Arguments are required because the server's IP may be banned for making too many requests. Alternatively, you can use a proxy.'''
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


async def get_rabota_ua_top_5_cvs(position: str, location: str, experience: str) -> List[CV]:
    pass


if __name__ == "__main__":
    position = "кухар"
    location = "Київ"
    experience = "Від 2 до 5 років"

    work_ua_top_5_cv = asyncio.run(get_work_ua_top_5_cvs(position=position, location=location, experience=experience, url_generator=work_ua_url_generator))
    print(work_ua_top_5_cv)

    # rabota_ua_top_5_cv = asyncio.run(get_rabota_ua_top_5_cvs(position=position, location=location, experience="", url_generator=rabota_ua_url_generator))
    # print(rabota_ua_top_5_cv)

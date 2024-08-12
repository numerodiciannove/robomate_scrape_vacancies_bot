import asyncio
from typing import List
from generic_scraper import CV
from generic_scraper import GenericScraper
from site_configs.work_ua import WORK_UA_CONFIG, EXPERIENCE_CATEGORIES

async def get_work_ua_cvs(position: str, location: str, experience: str) -> List[CV]:
    scraper = GenericScraper(
        config=WORK_UA_CONFIG,
        experience_categories=EXPERIENCE_CATEGORIES,
        position=position,
        location=location,
        experience=experience,
    )
    urls = await scraper.get_all_cv_urls()
    cv_data = await scraper.get_all_cv_data(urls)
    for cv in cv_data:
        cv.calculate_rating()

    return scraper.get_top_5_cv(cv_data)

if __name__ == "__main__":
    position = "Python"
    location = "Київ"
    experience = "Від 2 до 5 років"

    work_ua_top_5_cv = asyncio.run(get_work_ua_cvs(position=position, location=location, experience=experience))

    for cv in work_ua_top_5_cv:
        print(
            f"Name: {cv.name}, Rating: {cv.rating}, URL: {cv.url}, Age: {cv.age}, Salary: {cv.salary}"
        )

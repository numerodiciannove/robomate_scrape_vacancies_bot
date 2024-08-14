from urllib.parse import quote, urljoin

from app.parsers.parse_utils import SiteConfig

WORK_UA_BASE_URL = "https://www.work.ua"
WORK_UA_RESUMES_URL = urljoin(WORK_UA_BASE_URL, "resumes-")

WORK_UA_EXPERIENCE_CATEGORIES = {
    "Без досвіду": 0,
    "До 1 року": 1,
    "Від 1 до 2 років": 164,
    "Від 2 до 5 років": 165,
    "Понад 5 років": 166,
}


def work_ua_url_generator(
        position: str,
        location=None,
        experience=None, page=1
) -> str:
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
                str(
                    WORK_UA_EXPERIENCE_CATEGORIES.get(exp, exp)
                ) for exp in experience
            )
        else:
            experience_encoded = str(
                WORK_UA_EXPERIENCE_CATEGORIES.get(experience, experience)
            )
        query_params.append(f"experience={experience_encoded}")

    if page > 1:
        query_params.append(f"page={page}")

    full_url = base_url
    if query_params:
        full_url += "?" + "&".join(query_params)

    return full_url


WORK_UA_CONFIG = SiteConfig(
    base_url=WORK_UA_BASE_URL,
    selectors={
        "cv_card": (
            "div.card.card-hover.card-search.resume-link.card-visited.wordwrap"
        ),
        "name": "h1.mt-0.mb-0",
        "age": "dl.dl-horizontal dt:-soup-contains('Вік:') + dd",
        "location": (
            "dl.dl-horizontal dt:-soup-contains('Місто проживання:') + dd"
        ),
        "salary": "span.text-muted-print",
        "skills": "ul.list-unstyled li span.ellipsis",
        "education": "h2:-soup-contains('Освіта')",
        "additional_education": (
            "h2:-soup-contains('Додаткова освіта та сертифікати')"
        ),
        "languages": "h2:-soup-contains('Знання мов')",
        "additional_info": "h2:-soup-contains('Додаткова інформація')",
        "paginator": "ul.pagination.hidden-xs",
    },
)

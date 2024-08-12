from dataclasses import dataclass
from utils import SiteConfig

WORK_UA_CONFIG = SiteConfig(
    base_url="https://www.work.ua/resumes-",
    selectors={
        "cv_card": "div.card.card-hover.card-search.resume-link.card-visited.wordwrap",
        "name": "h1.mt-0.mb-0",
        "age": "dl.dl-horizontal dt:-soup-contains('Вік:') + dd",
        "location": "dl.dl-horizontal dt:-soup-contains('Місто проживання:') + dd",
        "salary": "span.text-muted-print",
        "skills": "ul.list-unstyled li span.ellipsis",
        "education": "h2:-soup-contains('Освіта')",
        "additional_education": "h2:-soup-contains('Додаткова освіта та сертифікати')",
        "languages": "h2:-soup-contains('Знання мов')",
        "additional_info": "h2:-soup-contains('Додаткова інформація')",
    },
)

EXPERIENCE_CATEGORIES = {
    "Без досвіду": 0,
    "До 1 року": 1,
    "Від 1 до 2 років": 164,
    "Від 2 до 5 років": 165,
    "Понад 5 років": 166,
}

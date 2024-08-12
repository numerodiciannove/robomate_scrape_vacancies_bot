from dataclasses import dataclass


@dataclass
class SiteConfig:
    base_url: str
    selectors: dict[str, str]

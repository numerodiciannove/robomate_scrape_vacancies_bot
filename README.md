# CV Parser Telegram Bot

This is a python-based web scraper, designed to extract data from major job portals (work.ua, rabota.ua) and find the most suitable job vacancies based on user requirements.
Bot provides the top 5 candidates based on a custom rating from the logic application.

You can also use the scraping functionality without the bot. To do this, navigate to the directory app/parsers/main.py and use the function def test_parsers(), which allows you to get the top 5 best vacancies from the sites rabota.ua and work.ua.
In the response, you will receive a list of CV objects with the necessary data.

## Installation:


1. **Clone the repository:**
   ```bash
   git clone https://github.com/numerodiciannove/robomate_scrape_vacancies_bot
   
2. **Create and activate virtual environment:**
    ```bash
   python -m venv venv
   source venv/bin/activate (on macOS)
    venv\Scripts\activate (on Windows)

3. **Install dependencies:**
   ```bash
    pip install -r requirements.txt

3. **Rename .env.sample to .env and edit it with you telegram params**
   
4. **Navigate to bot directory:**
    ```bash
   cd app/telegram_bot

5. **Run Bot on your server:**
   ```bash
   python main.py

important Class Descriptions
------------------

### **GenericApiScraper**

A class for interacting with an API that provides candidate resumes. It supports fetching a list of cities, finding city IDs by their names, and extracting and ranking resumes based on specified parameters.

**Methods:**

-   **`_fetch_data(url, params=None)`**: Performs a GET or POST request to the specified URL and returns the response data in JSON format. If parameters are provided, a POST request is made; otherwise, a GET request is performed.

-   **`get_city_list()`**: Retrieves a list of cities from the API.

-   **`get_city_id_by_name(city_name: str) -> int`**: Finds the city ID by its name. Raises an exception if the city is not found.

-   **`get_resumes(position: str, city_name: str, experience_label=None) -> None | Any`**: Extracts resumes based on the position, city, and experience. Returns JSON data or None if an error occurs.

-   **`create_cv_from_resume(resume: Dict) -> CV`**: Converts a resume dictionary into a CV object.

-   **`get_top_5_cv(resumes: List[Dict]) -> List[CV]`**: Ranks resumes based on their attributes and returns the top 5 as CV objects.

### **GenericScraper**

A class for scraping and processing CV data from a website. It fetches CV URLs, extracts detailed CV data, and ranks the CVs based on their attributes.

**Methods:**

-   **`__init__(self, config: SiteConfig, experience_categories: dict[str, int], position: str, location: str = None, experience: str = None, url_generator=Callable)`**: Initializes the scraper with site configuration, experience categories, position, location, experience, and a URL generator.

-   **`create_url_from_query(self, page: int = 1) -> Callable`**: Generates the URL for a specific query with pagination.

-   **`async get_page_html(session, url: str) -> str`**: Asynchronously fetches the HTML content of a webpage given its URL.

-   **`async extract_cv_urls(self, html: str) -> List[str]`**: Extracts CV URLs from the HTML content of a page.

-   **`async get_total_pages(self, session, url: str) -> int`**: Retrieves the total number of pages available for the query.

-   **`async process_page_range(self, page_range: range) -> List[str]`**: Processes a range of pages to extract all CV URLs from each page.

-   **`async get_all_cv_urls(self) -> List[str]`**: Retrieves all CV URLs by processing all pages in the search results.

-   **`async extract_cv_data(self, session, url: str) -> CV`**: Extracts detailed CV data from a given CV URL.

-   **`static extract_text(soup: BeautifulSoup, selector: str) -> str`**: Extracts text content from a given selector.

-   **`def extract_age(self, soup: BeautifulSoup) -> Optional[int]`**: Extracts the age from the CV if available.

-   **`def extract_salary(self, soup: BeautifulSoup) -> Optional[int]`**: Extracts the salary from the CV if available.

-   **`def extract_skills(self, soup: BeautifulSoup) -> List[str]`**: Extracts a list of skills from the CV.

-   **`def exists(self, soup: BeautifulSoup, selector: str) -> bool`**: Checks if a certain element exists in the CV based on the selector.

-   **`async get_all_cv_data(self, cv_urls: List[str]) -> tuple[Any]`**: Fetches and extracts detailed data from all CV URLs.

-   **`def get_top_5_cv(self, cv_data: List[CV]) -> List[CV]`**: Retrieves the top 5 CVs based on their rating.

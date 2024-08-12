import requests
import json

def fetch_resumes(api_url, params):
    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(params))
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

def main():
    api_url = 'https://employer-api.rabota.ua/cvdb/resumes'
    
    # Ввод данных пользователем
    job_title = input("Введите должность (например, 'водитель'): ")

    # Параметры запроса с настройками по умолчанию
    params = {
        "page": 0,
        "period": "ThreeMonths",
        "sort": "UpdateDate",
        "searchType": "default",
        "ukrainian": False,
        "onlyDisliked": False,
        "onlyFavorite": False,
        "onlyWithCurrentNotebookNotes": False,
        "showCvWithoutSalary": True,
        "sex": "female",
        "cityId": 0,
        "inside": False,
        "onlyNew": False,
        "age": {
            "from": 0,
            "to": 0
        },
        "salary": {
            "from": 0,
            "to": 0
        },
        "moveability": True,
        "onlyMoveability": False,
        "rubrics": [],
        "languages": [],
        "scheduleIds": [],
        "educationIds": [],
        "branchIds": [],
        "experienceIds": [
            "4"
        ],
        "keyWords": job_title,
        "hasPhoto": False,
        "onlyViewed": False,
        "onlyWithOpenedContacts": False,
        "resumeFillingTypeIds": [],
        "districtIds": [],
        "onlyStudents": False,
        "searchContext": "Filters"
    }
    
    try:
        result = fetch_resumes(api_url, params)
        print(json.dumps(result, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict

def get_dou_vacancies(
    search_query: str,
    max_vacancies: int = 20,
    delay: float = 0.5,
    desc_length: int = 500  # 👈 Максимальная длина описания
) -> List[Dict]:
    """
    Получает вакансии с сайта DOU.ua по поисковому запросу.
    
    Args:
        search_query (str): поисковый запрос.
        max_vacancies (int): максимальное количество вакансий для парсинга.
        delay (float): задержка между запросами к страницам вакансий.
        desc_length (int): максимальная длина текста описания (в символах).
        
    Returns:
        list of dict: список вакансий с полями title, company, city, salary, link, description.
    """
    base_url = "https://jobs.dou.ua/vacancies/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(f"{base_url}?search={search_query.replace(' ', '+')}", headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    vacancies = soup.select("li.l-vacancy")
    results = []
    
    for vac in vacancies[:max_vacancies]:
        title_tag = vac.select_one("a.vt")
        company_tag = vac.select_one("a.company")
        city_tag = vac.select_one("span.cities")
        salary_tag = vac.select_one("span.salary")

        title = title_tag.text.strip() if title_tag else "-"
        link = title_tag["href"] if title_tag else "-"
        company = company_tag.text.strip() if company_tag else "-"
        city = city_tag.text.strip() if city_tag else "-"
        salary = salary_tag.text.strip() if salary_tag else "-"

        # --- Получаем описание вакансии ---
        description = "-"
        if link != "-":
            try:
                vac_response = requests.get(link, headers=headers, timeout=10)
                vac_soup = BeautifulSoup(vac_response.text, "html.parser")
                desc_tag = vac_soup.select_one("div.vacancy-section")
                if desc_tag:
                    full_text = desc_tag.get_text(separator="\n").strip()
                    # Обрезаем описание, если слишком длинное
                    description = (full_text[:desc_length] + "...") if len(full_text) > desc_length else full_text
            except Exception as e:
                print(f"Ошибка при получении описания {link}: {e}")
            time.sleep(delay)

        results.append({
            "title": title,
            "company": company,
            "location": city,
            "salary": salary,
            "link": link,
            "description": description
        })
    
    return results

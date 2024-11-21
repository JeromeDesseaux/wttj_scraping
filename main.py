import argparse
import csv
import os
import re
import time
import traceback

from playwright.sync_api import sync_playwright

# Configurations globales
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
RESULTS_PER_PAGE = 32
TIMEOUT = 30000  # Timeout pour les sélecteurs


# Fonction pour assainir les noms de fichiers
def sanitize_filename(filename):
    return re.sub(r"[^a-zA-Z0-9_\-\.]", "_", filename)


# Fonction pour vérifier/créer les dossiers
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Extraire les détails d'un job
def scrape_job_details(page, url, retries=3):
    for attempt in range(retries):
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT)

            if response.status != 200:
                print(f"Skipping {url}: HTTP {response.status}")
                return None

            page.wait_for_selector(
                'div[data-testid*="job-metadata-block"]', timeout=TIMEOUT
            )

            job_details = {
                "company_name": page.query_selector(
                    'a[href*="/fr/companies/"] span'
                ).inner_text()
                if page.query_selector('a[href*="/fr/companies/"] span')
                else None,
                "remote": page.query_selector('i[name="remote"]').inner_text()
                if page.query_selector('i[name="remote"]')
                else None,
                "description": page.query_selector(
                    'div[id="the-position-section"]'
                ).inner_text()
                if page.query_selector('div[id="the-position-section"]')
                else None,
                "location": page.query_selector(
                    'i[name="location"] + span'
                ).inner_text()
                if page.query_selector('i[name="location"] + span')
                else None,
                "salary": page.query_selector('i[name="salary"] + span').inner_text()
                if page.query_selector('i[name="salary"] + span')
                else None,
                "experience": page.query_selector(
                    'i[name="suitcase"] + span'
                ).inner_text()
                if page.query_selector('i[name="suitcase"] + span')
                else None,
                "url": url,
            }

            # Filter out unwanted lines
            if (
                not job_details["company_name"]
                or job_details["company_name"].lower() == "qui sommes-nous ?"
            ):
                return None

            return job_details
        except Exception as e:
            print(f"Error on attempt {attempt + 1} for {url}: {e}")

            filename_base = sanitize_filename(url.split("/")[-1].split("?")[0])

            # Save stack trace
            ensure_directory_exists("error_logs")
            with open(
                f"error_logs/{filename_base}_stacktrace.log", "w", encoding="utf-8"
            ) as f:
                f.write("Error occurred while processing the following URL:\n")
                f.write(f"{url}\n\n")
                f.write("Stack Trace:\n")
                f.write(traceback.format_exc())

            # Save screenshot for debugging
            ensure_directory_exists("screenshots")
            page.screenshot(path=f"screenshots/{filename_base}.png")

            if attempt + 1 == retries:
                return None
            time.sleep(2)  # Delay before retrying


# Extraire les liens pour une requête spécifique
def scrape_links_for_query(page, query, debug):
    url = f"https://www.welcometothejungle.com/fr/jobs?query={query}&refinementList%5Bremote%5D%5B%5D=fulltime"
    all_links = []

    page.goto(url)

    total_results = extract_total_results(page) or 0
    total_pages = 1 if debug else -(-total_results // RESULTS_PER_PAGE)
    print(
        f"Nombre total de résultats pour '{query}' : {total_results}, Pages attendues : {total_pages}"
    )

    for page_number in range(1, total_pages + 1):
        print(f"Scraping page {page_number} for query '{query}'...")
        current_page_url = f"{url}&page={page_number}"
        page.goto(current_page_url)

        page.wait_for_selector(
            '[data-testid="search-results-list-item-wrapper"]', timeout=TIMEOUT
        )

        links = page.eval_on_selector_all(
            "a", "elements => elements.map(el => el.href)"
        )
        links = [
            link for link in links if "/fr/companies/" in link and "/jobs/" in link
        ]
        all_links.extend(list(set(links)))

    return list(set(all_links))


# Extraire le nombre total de résultats
def extract_total_results(page):
    page.wait_for_selector(
        'div[data-testid="jobs-search-results-count"]', timeout=TIMEOUT
    )
    total_results_text = page.query_selector(
        'div[data-testid="jobs-search-results-count"]'
    ).inner_text()
    total_results = int("".join(filter(str.isdigit, total_results_text)))
    return total_results


# Fonction principale
def main():
    parser = argparse.ArgumentParser(description="Scrape job listings from WTTJ")
    parser.add_argument(
        "-q",
        "--queries",
        nargs="+",
        required=True,
        help="List of job queries to scrape",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Limit scraping to one page per query",
    )
    parser.add_argument(
        "-o", "--output", default="wttj_jobs_details.csv", help="Output CSV file"
    )
    args = parser.parse_args()

    all_job_details = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=USER_AGENT,
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        page = context.new_page()

        for query in args.queries:
            print(f"Scraping jobs for query: {query}")
            links = scrape_links_for_query(page, query, args.debug)
            for link in links:
                job_details = scrape_job_details(page, link)
                if job_details:
                    all_job_details.append(job_details)

        # Write to CSV
        csv_columns = [
            "company_name",
            "remote",
            "description",
            "location",
            "salary",
            "experience",
            "url",
        ]
        with open(args.output, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            writer.writerows(all_job_details)

        print(f"Data has been written to {args.output}")


if __name__ == "__main__":
    main()

Here's a `README.md` file to help set up and run your project:

```markdown
# Job Scraper

This project scrapes job listings from Welcome to the Jungle (WTTJ) based on specified queries and outputs the results into a CSV file. It uses `playwright` for web scraping and `poetry` for dependency management.

## Requirements

- Python 3.8+
- [Poetry](https://python-poetry.org/) for dependency management
- Chromium browser (required by Playwright)

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository_url>
cd scrape
```

### 2. Install dependencies

Use `poetry` to set up the Python environment and install the required dependencies:

```bash
poetry install
```

### 3. Install Playwright browsers

Install the necessary Playwright browsers (Chromium):

```bash
poetry run playwright install
```

## Usage

Run the script using `poetry` with the following command:

```bash
poetry run python main.py -q "backend" "fullstack" "développeur" -d -o output_jobs.csv
```

### Parameters

- `-q, --queries`: **(Required)** List of job queries to scrape (e.g., "backend", "frontend").
- `-d, --debug`: **(Optional)** If set, limits scraping to one page per query for faster debugging.
- `-o, --output`: **(Optional)** Output CSV file name. Defaults to `wttj_jobs_details.csv`.

### Example

To scrape jobs for "backend", "frontend", and "data engineer" into a file called `jobs.csv`, and limit to one page per query:

```bash
poetry run python main.py -q "backend" "frontend" "data engineer" -d -o jobs.csv
```

## File Structure

- **`main.py`**: The main script for scraping.
- **`.venv/`**: The virtual environment directory (ignored in version control).
- **`error_logs/`**: Directory where error logs are stored (e.g., stack traces).
- **`screenshots/`**: Directory for screenshots of failed pages.

## Output

The output file is a CSV containing the following fields:

- `company_name`
- `remote`
- `description`
- `location`
- `salary`
- `experience`
- `url`

## Debugging

If the scraper encounters an error:

- Stack traces are saved in `error_logs/`.
- Screenshots of failed pages are saved in `screenshots/`.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
```

This file includes:
- Setup instructions for `poetry` and Playwright.
- Details on how to use the script with example commands.
- Information about debugging and file structure.
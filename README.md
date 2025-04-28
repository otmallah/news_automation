# News Scraping and Analysis Tool

This tool automatically scrapes news articles from BBC News, filters them based on a specific theme (e.g., Artificial Intelligence), and stores them in a database.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- OpenAI API key

## Setup Instructions

### 1. Database Setup

Create a new database and user:

```sql
CREATE DATABASE news_db;
CREATE USER news_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE news_db TO news_user;
```

### 2. Environment Setup

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=news_db
DB_USER=news_user
DB_PASSWORD=your_password

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### 3. Python Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Project Structure

```
news_automation/
├── main.py              # Main scraping script
├── db_adapter.py        # Database operations
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables
```

## Usage

1. Ensure your PostgreSQL database is running
2. Verify your `.env` file is properly configured
3. Run the script:

```bash
python main.py
```

The script will:

- Connect to BBC News
- Scrape articles from the previous day
- Filter articles based on the specified theme
- Store relevant articles in the database

## Output

The script will:

- Log progress and any errors to the console
- Store filtered articles in the PostgreSQL database
- Each article includes:
  - Title
  - URL
  - Publication date
  - Content
  - Source
  - Relevance status

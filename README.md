
# AI Job-Search Agent

## Project Overview
The AI Job-Search Agent is a Python application built with Streamlit. It allows users to enter a candidate profile, add job postings, search saved postings, and compare candidate skills with skills found in job descriptions.

## Features
- Candidate profile input
- Manual job posting entry
- Search and location filtering
- Basic skill matching and potential skill-gap detection
- Separate job-match scoring function
- Automated unit tests for scoring

## Technologies
- Python
- Streamlit
- Pandas
- Regular expressions
- Unittest

## Project Files
- `app.py` — Streamlit user interface and job-search features
- `matching.py` — Job-match scoring function
- `test_matching.py` — Automated tests for scoring
- `README.md` — Project documentation
- `.gitignore` — Files excluded from Git

## Run Locally
1. Create and activate a Python virtual environment.
2. Install the required packages:
   `python -m pip install streamlit pandas`
3. Start the application:
   `python -m streamlit run app.py`

## Run Tests
Execute:
`python -m unittest -v test_matching.py`

## Scoring Rules
- Must requirement weight: 2
- Nice requirement weight: 1
- Strong skill level: 2
- Basic skill level: 1
- None skill level: 0
- Fit threshold: 70% or higher

The score is calculated from earned points divided by maximum possible points, multiplied by 100.

## Current Limitations
- Job postings are entered manually.
- Job postings and candidate information are stored in the current Streamlit session.
- Skill matching is a basic keyword-based check.
- This prototype does not automatically apply for jobs.

## Skill Matching Rules

- Skill names are matched as complete terms to avoid false matches inside other words.
- Excel recognizes these aliases: Excel, MS Excel, Microsoft Excel.
- Power BI recognizes these aliases: Power BI, Microsoft Power BI.
- SQL, MySQL, and NoSQL are treated as separate skills.
- A job requiring MySQL or NoSQL does not automatically count as requiring SQL.
- The matching logic is a basic keyword check and does not determine a candidate's actual proficiency.

## Job Matching Scoring

The application calculates job match scores using:

- Must requirement weight: 2
- Nice requirement weight: 1
- Basic skill level: 1
- Strong skill level: 2
- None skill level: 0

Points = Requirement Weight ×
(min(Your Skill Level, Required Level) / Required Level)

A match score of 70% or higher is classified as Fit.

Users can review and change the suggested requirement type
and required skill level before calculating the score.

## Unit Test Results

All 4 unit tests passed successfully.

- Must, Basic, Basic: 2/2
- Must, Strong, Basic: 1/2
- Nice, Basic, None: 0/1
- Complete example: 6.5/9 = 72.2% (Fit)
# AI-Powered UX Evaluation Agent

An intelligent tool that automatically evaluates websites against UX best practices and heuristics, providing detailed reports and actionable insights.

## Problem Statement

Conducting heuristic evaluations of websites is a crucial part of UX strategy and redesigns. However, the process is highly manual, requiring page-by-page checks against UX frameworks like Nielsen's 10 Heuristics.

## Solution

This AI-powered UX agent can:

- Automatically assess a website's UX against known best practices
- Detect usability issues and provide insights
- Generate reports that streamline the UX evaluation process
- Reduce the time and effort required for UX analysis

## Features

- **Website Crawler**: Automatically navigates through website pages
- **Screenshot Capture**: Takes screenshots of pages for visual analysis
- **DOM Analysis**: Examines HTML structure for accessibility and usability issues
- **Heuristic Evaluation**: Applies Nielsen's 10 Heuristics and other UX frameworks
- **AI Analysis Engine**: Uses advanced AI models to identify UX issues
- **Comprehensive Reporting**: Generates detailed reports with actionable insights
- **Visual Annotations**: Highlights problem areas directly on screenshots

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: React.js
- **AI/ML**: Gemini AI
- **Web Crawling**: Playwright
- **Database**: MongoDB for storing evaluation results
- **Reporting**: PDF generation with ReportLab

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 16+
- MongoDB

### Installation

1. Clone the repository
2. Create a python env: `python3 -m venv env`
3. Install backend dependencies: `pip install -r requirements.txt`
4. Install frontend dependencies: `cd frontend && npm install`
5. Set up environment variables (see `.env.example`)
6. Start the backend server: `python app.py`
7. Start the frontend development server: `cd frontend && npm start`

## Usage

1. Enter the URL of the website to evaluate
2. Select evaluation criteria and depth of analysis
3. Start the evaluation process
4. View the generated report with identified issues and recommendations

## License

MIT

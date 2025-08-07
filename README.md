# Publication Log

A comprehensive system for managing, tracking, and archiving research publications related to projects executed on the BA-HPC. The Publication Log streamlines follow-ups, automates archiving, and harvests new publications, providing a centralized solution for researchers and administrators alike.

---

## Table of Contents
- [Features](#features)
- [Components](#components)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [License](#license)

## Features

### 1. Follow-up
- Notifies researchers via email when a project is nearing its end.
- Email contains a gentle reminder and a link for researchers to add their publications.
- Ensures timely publication logging by sending automated follow-ups.

### 2. Archive
- If a researcher uploads only the URL for a publication (without a PDF), the system tries to download the PDF from the given link.
- If the PDF can't be found, the system notifies the researcher to upload the publication's PDF.
- Uses the follow-up notification system to check whether the required PDF has been uploaded.

### 3. Harvest
- Periodically crawls selected domains (URIs) known to host research publications.
- Matches found publications to BA-HPC project metadata (Author, Published Date, Title, Abstract, etc.).
- Ensures that only publications after the project's acceptance date are considered.
- Adds matched publications to the project log and notifies relevant researchers.

---

## Components

- **Notification Service**: Sends automated emails to researchers for follow-ups and reminders.
- **Archiving Engine**: Downloads publication PDFs or requests uploads if unavailable.
- **Harvesting Module**: Crawls pre-defined publication sources and matches them with project data.
- **User Interface**: Allows researchers to view, add, and manage their publications (implemented with JavaScript, HTML, and CSS).
- **Backend/API**: Handles logic for notifications, archiving, and harvesting (implemented with Python and JavaScript).
- **Database**: Stores projects, researchers, and publication records.

---

## How It Works

1. **Project Tracking**: Each project is tracked with metadata (researcher, dates, etc.).
2. **Follow-up & Notifications**: As project deadlines approach, automated emails prompt researchers to update their publication records.
3. **Publication Submission**: Researchers can add publications (with URL and/or PDF).
4. **Archiving**: The system attempts to download PDFs from submitted URLs; if that fails, reminders are sent for manual PDF uploads.
5. **Harvesting**: The system regularly scans external publication sites, matches found publications against project data, and adds them to the log if relevant.

---

## Technology Stack
- **Frontend**: JavaScript, HTML, CSS
- **Backend**: Python, JavaScript
- **Database**: (Specify your database here, e.g., MySQL, PostgreSQL)
- **Email Service**: (Specify service, e.g., SMTP, SendGrid)
- **Web Crawling**: (Specify library, e.g., BeautifulSoup, Scrapy)

---

## Project Structure

- `/frontend` - User interface components (JavaScript, HTML, CSS)
- `/backend` - Logic for notifications, archiving, and harvesting (Python, JavaScript)
- `/database` - Database models and migration scripts
- `/docs` - Documentation

---

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/BasantAwad/Publication_Log.git
   ```
2. **Install dependencies:**
   - Frontend: See `/frontend/README.md`
   - Backend: See `/backend/README.md`
3. **Set up the database:**
   - Configure your database settings in `/backend/config`
   - Run migration scripts if necessary
4. **Configure email and harvesting settings:**
   - Add your SMTP or email service credentials
   - List publication source domains in the config
5. **Run the application:**
   - Start backend and frontend servers

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
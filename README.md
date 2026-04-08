# StyleSync

StyleSync is a full-stack application that scrapes style/color data, allows users to edit tokens/colors, and preview changes dynamically. The backend is built with FastAPI, the frontend is vanilla HTML/JS/CSS, and PostgreSQL is used for storing data.  

---

## **Table of Contents**

- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Setup Instructions](#setup-instructions)  
- [Running Locally](#running-locally)  
- [Deployment](#deployment)  
- [Frontend Testing](#frontend-testing)  
- [Contributing](#contributing)  
- [License](#license)  

---

## **Features**

- Scrape style/color data from external sources  
- Token editor for colors  
- Preview scraped or edited styles  
- Full backend API with `/test` endpoint  
- PostgreSQL database integration  

---

## **Tech Stack**

- **Backend:** Python, FastAPI, Uvicorn  
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** PostgreSQL (local or Render-hosted)  
- **Deployment:** Render  

---

## **Setup Instructions**

### 1. Clone the repository

```bash
git clone https://github.com/<yourusername>/stylesync-backend.git
cd stylesync-backend

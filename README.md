#  Flight Finder

A real-world **Flight Search & Delay Risk Analysis application** built to explore live flight data through APIs and transform it into a usable web application.

The project combines **JavaScript, Python, FastAPI, API integration, data exploration, and Machine Learning** to demonstrate how real-world API data can be collected, processed, analyzed, and presented to users.

---

##  Project Objective

The main objective of this project is to understand and explore how **live flight information can be accessed through an API**, how API responses can be analyzed, and how that data can be converted into useful insights for users.

Instead of working only with static datasets, this project focuses on the workflow:

**API → Data Retrieval → Data Exploration → Data Processing → ML Prediction → UI**

---

##  What I Explored

During this project, I explored the complete API-based data workflow:

* Understanding API documentation and endpoints
* Sending requests to an external flight-data service
* Passing parameters such as flight number and date
* Receiving structured JSON responses
* Exploring the API response and its nested data
* Extracting useful flight information from JSON
* Handling API responses inside a Python backend
* Connecting the backend API with a JavaScript frontend
* Working with real-world flight information
* Using the collected information for delay-risk analysis

The project was developed as an **API exploration and real-world data analysis project**, rather than simply displaying a static dataset.

---

##  Features

###  Live Flight Search

Search flight information using:

* Flight number
* Travel date
* API-based flight search

Live searches are retrieved through **SerpApi**.

###  Flight Information

The application processes available flight information and presents it through a clean two-page JavaScript interface.

###  Delay Risk Prediction

A small Machine Learning model provides an estimated delay-risk percentage.

>  The current model is trained on generated demo data for project demonstration. It should **not** be used for real operational flight decisions.

For production use, the model should be retrained using properly licensed historical airline on-time performance data.

###  FastAPI Backend

Python **FastAPI** is used as the backend layer responsible for:

* API requests
* Data processing
* Flight search logic
* ML prediction
* Frontend/backend communication

---

##  Project Architecture

```text
User
 │
 ▼
JavaScript Frontend
 │
 ▼
FastAPI Backend
 │
 ├── Flight Search
 │       │
 │       ▼
 │    SerpApi
 │       │
 │       ▼
 │    JSON Response
 │
 ├── Data Processing
 │
 └── ML Delay Risk Model
          │
          ▼
     Prediction
          │
          ▼
     Frontend UI
```

---

##  Tech Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* FastAPI
* Uvicorn

### API

* SerpApi
* JSON
* REST API concepts

### Data & ML

* Python
* Pandas
* Scikit-learn
* Machine Learning

---

##  Project Structure

```text
Flight-Finder/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   └── ib5634_serpapi.json
│
├── static/
│   ├── index.html
│   ├── ...
│
└── ...
```

---

##  API Configuration

Create a SerpApi API key and configure it as an environment variable.

### PowerShell

```powershell
$env:SERPAPI_API_KEY = "your_serpapi_key"
```

The application uses this key when performing live flight searches.

---

##  Run Locally

### 1. Clone the repository

```powershell
git clone <your-repository-url>
cd Flight-Finder
```

### 2. Create virtual environment

```powershell
python -m venv .venv
```

### 3. Activate environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure API key

```powershell
$env:SERPAPI_API_KEY = "your_serpapi_key"
```

### 6. Start FastAPI

```powershell
uvicorn app:app --reload
```

### 7. Open application

```text
http://127.0.0.1:8000
```

---

##  Demo / Offline Exploration

A sample API response for flight **IB5634** is included in:

```text
data/ib5634_serpapi.json
```

This bundled response allows the application to demonstrate the API-response processing workflow without requiring a live API request.

Choose:

```text
Flight: IB5634
Date: 2026-04-23
```

to explore the supplied sample response.

---

##  API Exploration Workflow

One of the main learning outcomes of this project was understanding how an external API can be explored and integrated into a real application.

The workflow was:

```text
1. Identify the API
        ↓
2. Understand API parameters
        ↓
3. Send API request
        ↓
4. Receive JSON response
        ↓
5. Explore JSON structure
        ↓
6. Extract required fields
        ↓
7. Clean / transform data
        ↓
8. Send processed data to frontend
        ↓
9. Apply ML-based delay-risk estimation
        ↓
10. Display results
```

This helped me understand the practical difference between working with a **static dataset** and consuming **real-world API-generated data**.

---

##  Machine Learning Component

The application contains a small delay-risk model that produces an estimated probability/percentage of flight delay.

The current model is trained using **generated demonstration data**, so the prediction should be considered a technical demonstration only.

For a production-grade system, the model would require:

* Historical flight data
* Airline-specific performance data
* Airport information
* Departure/arrival patterns
* Weather information
* Historical delay records
* Proper feature engineering
* Licensed and reliable datasets

---

##  What I Learned

Through this project, I practiced:

* REST API concepts
* API parameter handling
* JSON data exploration
* Nested JSON parsing
* External API integration
* FastAPI backend development
* Frontend/backend communication
* Real-world data processing
* Data transformation
* Machine Learning integration
* Environment variables and API keys
* Building an end-to-end data application

---

##  Future Improvements

* Integrate a dedicated licensed flight-data API
* Add airport autocomplete
* Add airline filtering
* Add historical flight tracking
* Add weather API integration
* Improve delay prediction using real historical data
* Add model evaluation metrics
* Add database storage
* Add authentication
* Deploy the application to a cloud platform
* Add automated API/data pipelines

---
##  views
---
<img width="1176" height="857" alt="image" src="https://github.com/user-attachments/assets/5a27510f-5cc4-4afa-94b3-010d30a9502b" />
<img width="1216" height="757" alt="image" src="https://github.com/user-attachments/assets/12fb8c58-1122-4785-83e2-199341075da5" />

---
##  Disclaimer

This project is created for **educational and portfolio purposes**.

The displayed delay-risk percentage is generated by a Machine Learning model trained on synthetic demonstration data. It does not represent an official airline prediction and should not be used for operational, financial, or travel-critical decisions.

---

##  Project Focus

**API Exploration + Real-World Data Analysis + FastAPI + Machine Learning**

This project demonstrates my ability to take an external API, understand its response structure, extract meaningful information, process the data, connect it to a backend, and build a user-facing application around it.

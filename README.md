# Data Pipe - Utilus

Welcome to the **Data Pipe project** 

A Python-based implementation of a Data Pipe system that processes data flow instructions from an input file, 
validates them, and computes the resulting visited coordinates within a defined boundary.

This project demonstrates clean modular design, file-based execution, boundary validation, and automated testing using Pytest.

---

## 📂 Repository Structure

```text
UtilusDataPipe/
│
├── app/
│   ├── __init__.py
│   ├── metrics/
│   │   ├── __init__.py
│   │   ├── mrr.py
│   │   ├── churn.py
│   │   └── cohorts.py
│   ├── main.py               # Application entrypoint
│   ├── cli.py                # Command-line interface and input parsing
│   ├── engine.py             # Generate report and compute metrics
│   └── model.py              # Data models
│   └── parser.py             # Data parsing and validation
│
├── data/                     # Sample input files for testing and development
│   ├── customers.csv
│   └── subscriptions.csv
│
├── tests/
│   ├── __init__.py
│   └── e2e_test.py           # End-to-end tests for the application
│
├── Dockerfile                # Docker configuration for the application
├── pytest.ini
├── requirements.txt
└── README.md
```

## 🚀 Features

✔ Modular architecture with separation of concerns 

✔ Deterministic file processing and input data handling

✔ Input validation and boundary enforcement

✔ End-to-end functional testing with Pytest


---

## 🧠 Getting Started

### 📦 Prerequisites

This project requires

**Python 3.8+**

**pip**

**Docker** (for viewing Allure reports)


It has been tested with standard Python interpreters on macOS.

Install the project dependencies:

```bash
pip install -r requirements.txt
```

### Run the application as follows:

```bash
python -m app.main data/customers.csv data/subscriptions.csv output.json
```

### Running the Test Suite:

```bash
pytest
```

### Test Coverage and Results
To generate a test coverage report, run:

```bash
pytest --cov=app
```

Or to generate an HTML coverage report:

```bash
pytest --cov=app --cov-report=html
```

This will create an `htmlcov/` directory with a detailed coverage report.

open `htmlcov/index.html` in a web browser to view the report.

To see the lines for which coverage is missing,
open the specific file in the coverage report and look for the red highlights in the report.

Or run the following command to see the missing lines in the terminal:

```bash
pytest --cov=app --cov-report=term-missing
```

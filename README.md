# Zendesk Data App

This is an app that creates a front-end for Zendesk data that is similar to Zendesk insights

---

## Requirements

- Python 2.7
- pip 10.0.1

## Setup

```
pip install -r requirements.txt
aws configure  # Set up your AWS credentials
```

Setup a `config.py` file in the root folder with these variables:

```
ZENDESK_TOKEN  # API token
ZENDESK_VIEW  # Metrics View ID from Zendesk
ZENDESK_URL  # URL of Zendesk site
S3_BUCKET_NAME  # Bucket name to store the csv file
```


## Run

```
export FLASK_ENV=development FLASK_APP=app.py && flask run
```

App is live at `http://localhost:5000/`

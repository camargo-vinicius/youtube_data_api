# YouTube Data API Exploration

This project is focused on exploring the YouTube Data API to retrieve and analyze data from YouTube. The goal is to understand how to interact with the API, extract useful information, and perform various analyses using streamlit.

Click [here](https://youtube-data-dashboard.streamlit.app/) to acess my streamlit app.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Project Structure](#projectstructure)
- [Usage](#usage)

## Introduction
The YouTube Data API allows developers to access YouTube data such as videos, playlists, and channels. This project aims to cover how to use the API to gather data and perform analyses.

## Features
- Retrieve video details
- Fetch channel statistics
- Analyze video statistics

## Installation
To get started, clone the repository and install the required dependencies:

```bash
git clone https://github.com/camargo-vinicius/youtube_data_api.git
cd youtube_data_api
pip install -r requirements.txt
```

## ProjectStructure
```
Youtube_Data_API/
└── app/
    └── app.py                # Main application file for Streamlit dashboard
└── data/
    └── video_stats.pkl 
└── src/
    └── etl.py				  # Main file to extract transformm and load the data
├── .gitignore          	  # File to avoid commits of personal data
├── .python-version           # Python version used in this project
├── pyproject.toml            # Project Dependencies   	 
├── README.md 				  # Project documentation
├── requirements.txt 		  # Project dependencies for installing via pip
├── uv.lock				      # Project dependencies
```
## Usage
1. Obtain an API key from the [Google Developers Console](https://console.developers.google.com/).

2. Create a `.env` file in the project root and add your API key:
    ```
    YOUTUBE_API_KEY=YOUR_API_KEY
    ```
3. Run the script to generate the output statistics in a pickle file:
    ```bash
    python src/etl.py
    ```
4. After that, run the streamlit app file to view the data:
    ```bash
    streamlit run app/app.py
    ```
# 🚛 Indian Mandi Crop Price Dashboard

## Overview
This project is a Python data pipeline and dashboard that helps find the best profit margins for buying and selling agricultural crops across different markets in India. It downloads live daily crop prices from the data.gov.in and calculates the price differences between cities to optimize supply chain and logistics planning.

## Features & Problem Solving
Working with raw government data can be messy. This project solves two main problems:
* **Realistic Profit Margins:** Instead of using the highest or lowest prices of the day (which might just be a few damaged or premium crops), the dashboard calculates profit using the **Modal Price** (the most common bulk price). This ensures logistics companies see realistic profits for filling a whole truck.
* **Security:** The data download script is separated from the dashboard and securely hides the API key using a `.env` file so credentials are never leaked.


## How to Run on Your Computer

### 1. Download the code
```bash
git clone [https://github.com/Sanjay333333/mandi_price_analytics.git](https://github.com/Sanjay333333/mandi_price_analytics.git)
cd mandi_price_analytics
```

### 2. Set up Python
Create a virtual environment and install the required libraries:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Add your API Key
Create a file named .env in the folder and paste your data.gov.in API key inside:
```text
API_KEY="your_api_key_here"
```

### 4. Run the App
First, run the script to download the latest market data:
```bash
python fetch_data.py
```
Then, launch the visual dashboard:
```bash
streamlit run live_app.py
```
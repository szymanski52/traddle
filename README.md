# Traddle

This project is a simple web application for a trading algorithm platform that allows users to view machine learning-based trading algorithm predictions. The platform includes a personal dashboard with a demo account balance, and it displays algorithm predictions for different stock tickers.

## Features

- **Personal Dashboard**: View demo account balance and top up the balance.
- **Algorithm Catalog**: Browse available trading algorithms.
- **Algorithm Predictions**: View predictions for selected algorithms and tickers, along with actual stock prices.

## Requirements

- Python 3.7 or higher
- `virtualenv` for creating a virtual environment

## Setup and Installation

1. **Clone the Repository**

2. **Create and Activate a Virtual Environment**

    On macOS and Linux:

    ```sh
    python3 -m venv traddle_env
    source traddle_env/bin/activate
    ```

    On Windows:

    ```sh
    python -m venv traddle_env
    traddle_env\Scripts\activate
    ```

3. **Install the Required Packages**

    ```sh
    pip install -r requirements.txt
    ```

4. **Run the Application**

    Start the Flask application:

    ```sh
    export FLASK_APP=app.py
    export FLASK_ENV=development
    flask run
    ```

    If you are using Windows, use the following commands to set the environment variables:

    ```sh
    set FLASK_APP=app.py
    set FLASK_ENV=development
    flask run
    ```

5. **Access the Application**

    Open your web browser and go to `http://127.0.0.1:5000/` to access the application.



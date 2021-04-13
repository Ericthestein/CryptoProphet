#!/usr/bin/env python3

from fastapi import FastAPI
from typing import Optional
import requests
from datetime import datetime, timedelta
import math
import pandas as pd
import os
from prophet import Prophet
from discord import Webhook, RequestsWebhookAdapter


GEMINI_TICKER_ENDPOINT = "https://api.gemini.com/v2/ticker/"
DISCORD_USERNAME = "Crypto Prophet"


class GenericError(Exception):
    def __init__(self, message):
        self.message = message


app = FastAPI()


@app.get("/")  # zone apex
def read_root():
    return {"Error": "Please specify the ticker symbol as the path (e.g. /btcusd)"}


def get_gemini_ticker_data(ticker):
    response_json = requests.get(GEMINI_TICKER_ENDPOINT + ticker).json()
    if "result" in response_json and response_json["result"] == "error":
        raise GenericError("Error fetching cryptocurrency price data from Gemini: " + response_json["message"])
    return response_json


def convert_gemini_to_prophet_training_data(gemini_data):
    time_history = []
    price_history = []
    current_datetime = datetime.now().replace(microsecond=0, second=0, minute=0)

    curr_hour = 0

    if "changes" not in gemini_data:
        raise GenericError("Invalid response from Gemini")

    for hourly_close in gemini_data["changes"]:
        time_history.append(pd.Timestamp(current_datetime - timedelta(hours=curr_hour)))
        price_history.append(float(hourly_close))
        curr_hour += 1

    return pd.DataFrame(data={"ds": time_history, "y": price_history})


def get_prophet_forecast(prophet_training_data):
    m = Prophet()
    m.fit(prophet_training_data)
    future = m.make_future_dataframe(periods=24)
    return m.predict(future)


def process_prophet_forecast(ticker, stats):
    line1 = """Over the next 24 hours, {} is expected to reach a low price of {:.2f} ({}{:.2f}%),
    a high price of {:.2f} ({}{:.2f}%),
    and an average price of {:.2f} ({}{:.2f}%).
    """.format(ticker, stats["min_price_next_day"], "+" if stats["min_percent_change"] > 0 else "",
               stats["min_percent_change"], stats["max_price_next_day"], "+" if stats["max_percent_change"] > 0 else "",
               stats["max_percent_change"], stats["average_price_next_day"],
               "+" if stats["average_percent_change"] > 0 else "", stats["average_percent_change"]).replace("\n", "").replace('    ', " ")

    line2 = """These predictions were made using the price history of {} over the past day, as provided by Gemini,
    and by using Prophet, a forecasting algorithm developed by Facebook. This is not financial advice.
    """.format(ticker).replace("\n", "").replace('    ', " ")

    return line1 + "\n\n" + line2


def calculate_price_statistics(history, forecast):
    # Process price history
    prices_last_day = history['y']

    min_price_last_day = prices_last_day.min()
    max_price_last_day = prices_last_day.max()
    average_price_last_day = prices_last_day.mean()

    # Process price forecast
    price_forecast = forecast[['ds', 'yhat']]
    price_forecast_next_day = price_forecast.head(24)
    prices_next_day = price_forecast_next_day['yhat']

    min_price_next_day = prices_next_day.min()
    max_price_next_day = prices_next_day.max()
    average_price_next_day = prices_next_day.mean()

    # Process changes since last day

    min_percent_change = (min_price_next_day - min_price_last_day) / min_price_last_day * 100
    max_percent_change = (max_price_next_day - max_price_last_day) / max_price_last_day * 100
    average_percent_change = (average_price_next_day - average_price_last_day) / average_price_last_day * 100

    return {
        "min_price_last_day": min_price_last_day,
        "min_price_next_day": min_price_next_day,
        "min_percent_change": min_percent_change,
        "max_price_last_day": max_price_last_day,
        "max_price_next_day": max_price_next_day,
        "max_percent_change": max_percent_change,
        "average_price_last_day": average_price_last_day,
        "average_price_next_day": average_price_next_day,
        "average_percent_change": average_percent_change,
    }


def _forecast_for_ticker(ticker: str):
    # Get recent price data for token from Gemini
    gemini_ticker_data = get_gemini_ticker_data(ticker)

    # Prepare data for Prophet
    prophet_training_data = convert_gemini_to_prophet_training_data(gemini_ticker_data)

    # Get prediction from Prophet
    prophet_forecast = get_prophet_forecast(prophet_training_data)

    # Run delta calculations
    stats = calculate_price_statistics(prophet_training_data, prophet_forecast)

    # Prepare data for return
    processed_forecast = process_prophet_forecast(ticker, stats)

    # Return data
    return {"Forecast Description": processed_forecast, "stats": stats}


@app.get("/{ticker}")
def forecast_for_ticker(ticker: str):
    try:
        return _forecast_for_ticker(ticker)
    except GenericError as err:
        return {"Error": err.message}


# Check if container was used with a ticker and Discord parameter

def handle_initial_run_request():
    # Check to see if we already ran the request
    if "RAN_INITIAL_REQUEST" in os.environ:
        return
    os.environ["RAN_INITIAL_REQUEST"] = "true"

    # Process input
    ticker = os.getenv("TICKER")
    if ticker is None:
        print("""Welcome to Crypto Prophet!
        1) To immediately receive a prediction for a particular cryptocurrency in your Discord server, pass in the ticker using the TICKER environment variable and the Discord Webhook URL using the DISCORD environment variable.
        2) To receive predictions once this app starts running, navigate to http://localhost:8080/{TICKER}
        """)
        return
    discord_webhook_url = os.getenv("DISCORD")
    if discord_webhook_url is None:
        print("Error: Please provide a Discord Webhook to post the result to a Discord channel using the DISCORD environment variable")
        return
    try:
        # Run request

        prediction = _forecast_for_ticker(ticker)
        print(prediction["Forecast Description"])
        # Post to Discord webhook
        webhook = Webhook.from_url(discord_webhook_url, adapter=RequestsWebhookAdapter())
        webhook.send(prediction["Forecast Description"], username=DISCORD_USERNAME)
    except GenericError as err:
        print("Error: " + err.message)


handle_initial_run_request()

from typing import Optional
import requests
from datetime import datetime, timedelta
import math
import pandas as pd
import os
from prophet import Prophet

GEMINI_TICKER_ENDPOINT = "https://api.gemini.com/v2/ticker/"

class GenericError(Exception):
    def __init__(self, message):
        self.message = message


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


def calculate_price_statistics(history, forecast):
    # Process price history
    prices_last_day = history['y']

    min_price_last_day = prices_last_day.min()
    max_price_last_day = prices_last_day.max()
    average_price_last_day = prices_last_day.mean()
    last_price = prices_last_day[0]

    # Process price forecast
    price_forecast = forecast[['ds', 'yhat']]
    price_forecast_next_day = price_forecast.head(24)
    prices_next_day = price_forecast_next_day['yhat']

    min_price_next_day = prices_next_day.min()
    max_price_next_day = prices_next_day.max()
    average_price_next_day = prices_next_day.mean()
    price_two_weeks = price_forecast['yhat'][38]

    # Process changes since last day

    min_percent_change = (min_price_next_day - min_price_last_day) / min_price_last_day * 100
    max_percent_change = (max_price_next_day - max_price_last_day) / max_price_last_day * 100
    average_percent_change = (average_price_next_day - average_price_last_day) / average_price_last_day * 100
    two_weeks_percent_change = (price_two_weeks - last_price) / last_price * 100

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
        "price_two_weeks": price_two_weeks,
        "two_weeks_percent_change": two_weeks_percent_change
    }


def process_prophet_forecast(ticker, stats):
    line1 = """Over the next 24 hours, {} is expected to reach a low price of ${:.2f} ({}{:.2f}%),
    a high price of ${:.2f} ({}{:.2f}%),
    and an average price of ${:.2f} ({}{:.2f}%).
    """.format(ticker, stats["min_price_next_day"], "+" if stats["min_percent_change"] > 0 else "",
               stats["min_percent_change"], stats["max_price_next_day"], "+" if stats["max_percent_change"] > 0 else "",
               stats["max_percent_change"], stats["average_price_next_day"],
               "+" if stats["average_percent_change"] > 0 else "", stats["average_percent_change"]).replace("\n",
                                                                                                            "").replace(
        '    ', " ")

    line2 = """In two weeks, {} is expected to reach ${:.2f} ({}{:.2f}%).
    """.format(ticker, stats["price_two_weeks"], "+" if stats["two_weeks_percent_change"] > 0 else "",
               stats["two_weeks_percent_change"]).replace("\n", "").replace('    ', " ")

    line3 = """These predictions were made using the price history of {} over the past day, as provided by Gemini,
    and by using Prophet, a forecasting algorithm developed by Facebook. This is not financial advice.
    """.format(ticker).replace("\n", "").replace('    ', " ")

    return line1 + "\n\n" + line2 + "\n\n" + line3


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
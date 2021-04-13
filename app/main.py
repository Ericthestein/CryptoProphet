#!/usr/bin/env python3

from fastapi import FastAPI
from typing import Optional

from forecast_for_ticker import _forecast_for_ticker, GenericError

app = FastAPI()


@app.get("/")  # zone apex
def read_root():
    return {"Error": "Please specify the ticker symbol as the path (e.g. /btcusd)"}


@app.get("/{ticker}")
def forecast_for_ticker(ticker: str):
    try:
        return _forecast_for_ticker(ticker)
    except GenericError as err:
        return {"Error": err.message}

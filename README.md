# CryptoProphet

This repository houses CryptoProphet, an app that retrieves the last 24 hourly prices of a given cryptocurrency token, runs these values through a forecasting algorithm, calculates statistics based on the next 24 hourly predicted prices, and summarizes its findings.

## Try it Out

To try out CryptoProphet, use this endpoint: https://container-service-1.fjuqejd7h0rbe.us-east-1.cs.amazonlightsail.com/[ticker]
where [ticker] corresponds to a cryptocurrency ticker, such as "ethusd". For example, the endpoint https://container-service-1.fjuqejd7h0rbe.us-east-1.cs.amazonlightsail.com/ethusd would return price predictions about Ethereum given the last day's price history.

## Building With Docker

To build a Docker image of CryptoProphet, run `docker build --progress=plain -t crypto_prophet .`

## Running With Docker

To run the previously-built Docker image, use one of the following commands:
1) For directly receiving a summary of CryptoProphet's predictions for a particular token in your Discord channel, use:
```
docker run -p 8080:80 -e MODE=DISCORD -e TICKER=[ticker] -e DISCORD=[discord_webhook_url] crypto_prophet
```
where `[ticker]` corresponds to a cryptocurrency ticker, such as "btcusd", and `[discord_webhook_url]` corresponds to a Discord Webhook URL one can generate for a Discord channel.

2) To run CryptoProphet as a REST API, use:
```
docker run -p 8080:80 -e MODE=API crypto_prophet
```
To access the API, navigate to http://localhost:8080/[ticker], where [ticker] corresponds to a cryptocurrency ticker, such as "btcusd".

## Sample Output

Below is a sample json output for a request where ticker=ethusd:
```
{
    "Forecast Description": "Over the next 24 hours, ethusd is expected to reach a low price of $2148.82 (+0.52%), a high price of $2290.19 (-0.97%), and an average price of $2222.28 (-0.00%). \n\nIn two weeks, ethusd is expected to reach $2334.94 (+2.22%). \n\nThese predictions were made using the price history of ethusd over the past day, as provided by Gemini, and by using Prophet, a forecasting algorithm developed by Facebook. This is not financial advice. ",
    "stats": {
        "min_price_last_day": 2137.76,
        "min_price_next_day": 2148.823555959902,
        "min_percent_change": 0.5175303102266767,
        "max_price_last_day": 2312.68,
        "max_price_next_day": 2290.1874543797035,
        "max_percent_change": -0.9725749182894464,
        "average_price_last_day": 2222.2775,
        "average_price_next_day": 2222.2767643098,
        "average_percent_change": -3.3105235513780125e-05,
        "price_two_weeks": 2334.9436777730066,
        "two_weeks_percent_change": 2.2224026903749596
    }
}
```

## Built With

CryptoProphet was developed using:
1) [Gemini's REST API](https://docs.gemini.com/rest-api/#ticker-v2)
2) [Prophet by Facebook](https://facebook.github.io/prophet/)
3) [Amazon Lightsail](https://lightsail.aws.amazon.com/)
4) [FastAPI](https://fastapi.tiangolo.com/)
5) [Docker](https://www.docker.com/)
6) [Python](https://www.python.org/)

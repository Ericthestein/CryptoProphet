# CryptoProphet

This repository houses CryptoProphet, an app that retrieves the last 24 hourly prices of a given cryptocurrency token, runs these values through a forecasting algorithm, calculates statistics based on the next 24 hourly predicted prices, and summarizes its findings.

## Building With Docker

To build a Docker image of CryptoProphet, run `docker build --progress=plain -t crypto_prophet .`

## Running With Docker

To run the previously-built Docker image, use one of the following commands:
1) For directly receiving a summary of CryptoProphet's predictions for a particular token in your Discord channel, use:
```
docker run -p 8080:80 -e TICKER=[ticker] -e DISCORD=[discord_webhook_url] crypto_prophet
```
where `[ticker]` corresponds to a cryptocurrency ticker, such as "btcusd", and `[discord_webhook_url]` corresponds to a Discord Webhook URL one can generate for a Discord channel.

2) To run CryptoProphet as a REST API, use:
```
docker run -p 8080:80 crypto_prophet
```
To access the API, navigate to http://localhost:8080/[ticker], where [ticker] corresponds to a cryptocurrency ticker, such as "btcusd".

## Sample Output

Below is a sample json output for a request where ticker=btcusd:
```
{
"Forecast Description": "Over the next 24 hours, btcusd is expected to reach a low price of 59862.84 (+0.25%), a high price of 60821.10 (+0.01%), and an average price of 60238.75 (-0.00%). \n\nThese predictions were made using the price history of btcusd over the past day, as provided by Gemini, and by using Prophet, a forecasting algorithm developed by Facebook. This is not financial advice. ",
    "stats": {
        "min_price_last_day": 59715.58,
        "min_price_next_day": 59862.842269370136,
        "min_percent_change": 0.24660611078404357,
        "max_price_last_day": 60814.05,
        "max_price_next_day": 60821.100097243914,
        "max_percent_change": 0.01159287573169571,
        "average_price_last_day": 60238.75208333333,
        "average_price_next_day": 60238.751229449,
        "average_percent_change": -1.4175000355116723e-06
    }
}
```

## Resources

CryptoProphet was built using:
1) [Gemini's REST API](https://docs.gemini.com/rest-api/#ticker-v2)
2) [Prophet by Facebook](https://facebook.github.io/prophet/)

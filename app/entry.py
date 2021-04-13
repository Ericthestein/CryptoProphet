import os
from discord import Webhook, RequestsWebhookAdapter
import uvicorn

from forecast_for_ticker import _forecast_for_ticker, GenericError

DISCORD_USERNAME = "Crypto Prophet"


def handle_initial_run_request():
    # Process input
    ticker = os.getenv("TICKER")
    if ticker is None:
        print("Error: Please supply a ticker symbol, such as btcusd, using the TICKER environment variable")
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
    except:
        print("Error: failed to run your request. The likely cause of this error is a faulty webhook URL")


def start_api():
    os.system("../start.sh")

def show_help_screen():
    print("""Welcome to Crypto Prophet!
                1) To immediately receive a prediction for a particular cryptocurrency in your Discord server, set the MODE environment variable to DISCORD, pass in the ticker using the TICKER environment variable, and pass in the Discord Webhook URL using the DISCORD environment variable.
                2) To start a REST API running Crypto Prophet, set the MODE environment variable to API. Then, to receive predictions once this app starts running, navigate to http://localhost:8080/{TICKER}
                """)

# Check run mode

run_mode = os.getenv("MODE")
if run_mode is None:
    show_help_screen()
elif run_mode == "DISCORD":
    handle_initial_run_request()
elif run_mode == "API":
    start_api()
else:
    show_help_screen()
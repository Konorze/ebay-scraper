**DISCLAIMER: This script is made for educational and learning purposes only. I am not responsible for any misuse or damage caused by the script**

# eBay Scraper

This is a python script for scraping eBay listings based on a search query, price range, and sends new items to a telegram chat It can run with or without proxies, checks multiple pages, and avoids sending duplicate items the script is made to find new listings in real-time and send them to you via telegram

## Features

* **Search eBay for items by keyword and price range**
* **Checks up to 3 pages of results to find new listings**
* **Sends new items to a telegram chat with title, price, and link**
* **Avoids duplicates by tracking sent items**
* **Supports proxy usage for anonymity**
* **Runs continuously at a set interval until stopped or duration ends**

## Requirements

You need python 3.7 or higher  the script uses some external packages, so you need to install them

### Python packages

* `aiohttp` - For async HTTP requests
* `beautifulsoup4` - For parsing HTML from eBay pages
* `argparse` - For command-line arguments (comes with python)
* `sys`, `random`, `time`, `itertools` - These are built-in, no need to install

To install the required packages, run:

```bash
pip install aiohttp beautifulsoup4
```

## Setup

* Clone or download this repository
* Make sure you have python installed (check with `python --version`)
* Install the required packages (see above)
* Get your telegram bot token and chat ID (see below)
* If using proxies, create a `proxies.txt` file in the same folder as the script add one proxy per line in the format ip\:port Example:

```
1.1.1.1:8
etc.etc.etc.etc:etc
```

## How to get telegram bot token and chat ID

To use this script, you need a telegram bot token and a chat ID. Here's how to get them:

1. Open telegram and search for `@BotFather`
2. Start a chat with `@BotFather` and send `/newbot`
3. BotFather will ask for a name for your bot (e.x., "My eBay bot")
4. Then it will ask for a username, which must end in `bot` (e.g. `@MyEbayBot`)
5. If the username is available, BotFather will give you a bot token (looks like `727254:AAEcbIAC2M9eBzFipZ2ygcbF_P-i150`)
6. Save this token, you need it for the `--token` argument
7. Go to your new bot (find it by its username, e.x `@MyEbayBot`)
8. Send `/start` to your bot, then send a message like `hello`
9. Open a browser and go to:

```
https://api.telegram.org/bot<your_token>/getUpdates
```

Replacing `<your_token>` with the token from BotFather You will see a JSON response with a `chat` section, and inside it, an `id` (e.x `2572398`) this is your chat ID save the chat ID, you need it for the `--chat` argument

If you don't see the chat ID, send another message to the bot and refresh the URL

## Usage

Run the script from the command line with required arguments below are the options and examples

### Command line arguments

* `--query`: The search term for eBay (e.x "laptop")
* `--min`: Minimum price for items (e.x 100)
* `--max`: Maximum price for items (e.x 500)
* `--interval`: Time between scans in seconds (default: 60)
* `--duration`: How long to run in seconds (default: 0, runs forever)
* `--token`: Your telegram bot token
* `--chat`: Your telegram chat ID
* `--max_send`: Max number of items to send per scan (default: 3)
* `--proxy`: Use proxies (true or false)

### Example: without proxies

To search for laptops between \$100 and \$500, scanning every 60 seconds, sending to telegram:

```bash
python ebay_scraper.py --query "laptop" --min 100 --max 500 --interval 60 --duration 3600 --token "your_bot_token" --chat "your_chat_id" --max_send 3 --proxy false
```

### Example: with proxies

To use proxies, make sure `proxies.txt` exists with valid proxies. The script will exit if no working proxies are found:

```bash
python ebay_scraper.py --query "laptop" --min 100 --max 500 --interval 60 --duration 3600 --token "your_bot_token" --chat "your_chat_id" --max_send 3 --proxy true
```

## How It works

* **The script starts and shows a banner**
* **If proxy true, it checks proxies from proxies.txt and uses only working ones**
* **It searches eBay for your query, checking 3 pages of results, sorted by new listings**
* **It filters items by price and ensures they are valid (title length > 10, valid URL)**
* **New items (not seen before) are sent to your telegram chat with title, price, and link**
* **It keeps running at the set interval, checking for new items, until stopped or duration ends**

## Notes

* **The script avoids duplicates by tracking item urls**
* **Proxies are tested for HTTP/HTTPS and removed if they fail**
* **If using proxies, it shuffles them to avoid bans**
* **Listings are sorted by "newly listed" to focus on recent items**
* **Stop the script with Ctrl+C, it will show total items found**

## Troubleshooting

* **No items found**: check your query, price range, or internet connection. eBay might also block your IP if not using proxies
* **Proxy errors**: Ensure `proxies.txt` has valid proxies.. test with `--proxy false` to see if it works without proxies
* **Telegram errors**: double-check your token and `chat_id` make sure your bot is added to the chat
* **Package errors**: Run `pip install aiohttp beautifulsoup4` again

## License

MIT License. Use it, modify it, share it, just don’t blame me if something breaks

import os
import requests
import logging
from lxml import etree
from ollama import Client
from slack_sdk import WebClient
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

def ai_connect(ollama_host):
  client = Client(host=ollama_host)
  try:
    client.ps()
    logging.info(f"Connected to Ollama at {ollama_host}")
    return client
  except Exception as e:
    logging.critical(f"Failed to connect to AI server at {ollama_host}: {e}", exc_info=True)
    exit(1)

def ai_model(client, llm_model, system_ops):
  try:
    logging.info(f"Pulling AI model '{llm_model}'...")
    client.pull(llm_model)
    client.create(model='custom_model', from_=llm_model, system=system_ops)
    client.show('custom_model')
    logging.info(f"AI model '{llm_model}' is ready.")
  except Exception as e:
    logging.error(f"AI model initialization failed: {e}", exc_info=True)
    exit(1)

def ai_summary(client, text):
  try:
    response = client.generate(model='custom_model', prompt=text)
    return response['response']
  except Exception as e:
    logging.error(f"AI processing failed: {e}", exc_info=True)
    exit(1)

def send_slack_message(title, message, link):
  slack_token = os.getenv("SLACK_API_TOKEN")
  if not slack_token:
    logging.error("Slack API token is missing. Set SLACK_API_TOKEN in your environment.")
    exit(1)
  client = WebClient(token=slack_token)
  try:
    response = client.chat_postMessage(
      channel="random",
      username="KokoAI",
      icon_emoji=":robot_face:",
      unfurl_links=False,
      text=f"{title}: {message}",
      blocks=[
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": f"*<{link}|{title}>*\n{message}"
          }
        }
      ]
    )
    if response["ok"]:
      logging.info(f"Sent Slack message: {title}")
    else:
      logging.error(f"Slack API error: {response['error']}")
  except Exception as e:
    logging.error(f"Failed to send Slack message: {e}", exc_info=True)

def get_feed_list():
  try:
    with open("feeds.txt", "r") as file:
      urls = [url.strip() for url in file if url.strip()]
    if not urls:
      logging.warning("feeds.txt is empty.")
    return urls
  except FileNotFoundError:
    logging.critical("feeds.txt not found. Please create the file with feed URLs.", exc_info=True)
    exit(1)

def save_feed_raw(url):
  try:
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    filename = "raw_feed.xml"
    with open(filename, mode='wb') as localfile:
      localfile.write(resp.content)
    return filename
  except requests.RequestException as e:
    logging.error(f"Failed to fetch {url}: {e}", exc_info=True)
    return None

def get_feed_content(file):
  namespaces = {"content": "http://purl.org/rss/1.0/modules/content/"}
  articles = []
  today = datetime.now().date()

  try:
    tree = etree.parse(file)
    root = tree.getroot()
  except etree.XMLSyntaxError as e:
    logging.critical(f"Failed to parse XML from {file}: {e}", exc_info=True)
    return []

  for item in root.findall(".//item"):
    pub_date_elem = item.find("pubDate")
    if pub_date_elem is not None:
      try:
        pub_date = parsedate_to_datetime(pub_date_elem.text).astimezone(timezone.utc).date()
        if pub_date != today:
          continue
      except Exception as e:
        logging.warning(f"Skipping article due to date parsing error in {file}: {e}", exc_info=True)
        continue

      title = item.findtext("title", "").strip()
      link = item.findtext("link", "").strip()
      content_elem = item.find("content:encoded", namespaces)
      content = content_elem.text.strip() if content_elem is not None else ""

      if title and link and content:
        articles.append((title, link, content))

  if not articles:
      logging.info(f"No new articles found in {file}")

  return articles

def main():
  urls = get_feed_list()
  if not urls:
    logging.info("No feed URLs found. Exiting.")
    return

  ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
  if ollama_host == "http://localhost:11434":
    logging.warning("OLLAMA_HOST not set, using default 'http://localhost:11434'")
  
  client = ai_connect(ollama_host)
  
  system_ops = os.getenv("SYSTEM_OPS", "")
  if not system_ops:
    logging.warning("SYSTEM_OPS not set, using empty system options.")

  model = os.getenv("MODEL", "llama3.2")
  if model == "llama3.2":
    logging.warning("MODEL not set, using default 'llama3.2'.")
  
  ai_model(client, model, system_ops)

  for url in urls:
    logging.info(f"Processing feed: {url}")
    filename = save_feed_raw(url)
    if not filename:
      continue 

    articles = get_feed_content(filename)
    if not articles:
      logging.info(f"No new articles today from {url}")
      continue

    for title, link, content in articles:
      response = ai_summary(client, content)
      send_slack_message(title, response, link)

if __name__ == "__main__": 
  main()

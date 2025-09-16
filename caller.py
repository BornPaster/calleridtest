import urllib.parse, requests as regular_requests, time as time_module, warnings, logging, re
from requests.exceptions import RequestException, Timeout
from datetime import datetime
from mail import mailer

warnings.filterwarnings("ignore", category=UserWarning, module="curl_cffi.requests.cookies")

def consolestamp():
    timestamp = str(datetime.fromtimestamp(time_module.time())).split(" ")[1]
    white_dots_and_colons = "\x1b[38;2;73;73;73m.\x1b[0m"
    white_colons = "\x1b[38;2;73;73;73m:\x1b[0m"
    formatted_timestamp = timestamp.replace(".", white_dots_and_colons).replace(":", white_colons)
    return f'\x1b[38;2;73;73;73m[\x1b[0m{formatted_timestamp}\x1b[38;2;73;73;73m]\x1b[0m '

def bracks(text):
    return f'\x1b[38;2;73;73;73m[\x1b[0m {text} \x1b[38;2;73;73;73m]\x1b[0m '

class DynamicTimeFormatter(logging.Formatter):
    def format(self, record):
        stamp = consolestamp()
        original = super().format(record)
        return f"{stamp}  \x1b[38;2;73;73;73m-\x1b[0m  {original}"

logger = logging.getLogger("bruce")
logger.setLevel(logging.DEBUG)
logger.propagate = False
formatter = DynamicTimeFormatter('%(levelname)s \x1b[38;2;73;73;73m:\x1b[0m %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


class platinum:
    def __init__(self, library="stealth", ua=None, proxy=None):
        if library == "stealth":
            from stealth_requests import StealthSession
            self.session = StealthSession()
        elif library == "requests":
            self.session = regular_requests.Session()
        else:
            raise ValueError("invalid library: choose 'stealth' or 'requests'")

        if ua:
            self.session.headers.update({"User-Agent": ua})

        if proxy:
            self.session.proxies.update({
                'http': proxy,
                'https': proxy
            })

    def get(self, url, **kwargs):
        try:
            return self.session.get(url, **kwargs)
        except (RequestException, Timeout) as e:
            self.logger.error(f"request failed: {e}")
            return None

    def post(self, url, data=None, json=None, **kwargs):
        try:
            return self.session.post(url, data=data, json=json, **kwargs)
        except (RequestException, Timeout) as e:
            self.logger.error(f"request failed: {e}")
            return None


requests = platinum(
    library="stealth",
    ua="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    proxy=""
)


def search(num):
    mailapi = mailer()
    email = mailapi.get_mail()

    url = "https://calleridtest.com/login"
    resp = requests.get(url)
    cookies = resp.cookies.get_dict()
    xsrf = urllib.parse.unquote(cookies["XSRF-TOKEN"])
    #logger.critical(f"received xsrf : {bracks(xsrf[:270])}")

    headers = {
        'accept': 'text/html, application/xhtml+xml',
        'accept-language': 'en-US,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://calleridtest.com',
        'priority': 'u=1, i',
        'referer': 'https://calleridtest.com/login',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'x-inertia': 'true',
        'x-inertia-version': 'b1570c9210f74a995f454e30708ffc83',
        'x-requested-with': 'XMLHttpRequest',
        'x-xsrf-token': xsrf,
    }

    data = {'email': email}
    resp = requests.post(url, cookies=cookies, headers=headers, json=data)
    #logger.critical(f"received resp : {bracks(resp.text)}:{bracks(resp.status_code)}")

    deadline = time_module.time() + 60
    inbox = []
    while time_module.time() < deadline:
        inbox = mailapi.fetch_inbox()
        if isinstance(inbox, list) and len(inbox) > 0:
            break
        time_module.sleep(1)

    #logger.critical(f"received email inbox : {bracks(inbox)}")

    if not inbox:
        logger.error("no messages found")
        return

    msg = next((m for m in inbox if m.get('from', {}).get('address') == 'no-reply@calleridtest.com'), inbox[0])
    message_id = msg.get('id') or str(msg.get('@id', '')).split('/')[-1]
    #logger.critical(f"message id : {bracks(message_id)}")

    body_text = mailapi.get_message_content(message_id)
    match = re.search(r"https:\/\/calleridtest\.com\/login\/magic\/[^\s]+", body_text)
    if match:
        magic_link = match.group(0)
        #logger.critical(f"magic link : {bracks(magic_link)}")
    else:
        logger.error("no magic link found")


    url = magic_link
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    }
    resp = requests.get(url, headers=headers, cookies=cookies)
    cookies = resp.cookies.get_dict()
    xsrf = urllib.parse.unquote(cookies["XSRF-TOKEN"])
    #logger.critical(f"received xsrf : {bracks(xsrf[:300])}")


    url = "https://calleridtest.com/lookups"
    headers = {
        'accept': 'text/html, application/xhtml+xml',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://calleridtest.com',
        'priority': 'u=1, i',
        'referer': 'https://calleridtest.com/',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'x-inertia': 'true',
        'x-inertia-version': 'b1570c9210f74a995f454e30708ffc83',
        'x-requested-with': 'XMLHttpRequest',
        'x-xsrf-token': xsrf,
    }
    data = {
        "number": num
    }
    resp = requests.post(url, headers=headers, cookies=cookies, json=data)
    return resp.json()


#num = search("17759802006")
#print(f"received resp : {bracks(num)}")
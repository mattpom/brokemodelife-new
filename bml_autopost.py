import urllib.request, urllib.parse, json, os, datetime, re, sys

sites = [
    {"name": "BrokeModeLife", "url": "brokemodelife.com", "focus": "budget living, saving money, living well on less", "credit": ""},
    {"name": "StopLookAround", "url": "stoplookaround.com", "focus": "travel without selfies, no faces just places, experiencing the world not performing it", "credit": "stoplookaround.com"},
    {"name": "DontBeHangry", "url": "dontbehangry.com", "focus": "world food culture and history journalism, the stories behind what people eat", "credit": "dontbehangry.com"},
    {"name": "FineLivingGuide", "url": "finelivingguide.com", "focus": "high-end luxury living, fine dining, rare spirits, buy once buy right", "credit": "finelivingguide.com"}
]

week = datetime.datetime.now().isocalendar()[1]
site = sites[week % 4]

if site["credit"]:
    credit_rule = ("End with the site URL " + site["credit"] + 
        " woven naturally into the post as part of a sentence. "
        "NEVER write 'from our friends at' or any variation of that phrase.")
else:
    credit_rule = "No external site credit needed."

prompt = ("Write one X post for @brokemode. "
    "Site: " + site["name"] + " covering " + site["focus"] + ". "
    "Rules: max 260 chars total. Sharp direct real voice. Budget mindset always. 1-2 hashtags max. "
    + credit_rule + 
    " Return ONLY the post text. No quotes, no labels, no explanation.")

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 150,
        "messages": [{"role": "user", "content": prompt}]
    }).encode(),
    headers={
        "x-api-key": os.environ["ANTHROPIC_KEY"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
)
with urllib.request.urlopen(req) as r:
    response = json.loads(r.read())

# Single text block only - prevents fragment posts
text_blocks = [b["text"] for b in response["content"] if b["type"] == "text"]
text = text_blocks[0].strip() if text_blocks else ""

# Fix cut-off first characters
text = re.sub(r'^[^\w\U00010000-\U0010ffff]+', '', text, flags=re.UNICODE).strip()

if not text:
    print("ERROR: empty post")
    sys.exit(1)

print("Post (" + str(len(text)) + " chars): " + text)

data = urllib.parse.urlencode({"profile_ids[]": os.environ["PROFILE_ID"], "text": text}).encode()
req2 = urllib.request.Request(
    "https://api.bufferapp.com/1/updates/create.json",
    data=data,
    headers={"Authorization": "Bearer " + os.environ["BUFFER_TOKEN"]}
)
with urllib.request.urlopen(req2) as r:
    result = json.loads(r.read())
    print("Buffer queued:", result.get("success"))

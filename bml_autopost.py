import urllib.request, urllib.parse, json, os, datetime, re, sys

sites = [
    {"name": "BrokeModeLife", "url": "brokemodelife.com", "focus": "budget living, saving money, living well on less", "credit": ""},
    {"name": "StopLookAround", "url": "stoplookaround.com", "focus": "travel without selfies, no faces just places, experiencing the world not performing it", "credit": "stoplookaround.com"},
    {"name": "DontBeHangry", "url": "dontbehangry.com", "focus": "world food culture and history journalism, the stories behind what people eat", "credit": "dontbehangry.com"},
    {"name": "FineLivingGuide", "url": "finelivingguide.com", "focus": "high-end luxury living, fine dining, rare spirits, buy once buy right", "credit": "finelivingguide.com"}
]

# Rotate site by day-of-year so each day gets a consistent site
# 2 posts per day = same site morning and evening, rotates daily
day = datetime.datetime.utcnow().timetuple().tm_yday
site = sites[day % 4]

# Use hour to vary tone between morning and evening post
hour = datetime.datetime.utcnow().hour
tone = "energizing and motivating" if hour < 15 else "reflective and practical"

if site["credit"]:
    credit_rule = "Weave " + site["credit"] + " naturally into the post body as part of a sentence. NEVER write 'from our friends at' or any variation."
else:
    credit_rule = "No external site credit needed."

prompt = ("Write one X post for @brokemode. "
    "Site: " + site["name"] + " covering " + site["focus"] + ". "
    "Tone: " + tone + ". "
    "Rules: max 260 chars. Sharp direct real voice. Budget mindset always. 1-2 hashtags max. "
    + credit_rule +
    " Return ONLY the post text. No quotes, no labels, no explanation.")

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=json.dumps({"model": "claude-sonnet-4-20250514", "max_tokens": 150,
        "messages": [{"role": "user", "content": prompt}]}).encode(),
    headers={"x-api-key": os.environ["ANTHROPIC_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"}
)
with urllib.request.urlopen(req) as r:
    response = json.loads(r.read())

text_blocks = [b["text"] for b in response["content"] if b["type"] == "text"]
text = text_blocks[0].strip() if text_blocks else ""
text = re.sub(r'^[^\w\U00010000-\U0010ffff]+', '', text, flags=re.UNICODE).strip()

if not text:
    print("ERROR: empty post")
    sys.exit(1)

print("Post (" + str(len(text)) + " chars): " + text)

data = urllib.parse.urlencode({"profile_ids[]": os.environ["PROFILE_ID"], "text": text}).encode()
req2 = urllib.request.Request("https://api.bufferapp.com/1/updates/create.json", data=data,
    headers={"Authorization": "Bearer " + os.environ["BUFFER_TOKEN"]})
with urllib.request.urlopen(req2) as r:
    result = json.loads(r.read())
    print("Buffer queued:", result.get("success"))

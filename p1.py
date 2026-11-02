# ---- 1. Variables: no const, no let, no semicolons ----
name = "Sara"                      # text (called a "string")
age = 29                           # number
is_urgent = True                   # True / False with a CAPITAL letter

# ---- 2. Printing: f-strings = JavaScript's `Hi ${name}` ----
print(f"Hi {name}, you are {age}")

# ---- 3. A list = JavaScript array ----
langs = ["en", "ar"]
langs.append("hi")                 # like .push()
print(langs)                       # ['en', 'ar', 'hi']
print(len(langs))                  # like .length  → 3

# ---- 4. A dict = JavaScript object (keys need quotes!) ----
msg = {"id": 1, "text": "My visa expires tomorrow!!", "urgent": True}
print(msg["text"])                 # square brackets, not msg.text

# ---- 5. if / else: colon + indentation instead of { } ----
if msg["urgent"]:
    print("🚨 urgent")
else:
    print("normal")

messages = [
    {"id": 1, "text": "My visa expires tomorrow!!", "lang": "en", "urgent": True},
    {"id": 2, "text": "كيف أجدد الهوية الإماراتية؟", "lang": "ar", "urgent": False},
    {"id": 3, "text": "DEWA bill is too high this month", "lang": "en", "urgent": False},
    {"id": 4, "text": "حسابي مقفول وما أقدر أدفع المخالفة", "lang": "ar", "urgent": True},
]

def print_msg():
    for message in messages:
        if message['urgent']:
            status = 'urgent' if message['urgent'] else 'normal'
            print(f"{message['text']} - {message['lang'] - message['urgent']}")

print_msg()


def count_urgent():
    count = 0
    for message in messages:
        if message['urgent']:
            count +=1
        print(count)

count_urgent()
        
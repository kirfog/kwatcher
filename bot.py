import feedparser
import requests
import time

session = requests.session()
#session.proxies = {}
#session.proxies['http'] = 'socks5h://localhost:9050'
#session.proxies['https'] = 'socks5h://localhost:9050'

url = "https://api.telegram.org/bot634132320:AAG52vGYQkoJYwrMoB2AFLQmkPz7SCMyaf0/"

def get_updates_json(request):
    params = {'timeout': 100, 'offset': None}
    response = session.get(request + 'getUpdates', data=params)
    return response.json()

def last_update(data):
    results = data['result']
    total_updates = len(results) - 1
    return results[total_updates]

def day_updates(data):
    results = data['result']
    total_updates = len(results) - 1
    return total_updates

def get_chat_id(update):
    chat_id = update['message']['chat']['id']
    return chat_id

def get_chat_first_name(update):
    chat_first_name = update['message']['chat']['first_name']
    return chat_first_name

def get_chat_text(update):
    chat_text = update['message']['text']
    return chat_text

def send_mess(chat, text):
    params = {'chat_id': chat, 'text': text}
    response = session.post(url + 'sendMessage', data=params)
    return response

def get_rss(link):
    rss = feedparser.parse(link)
    r = ""
    for i in rss['entries']:
        r = r + "\n" + i['title'] + " " + i['link'] + " " + i['description'] + "\n"
    return r

def get_sunrise():
	sessionSun = requests.session()
	#sessionSun.proxies = {}
	#sessionSun.proxies['http'] = 'socks5h://localhost:9050'
	#sessionSun.proxies['https'] = 'socks5h://localhost:9050'
	sun = sessionSun.get("https://api.sunrise-sunset.org/json?lat=59.9342802&lng=30.3350986").json()
	return sun

def month13(chat_id):
    year = time.localtime().tm_year
    month = time.localtime().tm_yday // 28 + 1
    day = time.localtime().tm_yday % 28
    time13 = (time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60 + time.localtime().tm_sec)/86400*8000
    time13hour = int(time13 // 400)
    time13min = int((time13 % 400)//20)
    time13sec = int(((time13 % 400) % 20))
    if time13hour == time13min and time13hour == day:
        send_mess(chat_id, "Today is " + str(day) + " day in " + str(month) + " month of " + str(year) + ". Time is " + str(time13hour) + ":" + str(time13min) +  ":" + str(time13sec))
        time.sleep(20)
    print("Today is " + str(day) + " day in " + str(month) + " month of " + str(year) + ". Time is " + str(time13hour) + ":" + str(time13min) +  ":" + str(time13sec))

def main():
    update_id = last_update(get_updates_json(url))['update_id']
    while True:
        updates = get_updates_json(url)
        day = day_updates(updates)
        last = last_update(updates)
        chat_id = get_chat_id(last)
        month13(chat_id)
        #print(day)
        #print(last['update_id'])
        #print(last)

        if last['update_id'] > update_id:
            chat_id = get_chat_id(last)
            first_name = get_chat_first_name(last)
            chat_text = get_chat_text(last)
            send_mess(chat_id, "Hi " + first_name + ", did you say " + chat_text + "?")            
            if chat_text.lower() == "nasa":
                send_mess(chat_id,"Colling to NASA.....")
                rss = get_rss("https://www.nasa.gov/rss/dyn/breaking_news.rss")
                send_mess(chat_id,rss)

            if chat_text.lower() == "earth":
                send_mess(chat_id,"Colling to EARTH.....")
                rss = get_rss("https://www.nasa.gov/rss/dyn/earth.rss")
                send_mess(chat_id,rss)

            if chat_text.lower() == "sun":
                send_mess(chat_id,"Colling to SUN.....")
                sun = get_sunrise()
                send_mess(chat_id, "Sun rises at " + str(sun["results"]["sunrise"]) + " and sets at " + str(sun["results"]["sunset"]) + "UTC")
            update_id += 1
        time.sleep(20)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

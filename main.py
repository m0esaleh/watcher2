import time
import requests

BOT_TOKEN = "8219584179:AAEWSwq_Q52IjdHQc4rBrbQEOQiu3GqC4-Y"   # ضع التوكن هنا
CHAT_ID = "5999882731"     # ضع الشات ID هنا

WATCHLIST = [
    {
        "manufacturer": "현대",
        "model": "그랜저",
        "detail": "GN7",
        "engine": "3.5",
        "max_price": 3500,
    },

    # مثال سيارة ثانية (احذفها لو مش بدك إياها)
    {
        "manufacturer": "기아",
        "model": "K5",
        "detail": "",
        "engine": "2.0",
        "max_price": 2000,
    }
]

LAST_SEEN = {}

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

def build_api_url(car):
    return (
        "https://api.encar.com/search/list/general?"
        f"count=30&q=(And.Hidden.N._.CarType.Y"
        f"._.Manufacturer.{car['manufacturer']}"
        f"._.Model.{car['model']}"
        f"._.ModelDetail.{car['detail']}"
        f"._.Engine.{car['engine']})"
        "&sr=%7B%22Sort%22:%22CreatedDate%20DESC%22%7D"
    )

def check_car(car):
    name = f"{car['manufacturer']} {car['model']} {car['detail']} {car['engine']}"
    api = build_api_url(car)

    r = requests.get(api, headers={"User-Agent": "Mozilla/5.0"})
    data = r.json()
    cars = data.get("SearchResults", [])

    if not cars:
        return

    latest = cars[0]
    car_id = latest["Id"]

    if name not in LAST_SEEN:
        LAST_SEEN[name] = car_id
        return

    if car_id != LAST_SEEN[name]:
        LAST_SEEN[name] = car_id

        price = int(latest["Price"])
        if price > car["max_price"] * 10000:
            return

        link = f"https://www.encar.com/dc/dc_cardetailview.do?carid={car_id}"
        year = latest.get("Year")
        model_name = latest.get("Model", "")

        msg = (
            f"🚗 New Car Found!\n\n"
            f"📌 {model_name} ({car['engine']})\n"
            f"📅 Year: {year}\n"
            f"💰 Price: {price:,} 원\n"
            f"🔗 {link}"
        )
        send_message(msg)

def main():
    send_message("🤖 Car Watcher Bot Started (Render 24/7)")

    while True:
        for car in WATCHLIST:
            try:
                check_car(car)
            except Exception as e:
                send_message(f"Error: {e}")

        time.sleep(15)

if __name__ == "__main__":
    main()
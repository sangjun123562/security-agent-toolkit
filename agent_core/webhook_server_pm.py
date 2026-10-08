import argparse
import json
from flask import Flask, request

parser = argparse.ArgumentParser(description="경보를 받는 웹훅 서버")
parser.add_argument("--port", type=int, default=5000)
args = parser.parse_args()

app = Flask(__name__)
received = []


@app.route("/webhook", methods=["POST"])
def webhook():
    event = request.get_json()
    received.append(event)
    with open("received_alerts.json", "w", encoding="utf-8") as f:
        json.dump(received, f, ensure_ascii=False, indent=2)
    return {"status": "ok", "count": len(received)}, 200


app.run(port=args.port)

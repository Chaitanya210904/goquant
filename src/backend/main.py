from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import requests
import json
import os
import re
from dotenv import load_dotenv
from utils.exchange_api import fetch_symbols, fetch_price

load_dotenv()

app = FastAPI()

# Mount static and template directories
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation state
conversation_state = {
    "exchange": None,
    "symbol": None,
    "price": None,
    "quantity": None
}

# Serve frontend UI
@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# WebSocket endpoint for frontend
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({
        "bot": "Welcome! Please select an exchange: OKX, Bybit, Deribit, Binance."
    }))

    while True:
        try:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "stop":
                break

            user_input = message.get("text", "Binance")
            response = handle_conversation(user_input)
            await websocket.send_text(json.dumps({
                "bot": response,
                "user": user_input
            }))

        except Exception as e:
            await websocket.send_text(json.dumps({
                "bot": f"Error: {str(e)}"
            }))


# Webhook for Bland.ai
@app.post("/bland-webhook")
async def bland_webhook(request: Request):
    body = await request.json()
    print("Incoming from Bland.ai:", body)

    if body.get("intent") == "order_execution":
        return {
            "messages": [
                {"type": "text", "text": "Please say your order like '1.5 at 27000'"}
            ]
        }

    user_input = body.get("message", "").strip()
    response = handle_conversation(user_input)

    return {
        "messages": [
            {"type": "text", "text": response}
        ]
    }


# Handle user input logic
def handle_conversation(user_input):
    global conversation_state
    user_input = user_input.strip()

    if user_input.lower() == "reset":
        conversation_state = {
            "exchange": None,
            "symbol": None,
            "price": None,
            "quantity": None
        }
        return "Conversation reset. Please select an exchange: OKX, Bybit, Deribit, or Binance."

    if conversation_state["exchange"] is None:
        exchange = user_input.capitalize()
        if exchange not in ["Binance", "Bybit", "Okx", "Deribit"]:
            return "Invalid exchange. Please choose from OKX, Bybit, Deribit, or Binance."
        conversation_state["exchange"] = exchange
        return f"Great! Which symbol would you like to trade on {exchange}? (e.g., BTCUSDT)"

    elif conversation_state["symbol"] is None:
        symbol = user_input.upper()
        try:
            available_symbols = fetch_symbols(conversation_state["exchange"])
        except Exception as e:
            print("Error fetching symbols:", e)
            return "Failed to fetch symbols. Please try again later."

        if symbol not in available_symbols:
            return f"Symbol '{symbol}' not found on {conversation_state['exchange']}. Please try another."

        conversation_state["symbol"] = symbol

        try:
            price = fetch_price(conversation_state["exchange"], symbol)
        except Exception as e:
            print(f"Error fetching price: {e}")
            price = "Unavailable"

        conversation_state["price"] = price

        return f"The current price of {symbol} is {price}. Please provide quantity and your desired price like '1.5 at 27000'."

    elif conversation_state["quantity"] is None:
        match = re.match(r"(\d+(?:\.\d+)?)\s*at\s*(\d+(?:\.\d+)?)", user_input.lower())
        if match:
            qty, price = match.groups()
            conversation_state["quantity"] = qty
            conversation_state["price"] = price
            return (f"Confirming order: {qty} of {conversation_state['symbol']} at {price} "
                    f"on {conversation_state['exchange']}. Say 'reset' to start over.")
        else:
            return "Please format your order like '1.5 at 27000'"

    else:
        return "Conversation completed. Say 'reset' to start a new one."


# Optional fallback price fetch
def get_price(exchange, symbol):
    try:
        if exchange.lower() == "binance":
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            res = requests.get(url)
            return res.json().get("price", "Unavailable")
    except Exception as e:
        print(f"Error in fallback price fetch: {e}")
        return "Unavailable"


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

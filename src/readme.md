# Trading Bot API

A FastAPI-based trading bot that handles order placement conversations via WebSocket and webhooks, with integration for external exchange APIs.

## Features
- **Real-time WebSocket communication** for interactive trading
- **Bland.ai webhook integration** for voice-based interactions
- **Multi-exchange support** (Binance, Bybit, OKX, Deribit)
- **Conversational order flow** with state management
- **Price/symbol validation** using exchange APIs

## Setup Instructions

### 1. Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 2. Environment Variables
Create `.env` file with:
```
EXCHANGE_API_KEY=your_api_key
# Add other exchange-specific credentials
```

### 3. Running the Application
```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

### WebSocket Interface
- **Endpoint**: `ws://localhost:8000/ws`
- **Protocol**: JSON messages
- **Flow**:
  1. Client connects to WebSocket
  2. Bot prompts for exchange selection
  3. User responds with exchange name
  4. Bot prompts for trading symbol
  5. User responds with symbol
  6. Bot shows current price and prompts for quantity/price
  7. User responds with `[quantity] at [price]`

### Bland.ai Webhook
- **Endpoint**: `POST /bland-webhook`
- **Request Format**:
  ```json
  {
    "intent": "order_execution",
    "message": "User input"
  }
  ```
- **Response Format**:
  ```json
  {
    "messages": [{"type": "text", "text": "Bot response"}]
  }
  ```

## Conversation Flow
```
Exchange Selection → Symbol Selection → Order Placement → Confirmation
```

### State Transitions
1. **Exchange Selection**:
   - Valid inputs: `Binance`, `Bybit`, `OKX`, `Deribit`
   - Sets `conversation_state['exchange']`

2. **Symbol Selection**:
   - Input must be valid symbol (e.g., `BTCUSDT`)
   - Verifies against exchange API
   - Sets `conversation_state['symbol']` and fetches current price

3. **Order Placement**:
   - Input format: `[quantity] at [price]` (e.g., `1.5 at 27000`)
   - Sets `conversation_state['quantity']` and `['price']`

4. **Reset Command**:
   - Input `reset` clears conversation state

## Dependencies
- Python 3.7+
- FastAPI
- Uvicorn
- Requests
- python-dotenv
- Exchange-specific SDKs (implemented in `utils/exchange_api.py`)

## File Structure
```
trading-bot/
├── main.py             # Primary application logic
├── utils/
│   └── exchange_api.py # Exchange API integrations
├── .env                # Environment variables
└── README.md
```

## Configuration
Modify these in the code:
- **CORS Settings**: Adjust `allow_origins` in `CORSMiddleware`
- **Port Configuration**: Change in `uvicorn.run()` at bottom of file
- **Exchange APIs**: Implement new exchanges in `utils/exchange_api.py`

## Error Handling
Common error responses:
- `Invalid exchange...`: When unsupported exchange is provided
- `Symbol not found...`: When invalid trading pair is entered
- `Please format your order...`: When quantity/price input is malformed
- `Error: ...`: WebSocket connection errors

## Testing

### 1. WebSocket Test
```python
import websockets
import asyncio
import json

async def test_ws():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        print(await ws.recv())  # Welcome message
        await ws.send(json.dumps({"text": "Binance"}))
        print(await ws.recv())  # Symbol prompt

asyncio.get_event_loop().run_until_complete(test_ws())
```

### 2. Webhook Test
```bash
curl -X POST http://localhost:8000/bland-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "Binance"}'
```

## Production Deployment
1. Remove `reload=True` in `uvicorn.run()`
2. Use production server:
```bash
uvicorn main:app --host 0.0.0.0 --port 80 --workers 4
```
3. Set up reverse proxy (Nginx/Apache)
4. Implement persistent state storage (currently in-memory)

## Troubleshooting
- **Symbols not loading**: Check exchange API connectivity in `fetch_symbols()`
- **Price fetch failures**: Verify API keys and network access
- **WebSocket disconnects**: Implement reconnect logic in client

## License
This project is licensed under the MIT License.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
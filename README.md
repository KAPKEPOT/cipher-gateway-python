# cipher-gateway-python

Official Python SDK for the **Cipher MT5 Gateway (CMG)** — a self-hosted bridge between your application and MetaTrader 5.

Built and maintained by [CipherBridge](https://cipherbridge.cloud).

---

## What is CMG?

The Cipher MT5 Gateway is a self-hosted Rust server that manages MT5 terminal connections through the CipherBridge (CMB) C++ bridge. Instead of routing through third-party cloud APIs, CMG runs on your own infrastructure — giving you full control over latency, cost, and data.

```
Your App (Python)
      │
      │  HTTPS / WSS
      ▼
CMG  (Rust — your server)
      │
      │  TCP
      ▼
CMB  (C++ DLL + MQL5)
      │
      ▼
MT5 Terminal → Broker
```

This SDK handles all communication with CMG so you never write raw HTTP calls.

---

## Installation

```bash
pip install git+https://github.com/ciphertrade/cipher-gateway-python.git
```

Or clone and install locally:

```bash
git clone https://github.com/ciphertrade/cipher-gateway-python.git
cd cipher-gateway-python
pip install -e .
```

**Requirements:** Python 3.10+, `httpx`, `websockets`

---

## Quick Start

```python
import asyncio
from cipher_gateway import CipherGatewayClient, GatewayConfig

config = GatewayConfig(
    host="gateway.yourdomain.com",
    port=443,
    use_ssl=True,
)

async def main():
    # 1. Create a gateway user — do this once per user, store the credentials
    async with CipherGatewayClient.admin(config) as client:
        user_creds = await client.create_user()
        print(f"api_key:    {user_creds.api_key}")
        print(f"user_id:    {user_creds.gateway_user_id}")

    # 2. Provision an MT5 account — do this once per MT5 account
    async with CipherGatewayClient.for_user(config, user_creds.api_key) as client:
        account = await client.create_account(
            mt5_login="12345678",
            mt5_password="YourMT5Password",
            mt5_server="ICMarkets-Demo",
        )
        print(f"account_id: {account.account_id}")

        # Wait for MT5 to connect (10–30 seconds)
        await client.wait_for_active(account.account_id, timeout=60)
        print("MT5 connected!")

    # 3. Trade — use api_key + account_id from now on, credentials never needed again
    async with CipherGatewayClient.for_user(config, user_creds.api_key) as client:
        info = await client.get_account_info()
        print(f"Balance: {info.balance} {info.currency}")

        result = await client.place_market_buy("EURUSD", volume=0.1, sl=1.0800, tp=1.1000)
        print(f"Order placed: ticket={result.ticket}")

asyncio.run(main())
```

---

## Core Concept — Credential Flow

CMG owns your MT5 credentials. The SDK reflects this:

```
Step 1 — Register (one time)
  create_user()        → returns api_key + gateway_user_id  (store these)
  create_account()     → returns account_id                 (store this)
  wait_for_active()    → confirms MT5 is connected

Step 2 — Every request after that
  for_user(api_key)    → authenticates the user
  account_id           → tells CMG which MT5 account to act on

MT5 login, password, server — never needed again after Step 1.
```

Store only these three values per user in your database:
- `gateway_user_id`
- `gateway_api_key`
- `gateway_account_id`

---

## Configuration

```python
from cipher_gateway import GatewayConfig

config = GatewayConfig(
    host="gateway.yourdomain.com",  # CMG hostname or IP
    port=443,                        # 443 for SSL, 8080 for plain HTTP
    use_ssl=True,                    # Must match your nginx/proxy setup
    api_key_header="X-API-Key",      # Header name CMG expects
    connect_timeout=10.0,            # Seconds to establish connection
    request_timeout=30.0,            # Seconds to wait for response
    ws_reconnect_delay=5.0,          # Seconds between WebSocket reconnect attempts
    max_reconnect_attempts=5,        # Max WebSocket reconnect attempts
)
```

---

## Client Modes

### Admin client — no authentication required
Used only for `health_check()` and `create_user()`.

```python
async with CipherGatewayClient.admin(config) as client:
    healthy = await client.health_check()
    user_creds = await client.create_user()
```

### User client — authenticated
Used for all trading operations.

```python
async with CipherGatewayClient.for_user(config, api_key="your-api-key") as client:
    info = await client.get_account_info()
```

---

## API Reference

### Health

```python
healthy = await client.health_check()  # → bool
```

### User Management

```python
# Create a new gateway user
user_creds = await client.create_user()
# user_creds.gateway_user_id  — store in DB
# user_creds.api_key           — store in DB
```

### Account Lifecycle

```python
# Provision a new MT5 account on CMG
account = await client.create_account(
    mt5_login="12345678",
    mt5_password="password",
    mt5_server="ICMarkets-Demo",
    region="eu",        # optional
)
# account.account_id  — store in DB

# Wait for MT5 connection to become active
await client.wait_for_active(account.account_id, timeout=60)

# Check status manually
status = await client.get_account_status(account.account_id)
# status["status"]     — "active", "connecting", "login_failed", "deleted"
# status["last_error"] — error message if login_failed

# List all accounts
accounts = await client.get_accounts()

# Pause / resume trading
await client.pause_account(account.account_id)
await client.resume_account(account.account_id)

# Remove account from CMG permanently
await client.delete_account(account.account_id)
```

### Account Information

```python
info = await client.get_account_info()
# info.login        → int
# info.name         → str
# info.server       → str
# info.balance      → float
# info.equity       → float
# info.margin       → float
# info.free_margin  → float
# info.leverage     → int
# info.currency     → str  ("USD", "EUR", ...)
# info.profit       → float
# info.margin_level → float  (computed property, %)
```

### Positions

```python
# Get all open positions
positions = await client.get_positions()
for p in positions:
    print(p.ticket, p.symbol, p.side, p.volume, p.profit)

# Close a position
result = await client.close_position(ticket=123456)
result = await client.close_position(ticket=123456, volume=0.05)  # partial close

# Modify SL/TP
result = await client.modify_position(ticket=123456, sl=1.0800, tp=1.1000)
```

### Orders

```python
# Market orders
result = await client.place_market_buy("EURUSD", volume=0.1)
result = await client.place_market_sell("GBPUSD", volume=0.2, sl=1.2500, tp=1.2200)

# Limit orders
result = await client.place_limit_buy("EURUSD", volume=0.1, price=1.0750)
result = await client.place_limit_sell("EURUSD", volume=0.1, price=1.1050)

# Stop orders
result = await client.place_stop_buy("EURUSD", volume=0.1, price=1.0950)
result = await client.place_stop_sell("EURUSD", volume=0.1, price=1.0700)

# All order methods accept optional parameters:
result = await client.place_market_buy(
    symbol="EURUSD",
    volume=0.1,
    sl=1.0800,       # stop loss price
    tp=1.1000,       # take profit price
    comment="bot",   # order comment
    magic=12345,     # magic number for EA identification
)

# OrderResult
# result.ticket   → int    (MT5 ticket number)
# result.success  → bool
# result.error    → str | None
```

### Market Data (REST)

```python
price = await client.get_symbol_price("EURUSD")
# price.symbol  → "EURUSD"
# price.bid     → float
# price.ask     → float
# Falls back to WebSocket cache if REST returns zeros
```

### Real-Time Data (WebSocket)

```python
# Connect WebSocket
await client.subscribe(["EURUSD", "GBPUSD"])

# Register callbacks
def on_tick(tick):
    print(f"{tick.symbol} bid={tick.bid} ask={tick.ask}")

async def on_position_update(position):
    print(f"Position update: {position.ticket} profit={position.profit}")

client.ws.on_tick("EURUSD", on_tick)
client.ws.on_position(on_position_update)
client.ws.on_candle("EURUSD", "H1", lambda c: print(f"New candle: {c.close}"))
client.ws.on_order_result(lambda r: print(f"Order result: {r.ticket}"))
client.ws.on_account(lambda a: print(f"Balance update: {a.balance}"))

# Ping
alive = await client.ping_ws()

# Unsubscribe
await client.unsubscribe(["GBPUSD"])
```

---

## Models

| Model | Fields |
|---|---|
| `GatewayConfig` | `host`, `port`, `use_ssl`, `api_key_header`, `connect_timeout`, `request_timeout` |
| `UserCredentials` | `gateway_user_id`, `api_key` |
| `AccountCredentials` | `account_id`, `auth_token` |
| `AccountInfo` | `login`, `name`, `server`, `balance`, `equity`, `margin`, `free_margin`, `leverage`, `currency`, `profit`, `margin_level` |
| `Position` | `ticket`, `symbol`, `side`, `volume`, `open_price`, `current_price`, `profit`, `swap`, `commission`, `sl`, `tp`, `comment` |
| `OrderResult` | `ticket`, `success`, `error` |
| `SymbolPrice` | `symbol`, `bid`, `ask` |
| `Tick` | `symbol`, `bid`, `ask`, `last`, `volume`, `time` |
| `Quote` | `symbol`, `bid`, `ask`, `time`, `spread`, `mid` |
| `Candle` | `symbol`, `timeframe`, `time`, `open`, `high`, `low`, `close`, `volume`, `complete` |

---

## Exceptions

All exceptions inherit from `CipherGatewayError`.

```python
from cipher_gateway import (
    CipherGatewayError,        # base — catch-all
    NotStartedError,           # client used before start()
    AuthenticationError,       # invalid or missing API key
    AccountNotFoundError,      # account_id does not exist
    AccountLoginFailedError,   # MT5 rejected the credentials
    AccountTimeoutError,       # account did not become active in time
    OrderError,                # order placement/close/modify failed
    ConnectionError,           # HTTP or WebSocket connection failed
    SubscriptionError,         # WebSocket subscription failed
    GatewayResponseError,      # unexpected HTTP response (has .status_code, .raw)
)
```

Example error handling:

```python
from cipher_gateway import (
    CipherGatewayClient,
    AccountLoginFailedError,
    AccountTimeoutError,
    OrderError,
    AuthenticationError,
)

try:
    await client.wait_for_active(account_id)
except AccountLoginFailedError as e:
    print(f"Wrong MT5 credentials: {e}")
except AccountTimeoutError as e:
    print(f"MT5 took too long to connect: {e}")

try:
    result = await client.place_market_buy("EURUSD", volume=0.1)
except OrderError as e:
    print(f"Order failed: {e}")
except AuthenticationError:
    print("API key is invalid or expired")
```

---

## Usage in a Telegram Bot

```python
# On registration — called once
async with CipherGatewayClient.admin(config) as c:
    user_creds = await c.create_user()

async with CipherGatewayClient.for_user(config, user_creds.api_key) as c:
    account = await c.create_account(login, password, server)
    await c.wait_for_active(account.account_id)

# Save to DB — this is all you need forever
db.save(
    telegram_id=user_id,
    gateway_api_key=user_creds.api_key,
    gateway_account_id=account.account_id,
)
# MT5 login, password, server — never stored, never needed again

# On every trade command — load from DB, use immediately
user = db.get(telegram_id=user_id)
async with CipherGatewayClient.for_user(config, user.gateway_api_key) as c:
    result = await c.place_market_buy("EURUSD", volume=0.1)
```

---

## Project Structure

```
cipher_gateway/
├── __init__.py     — public API exports
├── client.py       — CipherGatewayClient (main entry point)
├── models.py       — all data classes
├── exceptions.py   — exception hierarchy
├── transport.py    — HTTP layer (httpx wrapper)
└── websocket.py    — WebSocket layer (real-time data + reconnection)
```

---

## License

Proprietary — CipherTrade. All rights reserved.

# Independent Forex Order Book Trading Agent

This is a fully independent, automated trading agent designed to trade the BTC/USD pair. Its strategy is based solely on analyzing Level 2 order book data, such as liquidity distribution and order flow imbalance.

The agent connects directly to the **FXOpen TickTrader API** for both real-time market data (via WebSocket) and trade execution (via WebREST API). It **does not** require the MetaTrader 5 platform or any other desktop software to run.

## Key Features

- **Order Book Analysis:** The core strategy does not use traditional indicators. Instead, it analyzes:
  - **Order Book Imbalance:** Calculates the ratio of buy vs. sell pressure in the order book.
  - **Liquidity Walls:** Dynamically identifies significant price levels with high liquidity to act as support and resistance.
- **Dynamic Risk Management:**
  - **Stop Loss & Take Profit:** SL and TP levels are not fixed; they are calculated dynamically for each trade based on the nearest liquidity walls.
  - **Lot Sizing:** Position size is calculated automatically based on a fixed percentage of the account balance and the distance to the dynamic stop loss price.
- **Direct API Integration:**
  - Connects directly to **FXOpen's TickTrader API** for both data and trading.
  - Operates as a standalone Python application.
- **Secure Configuration:** All sensitive information (API keys, account details) is managed via a `.env` file and is not stored in the code.

---

## Requirements

Before you begin, ensure you have the following:
1.  **Python 3.8+** installed.
2.  An **FXOpen TickTrader account** (a free demo account is recommended for testing) to get your API credentials.

---

## How to Run the Agent (كيفية التشغيل)

Follow these steps to set up and run the trading agent:

### Step 1: Install Dependencies

Open a terminal or command prompt in the project's root directory and run the following command to install all the necessary Python libraries:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Your Credentials

You need to provide your FXOpen API credentials for the agent to work.

1.  Find the file named `.env.example` in the project folder.
2.  Create a copy of this file and rename the copy to **`.env`**.
3.  Open the new `.env` file with a text editor and fill in your details:

    - `FXOPEN_API_ID`, `FXOPEN_API_KEY`, `FXOPEN_API_SECRET`: Your personal API credentials from the FXOpen client portal.
    - `FXOPEN_WEBSOCKET_URL`: This should already be set to the correct feed URL.
    - `FXOPEN_TRADE_URL`: This should already be set to the correct trade API URL.
    - `FOREX_SYMBOL`: The symbol you wish to trade, e.g., "BTC/USD".
    - `RISK_PERCENTAGE`: The percentage of your account balance you want to risk per trade (e.g., `1.0` for 1%).


### Step 3: Run the Agent

1.  Open a terminal or command prompt in the project's root directory.
2.  Run the following command:

    ```bash
    python -m forex.main_forex
    ```

The agent will now start. It will attempt to connect to the FXOpen data and trade servers. If successful, it will enter its main trading loop, analyzing the market and executing trades based on its strategy.

To stop the agent, simply press `Ctrl+C` in the terminal.

---

## Disclaimer

This software is for educational and experimental purposes only. Trading financial markets involves significant risk. Always test thoroughly on a demo account before considering live trading. The author is not responsible for any financial losses.
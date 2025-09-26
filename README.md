# Forex Order Book Trading Agent

This is an automated trading agent designed to trade the BTC/USD pair on the MetaTrader 5 platform. Its strategy is based solely on analyzing Level 2 order book data, such as liquidity distribution and order flow imbalance. The agent fetches its market data from FXCM and executes trades via the MT5 terminal.

## Key Features

- **Order Book Analysis:** The core strategy does not use traditional indicators. Instead, it analyzes:
  - **Order Book Imbalance:** Calculates the ratio of buy vs. sell pressure in the order book.
  - **Liquidity Walls:** Dynamically identifies significant price levels with high liquidity to act as support and resistance.
- **Dynamic Risk Management:**
  - **Stop Loss & Take Profit:** SL and TP levels are not fixed; they are calculated dynamically for each trade based on the nearest liquidity walls.
  - **Lot Sizing:** Position size is calculated automatically based on a fixed percentage of the account balance and the distance to the dynamic stop loss price.
- **Live Data & Execution:**
  - Connects to **FXCM** for real-time Level 2 order book data.
  - Connects to the **MetaTrader 5** terminal for trade execution.
- **Secure Configuration:** All sensitive information (API keys, account details) is managed via a `.env` file and is not stored in the code.

---

## Requirements

Before you begin, ensure you have the following:
1.  A **Windows** operating system.
2.  The **MetaTrader 5** terminal installed and running.
3.  **Python 3.8+** installed.
4.  An **FXCM account** (a free demo account is recommended for testing) to get an API token.
5.  An **MT5 account** (demo or live) that you are logged into on the terminal.

---

## How to Run the Agent (كيفية التشغيل)

Follow these steps to set up and run the trading agent:

### Step 1: Install Dependencies

Open a terminal or command prompt in the project's root directory and run the following command to install all the necessary Python libraries:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Your Credentials

You need to provide your API keys and account details for the agent to work.

1.  Find the file named `.env.example` in the project folder.
2.  Create a copy of this file and rename the copy to `.env`.
3.  Open the new `.env` file with a text editor and fill in your details:

    - `FXCM_API_TOKEN`: Your personal access token from the MyFXCM portal (under "Token Management").
    - `FXCM_SERVER_MODE`: Keep this as `"demo"` for a demo account or change it to `"real"` for a live account.
    - `MT5_LOGIN`: Your MetaTrader 5 account number.
    - `MT5_PASSWORD`: Your MetaTrader 5 account password.
    - `MT5_SERVER`: The name of your broker's server (you can find this on the MT5 login screen).
    - `MT5_PATH`: The full path to the `terminal64.exe` file of your MT5 installation. The example path is a common default.
    - `FOREX_SYMBOL`: The symbol for Bitcoin vs. USD as it appears on your MT5 terminal (e.g., "BTCUSD", "BTC/USD").
    - `RISK_PERCENTAGE`: The percentage of your account balance you want to risk per trade (e.g., `1.0` for 1%).


### Step 3: Run the Agent

1.  Make sure your MetaTrader 5 terminal is open and logged into the correct account.
2.  Open a terminal or command prompt in the project's root directory.
3.  Run the following command:

    ```bash
    python -m forex.main_forex
    ```

The agent will now start. It will first attempt to connect to FXCM and MT5. If successful, it will enter its main trading loop, analyzing the market and executing trades based on its strategy.

To stop the agent, simply press `Ctrl+C` in the terminal.

---

## Disclaimer

This software is for educational and experimental purposes only. Trading financial markets involves significant risk. Always test thoroughly on a demo account before considering live trading. The author is not responsible for any financial losses.
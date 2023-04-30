import time
import numpy as np
from derivapi import DerivAPI

# Replace these with your actual Deriv API credentials
DERIV_EMAIL = 'manfredkeethphilander2@gmail.com '
DERIV_PASSWORD = 'Boengels2'
DERIV_APP_ID = '30703599'

# Define your trading parameters
SYMBOL = 'R_75'
TRADE_DURATION = 5
AMOUNT = 0.001
MAX_TRADES_PER_DAY = 5
STOP_LOSS_DISTANCE = 3
TAKE_PROFIT_DISTANCE = 9

# Connect to the Deriv API
api = DerivAPI(DERIV_EMAIL, DERIV_PASSWORD, app_id=DERIV_APP_ID)

# Define a function to get the latest candle data for the given symbol
def get_candle_data(symbol, duration, count):
    candles = api.get_candles(symbol, duration, count)
    # Reverse the list so that the latest candle is the first item
    return list(reversed(candles))

# Define a function to execute a buy trade
def buy():
    api.buy(AMOUNT, SYMBOL, 'CALL', TRADE_DURATION)

# Define a function to execute a sell trade
def sell():
    api.sell(AMOUNT, SYMBOL, 'PUT', TRADE_DURATION)

# Define a function to calculate the 200 SMA
def calculate_sma(candles, period):
    close_prices = [candle['close'] for candle in candles[-period:]]
    sma = np.mean(close_prices)
    return sma

# Define a function to calculate the average true range (ATR)
def calculate_atr(candles, period):
    high_prices = [candle['high'] for candle in candles[-period:]]
    low_prices = [candle['low'] for candle in candles[-period:]]
    close_prices = [candle['close'] for candle in candles[-period-1:-1]]
    tr = []
    for i in range(period):
        true_high = max(high_prices[i+1], close_prices[i])
        true_low = min(low_prices[i+1], close_prices[i])
        tr.append(true_high - true_low)
    atr = np.mean(tr)
    return atr

# Start the main loop
trades_today = 0
while True:
    try:
        # Get the latest 1000 candles
        candles = get_candle_data(SYMBOL, TRADE_DURATION, 1000)

        # Check if price is moving up or down
        close_prices = [candle['close'] for candle in candles]
        sma_200 = calculate_sma(candles, 200)
        sma_20 = calculate_sma(candles, 20)
        atr = calculate_atr(candles, 14)
        last_candle = candles[-1]
        prev_candle = candles[-2]

        if last_candle['close'] > prev_candle['close']:
            # Price is moving up, look for buy opportunities
            if sma_200 < sma_20:
                # Wait for 5 candles to close
                time.sleep(TRADE_DURATION * 5)
                candles = get_candle_data(SYMBOL, TRADE_DURATION, 1000)

                # Check if 200 SMA is still below 20 SMA
                sma_200 = calculate_sma(candles, 200)
                sma_20 = calculate_sma(candles, 20)
                if sma_200 < sma_20:
                    if last_candle['close'] > sma_20 and prev_candle['close'] < sma_20:
                        # Wait for price to come back to 20 SMA and form a bearish pin bar with big wick
                        while True:
                            # Get the latest candle
                            last_candle = get_candle_data(SYMBOL, TRADE_DURATION, 1)[0]

                            # Check if price is below 20 SMA
                            if last_candle['close'] < sma_20:
                                # Wait for the next candle to form
                                time.sleep(TRADE_DURATION)
                                last_candle = get_candle_data(SYMBOL, TRADE_DURATION, 1)[0]

                                # Check if it's a bearish pin bar with big wick
                                if last_candle['low'] - last_candle['open'] >= 3 * atr:
                                    if last_candle['close'] > last_candle['open']:
                                        # Wait for the next candle to form
                                        time.sleep(TRADE_DURATION)
                                        last_candle = get_candle_data(SYMBOL, TRADE_DURATION, 1)[0]

                                        # Check if it's a bullish engulfing pattern
                                        prev_candle = candles[-2]
                                        if last_candle['close'] > prev_candle['open'] and last_candle['open'] < prev_candle['close']:
                                            # Execute a buy trade with stop loss and take profit
                                            buy()
                                            stop_loss = last_candle['low'] - STOP_LOSS_DISTANCE
                                            take_profit = last_candle['open'] + TAKE_PROFIT_DISTANCE
                                            api.set_stop_loss(stop_loss)
                                            api.set_take_profit(take_profit)
                                            trades_today += 1
                                            break

                            # Wait for the next candle to form
                            time.sleep(TRADE_DURATION)
                            candles = get_candle_data(SYMBOL, TRADE_DURATION, 1000)
                            sma_200 = calculate_sma(candles, 200)
                            sma_20 = calculate_sma(candles, 20)
                            atr = calculate_atr(candles, 14)
        else:
            # Price is moving down, look for sell opportunities
            # TODO: Add code to look for sell opportunities
            pass

        # Check if we've reached the max number of trades for the day
        if trades_today >= MAX_TRADES_PER_DAY:
            break

    except KeyboardInterrupt:
        break
    except:
        # Handle errors gracefully
        pass

    # Wait for the next candle to form
    time.sleep(TRADE_DURATION)



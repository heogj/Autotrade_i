import time
import pyupbit
import datetime

access = ""
secret = ""

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_target_volatility(ticker):
    """자금관리 : 타겟변동성으로 조정"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    volatility = (df.iloc[0]['high'] - df.iloc[0]['low'])/df.iloc[0]['close']
    target_volatility = round(0.03 / volatility, 2)
    if target_volatility > 1 :
        target_volatility = 1
    return target_volatility

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma5(ticker):
    """5일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=5)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price_BTC = get_target_price("KRW-BTC", 0.5)
            target_price_ETH = get_target_price("KRW-ETH", 0.5)
            target_price_XRP = get_target_price("KRW-XRP", 0.5)
            ma5_BTC = get_ma5("KRW-BTC")
            ma5_ETH = get_ma5("KRW-ETH")
            ma5_XRP = get_ma5("KRW-XRP")
            current_price_BTC = get_current_price("KRW-BTC")
            current_price_ETH = get_current_price("KRW-ETH")
            current_price_XRP = get_current_price("KRW-XRP")
            target_volatility_BTC = get_target_volatility("KRW-BTC")
            target_volatility_ETH = get_target_volatility("KRW-ETH")
            target_volatility_XRP = get_target_volatility("KRW-XRP")
            if target_price_BTC < current_price_BTC and ma5_BTC < current_price_BTC:
                krw = get_balance("KRW")
                btc = get_balance("BTC")
                eth = get_balance("ETH")
                xrp = get_balance("XRP")
                if krw > 5000 and btc < 0.01:
                    print("buying BTC")
                    upbit.buy_market_order("KRW-BTC", (krw+eth*target_price_ETH+xrp*target_price_XRP)*0.25*target_volatility_BTC)
            if target_price_ETH < current_price_ETH and ma5_ETH < current_price_ETH:
                print("buying ETH")
                krw = get_balance("KRW")
                btc = get_balance("BTC")
                eth = get_balance("ETH")
                xrp = get_balance("XRP")
                if krw > 5000 and eth < 0.1:
                    upbit.buy_market_order("KRW-ETH", (krw+btc*target_price_BTC+xrp*target_price_XRP)*0.25*target_volatility_ETH)
            if target_price_XRP < current_price_XRP and ma5_XRP < current_price_XRP:
                print("buying XRP")
                krw = get_balance("KRW")
                btc = get_balance("BTC")
                eth = get_balance("ETH")
                xrp = get_balance("XRP")
                if krw > 5000 and xrp < 1000:
                    upbit.buy_market_order("KRW-XRP", (krw+btc*target_price_BTC+eth*target_price_ETH)*0.25*target_volatility_XRP)
        else:
            btc = get_balance("BTC")
            eth = get_balance("ETH")
            xrp = get_balance("XRP")
            if btc > 0.00016:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
            if eth > 0.0025:
                upbit.sell_market_order("KRW-ETH", eth*0.9995)
            if xrp > 11:
                upbit.sell_market_order("KRW-XRP", xrp*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
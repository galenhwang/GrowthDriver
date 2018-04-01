from flask import Flask, jsonify, request
import pandas
import random
import requests
import numpy
import json

app = Flask(__name__)

stocks_example = {
    "stocks": ["AAPL", "GOOG", "TSLA"],
    "risk_score": 80
}

jsonified = jsonify(stocksExample)

trading_days = 252

@app.route('/optimize', methods=['POST'])
def optimize():
    """def statistics(weight):
        weights = numpy.array(weights)"""

    assert(request.is_json)
    buffer = request.get_json()

    stocks = buffer['stocks']
    risk_score = buffer['risk_score']

    risk_free_rate = 0.0173
    num_stocks = len(stocks)
    data_frame = {}
    index = []
    index_date = False

    for stock in stocks:
        year = requests.get("https://api.iextrading.com/1.0/stock/"+stock+"/chart/1y").json()
        one_year_prices = []
        for day in year:
            one_year_prices.append(year["close"])
            if index_date is False:
                index.append(year["date"])
                index_date = True
        data_frame[stock] = one_year_prices

    df = pandas.DataFrame(data=data_frame, index=self.index)

    daily_log_returns = numpy.log(df/df.shift(1))

    returns = []
    risks = []
    sharpe_ratios = []
    weights = []

    for x in xrange(50000):
        weights_per_portfolio = []
        for y in range(0, numStocks):
            weights.append(random.random())
        weights_per_portfolio /= numpy.sum(weights_per_portfolio)
        # why am i putting trading_days here? lol idk (yet)
        returns_per_portfolio = numpy.sum(daily_log_returns.mean() * trading_days * weights_per_portfolio)
        variances_per_portfolio = numpy.sqrt(numpy.dot(weights_per_portfolio, numpy.dot(weights_per_portfolio, daily_log_returns.cov() * trading_days)))
        sharpe_ratios_per_portfolio = (returns_per_portfolio - risk_free_rate) / variances_per_portfolio

        returns.append(returns_per_portfolio)
        risks.append(variances_per_portfolio)
        sharpe_ratios.append(sharpe_ratios_per_portfolio)
        weights.append(weights_per_portfolio)

    returns = numpy.array(returns)
    risks = numpy.array(risks)


    data = {
    }

    resp = jsonify(data)

    return resp


app.run(host='0.0.0.0', port= 8080)

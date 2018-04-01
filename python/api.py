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

trading_days = 252

@app.route('/', methods=['GET'])
def index():
    return "testing"

@app.route('/optimize', methods=['POST'])
def optimize():

    assert(request.is_json)
    buffer = request.get_json()

    jsonified = jsonify(stocks_example)

    stocks = buffer["stocks"]
    risk_score = int(buffer["risk_score"])

    risk_free_rate = 0.0173
    num_stocks = len(stocks)
    data_frame = {}
    index = []
    index_date = False
    year_prices_query = ""

    for stock in stocks:
        year_prices_query += stock + ","

    iex_trading_request = requests.get("https://api.iextrading.com/1.0/stock/market/batch?symbols=" + year_prices_query + "&types=chart&range=1y").json()

    for stock in stocks:
        one_year_prices = []
        year = iex_trading_request[stock]["chart"]
        for day in year:
            one_year_prices.append(day["close"])
            if index_date is False:
                index.append(day["date"])
        index_date = True
        data_frame[stock] = one_year_prices

    for stock in stocks:
        stock_len = len(data_frame[stock])
        diff_len = stock_len - len(index)
        if diff_len > 0:
            data_frame[stock] = data_frame[stock][-stock_len+diff_len:]

    del iex_trading_request

    df = pandas.DataFrame(data=data_frame, index=index)

    daily_log_returns = numpy.log(df/df.shift(1))

    returns = []
    risks = []
    sharpe_ratios = []
    weights = []

    for x in xrange(10000):
        weights_per_portfolio = []
        for y in range(0, num_stocks):
            weights_per_portfolio.append(random.random())
        weights_per_portfolio /= numpy.sum(weights_per_portfolio)
        returns_per_portfolio = numpy.sum(daily_log_returns.mean() * trading_days * weights_per_portfolio)
        variances_per_portfolio = numpy.sqrt(numpy.dot(weights_per_portfolio, numpy.dot(weights_per_portfolio, daily_log_returns.cov() * trading_days)))
        sharpe_ratios_per_portfolio = (returns_per_portfolio - risk_free_rate) / variances_per_portfolio

        returns.append(returns_per_portfolio)
        risks.append(variances_per_portfolio)
        sharpe_ratios.append(sharpe_ratios_per_portfolio)
        weights.append(weights_per_portfolio)

    returns = numpy.array(returns)
    risks = numpy.array(risks)

    blackRock_query = ""
    data = {
        "weighting": {},
        "return": 0,
        "risk": 0,
        "sharpe_ratio": 0
    }

    if risk_score > 70:
        highest_return_weighting = weights[returns.tolist().index(max(returns))]
        for i in range(0, num_stocks):
            blackRock_query += stock + "~" + str(highest_return_weighting[i]) + "|"
        portfolio_analysis = requests.get("https://www.blackrock.com/tools/hackathon/portfolio-analysis?calculateExposures=true&calculatePerformance=true&positions=" + blackRock_query).json()
        portfolio_analysis = portfolio_analysis["resultMap"]["PORTFOLIOS"][0]["portfolios"][0]["returns"]["latestPerf"]
        for i in range(0, num_stocks):
            weights = highest_return_weighting.tolist()
            data["weighting"][stocks[i]] = weights[i]
    elif risk_score >= 30:
        return_over_risk_weighting = weights[sharpe_ratios.index(max(sharpe_ratios))]
        for i in range(0, num_stocks):
            blackRock_query += stock + "~" + str(return_over_risk_weighting[i]) + "|"
        portfolio_analysis = requests.get("https://www.blackrock.com/tools/hackathon/portfolio-analysis?calculateExposures=true&calculatePerformance=true&positions=" + blackRock_query).json()
        portfolio_analysis = portfolio_analysis["resultMap"]["PORTFOLIOS"][0]["portfolios"][0]["returns"]["latestPerf"]
        for i in range(0, num_stocks):
            weights = return_over_risk_weighting.tolist()
            data["weighting"][stocks[i]] = weights[i]
    elif risk_score >= 0:
        lowest_risk_weighting = weights[risks.tolist().index(min(risks))]
        for i in range(0, num_stocks):
            blackRock_query += stock + "~" + str(lowest_risk_weighting[i]) + "|"
        portfolio_analysis = requests.get("https://www.blackrock.com/tools/hackathon/portfolio-analysis?calculateExposures=true&calculatePerformance=true&positions=" + blackRock_query).json()
        portfolio_analysis = portfolio_analysis["resultMap"]["PORTFOLIOS"][0]["portfolios"][0]["returns"]["latestPerf"]
        for i in range(0, num_stocks):
            weights = lowest_risk_weighting.tolist()
            data["weighting"][stocks[i]] = weights[i]

    data["return"] = portfolio_analysis["oneYear"]
    data["risk"] = portfolio_analysis["oneYearRisk"]
    data["sharpe_ratio"] = portfolio_analysis["oneYearSharpeRatio"]

    resp = jsonify(data)

    return resp

if __name__ == '__main__':
    app.run()

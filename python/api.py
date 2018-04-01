from flask import Flask, jsonify, request
import pandas
import random
import requests
import numpy
import json
import scipy.optimize as sco

app = Flask(__name__)

stocks_example = {
    "stocks": ["AAPL", "GOOG", "TSLA"],
    "risk_score": 80
}

trading_days = 252

@app.route('/optimize', methods=['POST'])
def optimize():
    """def statistics(weight):
        weights = numpy.array(weights)"""

    assert(request.is_json)
    buffer = request.get_json()

    jsonified = jsonify(stocks_example)

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

    blackRock_query = []
    data = {
        "weighting": [],
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
        data["weighting"] = highest_return_weighting.tolist()
    elif risk_score >= 30:
        return_over_risk_weighting = weights[sharpe_ratios.tolist().index(max(sharpe_ratios))]
        for i in range(0, num_stocks):
            blackRock_query += stock + "~" + str(return_over_risk_weighting[i]) + "|"
        portfolio_analysis = requests.get("https://www.blackrock.com/tools/hackathon/portfolio-analysis?calculateExposures=true&calculatePerformance=true&positions=" + blackRock_query).json()
        portfolio_analysis = portfolio_analysis["resultMap"]["PORTFOLIOS"][0]["portfolios"][0]["returns"]["latestPerf"]
        data["weighting"] = return_over_risk_weighting.tolist()
    elif risk_score >= 0:
        lowest_risk_weighting = weights[risks.tolist().index(min(risks))]
        for i in range(0, num_stocks):
            blackRock_query += stock + "~" + str(lowest_risk_weighting[i]) + "|"
        portfolio_analysis = requests.get("https://www.blackrock.com/tools/hackathon/portfolio-analysis?calculateExposures=true&calculatePerformance=true&positions=" + blackRock_query).json()
        portfolio_analysis = portfolio_analysis["resultMap"]["PORTFOLIOS"][0]["portfolios"][0]["returns"]["latestPerf"]
        data["weighting"] = lowest_risk_weighting.tolist()

    data["return"] = portfolio_analysis["oneYear"]
    data["risk"] = portfolio_analysis["oneYearRisk"]
    data["sharpe_ratio"] = portfolio_analysis["oneYearSharpeRatio"]

    """
    highest_return = {}
    lowest_risk = {}
    highest_sharpe = {}

    lowest_risk["risk"]=min(port_variance)
    lowestRisk["sharpe"]=port_sharpe[port_variance.tolist().index(min(port_variance))]
    lowestRisk["return"]=port_returns[port_variance.tolist().index(min(port_variance))]

    highestSharpe["risk"]=port_variance[port_sharpe.index(max(port_sharpe))]
    highestSharpe["sharpe"]=max(port_sharpe)
    highestSharpe["return"]=port_returns[port_sharpe.index(max(port_sharpe))]

    highestReturn["risk"]=port_variance[port_returns.tolist().index(max(port_returns))]
    highestReturn["sharpe"]=port_sharpe[port_returns.tolist().index(max(port_returns))]
    highestReturn["return"]=max(port_returns)

    print(portfolio_analysis)
    """



    resp = jsonify(data)

    return resp


app.run(host='0.0.0.0', port= 8080)

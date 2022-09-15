import yahoo_fin.stock_info as yf
import pandas as pd
import time


balance_sheet = []
income_statement = []
cfs = []
years = []
profitability_score = 0
tickers = yf.tickers_sp500()
ROA = 0
CF = 0
deltaROA = 0
Acc = 0

summary = pd.DataFrame(columns=['Ticker',
                                'Profitability', 'ROA', 'Change in ROA',
                                'Operating Cash Flow', 'Accruals'])

def get_data(stock):
    global balance_sheet
    global income_statement
    global cfs
    global years
    balance_sheet = yf.get_balance_sheet(stock)
    income_statement = yf.get_income_statement(stock)
    cfs = yf.get_cash_flow(stock)
    years = balance_sheet.columns


def profitability():
    global profitability_score
    global ROA
    global CF
    global deltaROA
    global Acc
    net_income = income_statement[years[0]]['netIncome']
    ROA = net_income
    net_income_prior = income_statement[years[1]]['netIncome']
    # First 2 scores below are calculated using net income found in income statement (Return on Assets)
    # note: This is more like 1 and 1.5 so this falls under the same 1 point of Return on Assets
    net_income_score = 1 if net_income > 0 else 0
    net_income_score_comp = 1 if net_income > net_income_prior else 0

    # The second score will be calculated using the Cash Flow Statement's total cash from operating activities
    operating_cf = cfs[years[0]]['totalCashFromOperatingActivities']
    CF = operating_cf
    operating_cf_score = 1 if operating_cf > 0 else 0

    # The third score is the change in the Return on
    # Assets found in the balance sheet
    # The average of the assets is found by adding the total assets of all years and divide by number of years
    assets_average = (balance_sheet[years[0]]['totalAssets'] + balance_sheet[years[1]]['totalAssets']) / 2
    assets_average_prior = (balance_sheet[years[1]]['totalAssets'] + balance_sheet[years[2]]['totalAssets']) / 2
    return_on_assets = net_income / assets_average
    return_on_assets_prior = net_income_prior / assets_average_prior
    deltaROA = return_on_assets - return_on_assets_prior
    print(deltaROA)
    return_on_assets_score = 1 if return_on_assets > return_on_assets_prior else 0

    # fourth score is accruals.
    # Accruals (1 point if Operating Cash Flow/Total Assets is higher than ROA in the current year, 0 otherwise);
    total_assets = balance_sheet[years[0]]['totalAssets']
    accruals = operating_cf / total_assets
    Acc = accruals
    accruals_score = 1 if accruals > 0 else 0

    # Finally, update the profitability score
    profitability_score = net_income_score + operating_cf_score + return_on_assets_score + accruals_score
    print(profitability_score, "/ 4")

for ticker in tickers[32:76]:
    get_data(ticker)
    print(ticker)
    profitability()
    new_row = {'Ticker': ticker,
                'Profitability': profitability_score,
                'ROA': ROA,
                'Change in ROA': deltaROA,
                'Operating Cash Flow': CF,
                'Accruals': Acc}

    summary = summary.append(new_row, ignore_index=True)
    print(ticker + ' added.')
    time.sleep(3)
summary.to_csv('Profitability Analysis.csv')


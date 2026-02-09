from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def fmt_currency(v, currency='USD'):
    currency_symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CAD': 'CA$', 'AUD': 'A$', 'CHF': 'CHF', 'INR': '₹', 'SGD': 'S$', 'HKD': 'HK$'}
    symbol = currency_symbols.get(currency, currency)
    if currency == 'JPY':
        return f"{symbol}{int(round(v))}"
    return f"{symbol}{v:,.2f}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        income = float(request.form.get('income') or 0)
    except ValueError:
        income = 0.0
    try:
        fixed = float(request.form.get('fixed') or 0)
    except ValueError:
        fixed = 0.0
    try:
        daily = float(request.form.get('daily') or 0)
    except ValueError:
        daily = 0.0

    protocol = request.form.get('protocol') or 'balanced'
    vol = request.form.get('vol') or 'medium'
    currency = request.form.get('currency') or 'USD'

    monthlyDaily = daily * 30.0
    disposable = income - fixed - monthlyDaily

    base_map = {'conservative': 0.35, 'balanced': 0.5, 'aggressive': 0.7}
    baseFraction = base_map.get(protocol, 0.5)

    vol_map = {'low': 0.8, 'medium': 1.0, 'high': 1.1}
    volAdj = vol_map.get(vol, 1.0)

    recommended = max(0.0, disposable * baseFraction * volAdj)

    presets = {
        'conservative': {'low':[0.20,0.60,0.20],'medium':[0.30,0.50,0.20],'high':[0.40,0.40,0.20]},
        'balanced': {'low':[0.50,0.30,0.20],'medium':[0.60,0.25,0.15],'high':[0.70,0.20,0.10]},
        'aggressive': {'low':[0.70,0.20,0.10],'medium':[0.80,0.15,0.05],'high':[0.90,0.08,0.02]}
    }

    alloc = presets.get(protocol, presets['balanced']).get(vol, presets['balanced']['medium'])
    labels = ['Equities','Bonds / Fixed Income','Cash & Short-term']
    allocations = []
    for i, frac in enumerate(alloc):
        amt = round(recommended * frac, 2)
        allocations.append({'label': labels[i], 'pct': int(round(frac*100)), 'amt': fmt_currency(amt, currency)})

    return render_template('result.html',
                           income_fmt=fmt_currency(income, currency),
                           fixed_fmt=fmt_currency(fixed, currency),
                           monthlyDaily_fmt=fmt_currency(monthlyDaily, currency),
                           disposable_fmt=fmt_currency(disposable, currency),
                           recommended_fmt=(fmt_currency(recommended, currency) if recommended>0 else 'No positive disposable funds available'),
                           allocations=allocations,
                           disposable_warning=(disposable <= 0),
                           currency=currency)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=True)

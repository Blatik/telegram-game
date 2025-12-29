from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import io
import base64
import numpy as np
from typing import Optional, List
import tempfile
import os

# Register fonts for Cyrillic support
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"

if os.path.exists(FONT_PATH):
    try:
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Arial']
    except Exception as e:
        print(f"Error registering font: {e}")
else:
    plt.rcParams['font.family'] = 'DejaVu Sans'

app = FastAPI(title="Financial Calculator API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# --- Pydantic models ---

class HourlyIncomeRequest(BaseModel):
    monthly_income: float
    taxes: float
    work_hours: float
    commute_time: float
    work_expenses: float
    currency: str = "EUR"

class TimeValueRequest(BaseModel):
    annual_income: float
    annual_hours: float
    currency: str = "EUR"

class CreditRequest(BaseModel):
    amount: float
    rate: float
    term: float
    inflation: float = 0
    alternative_return: float = 0
    currency: str = "EUR"

class BuyRentRequest(BaseModel):
    property_price: float
    down_payment: float
    mortgage_rate: float
    mortgage_term: float
    monthly_rent: float
    rent_growth: float
    property_growth: float
    horizon: float
    currency: str = "EUR"

class InvestmentRequest(BaseModel):
    initial_amount: float
    monthly_contribution: float
    annual_return: float
    period: float
    currency: str = "EUR"

class RetirementRequest(BaseModel):
    current_age: float
    retirement_age: float
    desired_income: float
    current_savings: float
    monthly_savings: float = 0
    expected_return: float
    inflation: float = 2
    currency: str = "EUR"

class DebtPayoffRequest(BaseModel):
    balance: float
    interest_rate: float
    monthly_payment: float
    extra_payment: float = 0
    currency: str = "EUR"

class EmergencyFundRequest(BaseModel):
    monthly_expenses: float
    months_coverage: float
    current_savings: float
    monthly_contribution: float
    investment_return: float = 0
    currency: str = "EUR"

class TaxRequest(BaseModel):
    income: float
    country: str
    status: str
    currency: str = "EUR"

# --- Utility Functions ---

CURRENCY_SYMBOLS = {"EUR": "€", "USD": "$", "UAH": "₴", "BTC": "₿"}

def create_chart_base64(fig):
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close(fig)
    return f"data:image/png;base64,{img_str}"

# --- Endpoints ---

@app.post("/calculate/hourly-income")
async def calculate_hourly_income(data: HourlyIncomeRequest):
    net_monthly = data.monthly_income * (1 - data.taxes/100) - data.work_expenses
    total_hours = data.work_hours + data.commute_time
    real_hourly = net_monthly / total_hours
    nom_hourly = data.monthly_income / data.work_hours
    efficiency = (real_hourly / nom_hourly) * 100
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(['Номінальна', 'Реальна'], [nom_hourly, real_hourly], color=['#95a5a6', '#2ecc71'])
    ax.set_title('Порівняння погодинних ставок', fontweight='bold')
    ax.set_ylabel('Ставка')
    
    return {
        "real_hourly_income": round(real_hourly, 2),
        "nominal_hourly_income": round(nom_hourly, 2),
        "net_income": round(net_monthly, 2),
        "efficiency": round(efficiency, 1),
        "currency_symbol": CURRENCY_SYMBOLS.get(data.currency, "€"),
        "chart": create_chart_base64(fig)
    }


@app.post("/calculate/time-value")
async def calculate_time_value(data: TimeValueRequest):
    hourly = data.annual_income / data.annual_hours
    fig, ax = plt.subplots(figsize=(8, 6))
    periods = ['Година', 'День (8г)', 'Тиждень (40г)', 'Місяць (160г)']
    values = [hourly, hourly*8, hourly*40, hourly*160]
    ax.bar(periods, values, color='#3498db')
    ax.set_title('Грошова вартість вашого часу', fontweight='bold')
    
    return {
        "time_value": round(hourly, 2),
        "currency_symbol": CURRENCY_SYMBOLS.get(data.currency, "€"),
        "chart": create_chart_base64(fig)
    }


@app.post("/calculate/investment")
async def calculate_investment(data: InvestmentRequest):
    r = data.annual_return / 100 / 12
    n = int(data.period * 12)
    fv = data.initial_amount * (1+r)**n + data.monthly_contribution * (((1+r)**n - 1) / r)
    total_inv = data.initial_amount + data.monthly_contribution * n
    gain = fv - total_inv
    
    years = np.arange(0, data.period + 1)
    values = [data.initial_amount * (1+r)**(y*12) + data.monthly_contribution * (((1+r)**(y*12) - 1) / r) if y>0 else data.initial_amount for y in years]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(years, values, marker='o', color='#27ae60', linewidth=2)
    ax.fill_between(years, values, alpha=0.2, color='#2ecc71')
    ax.set_title('Прогноз зростання капіталу', fontweight='bold')
    ax.set_xlabel('Роки')
    
    return {
        "future_value": round(fv, 2),
        "total_contributions": round(total_inv, 2),
        "total_gain": round(gain, 2),
        "roi": round((gain/total_inv)*100, 1),
        "currency_symbol": CURRENCY_SYMBOLS.get(data.currency, "€"),
        "chart": create_chart_base64(fig)
    }


@app.post("/calculate/credit")
async def calculate_credit(data: CreditRequest):
    r = data.rate / 100 / 12
    n = data.term * 12
    pmt = data.amount * (r * (1+r)**n) / ((1+r)**n - 1)
    total = pmt * n
    overpayment = total - data.amount
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie([data.amount, overpayment], labels=['Тіло', 'Відсотки'], autopct='%1.1f%%', colors=['#3498db', '#e74c3c'])
    ax.set_title('Структура кредиту', fontweight='bold')
    
    return {
        "monthly_payment": round(pmt, 2),
        "total_payment": round(total, 2),
        "overpayment": round(overpayment, 2),
        "currency_symbol": CURRENCY_SYMBOLS.get(data.currency, "€"),
        "chart": create_chart_base64(fig)
    }


@app.post("/calculate/buy-rent")
async def calculate_buy_rent(data: BuyRentRequest):
    # Simplified comparison
    loan = data.property_price - data.down_payment
    r = data.mortgage_rate / 100 / 12
    n = data.mortgage_term * 12
    mp = loan * (r * (1+r)**n) / ((1+r)**n - 1) if loan > 0 else 0
    
    years = np.arange(1, data.horizon + 1)
    buy_costs = [data.down_payment + (mp*12 + data.property_price*0.01)*y for y in years]
    
    rent_costs = []
    curr_rent = data.monthly_rent
    cum_rent = 0
    for y in years:
        cum_rent += curr_rent * 12
        rent_costs.append(cum_rent)
        curr_rent *= (1 + data.rent_growth/100)
    
    final_prop_val = data.property_price * (1 + data.property_growth/100) ** data.horizon
    net_buy = final_prop_val - buy_costs[-1]
    net_rent = data.down_payment * (1.07 ** data.horizon) - rent_costs[-1] # 7% growth on downpayment if rent
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(years, buy_costs, label='Купівля (витрати)', color='#e74c3c')
    ax.plot(years, rent_costs, label='Оренда (витрати)', color='#3498db')
    ax.legend()
    ax.set_title('Порівняння витрат', fontweight='bold')
    
    return {
        "net_buy_position": round(net_buy, 2),
        "net_rent_position": round(net_rent, 2),
        "recommendation": "buy" if net_buy > net_rent else "rent",
        "currency_symbol": CURRENCY_SYMBOLS.get(data.currency, "€"),
        "chart": create_chart_base64(fig)
    }


@app.post("/calculate/retirement")
async def calculate_retirement(data: RetirementRequest):
    years_to_save = data.retirement_age - data.current_age
    r = data.expected_return / 100 / 12
    n = int(years_to_save * 12)
    
    # Future Value of Existing Savings
    fv_existing = data.current_savings * (1+r)**n
    
    # Future Value of Monthly Savings
    fv_monthly = data.monthly_savings * (((1+r)**n - 1) / r) if r > 0 else data.monthly_savings * n
    total_fv = fv_existing + fv_monthly
    
    # Required capital for desired income (assuming 4% withdrawal rule, adjusted for inflation)
    # This is a simplification
    required_capital = (data.desired_income * 12) / 0.04
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(['Матимете', 'Необхідно'], [total_fv, required_capital], color=['#2ecc71', '#e67e22'])
    ax.set_title('Пенсійне забезпечення', fontweight='bold')
    
    return {
        "future_value": round(total_fv, 2),
        "required_capital": round(required_capital, 2),
        "gap": round(max(0, required_capital - total_fv), 2),
        "currency_symbol": CURRENCY_SYMBOLS.get(data.currency, "€"),
        "chart": create_chart_base64(fig)
    }


@app.post("/calculate/debt-payoff")
async def calculate_debt_payoff(data: DebtPayoffRequest):
    r = data.interest_rate / 100 / 12
    p = data.monthly_payment + data.extra_payment
    
    if p <= data.balance * r:
        raise HTTPException(status_code=400, detail="Платіж занадто малий для покриття відсотків")
        
    months = np.log(p / (p - data.balance * r)) / np.log(1 + r)
    total_paid = p * months
    total_interest = total_paid - data.balance
    
    # Timeline
    m_list = np.arange(0, int(months) + 2)
    balances = [data.balance * (1+r)**m - p * (((1+r)**m - 1) / r) for m in m_list]
    balances = [max(0, b) for b in balances]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(m_list, balances, color='#e74c3c', linewidth=2)
    ax.set_title('Процес погашення боргу', fontweight='bold')
    ax.set_xlabel('Місяці')
    
    return {
        "months": int(np.ceil(months)),
        "total_paid": round(total_paid, 2),
        "total_interest": round(total_interest, 2),
        "currency_symbol": CURRENCY_SYMBOLS.get(data.currency, "€"),
        "chart": create_chart_base64(fig)
    }


@app.post("/calculate/emergency-fund")
async def calculate_emergency_fund(data: EmergencyFundRequest):
    target = data.monthly_expenses * data.months_coverage
    remaining = max(0, target - data.current_savings)
    
    if data.monthly_contribution > 0:
        months_to_target = remaining / data.monthly_contribution
    else:
        months_to_target = float('inf')
        
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(['Наявне', 'Ціль'], [data.current_savings, target], color=['#3498db', '#f1c40f'])
    ax.set_title('Статус фінансової подушки', fontweight='bold')
    
    return {
        "target_amount": round(target, 2),
        "remaining_amount": round(remaining, 2),
        "months_to_target": round(months_to_target, 1) if months_to_target != float('inf') else -1,
        "currency_symbol": CURRENCY_SYMBOLS.get(data.currency, "€"),
        "chart": create_chart_base64(fig)
    }


@app.post("/calculate/tax")
async def calculate_tax(data: TaxRequest):
    # Very simplified tax logic for proof of concept
    tax_rates = {
        "ukraine": 0.195, # 18% + 1.5%
        "poland": 0.12,   # simplified
        "germany": 0.30,  # simplified
        "netherlands": 0.37 # simplified
    }
    rate = tax_rates.get(data.country.lower(), 0.20)
    tax_amount = data.income * rate
    net_income = data.income - tax_amount
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie([net_income, tax_amount], labels=['Чистий дохід', 'Податки'], autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'])
    ax.set_title(f'Податковий розрахунок ({data.country})', fontweight='bold')
    
    return {
        "tax_amount": round(tax_amount, 2),
        "net_income": round(net_income, 2),
        "effective_rate": round(rate * 100, 1),
        "currency_symbol": CURRENCY_SYMBOLS.get(data.currency, "€"),
        "chart": create_chart_base64(fig)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

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
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register fonts for Cyrillic support
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_NAME = 'Helvetica' # Default fallback

if os.path.exists(FONT_PATH):
    try:
        pdfmetrics.registerFont(TTFont('Arial', FONT_PATH))
        FONT_NAME = 'Arial'
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

def create_image_report(fig):
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='jpeg', dpi=300, bbox_inches='tight', facecolor='white')
    img_buffer.seek(0)
    data = img_buffer.getvalue()
    plt.close(fig)
    return data

def create_pdf_report(title, data_dict, fig, summary_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Use the registered font or fallback
    styles['Normal'].fontName = FONT_NAME
    styles['Heading1'].fontName = FONT_NAME
    
    story = []
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, alignment=1, spaceAfter=20, fontName=FONT_NAME)
    story.append(Paragraph(title, title_style))
    
    # Render Chart to Image
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    img_buf.seek(0)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        tmp.write(img_buf.getvalue())
        tmp_path = tmp.name
    
    story.append(Image(tmp_path, width=6.5*inch, height=4.5*inch))
    story.append(Spacer(1, 20))
    
    # Summary
    summary_style = ParagraphStyle('Summary', parent=styles['Normal'], fontSize=12, leading=16, fontName=FONT_NAME)
    story.append(Paragraph("<b>Результати та аналіз:</b>", summary_style))
    story.append(Spacer(1, 10))
    
    for line in summary_text.split('\n'):
        if line.strip():
            story.append(Paragraph(line, summary_style))
    
    doc.build(story)
    os.unlink(tmp_path)
    plt.close(fig)
    return buffer.getvalue()

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

@app.post("/calculate/hourly-income/report")
async def calculate_hourly_income_report(data: HourlyIncomeRequest, format: str = "pdf"):
    res = await calculate_hourly_income(data)
    symbol = res["currency_symbol"]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Звіт про реальний погодинний дохід', fontsize=16, fontweight='bold')
    
    # Charts...
    ax1.pie([res["net_income"], data.monthly_income*data.taxes/100, data.work_expenses], 
            labels=['Чистий', 'Податки', 'Витрати'], autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c', '#f1c40f'])
    ax1.set_title('Структура доходу')
    
    ax2.bar(['Робота', 'Дорога'], [data.work_hours, data.commute_time], color=['#3498db', '#9b59b6'])
    ax2.set_title('Розподіл часу')
    
    ax3.bar(['Номінальна', 'Реальна'], [res["nominal_hourly_income"], res["real_hourly_income"]], color=['#bdc3c7', '#27ae60'])
    ax3.set_title('Погодинна ставка')
    
    ax4.axis('off')
    summary = f"Чистий дохід: {symbol}{res['net_income']:,.2f}\n" \
              f"Реальна ставка: {symbol}{res['real_hourly_income']:,.2f}/год\n" \
              f"Ефективність: {res['efficiency']}%"
    ax4.text(0.1, 0.5, summary, fontsize=12)

    if format.lower() in ["jpg", "jpeg"]:
        return Response(content=create_image_report(fig), 
                      media_type="image/jpeg",
                      headers={
                          "Content-Disposition": "attachment; filename=hourly_report.jpg",
                          "Access-Control-Expose-Headers": "Content-Disposition"
                      })
    return Response(content=create_pdf_report("Аналіз погодинного доходу", data.dict(), fig, summary), 
                  media_type="application/pdf", 
                  headers={
                      "Content-Disposition": "attachment; filename=hourly_report.pdf",
                      "Access-Control-Expose-Headers": "Content-Disposition"
                  })

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

@app.post("/calculate/time-value/report")
async def calculate_time_value_report(data: TimeValueRequest, format: str = "pdf"):
    res = await calculate_time_value(data)
    symbol = res["currency_symbol"]
    h = res["time_value"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    periods = ['Година', 'День', 'Тиждень', 'Місяць']
    values = [h, h*8, h*40, h*160]
    ax.bar(periods, values, color='#3498db')
    ax.set_title('Вартість часу в різних масштабах')
    
    summary = f"Вартість години: {symbol}{h:,.2f}\n" \
              f"Вартість дня: {symbol}{h*8:,.2f}\n" \
              f"Вартість тижня: {symbol}{h*40:,.2f}\n" \
              f"Вартість місяця: {symbol}{h*160:,.2f}"

    if format.lower() in ["jpg", "jpeg"]:
        return Response(content=create_image_report(fig), 
                      media_type="image/jpeg",
                      headers={
                          "Content-Disposition": "attachment; filename=time_report.jpg",
                          "Access-Control-Expose-Headers": "Content-Disposition"
                      })
    return Response(content=create_pdf_report("Аналіз вартості часу", data.dict(), fig, summary), 
                  media_type="application/pdf", 
                  headers={
                      "Content-Disposition": "attachment; filename=time_report.pdf",
                      "Access-Control-Expose-Headers": "Content-Disposition"
                  })

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

@app.post("/calculate/investment/report")
async def calculate_investment_report(data: InvestmentRequest, format: str = "pdf"):
    res = await calculate_investment(data)
    symbol = res["currency_symbol"]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    # Reuse chart logic
    r = data.annual_return / 100 / 12
    years = np.arange(0, data.period + 1)
    vals = [data.initial_amount * (1+r)**(y*12) + data.monthly_contribution * (((1+r)**(y*12) - 1) / r) if y>0 else data.initial_amount for y in years]
    ax1.plot(years, vals, marker='o', color='#2ecc71')
    ax1.set_title('Графік зростання')
    
    ax2.pie([data.initial_amount + data.monthly_contribution*data.period*12, res["total_gain"]], 
            labels=['Внески', 'Прибуток'], autopct='%1.1f%%', colors=['#3498db', '#2ecc71'])
    ax2.set_title('Структура фінального капіталу')
    
    summary = f"Фінальна сума: {symbol}{res['future_value']:,.2f}\n" \
              f"Всього інвестовано: {symbol}{res['total_contributions']:,.2f}\n" \
              f"Чистий прибуток: {symbol}{res['total_gain']:,.2f}\n" \
              f"Загальний ROI: {res['roi']}%"

    if format.lower() in ["jpg", "jpeg"]:
        return Response(content=create_image_report(fig), 
                      media_type="image/jpeg",
                      headers={
                          "Content-Disposition": "attachment; filename=investment_report.jpg",
                          "Access-Control-Expose-Headers": "Content-Disposition"
                      })
    return Response(content=create_pdf_report("Інвестиційний звіт", data.dict(), fig, summary), 
                  media_type="application/pdf", 
                  headers={
                      "Content-Disposition": "attachment; filename=investment_report.pdf",
                      "Access-Control-Expose-Headers": "Content-Disposition"
                  })

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

@app.post("/calculate/credit/report")
async def calculate_credit_report(data: CreditRequest, format: str = "pdf"):
    res = await calculate_credit(data)
    symbol = res["currency_symbol"]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    ax1.pie([data.amount, res["overpayment"]], labels=['Тіло', 'Відсотки'], autopct='%1.1f%%')
    ax1.set_title('Розподіл виплат')
    
    # Simple bar for comparison with inflation/alt return
    ax2.bar(['Ставка', 'Інфляція', 'Альтерн.'], [data.rate, data.inflation, data.alternative_return], color=['#e74c3c', '#95a5a6', '#2ecc71'])
    ax2.set_title('Порівняння показників (%)')
    
    summary = f"Кредит: {symbol}{data.amount:,.2f}\n" \
              f"Щомісячний платіж: {symbol}{res['monthly_payment']:,.2f}\n" \
              f"Загальна переплата: {symbol}{res['overpayment']:,.2f}\n" \
              f"Загальна сума: {symbol}{res['total_payment']:,.2f}"

    if format.lower() in ["jpg", "jpeg"]:
        return Response(content=create_image_report(fig), 
                      media_type="image/jpeg",
                      headers={
                          "Content-Disposition": "attachment; filename=credit_report.jpg",
                          "Access-Control-Expose-Headers": "Content-Disposition"
                      })
    return Response(content=create_pdf_report("Кредитний звіт", data.dict(), fig, summary), 
                  media_type="application/pdf", 
                  headers={
                      "Content-Disposition": "attachment; filename=credit_report.pdf",
                      "Access-Control-Expose-Headers": "Content-Disposition"
                  })

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

@app.post("/calculate/buy-rent/report")
async def calculate_buy_rent_report(data: BuyRentRequest, format: str = "pdf"):
    res = await calculate_buy_rent(data)
    symbol = res["currency_symbol"]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    # Redo chart logic for report
    years = np.arange(1, data.horizon + 1)
    # ... Simplified for brevity in report
    ax1.bar(['Купівля', 'Оренда'], [res["net_buy_position"], res["net_rent_position"]], color=['#27ae60', '#3498db'])
    ax1.set_title('Чистий капітал через горизонт')
    
    ax2.axis('off')
    summary = f"Капітал при купівлі: {symbol}{res['net_buy_position']:,.2f}\n" \
              f"Капітал при оренді: {symbol}{res['net_rent_position']:,.2f}\n" \
              f"Рекомендація: {'КУПУВАТИ' if res['recommendation']=='buy' else 'ОРЕНДУВАТИ'}"
    ax2.text(0.1, 0.5, summary, fontsize=12)

    if format.lower() in ["jpg", "jpeg"]:
        return Response(content=create_image_report(fig), 
                      media_type="image/jpeg",
                      headers={
                          "Content-Disposition": "attachment; filename=buy_rent_report.jpg",
                          "Access-Control-Expose-Headers": "Content-Disposition"
                      })
    return Response(content=create_pdf_report("Аналіз: Купівля vs Оренда", data.dict(), fig, summary), 
                  media_type="application/pdf", 
                  headers={
                      "Content-Disposition": "attachment; filename=buy_rent_report.pdf",
                      "Access-Control-Expose-Headers": "Content-Disposition"
                  })

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

@app.post("/calculate/retirement/report")
async def calculate_retirement_report(data: RetirementRequest, format: str = "pdf"):
    res = await calculate_retirement(data)
    symbol = res["currency_symbol"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(['Поточний план', 'Ціль'], [res["future_value"], res["required_capital"]], color=['#27ae60', '#f39c12'])
    ax.set_title('Аналіз пенсійних накопичень')
    
    summary = f"Прогноз накопичень: {symbol}{res['future_value']:,.2f}\n" \
              f"Необхідний капітал: {symbol}{res['required_capital']:,.2f}\n" \
              f"Дефіцит: {symbol}{res['gap']:,.2f}"

    if format.lower() in ["jpg", "jpeg"]:
        return Response(content=create_image_report(fig), 
                      media_type="image/jpeg",
                      headers={
                          "Content-Disposition": "attachment; filename=retirement_report.jpg",
                          "Access-Control-Expose-Headers": "Content-Disposition"
                      })
    return Response(content=create_pdf_report("Пенсійний звіт", data.dict(), fig, summary), 
                  media_type="application/pdf", 
                  headers={
                      "Content-Disposition": "attachment; filename=retirement_report.pdf",
                      "Access-Control-Expose-Headers": "Content-Disposition"
                  })

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

@app.post("/calculate/debt-payoff/report")
async def calculate_debt_payoff_report(data: DebtPayoffRequest, format: str = "pdf"):
    res = await calculate_debt_payoff(data)
    symbol = res["currency_symbol"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie([data.balance, res["total_interest"]], labels=['Борг', 'Відсотки'], autopct='%1.1f%%', colors=['#3498db', '#e74c3c'])
    ax.set_title('Структура виплат боргу')
    
    summary = f"Термін погашення: {res['months']} міс.\n" \
              f"Всього буде сплачено: {symbol}{res['total_paid']:,.2f}\n" \
              f"З них відсотків: {symbol}{res['total_interest']:,.2f}"

    if format.lower() in ["jpg", "jpeg"]:
        return Response(content=create_image_report(fig), 
                      media_type="image/jpeg",
                      headers={
                          "Content-Disposition": "attachment; filename=debt_report.jpg",
                          "Access-Control-Expose-Headers": "Content-Disposition"
                      })
    return Response(content=create_pdf_report("Звіт про погашення боргу", data.dict(), fig, summary), 
                  media_type="application/pdf", 
                  headers={
                      "Content-Disposition": "attachment; filename=debt_report.pdf",
                      "Access-Control-Expose-Headers": "Content-Disposition"
                  })

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

@app.post("/calculate/emergency-fund/report")
async def calculate_emergency_fund_report(data: EmergencyFundRequest, format: str = "pdf"):
    res = await calculate_emergency_fund(data)
    symbol = res["currency_symbol"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie([data.current_savings, res["remaining_amount"]], labels=['Накопичено', 'Залишилось'], autopct='%1.1f%%', colors=['#2ecc71', '#bdc3c7'])
    ax.set_title('Прогрес фінансової подушки')
    
    summary = f"Цільова сума: {symbol}{res['target_amount']:,.2f}\n" \
              f"Залишилось зібрати: {symbol}{res['remaining_amount']:,.2f}\n" \
              f"Час до мети: {res['months_to_target']} міс."

    if format.lower() in ["jpg", "jpeg"]:
        return Response(content=create_image_report(fig), 
                      media_type="image/jpeg",
                      headers={
                          "Content-Disposition": "attachment; filename=emergency_report.jpg",
                          "Access-Control-Expose-Headers": "Content-Disposition"
                      })
    return Response(content=create_pdf_report("Звіт про фінансову подушку", data.dict(), fig, summary), 
                  media_type="application/pdf", 
                  headers={
                      "Content-Disposition": "attachment; filename=emergency_report.pdf",
                      "Access-Control-Expose-Headers": "Content-Disposition"
                  })

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

@app.post("/calculate/tax/report")
async def calculate_tax_report(data: TaxRequest, format: str = "pdf"):
    res = await calculate_tax(data)
    symbol = res["currency_symbol"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie([res["net_income"], res["tax_amount"]], labels=['Чистий дохід', 'Податки'], autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'])
    ax.set_title(f'Деталізація податків: {data.country}')
    
    summary = f"Дохід брутто: {symbol}{data.income:,.2f}\n" \
              f"Сума податків: {symbol}{res['tax_amount']:,.2f}\n" \
              f"Дохід нетто: {symbol}{res['net_income']:,.2f}\n" \
              f"Ефективна ставка: {res['effective_rate']}%"

    if format.lower() in ["jpg", "jpeg"]:
        return Response(content=create_image_report(fig), 
                      media_type="image/jpeg",
                      headers={
                          "Content-Disposition": "attachment; filename=tax_report.jpg",
                          "Access-Control-Expose-Headers": "Content-Disposition"
                      })
    return Response(content=create_pdf_report("Податковий звіт", data.dict(), fig, summary), 
                  media_type="application/pdf", 
                  headers={
                      "Content-Disposition": "attachment; filename=tax_report.pdf",
                      "Access-Control-Expose-Headers": "Content-Disposition"
                  })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

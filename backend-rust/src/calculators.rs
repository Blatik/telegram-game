use crate::models::*;

pub fn get_currency_symbol(currency: &str) -> String {
    match currency {
        "EUR" => "€".to_string(),
        "USD" => "$".to_string(),
        "UAH" => "₴".to_string(),
        "BTC" => "₿".to_string(),
        _ => "€".to_string(),
    }
}

fn create_bar_chart(title: &str, labels: Vec<&str>, values: Vec<f64>, colors: Vec<&str>) -> String {
    let width = 400;
    let height = 300;
    let padding = 40;
    let chart_width = width - padding * 2;
    let chart_height = height - padding * 2;
    
    let max_val = values.iter().cloned().fold(0.0, f64::max);
    let scale = if max_val > 0.0 { chart_height as f64 / max_val } else { 1.0 };
    
    let bar_width = chart_width / labels.len() as i32 - 10;
    
    let mut svg = format!(
        r#"<svg width="{}" height="{}" viewBox="0 0 {} {}" xmlns="http://www.w3.org/2000/svg">"#,
        width, height, width, height
    );
    
    // Background
    svg.push_str(r#"<rect width="100%" height="100%" fill="white" />"#);
    
    // Title
    svg.push_str(&format!(
        r#"<text x="{}" y="25" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="middle">{}</text>"#,
        width / 2, title
    ));
    
    for (i, (&label, &value)) in labels.iter().zip(values.iter()).enumerate() {
        let x = padding + i as i32 * (bar_width + 10) + 5;
        let h = (value * scale) as i32;
        let y = height - padding - h;
        let color = colors.get(i).unwrap_or(&"#3498db");
        
        svg.push_str(&format!(
            r#"<rect x="{}" y="{}" width="{}" height="{}" fill="{}" rx="4" />"#,
            x, y, bar_width, h, color
        ));
        
        svg.push_str(&format!(
            r#"<text x="{}" y="{}" font-family="sans-serif" font-size="10" text-anchor="middle">{}</text>"#,
            x + bar_width / 2, height - padding + 15, label
        ));
        
        svg.push_str(&format!(
            r#"<text x="{}" y="{}" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle">{}</text>"#,
            x + bar_width / 2, y - 5, value.round()
        ));
    }
    
    svg.push_str("</svg>");
    svg
}

pub fn calculate_hourly_income(req: HourlyIncomeRequest) -> HourlyIncomeResponse {
    let net_monthly = req.monthly_income * (1.0 - req.taxes / 100.0) - req.work_expenses;
    let total_hours = req.work_hours + req.commute_time;
    let real_hourly = net_monthly / total_hours;
    let nom_hourly = req.monthly_income / req.work_hours;
    let efficiency = (real_hourly / nom_hourly) * 100.0;

    let chart = create_bar_chart(
        "Порівняння ставок",
        vec!["Номінальна", "Реальна"],
        vec![nom_hourly, real_hourly],
        vec!["#95a5a6", "#2ecc71"]
    );

    HourlyIncomeResponse {
        real_hourly_income: (real_hourly * 100.0).round() / 100.0,
        nominal_hourly_income: (nom_hourly * 100.0).round() / 100.0,
        net_income: (net_monthly * 100.0).round() / 100.0,
        efficiency: (efficiency * 10.0).round() / 10.0,
        currency_symbol: get_currency_symbol(&req.currency),
        chart,
    }
}

pub fn calculate_time_value(req: TimeValueRequest) -> TimeValueResponse {
    let hourly = req.annual_income / req.annual_hours;
    
    let chart = create_bar_chart(
        "Вартість часу",
        vec!["Година", "День", "Тиждень", "Місяць"],
        vec![hourly, hourly * 8.0, hourly * 40.0, hourly * 160.0],
        vec!["#3498db", "#3498db", "#3498db", "#3498db"]
    );

    TimeValueResponse {
        time_value: (hourly * 100.0).round() / 100.0,
        currency_symbol: get_currency_symbol(&req.currency),
        chart,
    }
}

pub fn calculate_investment(req: InvestmentRequest) -> InvestmentResponse {
    let r = req.annual_return / 100.0 / 12.0;
    let n = (req.period * 12.0) as i32;
    
    let fv = if r > 0.0 {
        req.initial_amount * (1.0 + r).powi(n) + req.monthly_contribution * (((1.0 + r).powi(n) - 1.0) / r)
    } else {
        req.initial_amount + req.monthly_contribution * n as f64
    };
    
    let total_inv = req.initial_amount + req.monthly_contribution * n as f64;
    let gain = fv - total_inv;
    let roi = if total_inv > 0.0 { (gain / total_inv) * 100.0 } else { 0.0 };

    // simplified "chart" for investment (just end state comparison)
    let chart = create_bar_chart(
        "Структура капіталу",
        vec!["Внески", "Прибуток"],
        vec![total_inv, gain],
        vec!["#3498db", "#2ecc71"]
    );

    InvestmentResponse {
        future_value: (fv * 100.0).round() / 100.0,
        total_contributions: (total_inv * 100.0).round() / 100.0,
        total_gain: (gain * 100.0).round() / 100.0,
        roi: (roi * 10.0).round() / 10.0,
        currency_symbol: get_currency_symbol(&req.currency),
        chart,
    }
}

pub fn calculate_credit(req: CreditRequest) -> CreditResponse {
    let r = req.rate / 100.0 / 12.0;
    let n = req.term * 12.0;
    
    let pmt = if r > 0.0 && n > 0.0 {
        req.amount * (r * (1.0 + r).powf(n)) / ((1.0 + r).powf(n) - 1.0)
    } else if n > 0.0 {
        req.amount / n
    } else {
        0.0
    };
    
    let total = pmt * n;
    let overpayment = total - req.amount;

    let chart = create_bar_chart(
        "Структура виплат",
        vec!["Тіло", "Переплата"],
        vec![req.amount, overpayment],
        vec!["#3498db", "#e74c3c"]
    );

    CreditResponse {
        monthly_payment: (pmt * 100.0).round() / 100.0,
        total_payment: (total * 100.0).round() / 100.0,
        overpayment: (overpayment * 100.0).round() / 100.0,
        currency_symbol: get_currency_symbol(&req.currency),
        chart,
    }
}

pub fn calculate_retirement(req: RetirementRequest) -> RetirementResponse {
    let years_to_save = req.retirement_age - req.current_age;
    let r = req.expected_return / 100.0 / 12.0;
    let n = (years_to_save * 12.0) as i32;
    
    let fv_existing = req.current_savings * (1.0 + r).powi(n);
    let fv_monthly = if r > 0.0 {
        req.monthly_savings * (((1.0 + r).powi(n) - 1.0) / r)
    } else {
        req.monthly_savings * n as f64
    };
    
    let total_fv = fv_existing + fv_monthly;
    let required_capital = (req.desired_income * 12.0) / 0.04;
    let gap = (required_capital - total_fv).max(0.0);

    let chart = create_bar_chart(
        "Пенсійне забезпечення",
        vec!["Матимете", "Необхідно"],
        vec![total_fv, required_capital],
        vec!["#2ecc71", "#e67e22"]
    );

    RetirementResponse {
        future_value: (total_fv * 100.0).round() / 100.0,
        required_capital: (required_capital * 100.0).round() / 100.0,
        gap: (gap * 100.0).round() / 100.0,
        currency_symbol: get_currency_symbol(&req.currency),
        chart,
    }
}

pub fn calculate_debt_payoff(req: DebtPayoffRequest) -> DebtPayoffResponse {
    let r = req.interest_rate / 100.0 / 12.0;
    let p = req.monthly_payment + req.extra_payment;
    
    if p <= req.balance * r {
        return DebtPayoffResponse {
            months: 999,
            total_paid: 0.0,
            total_interest: 0.0,
            currency_symbol: get_currency_symbol(&req.currency),
            chart: "<svg></svg>".into(),
        };
    }
    
    let months = (p / (p - req.balance * r)).ln() / (1.0 + r).ln();
    let total_paid = p * months;
    let total_interest = total_paid - req.balance;

    let chart = create_bar_chart(
        "Структура боргу",
        vec!["Борг", "Відсотки"],
        vec![req.balance, total_interest],
        vec!["#3498db", "#e74c3c"]
    );

    DebtPayoffResponse {
        months: months.ceil() as u32,
        total_paid: (total_paid * 100.0).round() / 100.0,
        total_interest: (total_interest * 100.0).round() / 100.0,
        currency_symbol: get_currency_symbol(&req.currency),
        chart,
    }
}

pub fn calculate_emergency_fund(req: EmergencyFundRequest) -> EmergencyFundResponse {
    let target = req.monthly_expenses * req.months_coverage;
    let remaining = (target - req.current_savings).max(0.0);
    
    let months_to_target = if req.monthly_contribution > 0.0 {
        remaining / req.monthly_contribution
    } else {
        -1.0
    };

    let chart = create_bar_chart(
        "Статус подушки",
        vec!["Наявне", "Ціль"],
        vec![req.current_savings, target],
        vec!["#3498db", "#f1c40f"]
    );

    EmergencyFundResponse {
        target_amount: (target * 100.0).round() / 100.0,
        remaining_amount: (remaining * 100.0).round() / 100.0,
        months_to_target: (months_to_target * 10.0).round() / 10.0,
        currency_symbol: get_currency_symbol(&req.currency),
        chart,
    }
}

pub fn calculate_tax(req: TaxRequest) -> TaxResponse {
    let rate = req.tax_rate / 100.0;
    
    let tax_amount = req.income * rate;
    let net_income = req.income - tax_amount;

    let chart = create_bar_chart(
        "Структура доходу",
        vec!["Чистий", "Податок"],
        vec![net_income, tax_amount],
        vec!["#2ecc71", "#e74c3c"]
    );

    TaxResponse {
        tax_amount: (tax_amount * 100.0).round() / 100.0,
        net_income: (net_income * 100.0).round() / 100.0,
        effective_rate: (rate * 100.0 * 10.0).round() / 10.0,
        currency_symbol: get_currency_symbol(&req.currency),
        chart,
    }
}

pub fn calculate_buy_rent(req: BuyRentRequest) -> BuyRentResponse {
    let loan = (req.property_price - req.down_payment).max(0.0);
    let r = req.mortgage_rate / 100.0 / 12.0;
    let n = (req.mortgage_term * 12.0) as i32;
    
    let mp = if loan > 0.0 && r > 0.0 {
        loan * (r * (1.0 + r).powi(n)) / ((1.0 + r).powi(n) - 1.0)
    } else if loan > 0.0 && n > 0 {
        loan / n as f64
    } else {
        0.0
    };
    
    let mut buy_costs_total = req.down_payment;
    for _ in 1..=(req.horizon as i32 * 12) {
        buy_costs_total += mp + (req.property_price * 0.01 / 12.0);
    }
    
    let mut rent_costs_total = 0.0;
    let mut curr_rent = req.monthly_rent;
    for m in 1..=(req.horizon as i32 * 12) {
        rent_costs_total += curr_rent;
        if m % 12 == 0 {
            curr_rent *= 1.0 + req.rent_growth / 100.0;
        }
    }
    
    let final_prop_val = req.property_price * (1.0 + req.property_growth / 100.0).powf(req.horizon);
    let net_buy = final_prop_val - buy_costs_total;
    let net_rent = req.down_payment * (1.07_f64).powf(req.horizon) - rent_costs_total;
    
    let chart = create_bar_chart(
        "Капітал через горизонт",
        vec!["Купівля", "Оренда"],
        vec![net_buy, net_rent],
        vec!["#2ecc71", "#3498db"]
    );

    BuyRentResponse {
        net_buy_position: (net_buy * 100.0).round() / 100.0,
        net_rent_position: (net_rent * 100.0).round() / 100.0,
        recommendation: if net_buy > net_rent { "buy".to_string() } else { "rent".to_string() },
        currency_symbol: get_currency_symbol(&req.currency),
        chart,
    }
}

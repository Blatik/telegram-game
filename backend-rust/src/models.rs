use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct HourlyIncomeRequest {
    pub monthly_income: f64,
    pub taxes: f64,
    pub work_hours: f64,
    pub commute_time: f64,
    pub work_expenses: f64,
    pub currency: String,
}

#[derive(Serialize)]
pub struct HourlyIncomeResponse {
    pub real_hourly_income: f64,
    pub nominal_hourly_income: f64,
    pub net_income: f64,
    pub efficiency: f64,
    pub currency_symbol: String,
    pub chart: String,
}

#[derive(Deserialize)]
pub struct TimeValueRequest {
    pub annual_income: f64,
    pub annual_hours: f64,
    pub currency: String,
}

#[derive(Serialize)]
pub struct TimeValueResponse {
    pub time_value: f64,
    pub currency_symbol: String,
    pub chart: String,
}

#[derive(Deserialize)]
pub struct CreditRequest {
    pub amount: f64,
    pub rate: f64,
    pub term: f64,
    pub currency: String,
}

#[derive(Serialize)]
pub struct CreditResponse {
    pub monthly_payment: f64,
    pub total_payment: f64,
    pub overpayment: f64,
    pub currency_symbol: String,
    pub chart: String,
}

#[derive(Deserialize)]
pub struct InvestmentRequest {
    pub initial_amount: f64,
    pub monthly_contribution: f64,
    pub annual_return: f64,
    pub period: f64,
    pub currency: String,
}

#[derive(Serialize)]
pub struct InvestmentResponse {
    pub future_value: f64,
    pub total_contributions: f64,
    pub total_gain: f64,
    pub roi: f64,
    pub currency_symbol: String,
    pub chart: String,
}

#[derive(Deserialize)]
pub struct RetirementRequest {
    pub current_age: f64,
    pub retirement_age: f64,
    pub desired_income: f64,
    pub current_savings: f64,
    pub monthly_savings: f64,
    pub expected_return: f64,
    pub currency: String,
}

#[derive(Serialize)]
pub struct RetirementResponse {
    pub future_value: f64,
    pub required_capital: f64,
    pub gap: f64,
    pub currency_symbol: String,
    pub chart: String,
}

#[derive(Deserialize)]
pub struct DebtPayoffRequest {
    pub balance: f64,
    pub interest_rate: f64,
    pub monthly_payment: f64,
    pub extra_payment: f64,
    pub currency: String,
}

#[derive(Serialize)]
pub struct DebtPayoffResponse {
    pub months: u32,
    pub total_paid: f64,
    pub total_interest: f64,
    pub currency_symbol: String,
    pub chart: String,
}

#[derive(Deserialize)]
pub struct EmergencyFundRequest {
    pub monthly_expenses: f64,
    pub months_coverage: f64,
    pub current_savings: f64,
    pub monthly_contribution: f64,
    pub currency: String,
}

#[derive(Serialize)]
pub struct EmergencyFundResponse {
    pub target_amount: f64,
    pub remaining_amount: f64,
    pub months_to_target: f64,
    pub currency_symbol: String,
    pub chart: String,
}

#[derive(Deserialize)]
pub struct TaxRequest {
    pub income: f64,
    pub tax_rate: f64,
    pub currency: String,
}

#[derive(Serialize)]
pub struct TaxResponse {
    pub tax_amount: f64,
    pub net_income: f64,
    pub effective_rate: f64,
    pub currency_symbol: String,
    pub chart: String,
}

#[derive(Deserialize)]
pub struct BuyRentRequest {
    pub property_price: f64,
    pub down_payment: f64,
    pub mortgage_rate: f64,
    pub mortgage_term: f64,
    pub monthly_rent: f64,
    pub rent_growth: f64,
    pub property_growth: f64,
    pub horizon: f64,
    pub currency: String,
}

#[derive(Serialize)]
pub struct BuyRentResponse {
    pub net_buy_position: f64,
    pub net_rent_position: f64,
    pub recommendation: String,
    pub currency_symbol: String,
    pub chart: String,
}

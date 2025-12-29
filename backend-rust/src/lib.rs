use worker::*;
mod models;
mod calculators;

use models::*;

#[event(fetch)]
async fn main(mut req: Request, _env: Env, _ctx: Context) -> Result<Response> {
    console_error_panic_hook::set_once();
    
    let path = req.path();
    let method = req.method();

    // CORS handling for all endpoints
    if method == Method::Options {
         let mut headers = Headers::new();
         headers.set("Access-Control-Allow-Origin", "*")?;
         headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")?;
         headers.set("Access-Control-Allow-Headers", "Content-Type")?;
         return Ok(Response::empty()?.with_headers(headers));
    }

    // Health check
    if method == Method::Get && path == "/health" {
        return Response::ok("OK");
    }

    // Calculator Endpoints
    if method == Method::Post {
        let mut headers = Headers::new();
        headers.set("Content-Type", "application/json")?;
        headers.set("Access-Control-Allow-Origin", "*")?;

        match path.as_str() {
            "/calculate/hourly-income" => {
                let data: HourlyIncomeRequest = match req.json().await {
                    Ok(d) => d,
                    Err(e) => return Response::error(format!("Bad Request: {}", e), 400),
                };
                let result = calculators::calculate_hourly_income(data);
                let json = serde_json::to_string(&result).map_err(|e| worker::Error::from(e.to_string()))?;
                return Ok(Response::ok(json)?.with_headers(headers));
            },
            "/calculate/time-value" => {
                let data: TimeValueRequest = match req.json().await {
                    Ok(d) => d,
                    Err(e) => return Response::error(format!("Bad Request: {}", e), 400),
                };
                let result = calculators::calculate_time_value(data);
                let json = serde_json::to_string(&result).map_err(|e| worker::Error::from(e.to_string()))?;
                return Ok(Response::ok(json)?.with_headers(headers));
            },
            "/calculate/investment" => {
                let data: InvestmentRequest = match req.json().await {
                    Ok(d) => d,
                    Err(e) => return Response::error(format!("Bad Request: {}", e), 400),
                };
                let result = calculators::calculate_investment(data);
                let json = serde_json::to_string(&result).map_err(|e| worker::Error::from(e.to_string()))?;
                return Ok(Response::ok(json)?.with_headers(headers));
            },
            "/calculate/credit" => {
                let data: CreditRequest = match req.json().await {
                    Ok(d) => d,
                    Err(e) => return Response::error(format!("Bad Request: {}", e), 400),
                };
                let result = calculators::calculate_credit(data);
                let json = serde_json::to_string(&result).map_err(|e| worker::Error::from(e.to_string()))?;
                return Ok(Response::ok(json)?.with_headers(headers));
            },
            "/calculate/retirement" => {
                let data: RetirementRequest = match req.json().await {
                    Ok(d) => d,
                    Err(e) => return Response::error(format!("Bad Request: {}", e), 400),
                };
                let result = calculators::calculate_retirement(data);
                let json = serde_json::to_string(&result).map_err(|e| worker::Error::from(e.to_string()))?;
                return Ok(Response::ok(json)?.with_headers(headers));
            },
            "/calculate/debt-payoff" => {
                let data: DebtPayoffRequest = match req.json().await {
                    Ok(d) => d,
                    Err(e) => return Response::error(format!("Bad Request: {}", e), 400),
                };
                let result = calculators::calculate_debt_payoff(data);
                let json = serde_json::to_string(&result).map_err(|e| worker::Error::from(e.to_string()))?;
                return Ok(Response::ok(json)?.with_headers(headers));
            },
            "/calculate/emergency-fund" => {
                let data: EmergencyFundRequest = match req.json().await {
                    Ok(d) => d,
                    Err(e) => return Response::error(format!("Bad Request: {}", e), 400),
                };
                let result = calculators::calculate_emergency_fund(data);
                let json = serde_json::to_string(&result).map_err(|e| worker::Error::from(e.to_string()))?;
                return Ok(Response::ok(json)?.with_headers(headers));
            },
            "/calculate/tax" => {
                let data: TaxRequest = match req.json().await {
                    Ok(d) => d,
                    Err(e) => return Response::error(format!("Bad Request: {}", e), 400),
                };
                let result = calculators::calculate_tax(data);
                let json = serde_json::to_string(&result).map_err(|e| worker::Error::from(e.to_string()))?;
                return Ok(Response::ok(json)?.with_headers(headers));
            },
            "/calculate/buy-rent" => {
                let data: BuyRentRequest = match req.json().await {
                    Ok(d) => d,
                    Err(e) => return Response::error(format!("Bad Request: {}", e), 400),
                };
                let result = calculators::calculate_buy_rent(data);
                let json = serde_json::to_string(&result).map_err(|e| worker::Error::from(e.to_string()))?;
                return Ok(Response::ok(json)?.with_headers(headers));
            },
            _ => {
                return Response::error("Not Found", 404);
            }
        }
    }

    Response::error("Not Found", 404)
}

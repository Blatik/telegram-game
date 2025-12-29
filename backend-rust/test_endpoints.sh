#!/bin/bash

BASE_URL="http://localhost:8787"

test_endpoint() {
    local name=$1
    local endpoint=$2
    local data=$3
    
    echo "Testing $name..."
    response=$(curl -s -X POST "$BASE_URL$endpoint" \
        -H "Content-Type: application/json" \
        -d "$data")
    
    if echo "$response" | grep -q "chart"; then
        echo "✅ $name: Success"
    else
        echo "❌ $name: Failed"
        echo "Response: $response"
    fi
    echo "-----------------------------------"
}

# 1. Hourly Income
test_endpoint "Hourly Income" "/calculate/hourly-income" \
    '{"monthly_income": 3000, "taxes": 20, "work_hours": 160, "commute_time": 40, "work_expenses": 200, "currency": "EUR"}'

# 2. Time Value
test_endpoint "Time Value" "/calculate/time-value" \
    '{"annual_income": 36000, "annual_hours": 2000, "currency": "USD"}'

# 3. Investment
test_endpoint "Investment" "/calculate/investment" \
    '{"initial_amount": 1000, "monthly_contribution": 200, "annual_return": 8, "period": 10, "currency": "EUR"}'

# 4. Credit
test_endpoint "Credit" "/calculate/credit" \
    '{"amount": 5000, "rate": 5, "term": 3, "currency": "USD"}'

# 5. Retirement
test_endpoint "Retirement" "/calculate/retirement" \
    '{"current_age": 30, "retirement_age": 65, "current_savings": 5000, "monthly_savings": 500, "expected_return": 7, "desired_income": 2000, "currency": "EUR"}'

# 6. Debt Payoff
test_endpoint "Debt Payoff" "/calculate/debt-payoff" \
    '{"balance": 10000, "interest_rate": 12, "monthly_payment": 300, "extra_payment": 100, "currency": "USD"}'

# 7. Emergency Fund
test_endpoint "Emergency Fund" "/calculate/emergency-fund" \
    '{"monthly_expenses": 1500, "months_coverage": 6, "current_savings": 2000, "monthly_contribution": 200, "currency": "EUR"}'

# 8. Tax
test_endpoint "Tax" "/calculate/tax" \
    '{"income": 5000, "country": "Ukraine", "currency": "UAH"}'

# 9. Buy vs Rent
test_endpoint "Buy vs Rent" "/calculate/buy-rent" \
    '{"property_price": 250000, "down_payment": 50000, "mortgage_rate": 4, "mortgage_term": 25, "monthly_rent": 1000, "rent_growth": 3, "property_growth": 2, "horizon": 10, "currency": "EUR"}'

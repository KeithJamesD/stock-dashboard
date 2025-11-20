import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Stock Analysis Dashboard")
st.markdown("### Comprehensive Financial Metrics & Valuation Analysis")

# Sidebar for API key and stock input
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your FMP API Key:", type="password")
    stock_symbol = st.text_input("Enter Stock Symbol:", value="AAPL").upper()
    analyze_button = st.button("Analyze Stock", type="primary")
    
    st.markdown("---")
    st.markdown("**Dashboard Sections:**")
    st.markdown("- Key Metrics & Ratios")
    st.markdown("- Valuation Analysis")
    st.markdown("- Fair Value Calculation")

# Helper functions
def fetch_quote(symbol, api_key):
    """Fetch current stock quote"""
    url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={api_key}"
    response = requests.get(url)
    return response.json()

def fetch_key_metrics(symbol, api_key):
    """Fetch key metrics TTM"""
    url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{symbol}?apikey={api_key}"
    response = requests.get(url)
    return response.json()

def fetch_ratios(symbol, api_key):
    """Fetch financial ratios TTM"""
    url = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{symbol}?apikey={api_key}"
    response = requests.get(url)
    return response.json()

def fetch_financial_growth(symbol, api_key):
    """Fetch financial growth metrics"""
    url = f"https://financialmodelingprep.com/api/v3/financial-growth/{symbol}?limit=10&apikey={api_key}"
    response = requests.get(url)
    return response.json()

def fetch_cash_flow(symbol, api_key):
    """Fetch cash flow statements"""
    url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}?limit=3&apikey={api_key}"
    response = requests.get(url)
    return response.json()

def fetch_dcf(symbol, api_key):
    """Fetch DCF valuation"""
    url = f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{symbol}?apikey={api_key}"
    response = requests.get(url)
    return response.json()

def fetch_advanced_dcf(symbol, api_key):
    """Fetch advanced DCF"""
    url = f"https://financialmodelingprep.com/api/v4/advanced_discounted_cash_flow?symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    return response.json()

def calculate_margin_of_safety(fair_value, current_price):
    """Calculate margin of safety"""
    if fair_value and current_price and fair_value > 0:
        return ((fair_value - current_price) / fair_value) * 100
    return None

def safe_get(data, key, default="N/A"):
    """Safely get value from dictionary"""
    try:
        if isinstance(data, list) and len(data) > 0:
            value = data[0].get(key, default)
        elif isinstance(data, dict):
            value = data.get(key, default)
        else:
            return default
        
        if value is None or value == "":
            return default
        return value
    except:
        return default

# Main analysis logic
if analyze_button and api_key and stock_symbol:
    try:
        with st.spinner(f"Fetching data for {stock_symbol}..."):
            # Fetch all data
            quote_data = fetch_quote(stock_symbol, api_key)
            key_metrics_data = fetch_key_metrics(stock_symbol, api_key)
            ratios_data = fetch_ratios(stock_symbol, api_key)
            growth_data = fetch_financial_growth(stock_symbol, api_key)
            cash_flow_data = fetch_cash_flow(stock_symbol, api_key)
            dcf_data = fetch_dcf(stock_symbol, api_key)
            advanced_dcf_data = fetch_advanced_dcf(stock_symbol, api_key)
        
        # Check if data is valid
        if not quote_data or (isinstance(quote_data, dict) and 'Error Message' in quote_data):
            st.error("Invalid stock symbol or API error. Please check your inputs.")
        else:
            # Extract current price info
            current_price = safe_get(quote_data, 'price', 0)
            previous_close = safe_get(quote_data, 'previousClose', 0)
            
            # Display header with stock info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Price", f"${current_price:.2f}" if isinstance(current_price, (int, float)) else current_price)
            with col2:
                st.metric("Previous Close", f"${previous_close:.2f}" if isinstance(previous_close, (int, float)) else previous_close)
            with col3:
                price_change = safe_get(quote_data, 'change', 0)
                st.metric("Change", f"${price_change:.2f}" if isinstance(price_change, (int, float)) else price_change)
            with col4:
                market_cap = safe_get(quote_data, 'marketCap', 0)
                if isinstance(market_cap, (int, float)) and market_cap > 0:
                    st.metric("Market Cap", f"${market_cap/1e9:.2f}B")
                else:
                    st.metric("Market Cap", "N/A")
            
            st.markdown("---")
            
            # Section 1: Key Metrics & Ratios
            st.header("📈 Key Metrics & Financial Ratios")
            
            # Prepare data for table
            metrics_dict = {
                "Metric": [
                    "Current Price",
                    "Last Close Price",
                    "Relative Strength Index (RSI)",
                    "Earnings Per Share (EPS)",
                    "Price-to-Sales (P/S)",
                    "Price-to-Earnings (P/E)",
                    "PEG Ratio",
                    "Debt-to-Equity",
                    "Price-to-Book (P/B)",
                    "Price-to-Free Cash Flow",
                    "EV to Assets",
                    "EV to Sales",
                    "Current Ratio",
                    "Quick Ratio",
                    "Return on Assets (ROA)",
                    "Return on Equity (ROE)",
                    "Free Cash Flow Yield",
                    "Net Profit Margin",
                    "Gross Profit Margin",
                    "Return on Invested Capital (ROIC)"
                ],
                "Value": []
            }
            
            # Populate values
            metrics_dict["Value"].append(f"${current_price:.2f}" if isinstance(current_price, (int, float)) else current_price)
            metrics_dict["Value"].append(f"${previous_close:.2f}" if isinstance(previous_close, (int, float)) else previous_close)
            
            # RSI (if available from key metrics)
            rsi = "N/A"  # FMP doesn't provide RSI in standard endpoints
            metrics_dict["Value"].append(rsi)
            
            # EPS
            eps = safe_get(key_metrics_data, 'netIncomePerShareTTM', 'N/A')
            metrics_dict["Value"].append(f"{eps:.2f}" if isinstance(eps, (int, float)) else eps)
            
            # Price-to-Sales
            ps_ratio = safe_get(ratios_data, 'priceToSalesRatioTTM', 'N/A')
            metrics_dict["Value"].append(f"{ps_ratio:.2f}" if isinstance(ps_ratio, (int, float)) else ps_ratio)
            
            # PE Ratio
            pe_ratio = safe_get(key_metrics_data, 'peRatioTTM', 'N/A')
            metrics_dict["Value"].append(f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio)
            
            # PEG Ratio
            peg_ratio = safe_get(key_metrics_data, 'pegRatioTTM', 'N/A')
            metrics_dict["Value"].append(f"{peg_ratio:.2f}" if isinstance(peg_ratio, (int, float)) else peg_ratio)
            
            # Debt-to-Equity
            de_ratio = safe_get(ratios_data, 'debtEquityRatioTTM', 'N/A')
            metrics_dict["Value"].append(f"{de_ratio:.2f}" if isinstance(de_ratio, (int, float)) else de_ratio)
            
            # Price-to-Book
            pb_ratio = safe_get(key_metrics_data, 'pbRatioTTM', 'N/A')
            metrics_dict["Value"].append(f"{pb_ratio:.2f}" if isinstance(pb_ratio, (int, float)) else pb_ratio)
            
            # Price-to-FCF
            pfcf_ratio = safe_get(key_metrics_data, 'pfcfRatioTTM', 'N/A')
            metrics_dict["Value"].append(f"{pfcf_ratio:.2f}" if isinstance(pfcf_ratio, (int, float)) else pfcf_ratio)
            
            # EV to Assets (calculated)
            ev = safe_get(key_metrics_data, 'enterpriseValueTTM', 0)
            total_assets = safe_get(ratios_data, 'totalAssetsTurnoverTTM', 0)
            ev_to_assets = "N/A"
            metrics_dict["Value"].append(ev_to_assets)
            
            # EV to Sales
            ev_to_sales = safe_get(key_metrics_data, 'enterpriseValueOverEBITDATTM', 'N/A')
            metrics_dict["Value"].append(f"{ev_to_sales:.2f}" if isinstance(ev_to_sales, (int, float)) else ev_to_sales)
            
            # Current Ratio
            current_ratio = safe_get(ratios_data, 'currentRatioTTM', 'N/A')
            metrics_dict["Value"].append(f"{current_ratio:.2f}" if isinstance(current_ratio, (int, float)) else current_ratio)
            
            # Quick Ratio
            quick_ratio = safe_get(ratios_data, 'quickRatioTTM', 'N/A')
            metrics_dict["Value"].append(f"{quick_ratio:.2f}" if isinstance(quick_ratio, (int, float)) else quick_ratio)
            
            # ROA
            roa = safe_get(ratios_data, 'returnOnAssetsTTM', 'N/A')
            if isinstance(roa, (int, float)):
                metrics_dict["Value"].append(f"{roa*100:.2f}%")
            else:
                metrics_dict["Value"].append(roa)
            
            # ROE
            roe = safe_get(ratios_data, 'returnOnEquityTTM', 'N/A')
            if isinstance(roe, (int, float)):
                metrics_dict["Value"].append(f"{roe*100:.2f}%")
            else:
                metrics_dict["Value"].append(roe)
            
            # FCF Yield
            fcf_yield = safe_get(key_metrics_data, 'freeCashFlowYieldTTM', 'N/A')
            if isinstance(fcf_yield, (int, float)):
                metrics_dict["Value"].append(f"{fcf_yield*100:.2f}%")
            else:
                metrics_dict["Value"].append(fcf_yield)
            
            # Net Profit Margin
            net_margin = safe_get(ratios_data, 'netProfitMarginTTM', 'N/A')
            if isinstance(net_margin, (int, float)):
                metrics_dict["Value"].append(f"{net_margin*100:.2f}%")
            else:
                metrics_dict["Value"].append(net_margin)
            
            # Gross Profit Margin
            gross_margin = safe_get(ratios_data, 'grossProfitMarginTTM', 'N/A')
            if isinstance(gross_margin, (int, float)):
                metrics_dict["Value"].append(f"{gross_margin*100:.2f}%")
            else:
                metrics_dict["Value"].append(gross_margin)
            
            # ROIC
            roic = safe_get(key_metrics_data, 'roicTTM', 'N/A')
            if isinstance(roic, (int, float)):
                metrics_dict["Value"].append(f"{roic*100:.2f}%")
            else:
                metrics_dict["Value"].append(roic)
            
            # Display metrics table
            df_metrics = pd.DataFrame(metrics_dict)
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Section 2: Valuation Analysis
            st.header("💰 Valuation & Fair Value Analysis")
            
            # Calculate 3-year average FCF
            fcf_values = []
            if cash_flow_data and isinstance(cash_flow_data, list):
                for cf in cash_flow_data[:3]:
                    fcf = cf.get('freeCashFlow', 0)
                    if fcf:
                        fcf_values.append(fcf)
            
            avg_fcf_3yr = sum(fcf_values) / len(fcf_values) if fcf_values else 0
            shares_outstanding = safe_get(key_metrics_data, 'numberOfSharesTTM', 0)
            fcf_per_share_3yr = avg_fcf_3yr / shares_outstanding if shares_outstanding else 0
            
            # Get growth rates
            growth_10yr = "N/A"
            if growth_data and isinstance(growth_data, list) and len(growth_data) > 0:
                revenue_growth = safe_get(growth_data, 'revenueGrowth', 0)
                if isinstance(revenue_growth, (int, float)):
                    growth_10yr = f"{revenue_growth*100:.2f}%"
            
            # DCF Fair Value
            dcf_value = safe_get(dcf_data, 'dcf', 0)
            
            # Advanced DCF if available
            advanced_dcf_value = safe_get(advanced_dcf_data, 'intrinsicValue', dcf_value)
            
            # Exit multiple (typically EV/EBITDA)
            exit_multiple = safe_get(key_metrics_data, 'enterpriseValueOverEBITDATTM', 'N/A')
            
            # Discount rate (WACC or cost of equity - approximation)
            # FMP provides some of this in advanced endpoints
            discount_rate = "10.0%"  # Standard assumption
            
            # EPS-based fair value (using PE)
            eps_value = safe_get(key_metrics_data, 'netIncomePerShareTTM', 0)
            industry_pe = 15  # Conservative industry average
            eps_fair_value = eps_value * industry_pe if isinstance(eps_value, (int, float)) else 0
            
            # Calculate margin of safety
            fair_value_final = dcf_value if isinstance(dcf_value, (int, float)) and dcf_value > 0 else advanced_dcf_value
            margin_of_safety = calculate_margin_of_safety(fair_value_final, current_price)
            
            # Valuation metrics
            valuation_dict = {
                "Valuation Metric": [
                    "Fair Value Price (DCF)",
                    "Margin of Safety",
                    "Free Cash Flow Per Share (3-Year Avg)",
                    "Growth Rate (Recent)",
                    "Discount Rate (Assumed)",
                    "Exit Multiple (EV/EBITDA)",
                    "EPS Fair Value Price"
                ],
                "Value": []
            }
            
            valuation_dict["Value"].append(f"${fair_value_final:.2f}" if isinstance(fair_value_final, (int, float)) and fair_value_final > 0 else "N/A")
            valuation_dict["Value"].append(f"{margin_of_safety:.2f}%" if margin_of_safety else "N/A")
            valuation_dict["Value"].append(f"${fcf_per_share_3yr:.2f}" if fcf_per_share_3yr > 0 else "N/A")
            valuation_dict["Value"].append(growth_10yr)
            valuation_dict["Value"].append(discount_rate)
            valuation_dict["Value"].append(f"{exit_multiple:.2f}" if isinstance(exit_multiple, (int, float)) else exit_multiple)
            valuation_dict["Value"].append(f"${eps_fair_value:.2f}" if isinstance(eps_fair_value, (int, float)) and eps_fair_value > 0 else "N/A")
            
            df_valuation = pd.DataFrame(valuation_dict)
            st.dataframe(df_valuation, use_container_width=True, hide_index=True)
            
            # Valuation summary
            st.markdown("---")
            st.subheader("📊 Valuation Summary")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if isinstance(fair_value_final, (int, float)) and fair_value_final > 0:
                    if current_price < fair_value_final:
                        st.success(f"**Potentially Undervalued** ✅")
                        st.write(f"Current: ${current_price:.2f} vs Fair Value: ${fair_value_final:.2f}")
                    else:
                        st.warning(f"**Potentially Overvalued** ⚠️")
                        st.write(f"Current: ${current_price:.2f} vs Fair Value: ${fair_value_final:.2f}")
                else:
                    st.info("Fair value data not available")
            
            with col2:
                if margin_of_safety:
                    if margin_of_safety > 20:
                        st.success(f"**Strong MOS: {margin_of_safety:.1f}%** 🎯")
                    elif margin_of_safety > 0:
                        st.info(f"**Moderate MOS: {margin_of_safety:.1f}%**")
                    else:
                        st.error(f"**Negative MOS: {margin_of_safety:.1f}%** 🚨")
            
            with col3:
                if fcf_per_share_3yr > 0:
                    st.metric("3-Yr Avg FCF/Share", f"${fcf_per_share_3yr:.2f}")
                else:
                    st.info("FCF data not available")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please check your API key and stock symbol.")

elif not api_key:
    st.info("👈 Please enter your FMP API key in the sidebar to get started.")
    st.markdown("""
    ### How to use this dashboard:
    1. Enter your Financial Modeling Prep API key in the sidebar
    2. Enter a stock symbol (e.g., AAPL, MSFT, GOOGL)
    3. Click 'Analyze Stock' to view comprehensive metrics
    
    ### Features:
    - **Key Metrics & Ratios**: 20+ essential financial metrics
    - **Valuation Analysis**: DCF-based fair value and margin of safety
    - **Real-time Data**: Current prices and financial statements
    
    ### Get your FMP API key:
    Visit [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/) to sign up for a free API key.
    """)

# Footer
st.markdown("---")
st.markdown("**Data provided by Financial Modeling Prep API** | Dashboard built with Streamlit")

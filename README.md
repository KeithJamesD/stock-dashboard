# Stock Analysis Dashboard

A comprehensive stock analysis dashboard built with Flask that provides detailed financial metrics, ratios, and DCF intrinsic value analysis.

## Features

- **50+ Financial Metrics & Ratios**
  - Valuation ratios (P/E, P/B, EV/EBITDA, etc.)
  - Profitability metrics (ROE, ROA, margins)
  - Liquidity ratios (current, quick ratios)
  - Efficiency ratios (asset turnover, inventory turnover)
  - Leverage ratios (debt-to-equity, interest coverage)
  - Growth metrics (revenue, earnings, FCF growth)

- **Interactive Price Charts**
  - Historical price visualization with Plotly
  - Volume analysis

- **DCF Intrinsic Value Analysis**
  - Two-stage DCF model (5-year projections + terminal value)
  - WACC calculation with transparent assumptions
  - Margin of safety analysis
  - Automated investment recommendations

## Files

- `stockapp_flask_alternative.py` - Main Flask dashboard application
- `stockapp2_claude.py` - Original Streamlit version (requires PyArrow compatibility)

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install flask requests pandas plotly
   ```

3. Get a free API key from [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs)

4. Run the Flask app:
   ```bash
   python stockapp_flask_alternative.py
   ```

5. Open your browser to `http://127.0.0.1:5000`

## Usage

Enter a stock ticker symbol (e.g., AAPL, MSFT, TSLA) to get comprehensive financial analysis including:
- Real-time quote data
- Financial metrics and ratios
- Interactive price charts
- DCF valuation with investment guidance

## API

This application uses the Financial Modeling Prep API for financial data. A free API key provides sufficient data for personal use.

## Note

The original Streamlit version (`stockapp2_claude.py`) may not work with Python 3.14 due to PyArrow compatibility issues. Use the Flask version for the latest Python releases.
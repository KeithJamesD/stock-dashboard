"""
Flask Alternative to Streamlit Stock App
This runs as a web app without the dependency issues
"""

from flask import Flask, render_template_string, request, jsonify
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import base64
import io

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f0f2f6; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-container { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .chart-container { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-value { font-size: 20px; font-weight: bold; color: #1f77b4; }
        .metric-label { color: #666; margin-top: 5px; font-size: 14px; }
        .section-title { font-size: 24px; font-weight: bold; margin: 30px 0 20px 0; color: #333; border-bottom: 2px solid #1f77b4; padding-bottom: 10px; }
        .input-group { margin: 10px 0; }
        .input-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .input-group input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { background-color: #1f77b4; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background-color: #155a8a; }
        .error { color: red; background-color: #fee; padding: 10px; border-radius: 4px; margin: 10px 0; }
        .success { color: green; background-color: #efe; padding: 10px; border-radius: 4px; margin: 10px 0; }
        .two-column { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .three-column { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
        .four-column { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Enhanced Stock Analysis Dashboard</h1>
            <p>Comprehensive Financial Metrics, Ratios & Performance Analysis</p>
        </div>
        
        <div class="form-container">
            <form method="POST">
                <div class="two-column">
                    <div class="input-group">
                        <label for="api_key">FMP API Key:</label>
                        <input type="password" id="api_key" name="api_key" value="{{ api_key or '' }}" placeholder="Enter your Financial Modeling Prep API key">
                    </div>
                    <div class="input-group">
                        <label for="symbol">Stock Symbol:</label>
                        <input type="text" id="symbol" name="symbol" value="{{ symbol or 'AAPL' }}" placeholder="e.g., AAPL">
                    </div>
                </div>
                <button type="submit" class="btn">🔍 Analyze Stock</button>
            </form>
        </div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        {% if data %}
        <div class="success">✅ Analysis completed successfully!</div>
        
        <!-- Current Quote -->
        {% if data.quote %}
        <div class="metric-card">
            <h2>📈 {{ data.quote.symbol }} - {{ data.quote.name }}</h2>
            
            <!-- Price Comparison Section -->
            {% if data.dcf %}
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 15px; margin: 15px 0; border-radius: 10px; border-left: 4px solid #007bff;">
                <h3 style="margin: 0 0 10px 0; color: #333;">💰 Price vs Intrinsic Value Analysis</h3>
                <div class="two-column" style="gap: 20px;">
                    <div style="text-align: center; padding: 10px; background: white; border-radius: 8px; border: 2px solid #ddd;">
                        <div class="metric-value" style="font-size: 24px;">${{ "%.2f"|format(data.quote.price) }}</div>
                        <div class="metric-label" style="font-weight: bold;">📊 Current Market Price</div>
                    </div>
                    <div style="text-align: center; padding: 10px; background: white; border-radius: 8px; border: 2px solid #28a745;">
                        <div class="metric-value" style="font-size: 24px; color: #28a745;">${{ "%.2f"|format(data.dcf.intrinsic_value) }}</div>
                        <div class="metric-label" style="font-weight: bold; color: #28a745;">🎯 DCF Intrinsic Value</div>
                    </div>
                </div>
                
                <!-- Valuation Indicator -->
                {% set price_ratio = (data.quote.price / data.dcf.intrinsic_value * 100) if data.dcf.intrinsic_value > 0 else 0 %}
                {% set margin_of_safety = data.dcf.margin_of_safety %}
                <div style="margin-top: 15px; text-align: center;">
                    {% if price_ratio < 80 %}
                        <div style="background: #d4edda; color: #155724; padding: 10px; border-radius: 8px; border: 1px solid #c3e6cb;">
                            <strong>🟢 POTENTIALLY UNDERVALUED</strong><br>
                            Current price is {{ "%.1f"|format(price_ratio) }}% of intrinsic value<br>
                            Margin of Safety: {{ "%.1f"|format(margin_of_safety) }}%
                        </div>
                    {% elif price_ratio > 120 %}
                        <div style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 8px; border: 1px solid #f5c6cb;">
                            <strong>🔴 POTENTIALLY OVERVALUED</strong><br>
                            Current price is {{ "%.1f"|format(price_ratio) }}% of intrinsic value<br>
                            Margin of Safety: {{ "%.1f"|format(margin_of_safety) }}%
                        </div>
                    {% else %}
                        <div style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 8px; border: 1px solid #ffeaa7;">
                            <strong>🟡 FAIRLY VALUED</strong><br>
                            Current price is {{ "%.1f"|format(price_ratio) }}% of intrinsic value<br>
                            Margin of Safety: {{ "%.1f"|format(margin_of_safety) }}%
                        </div>
                    {% endif %}
                </div>
            </div>
            {% else %}
            <!-- Message when DCF is not available -->
            <div style="background: #e9ecef; padding: 15px; margin: 15px 0; border-radius: 10px; border-left: 4px solid #6c757d; text-align: center;">
                <h4 style="margin: 0; color: #495057;">📊 DCF Intrinsic Value Analysis</h4>
                <p style="margin: 5px 0 0 0; color: #6c757d;">DCF valuation requires complete financial statements. Try a different stock symbol or check if financial data is available.</p>
            </div>
            {% endif %}
            
            <div class="four-column">
                <div>
                    <div class="metric-value">${{ "%.2f"|format(data.quote.price) }}</div>
                    <div class="metric-label">Current Price</div>
                </div>
                <div>
                    <div class="metric-value" style="color: {{ 'green' if data.quote.change >= 0 else 'red' }}">
                        {{ "%.2f"|format(data.quote.change) }} ({{ "%.2f"|format(data.quote.changesPercentage) }}%)
                    </div>
                    <div class="metric-label">Change (24h)</div>
                </div>
                <div>
                    <div class="metric-value">${{ "{:,.0f}".format(data.quote.marketCap or 0) }}</div>
                    <div class="metric-label">Market Cap</div>
                </div>
                <div>
                    <div class="metric-value">{{ "{:,.0f}".format(data.quote.volume or 0) }}</div>
                    <div class="metric-label">Volume</div>
                </div>
            </div>
            <div class="four-column" style="margin-top: 15px;">
                <div>
                    <div class="metric-value">${{ "%.2f"|format(data.quote.dayLow or 0) }}</div>
                    <div class="metric-label">Day Low</div>
                </div>
                <div>
                    <div class="metric-value">${{ "%.2f"|format(data.quote.dayHigh or 0) }}</div>
                    <div class="metric-label">Day High</div>
                </div>
                <div>
                    <div class="metric-value">${{ "%.2f"|format(data.quote.yearLow or 0) }}</div>
                    <div class="metric-label">52W Low</div>
                </div>
                <div>
                    <div class="metric-value">${{ "%.2f"|format(data.quote.yearHigh or 0) }}</div>
                    <div class="metric-label">52W High</div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Enhanced Price Chart with Candlesticks and Bollinger Bands -->
        {% if data.chart_data %}
        <div class="chart-container">
            <h2>📊 Enhanced Price Analysis - Candlestick Chart with Bollinger Bands (1 Year)</h2>
            <div id="priceChart"></div>
            <div style="margin-top: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 5px; font-size: 14px;">
                <strong>📈 Chart Features:</strong><br>
                • <span style="color: #00CC96;">🟢 Green Candles:</span> Closing price higher than opening price<br>
                • <span style="color: #EF553B;">🔴 Red Candles:</span> Closing price lower than opening price<br>
                • <span style="color: #FF6500;">📊 Orange Line:</span> 20-period Simple Moving Average (SMA)<br>
                • <span style="color: #808080;">⚫ Gray Dotted Lines:</span> Bollinger Bands (±2 standard deviations from SMA)<br>
                • <span style="color: #E0E0E0;">🔹 Shaded Area:</span> Bollinger Band channel indicating volatility
            </div>
        </div>
        {% endif %}

        <!-- Trend Analysis Chart with EMAs and Regression -->
        {% if data.trend_data %}
        <div class="chart-container">
            <h2>📈 Trend Analysis - EMAs, Linear Regression & Trend Lines (1 Year)</h2>
            <div id="trendChart"></div>
            <div style="margin-top: 10px; padding: 10px; background-color: #f0f8ff; border-radius: 5px; font-size: 14px;">
                <strong>📊 Trend Analysis Features:</strong><br>
                • <span style="color: #1f77b4;">🔵 Blue Line:</span> Stock closing price<br>
                • <span style="color: #ff7f0e;">🟠 Orange Line:</span> 20-period Exponential Moving Average (fast trend)<br>
                • <span style="color: #2ca02c;">🟢 Green Line:</span> 50-period Exponential Moving Average (medium trend)<br>
                • <span style="color: #d62728;">🔴 Red Line:</span> 200-period Exponential Moving Average (long-term trend)<br>
                • <span style="color: #ff00ff;">🟣 Magenta Dashed:</span> Linear regression line (overall trend direction)<br>
                • <span style="color: #800080;">🟣 Purple Dotted:</span> Dynamic trend line (recent price action)
            </div>
        </div>
        {% endif %}
        
        <div class="section-title">💰 Valuation Metrics</div>
        <!-- Valuation Metrics -->
        {% if data.metrics %}
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>📊 Core Valuation</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.metrics.peRatioTTM or 0) }}</div>
                        <div class="metric-label">P/E Ratio (TTM)</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.metrics.pbRatioTTM or 0) }}</div>
                        <div class="metric-label">P/B Ratio (TTM)</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.metrics.pegRatioTTM or 0) }}</div>
                        <div class="metric-label">PEG Ratio</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.metrics.pfcfRatioTTM or 0) }}</div>
                        <div class="metric-label">P/FCF Ratio</div>
                    </div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>💵 Price Multiples</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.metrics.psRatioTTM or 0) }}</div>
                        <div class="metric-label">P/S Ratio</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.metrics.pocfratioTTM or 0) }}</div>
                        <div class="metric-label">P/OCF Ratio</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.metrics.evToSales or 0) }}</div>
                        <div class="metric-label">EV/Sales</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.metrics.enterpriseValueOverEBITDATTM or 0) }}</div>
                        <div class="metric-label">EV/EBITDA</div>
                    </div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>📈 Per Share Metrics</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">${{ "%.2f"|format(data.metrics.bookValuePerShareTTM or 0) }}</div>
                        <div class="metric-label">Book Value/Share</div>
                    </div>
                    <div>
                        <div class="metric-value">${{ "%.2f"|format(data.metrics.tangibleBookValuePerShareTTM or 0) }}</div>
                        <div class="metric-label">Tangible BV/Share</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">${{ "%.2f"|format(data.metrics.revenuePerShareTTM or 0) }}</div>
                        <div class="metric-label">Revenue/Share</div>
                    </div>
                    <div>
                        <div class="metric-value">${{ "%.2f"|format(data.metrics.cashPerShareTTM or 0) }}</div>
                        <div class="metric-label">Cash/Share</div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
        
        <div class="section-title">🏆 Profitability & Returns</div>
        <!-- Profitability Metrics -->
        {% if data.metrics %}
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>💰 Return Ratios</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.metrics.roeTTM or 0) * 100) }}%</div>
                        <div class="metric-label">ROE (Return on Equity)</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.metrics.roaTTM or 0) * 100) }}%</div>
                        <div class="metric-label">ROA (Return on Assets)</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.metrics.roicTTM or 0) * 100) }}%</div>
                        <div class="metric-label">ROIC (Return on Capital)</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.ratios.returnOnTangibleAssetsTTM or 0) * 100) }}%</div>
                        <div class="metric-label">Return on Tangible Assets</div>
                    </div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>📊 Margin Analysis</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.ratios.grossProfitMarginTTM or 0) * 100) }}%</div>
                        <div class="metric-label">Gross Margin</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.ratios.operatingProfitMarginTTM or 0) * 100) }}%</div>
                        <div class="metric-label">Operating Margin</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.ratios.netProfitMarginTTM or 0) * 100) }}%</div>
                        <div class="metric-label">Net Margin</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.ratios.pretaxProfitMarginTTM or 0) * 100) }}%</div>
                        <div class="metric-label">Pre-tax Margin</div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
        
        <div class="section-title">🏛️ Financial Health & Liquidity</div>
        <!-- Financial Health -->
        {% if data.metrics %}
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>💪 Leverage & Debt</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.metrics.debtToEquityTTM or 0) }}</div>
                        <div class="metric-label">Debt-to-Equity</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.ratios.debtRatioTTM or 0) }}</div>
                        <div class="metric-label">Debt Ratio</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.ratios.longTermDebtToCapitalizationTTM or 0) }}</div>
                        <div class="metric-label">LT Debt/Capitalization</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.ratios.timesInterestEarnedTTM or 0) }}</div>
                        <div class="metric-label">Interest Coverage</div>
                    </div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>💧 Liquidity Ratios</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.metrics.currentRatioTTM or 0) }}</div>
                        <div class="metric-label">Current Ratio</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.ratios.quickRatioTTM or 0) }}</div>
                        <div class="metric-label">Quick Ratio</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.ratios.cashRatioTTM or 0) }}</div>
                        <div class="metric-label">Cash Ratio</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.ratios.operatingCashFlowPerShareTTM or 0) }}</div>
                        <div class="metric-label">OCF per Share</div>
                    </div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>🔄 Efficiency Metrics</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.ratios.receivablesTurnoverTTM or 0) }}</div>
                        <div class="metric-label">Receivables Turnover</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.1f"|format(data.ratios.daysOfSalesOutstandingTTM or 0) }}</div>
                        <div class="metric-label">Days Sales Outstanding</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">{{ "%.1f"|format(data.ratios.daysOfInventoryOutstandingTTM or 0) }}</div>
                        <div class="metric-label">Days Inventory Outstanding</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.1f"|format(data.ratios.daysOfPayablesOutstandingTTM or 0) }}</div>
                        <div class="metric-label">Days Payable Outstanding</div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <div class="section-title">📈 Growth & Dividends</div>
        <!-- Growth Metrics -->
        {% if data.growth %}
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>📈 Revenue Growth</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.growth.revenueGrowth or 0) * 100) }}%</div>
                        <div class="metric-label">Revenue Growth (YoY)</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.growth.grossProfitGrowth or 0) * 100) }}%</div>
                        <div class="metric-label">Gross Profit Growth</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.growth.netIncomeGrowth or 0) * 100) }}%</div>
                        <div class="metric-label">Net Income Growth</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.growth.epsgrowth or 0) * 100) }}%</div>
                        <div class="metric-label">EPS Growth</div>
                    </div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>💼 Operational Growth</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.growth.operatingIncomeGrowth or 0) * 100) }}%</div>
                        <div class="metric-label">Operating Income Growth</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.growth.freeCashFlowGrowth or 0) * 100) }}%</div>
                        <div class="metric-label">FCF Growth</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.growth.totalAssetsGrowth or 0) * 100) }}%</div>
                        <div class="metric-label">Total Assets Growth</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.growth.bookValuePerShareGrowth or 0) * 100) }}%</div>
                        <div class="metric-label">Book Value Growth</div>
                    </div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>💎 Dividend Information</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.ratios.dividendYielTTM or 0) * 100) }}%</div>
                        <div class="metric-label">Dividend Yield</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.ratios.payoutRatioTTM or 0) * 100) }}%</div>
                        <div class="metric-label">Payout Ratio</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">${{ "%.4f"|format(data.ratios.dividendPerShareTTM or 0) }}</div>
                        <div class="metric-label">Dividend per Share</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format((data.growth.dividendperShareGrowth or 0) * 100) }}%</div>
                        <div class="metric-label">Dividend Growth</div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- DCF Intrinsic Value Analysis -->
        {% if data.dcf %}
        <div class="section-title">💎 DCF Intrinsic Value Analysis</div>
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>🎯 Valuation Results</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value" style="color: #2e7d32;">${{ "%.2f"|format(data.dcf.intrinsic_value) }}</div>
                        <div class="metric-label">Intrinsic Value per Share</div>
                    </div>
                    <div>
                        <div class="metric-value">${{ "%.2f"|format(data.dcf.current_price) }}</div>
                        <div class="metric-label">Current Market Price</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value" style="color: {{ 'green' if data.dcf.margin_of_safety > 0 else 'red' }}">
                            {{ "%.1f"|format(data.dcf.margin_of_safety) }}%
                        </div>
                        <div class="metric-label">Margin of Safety</div>
                    </div>
                    <div>
                        <div class="metric-value" style="color: {{ 'red' if data.dcf.price_to_intrinsic > 1 else 'green' }}">
                            {{ "%.2f"|format(data.dcf.price_to_intrinsic) }}x
                        </div>
                        <div class="metric-label">Price to Intrinsic Value</div>
                    </div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>⚙️ DCF Assumptions</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.dcf.wacc) }}%</div>
                        <div class="metric-label">Discount Rate (WACC)</div>
                    </div>
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.dcf.terminal_growth) }}%</div>
                        <div class="metric-label">Terminal Growth Rate</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">{{ "%.2f"|format(data.dcf.fcf_growth_5yr) }}%</div>
                        <div class="metric-label">5-Year FCF Growth</div>
                    </div>
                    <div>
                        <div class="metric-value">${{ "{:,.0f}".format(data.dcf.free_cash_flow / 1000000) }}M</div>
                        <div class="metric-label">Current Free Cash Flow</div>
                    </div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>🏢 Enterprise Valuation</h3>
                <div class="two-column">
                    <div>
                        <div class="metric-value">${{ "{:,.0f}".format(data.dcf.enterprise_value / 1000000) }}M</div>
                        <div class="metric-label">Enterprise Value</div>
                    </div>
                    <div>
                        <div class="metric-value">${{ "{:,.0f}".format(data.dcf.equity_value / 1000000) }}M</div>
                        <div class="metric-label">Equity Value</div>
                    </div>
                </div>
                <div class="two-column" style="margin-top: 15px;">
                    <div>
                        <div class="metric-value">${{ "{:,.0f}".format(data.dcf.total_debt / 1000000) }}M</div>
                        <div class="metric-label">Total Debt</div>
                    </div>
                    <div>
                        <div class="metric-value">${{ "{:,.0f}".format(data.dcf.cash_and_equivalents / 1000000) }}M</div>
                        <div class="metric-label">Cash & Equivalents</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- DCF Sensitivity Analysis -->
        <div class="metric-card">
            <h3>📊 Investment Decision Guide</h3>
            <div style="padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin-top: 15px;">
                {% if data.dcf.margin_of_safety > 20 %}
                    <div style="color: #2e7d32; font-weight: bold; font-size: 18px;">🟢 STRONG BUY</div>
                    <p>High margin of safety ({{ "%.1f"|format(data.dcf.margin_of_safety) }}%) suggests the stock is significantly undervalued.</p>
                {% elif data.dcf.margin_of_safety > 10 %}
                    <div style="color: #388e3c; font-weight: bold; font-size: 18px;">🟢 BUY</div>
                    <p>Good margin of safety ({{ "%.1f"|format(data.dcf.margin_of_safety) }}%) indicates potential upside.</p>
                {% elif data.dcf.margin_of_safety > 0 %}
                    <div style="color: #f57c00; font-weight: bold; font-size: 18px;">🟡 HOLD</div>
                    <p>Small margin of safety ({{ "%.1f"|format(data.dcf.margin_of_safety) }}%). Stock is fairly valued.</p>
                {% elif data.dcf.margin_of_safety > -10 %}
                    <div style="color: #e64a19; font-weight: bold; font-size: 18px;">🟡 CAUTION</div>
                    <p>Negative margin of safety ({{ "%.1f"|format(data.dcf.margin_of_safety) }}%). Stock appears slightly overvalued.</p>
                {% else %}
                    <div style="color: #c62828; font-weight: bold; font-size: 18px;">🔴 AVOID</div>
                    <p>Large negative margin of safety ({{ "%.1f"|format(data.dcf.margin_of_safety) }}%). Stock appears significantly overvalued.</p>
                {% endif %}
                
                <div style="margin-top: 10px; font-size: 14px; color: #666;">
                    <strong>Key Metrics:</strong><br>
                    • Current Price: ${{ "%.2f"|format(data.dcf.current_price) }}<br>
                    • Intrinsic Value: ${{ "%.2f"|format(data.dcf.intrinsic_value) }}<br>
                    • Price/Intrinsic: {{ "%.2f"|format(data.dcf.price_to_intrinsic) }}x<br>
                    • Discount Rate: {{ "%.2f"|format(data.dcf.wacc) }}%
                </div>
            </div>
        </div>
        {% endif %}
        
        {% endif %}
    </div>

    {% if data and data.chart_data %}
    <script>
        // Enhanced Price Chart with Candlesticks and Bollinger Bands
        var priceData = {{ data.chart_data|safe }};
        var layout = {
            title: {
                text: '📊 {{ data.quote.symbol }} - Candlestick Chart with Bollinger Bands (1 Year)',
                font: { size: 18, color: '#333' }
            },
            xaxis: { 
                title: 'Date',
                type: 'date',
                rangeslider: { visible: false },
                showgrid: true,
                gridcolor: 'rgba(128,128,128,0.2)'
            },
            yaxis: { 
                title: 'Price ($)',
                showgrid: true,
                gridcolor: 'rgba(128,128,128,0.2)'
            },
            hovermode: 'x unified',
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'white',
            legend: {
                orientation: 'h',
                yanchor: 'bottom',
                y: 1.02,
                xanchor: 'right',
                x: 1
            },
            margin: { l: 60, r: 60, t: 80, b: 60 }
        };
        
        var config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false
        };
        
        Plotly.newPlot('priceChart', priceData, layout, config);
    </script>
    {% endif %}

    {% if data and data.trend_data %}
    <script>
        // Trend Analysis Chart with EMAs and Regression
        var trendData = {{ data.trend_data|safe }};
        var trendLayout = {
            title: {
                text: '📈 {{ data.quote.symbol }} - Trend Analysis with EMAs & Regression (1 Year)',
                font: { size: 18, color: '#333' }
            },
            xaxis: { 
                title: 'Date',
                type: 'date',
                showgrid: true,
                gridcolor: 'rgba(128,128,128,0.2)'
            },
            yaxis: { 
                title: 'Price ($)',
                showgrid: true,
                gridcolor: 'rgba(128,128,128,0.2)'
            },
            hovermode: 'x unified',
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'white',
            legend: {
                orientation: 'h',
                yanchor: 'bottom',
                y: 1.02,
                xanchor: 'right',
                x: 1
            },
            margin: { l: 60, r: 60, t: 80, b: 60 }
        };
        
        var trendConfig = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false
        };
        
        Plotly.newPlot('trendChart', trendData, trendLayout, trendConfig);
    </script>
    {% endif %}
</body>
</html>
"""

# Helper functions
def fetch_quote(symbol, api_key):
    """Fetch current stock quote"""
    try:
        url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={api_key}"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return None

def fetch_key_metrics(symbol, api_key):
    """Fetch key metrics TTM"""
    try:
        url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{symbol}?apikey={api_key}"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return None

def fetch_ratios(symbol, api_key):
    """Fetch financial ratios TTM"""
    try:
        url = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{symbol}?apikey={api_key}"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except Exception as e:
        print(f"Error fetching ratios: {e}")
        return None

def fetch_financial_growth(symbol, api_key):
    """Fetch financial growth metrics"""
    try:
        url = f"https://financialmodelingprep.com/api/v3/financial-growth/{symbol}?apikey={api_key}&limit=1"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except Exception as e:
        print(f"Error fetching growth data: {e}")
        return None

def calculate_bollinger_bands(prices, window=20, num_std=2):
    """Calculate Bollinger Bands"""
    if len(prices) < window:
        return None, None, None
    
    # Convert to pandas Series for easier calculation
    price_series = pd.Series(prices)
    
    # Calculate moving average and standard deviation
    sma = price_series.rolling(window=window).mean()
    std = price_series.rolling(window=window).std()
    
    # Calculate Bollinger Bands
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    
    return sma.tolist(), upper_band.tolist(), lower_band.tolist()


def calculate_ema(prices, window):
    """Calculate Exponential Moving Average"""
    if len(prices) < window:
        return [None] * len(prices)
    
    price_series = pd.Series(prices)
    ema = price_series.ewm(span=window, adjust=False).mean()
    return ema.tolist()


def calculate_linear_regression(prices, dates):
    """Calculate linear regression line"""
    try:
        import numpy as np
        from datetime import datetime
        
        # Convert dates to numeric values (days since first date)
        date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
        start_date = date_objects[0]
        x_values = [(date - start_date).days for date in date_objects]
        
        # Calculate linear regression
        x = np.array(x_values)
        y = np.array(prices)
        
        # Remove any NaN values
        mask = ~np.isnan(y)
        x = x[mask]
        y = y[mask]
        
        if len(x) < 2:
            return [None] * len(prices)
        
        # Calculate slope and intercept
        slope, intercept = np.polyfit(x, y, 1)
        
        # Generate regression line for all dates
        regression_line = [slope * x_val + intercept for x_val in x_values]
        
        return regression_line
    except Exception as e:
        print(f"Error calculating linear regression: {e}")
        return [None] * len(prices)


def calculate_trend_line(prices, dates, lookback_period=50):
    """Calculate trend line based on significant highs and lows"""
    try:
        import numpy as np
        
        if len(prices) < lookback_period:
            return [None] * len(prices)
        
        # Get recent data for trend calculation
        recent_prices = prices[-lookback_period:]
        recent_dates = dates[-lookback_period:]
        
        # Find significant highs and lows (simplified approach)
        highs = []
        lows = []
        
        for i in range(2, len(recent_prices) - 2):
            # Local high
            if (recent_prices[i] > recent_prices[i-1] and 
                recent_prices[i] > recent_prices[i+1] and
                recent_prices[i] > recent_prices[i-2] and 
                recent_prices[i] > recent_prices[i+2]):
                highs.append((i, recent_prices[i]))
            
            # Local low
            if (recent_prices[i] < recent_prices[i-1] and 
                recent_prices[i] < recent_prices[i+1] and
                recent_prices[i] < recent_prices[i-2] and 
                recent_prices[i] < recent_prices[i+2]):
                lows.append((i, recent_prices[i]))
        
        # Calculate trend based on recent highs/lows
        trend_line = [None] * len(prices)
        
        if len(highs) >= 2:
            # Use last two highs for uptrend line
            x1, y1 = highs[-2]
            x2, y2 = highs[-1]
            slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
            
            # Extend trend line
            start_idx = len(prices) - lookback_period
            for i in range(len(prices)):
                if i >= start_idx:
                    trend_line[i] = y1 + slope * (i - start_idx - x1)
        
        return trend_line
    except Exception as e:
        print(f"Error calculating trend line: {e}")
        return [None] * len(prices)

def fetch_historical_prices(symbol, api_key, period="1year"):
    """Fetch historical price data for candlestick charts with Bollinger bands"""
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?from={start_date.strftime('%Y-%m-%d')}&to={end_date.strftime('%Y-%m-%d')}&apikey={api_key}"
        response = requests.get(url, timeout=15)
        data = response.json()
        
        if 'historical' in data and len(data['historical']) > 0:
            # Prepare data for Plotly candlestick chart
            historical = data['historical'][::-1]  # Reverse to get chronological order
            
            dates = [item['date'] for item in historical]
            opens = [item['open'] for item in historical]
            highs = [item['high'] for item in historical]
            lows = [item['low'] for item in historical]
            closes = [item['close'] for item in historical]
            
            # Calculate Bollinger Bands
            sma, upper_band, lower_band = calculate_bollinger_bands(closes)
            
            # Candlestick chart data
            candlestick_trace = {
                'x': dates,
                'open': opens,
                'high': highs,
                'low': lows,
                'close': closes,
                'type': 'candlestick',
                'name': f'{symbol} Price',
                'increasing': {'line': {'color': '#00CC96'}},
                'decreasing': {'line': {'color': '#EF553B'}},
                'xaxis': 'x',
                'yaxis': 'y'
            }
            
            chart_data = [candlestick_trace]
            
            # Add Bollinger Bands if calculation was successful
            if sma and upper_band and lower_band:
                # Upper Bollinger Band
                upper_trace = {
                    'x': dates,
                    'y': upper_band,
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'Upper BB (20,2)',
                    'line': {'color': 'rgba(128, 128, 128, 0.8)', 'width': 1, 'dash': 'dot'},
                    'hovertemplate': 'Upper BB: $%{y:.2f}<extra></extra>'
                }
                
                # Lower Bollinger Band
                lower_trace = {
                    'x': dates,
                    'y': lower_band,
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'Lower BB (20,2)',
                    'line': {'color': 'rgba(128, 128, 128, 0.8)', 'width': 1, 'dash': 'dot'},
                    'fill': 'tonexty',
                    'fillcolor': 'rgba(128, 128, 128, 0.1)',
                    'hovertemplate': 'Lower BB: $%{y:.2f}<extra></extra>'
                }
                
                # Middle line (SMA)
                sma_trace = {
                    'x': dates,
                    'y': sma,
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'SMA (20)',
                    'line': {'color': 'rgba(255, 165, 0, 0.8)', 'width': 2},
                    'hovertemplate': 'SMA: $%{y:.2f}<extra></extra>'
                }
                
                # Add Bollinger Bands to chart data
                chart_data.extend([upper_trace, sma_trace, lower_trace])
            
            return chart_data
        return None
    except Exception as e:
        print(f"Error fetching historical prices: {e}")
        return None


def fetch_trend_analysis_data(symbol, api_key, period="1year"):
    """Fetch historical data for trend analysis with EMAs and regression"""
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?from={start_date.strftime('%Y-%m-%d')}&to={end_date.strftime('%Y-%m-%d')}&apikey={api_key}"
        response = requests.get(url, timeout=15)
        data = response.json()
        
        if 'historical' in data and len(data['historical']) > 0:
            # Prepare data for trend analysis
            historical = data['historical'][::-1]  # Reverse to get chronological order
            
            dates = [item['date'] for item in historical]
            closes = [item['close'] for item in historical]
            
            # Calculate EMAs
            ema20 = calculate_ema(closes, 20)
            ema50 = calculate_ema(closes, 50)
            ema200 = calculate_ema(closes, 200)
            
            # Calculate linear regression
            regression_line = calculate_linear_regression(closes, dates)
            
            # Calculate trend line
            trend_line = calculate_trend_line(closes, dates)
            
            # Create closing price line
            price_trace = {
                'x': dates,
                'y': closes,
                'type': 'scatter',
                'mode': 'lines',
                'name': f'{symbol} Price',
                'line': {'color': '#1f77b4', 'width': 2},
                'hovertemplate': 'Price: $%{y:.2f}<br>Date: %{x}<extra></extra>'
            }
            
            chart_data = [price_trace]
            
            # Add EMA traces
            if len([x for x in ema20 if x is not None]) > 0:
                ema20_trace = {
                    'x': dates,
                    'y': ema20,
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'EMA 20',
                    'line': {'color': '#ff7f0e', 'width': 2},
                    'hovertemplate': 'EMA 20: $%{y:.2f}<extra></extra>'
                }
                chart_data.append(ema20_trace)
            
            if len([x for x in ema50 if x is not None]) > 0:
                ema50_trace = {
                    'x': dates,
                    'y': ema50,
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'EMA 50',
                    'line': {'color': '#2ca02c', 'width': 2},
                    'hovertemplate': 'EMA 50: $%{y:.2f}<extra></extra>'
                }
                chart_data.append(ema50_trace)
            
            if len([x for x in ema200 if x is not None]) > 0:
                ema200_trace = {
                    'x': dates,
                    'y': ema200,
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'EMA 200',
                    'line': {'color': '#d62728', 'width': 3},
                    'hovertemplate': 'EMA 200: $%{y:.2f}<extra></extra>'
                }
                chart_data.append(ema200_trace)
            
            # Add linear regression line
            if len([x for x in regression_line if x is not None]) > 0:
                regression_trace = {
                    'x': dates,
                    'y': regression_line,
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'Linear Regression',
                    'line': {'color': 'rgba(255, 0, 255, 0.8)', 'width': 2, 'dash': 'dash'},
                    'hovertemplate': 'Regression: $%{y:.2f}<extra></extra>'
                }
                chart_data.append(regression_trace)
            
            # Add trend line
            if len([x for x in trend_line if x is not None]) > 0:
                trend_trace = {
                    'x': dates,
                    'y': trend_line,
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'Trend Line',
                    'line': {'color': 'rgba(128, 0, 128, 0.8)', 'width': 2, 'dash': 'dot'},
                    'hovertemplate': 'Trend: $%{y:.2f}<extra></extra>'
                }
                chart_data.append(trend_trace)
            
            return chart_data
        return None
    except Exception as e:
        print(f"Error fetching trend analysis data: {e}")
        return None

def fetch_cash_flow_statement(symbol, api_key):
    """Fetch cash flow statement for DCF analysis"""
    try:
        url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}?apikey={api_key}&limit=5"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data if data and len(data) > 0 else None
    except Exception as e:
        print(f"Error fetching cash flow statement: {e}")
        return None

def fetch_income_statement(symbol, api_key):
    """Fetch income statement for DCF analysis"""
    try:
        url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?apikey={api_key}&limit=5"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data if data and len(data) > 0 else None
    except Exception as e:
        print(f"Error fetching income statement: {e}")
        return None

def fetch_balance_sheet(symbol, api_key):
    """Fetch balance sheet for DCF analysis"""
    try:
        url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?apikey={api_key}&limit=5"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data if data and len(data) > 0 else None
    except Exception as e:
        print(f"Error fetching balance sheet: {e}")
        return None

def calculate_dcf_valuation(cash_flow_data, income_data, balance_sheet_data, growth_data, quote_data):
    """Calculate DCF intrinsic value with detailed assumptions"""
    try:
        if not cash_flow_data or not income_data or not balance_sheet_data:
            return None
            
        # Get latest financial data
        latest_cf = cash_flow_data[0]
        latest_income = income_data[0]
        latest_bs = balance_sheet_data[0]
        
        # Key DCF inputs
        free_cash_flow = latest_cf.get('freeCashFlow', 0)
        revenue = latest_income.get('revenue', 0)
        total_debt = latest_bs.get('totalDebt', 0)
        cash_and_equivalents = latest_bs.get('cashAndCashEquivalents', 0)
        shares_outstanding = quote_data.get('sharesOutstanding', 0)
        
        if free_cash_flow <= 0 or shares_outstanding <= 0:
            return None
            
        # Growth assumptions
        revenue_growth = growth_data.get('revenueGrowth', 0.05) if growth_data else 0.05
        fcf_growth_5yr = min(max(revenue_growth, 0.02), 0.25)  # Cap between 2% and 25%
        terminal_growth = 0.025  # Long-term GDP growth assumption
        
        # Discount rate calculation (WACC approximation)
        risk_free_rate = 0.045  # Current 10-year treasury approximate
        market_risk_premium = 0.06  # Historical equity risk premium
        beta = 1.2  # Default beta assumption
        cost_of_equity = risk_free_rate + (beta * market_risk_premium)
        
        # Weight of debt and equity (simplified)
        market_cap = quote_data.get('marketCap', 0)
        total_value = market_cap + total_debt
        if total_value > 0:
            equity_weight = market_cap / total_value
            debt_weight = total_debt / total_value
            cost_of_debt = 0.04  # Assumed cost of debt
            tax_rate = 0.25  # Assumed tax rate
            wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
        else:
            wacc = cost_of_equity
            
        # Project future cash flows (5 years)
        projected_fcf = []
        current_fcf = free_cash_flow
        
        for year in range(1, 6):
            # Declining growth rate over 5 years
            growth_rate = fcf_growth_5yr * (0.8 ** (year - 1))  # Declining growth
            current_fcf = current_fcf * (1 + growth_rate)
            projected_fcf.append(current_fcf)
            
        # Terminal value calculation
        terminal_fcf = projected_fcf[-1] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (wacc - terminal_growth)
        
        # Discount all cash flows to present value
        present_values = []
        for i, fcf in enumerate(projected_fcf):
            pv = fcf / ((1 + wacc) ** (i + 1))
            present_values.append(pv)
            
        # Present value of terminal value
        pv_terminal = terminal_value / ((1 + wacc) ** 5)
        
        # Enterprise value
        enterprise_value = sum(present_values) + pv_terminal
        
        # Equity value
        equity_value = enterprise_value - total_debt + cash_and_equivalents
        
        # Intrinsic value per share
        intrinsic_value = equity_value / shares_outstanding
        
        # Current price and margin of safety
        current_price = quote_data.get('price', 0)
        margin_of_safety = ((intrinsic_value - current_price) / intrinsic_value) * 100 if intrinsic_value > 0 else 0
        
        # Price to intrinsic value ratio
        price_to_intrinsic = (current_price / intrinsic_value) if intrinsic_value > 0 else 0
        
        return {
            'intrinsic_value': intrinsic_value,
            'current_price': current_price,
            'margin_of_safety': margin_of_safety,
            'price_to_intrinsic': price_to_intrinsic,
            'enterprise_value': enterprise_value,
            'equity_value': equity_value,
            'wacc': wacc * 100,  # Convert to percentage
            'terminal_growth': terminal_growth * 100,
            'fcf_growth_5yr': fcf_growth_5yr * 100,
            'projected_fcf': projected_fcf,
            'pv_fcf': present_values,
            'terminal_value': terminal_value,
            'pv_terminal': pv_terminal,
            'total_debt': total_debt,
            'cash_and_equivalents': cash_and_equivalents,
            'free_cash_flow': free_cash_flow
        }
        
    except Exception as e:
        print(f"Error calculating DCF: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    data = {}
    api_key = ""
    symbol = "AAPL"
    
    if request.method == 'POST':
        api_key = request.form.get('api_key', '').strip()
        symbol = request.form.get('symbol', 'AAPL').upper().strip()
        
        if not api_key:
            error = "Please enter your FMP API key"
        elif not symbol:
            error = "Please enter a stock symbol"
        else:
            try:
                print(f"Fetching data for {symbol}...")
                
                # Fetch all data
                quote = fetch_quote(symbol, api_key)
                metrics = fetch_key_metrics(symbol, api_key)
                ratios = fetch_ratios(symbol, api_key)
                growth = fetch_financial_growth(symbol, api_key)
                chart_data = fetch_historical_prices(symbol, api_key)
                trend_data = fetch_trend_analysis_data(symbol, api_key)
                
                # Fetch financial statements for DCF
                cash_flow_data = fetch_cash_flow_statement(symbol, api_key)
                income_data = fetch_income_statement(symbol, api_key)
                balance_sheet_data = fetch_balance_sheet(symbol, api_key)
                
                # Calculate DCF valuation
                dcf_analysis = None
                if quote and cash_flow_data and income_data and balance_sheet_data:
                    dcf_analysis = calculate_dcf_valuation(
                        cash_flow_data, income_data, balance_sheet_data, growth, quote
                    )
                
                if not quote:
                    error = f"Could not fetch data for symbol '{symbol}'. Please check the symbol and API key."
                else:
                    data = {
                        'quote': quote,
                        'metrics': metrics,
                        'ratios': ratios,
                        'growth': growth,
                        'chart_data': json.dumps(chart_data) if chart_data else None,
                        'trend_data': json.dumps(trend_data) if trend_data else None,
                        'dcf': dcf_analysis
                    }
                    print(f"Successfully fetched data for {symbol}")
                    if dcf_analysis:
                        print(f"DCF Intrinsic Value: ${dcf_analysis['intrinsic_value']:.2f}")
                    
            except Exception as e:
                error = f"Error occurred while fetching data: {str(e)}"
                print(f"Error: {e}")
    
    return render_template_string(HTML_TEMPLATE, 
                                error=error, 
                                data=data, 
                                api_key=api_key, 
                                symbol=symbol)

if __name__ == '__main__':
    print("Starting Stock Analysis Dashboard...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='127.0.0.1', port=5000)
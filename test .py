"""
Pytest Configuration & Fixtures
Shared test utilities and fixtures for financial models
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


# ============================================================================
# FIXTURES FOR BLACK-SCHOLES TESTS
# ============================================================================

@pytest.fixture
def standard_option_params():
    """Standard parameters for option pricing tests"""
    return {
        'S': 100.0,      # Current stock price
        'K': 100.0,      # Strike price
        'T': 1.0,        # Time to maturity (1 year)
        'r': 0.05,       # Risk-free rate (5%)
        'sigma': 0.2     # Volatility (20%)
    }


@pytest.fixture
def option_scenarios():
    """Multiple option scenarios for comprehensive testing"""
    return {
        'atm_call': {
            'S': 100, 'K': 100, 'T': 1, 'r': 0.05, 'sigma': 0.2,
            'type': 'call',
            'expected_delta_range': (0.4, 0.6)
        },
        'atm_put': {
            'S': 100, 'K': 100, 'T': 1, 'r': 0.05, 'sigma': 0.2,
            'type': 'put',
            'expected_delta_range': (-0.6, -0.4)
        },
        'deep_itm_call': {
            'S': 150, 'K': 100, 'T': 0.5, 'r': 0.05, 'sigma': 0.2,
            'type': 'call',
            'expected_delta_range': (0.95, 1.0)
        },
        'deep_otm_call': {
            'S': 50, 'K': 100, 'T': 0.5, 'r': 0.05, 'sigma': 0.2,
            'type': 'call',
            'expected_delta_range': (0.0, 0.05)
        }
    }


@pytest.fixture
def volatility_scenarios():
    """Different volatility levels for sensitivity testing"""
    return {
        'low_vol': 0.05,      # 5% - Very stable stock
        'normal_vol': 0.20,   # 20% - Average stock
        'high_vol': 0.50,     # 50% - Volatile stock
        'extreme_vol': 1.00   # 100% - Highly volatile
    }


@pytest.fixture
def interest_rate_scenarios():
    """Different interest rate environments"""
    return {
        'low_rate': 0.01,     # 1% - Low rate environment (COVID-era)
        'normal_rate': 0.05,  # 5% - Normal environment
        'high_rate': 0.10     # 10% - High rate environment (inflation)
    }


# ============================================================================
# FIXTURES FOR ALTMAN Z-SCORE TESTS
# ============================================================================

@pytest.fixture
def healthy_company():
    """Financial data for a healthy, solvent company"""
    return {
        'total_assets': 2000000,
        'working_capital': 600000,
        'retained_earnings': 800000,
        'ebit': 300000,
        'market_cap': 5000000,
        'total_liabilities': 500000,
        'revenue': 3000000
    }


@pytest.fixture
def distressed_company():
    """Financial data for a company in financial distress"""
    return {
        'total_assets': 1000000,
        'working_capital': 50000,      # Very low
        'retained_earnings': -100000,   # Negative (accumulated losses)
        'ebit': 30000,                 # Low profitability
        'market_cap': 400000,          # Low market cap
        'total_liabilities': 700000,   # High debt
        'revenue': 800000
    }


@pytest.fixture
def moderate_company():
    """Financial data for a company in the grey zone"""
    return {
        'total_assets': 1500000,
        'working_capital': 200000,
        'retained_earnings': 250000,
        'ebit': 100000,
        'market_cap': 1200000,
        'total_liabilities': 800000,
        'revenue': 1500000
    }


@pytest.fixture
def company_variations():
    """Multiple company scenarios for comprehensive testing"""
    return {
        'tech_startup': {
            'total_assets': 500000,
            'working_capital': 150000,
            'retained_earnings': -50000,  # Typical startup: burning cash
            'ebit': -30000,
            'market_cap': 5000000,        # High valuation (VC-backed)
            'total_liabilities': 100000,
            'revenue': 200000
        },
        'mature_industrial': {
            'total_assets': 10000000,
            'working_capital': 2000000,
            'retained_earnings': 5000000,  # Long history of profits
            'ebit': 1000000,
            'market_cap': 15000000,
            'total_liabilities': 3000000,
            'revenue': 8000000
        },
        'struggling_retailer': {
            'total_assets': 3000000,
            'working_capital': 300000,
            'retained_earnings': -500000,  # Accumulated losses
            'ebit': -100000,               # Operating losses
            'market_cap': 500000,          # Depressed valuation
            'total_liabilities': 2500000,  # High debt
            'revenue': 2000000
        }
    }


# ============================================================================
# FIXTURES FOR MARKET DATA TESTS
# ============================================================================

@pytest.fixture
def sample_price_series():
    """Generate a sample price time series"""
    dates = pd.date_range('2024-01-01', periods=20, freq='D')
    prices = np.linspace(100, 110, 20) + np.random.randn(20) * 0.5
    return pd.Series(prices, index=dates)


@pytest.fixture
def uptrend_series():
    """Price series with clear uptrend"""
    dates = pd.date_range('2024-01-01', periods=20, freq='D')
    prices = np.linspace(100, 120, 20)  # Consistent uptrend
    return pd.Series(prices, index=dates)


@pytest.fixture
def downtrend_series():
    """Price series with clear downtrend"""
    dates = pd.date_range('2024-01-01', periods=20, freq='D')
    prices = np.linspace(120, 100, 20)  # Consistent downtrend
    return pd.Series(prices, index=dates)


@pytest.fixture
def volatile_series():
    """Price series with high volatility"""
    dates = pd.date_range('2024-01-01', periods=20, freq='D')
    prices = 100 + np.random.randn(20) * 5  # High random walk
    return pd.Series(prices, index=dates)


@pytest.fixture
def ticker_dict():
    """Standard ticker dictionary for testing"""
    return {
        "S&P 500": "^GSPC",
        "DAX": "^GDAXI",
        "CAC 40": "^FCHI",
        "VIX": "^VIX"
    }


# ============================================================================
# FIXTURES FOR MATHEMATICAL OPERATIONS
# ============================================================================

@pytest.fixture
def normal_distribution_values():
    """Sample values from standard normal distribution"""
    np.random.seed(42)  # For reproducibility
    return np.random.randn(1000)


@pytest.fixture
def epsilon_values():
    """Small epsilon values for numerical stability tests"""
    return {
        'tiny': 1e-10,
        'small': 1e-6,
        'medium': 1e-3,
        'large': 0.01
    }


# ============================================================================
# PYTEST HOOKS & CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )


@pytest.fixture(autouse=True)
def reset_random_seed():
    """Reset random seed before each test for reproducibility"""
    np.random.seed(42)
    yield
    # Cleanup after test


# ============================================================================
# HELPER FIXTURES
# ============================================================================

@pytest.fixture
def tolerance():
    """Numerical tolerance levels for assertions"""
    return {
        'strict': 1e-8,      # Very strict (mathematical operations)
        'normal': 1e-6,      # Normal (financial calculations)
        'loose': 1e-2,       # Loose (market data, empirical results)
        'percentage': 0.01   # 1% tolerance
    }


@pytest.fixture
def financial_constants():
    """Common financial constants"""
    return {
        'trading_days_per_year': 252,
        'business_days_per_year': 252,
        'months_per_year': 12,
        'quarters_per_year': 4,
        'weeks_per_year': 52,
        'hours_per_day': 6.5,  # US stock market hours
        'minutes_per_day': 390  # 6.5 hours in minutes
    }


@pytest.fixture
def expected_values():
    """Benchmark values for validation"""
    return {
        'atm_call_delta': 0.5,      # ATM call delta should be ~0.5
        'atm_call_gamma_max': True,  # Gamma highest ATM
        'put_call_parity': True,     # Put-Call Parity must hold
        'option_price_bounds': {
            'call': (0, float('inf')),     # Call price >= 0
            'put': (0, float('inf'))       # Put price >= 0
        }
    }

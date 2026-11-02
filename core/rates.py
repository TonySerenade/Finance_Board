"""Sovereign yield data access and calculations.

This module contains NO Streamlit UI: it fetches data, validates observations,
and computes spreads. The application is responsible only for presentation.

Source: OECD monthly 10-year benchmark yields distributed through FRED.
These are NOT live executable bond quotes.
"""
from datetime import date
from io import StringIO

import pandas as pd
import requests

# Display label, FRED series identifier, and geographical grouping.
SERIES = [
    ("UST 10Y", "IRLTLT01USM156N", "US"),
    ("OAT 10Y", "IRLTLT01FRM156N", "Europe"),
    ("BUND 10Y", "IRLTLT01DEM156N", "Bund"),
    ("BONO 10Y", "IRLTLT01ESM156N", "Europe"),
    ("OLO 10Y", "IRLTLT01BEM156N", "Europe"),
    ("GILT 10Y", "IRLTLT01GBM156N", "UK"),
    ("BTP 10Y", "IRLTLT01ITM156N", "Europe"),
]

FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"


def fetch_sovereign_yields(as_of=None, max_age_days=75):
    """Download the latest usable observation for each country.

    Returns one dictionary per series. A stale or failed series has value=None
    rather than silently displaying an old number as today's market yield.
    """
    today = as_of or date.today()
    results = []

    for label, series_id, region in SERIES:
        observation = {
            "label": label, "region": region, "series_id": series_id,
            "value": None, "date": None, "stale": False,
        }
        try:
            # FRED serves CSV directly; no API key required for this endpoint.
            response = requests.get(
                FRED_CSV_URL,
                params={"id": series_id, "cosd": "2025-01-01"},
                timeout=8,
                headers={"User-Agent": "FinanceBoard/1.0 educational analytics"},
            )
            response.raise_for_status()
            frame = pd.read_csv(StringIO(response.text))

            # FRED CSV exports can label the observation date differently.
            date_column = next(
                (column for column in ("observation_date", "DATE") if column in frame.columns),
                None,
            )
            if date_column is None or series_id not in frame.columns:
                raise ValueError("Unexpected FRED CSV format")

            # Missing observations (e.g. '.') become NaN and are discarded.
            frame[date_column] = pd.to_datetime(frame[date_column], errors="coerce")
            frame[series_id] = pd.to_numeric(frame[series_id], errors="coerce")
            frame = frame.dropna(subset=[date_column, series_id]).sort_values(date_column)
            if frame.empty:
                raise ValueError("No valid observations")

            latest = frame.iloc[-1]
            observation["date"] = latest[date_column].date()
            observation["stale"] = (today - observation["date"]).days > max_age_days
            if not observation["stale"]:
                observation["value"] = float(latest[series_id])
        except (requests.RequestException, ValueError, KeyError, IndexError, pd.errors.ParserError):
            # One failed country should not take down the whole dashboard.
            pass

        results.append(observation)

    return results


def add_bund_spreads(rates):
    """Add spread_bp for European countries with an available Bund reference.

    Yields are percentages, so a 1 percentage-point difference is 100 bp.
    Countries outside the European comparison group get spread_bp=None.
    """
    bund = next((row["value"] for row in rates if row["region"] == "Bund"), None)
    enriched = []
    for row in rates:
        item = dict(row)
        value = item["value"]
        item["spread_bp"] = (
            (value - bund) * 100
            if item["region"] == "Europe" and value is not None and bund is not None
            else None
        )
        enriched.append(item)
    return enriched

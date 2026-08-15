"""
data_loader.py — Upload handling, schema validation, and data cleaning.

Handles CSV/XLSX ingestion, validates required columns, flags data quality
issues (missing values, duplicates, impossible rows), and returns a clean
DataFrame ready for metric calculations.
"""

import pandas as pd
import streamlit as st


# ------------------------------------------------------------------
# Required columns (lowercase keys used for case-insensitive matching)
# ------------------------------------------------------------------
REQUIRED_COLUMNS = [
    "campaign name",
    "date",
    "impressions",
    "clicks",
    "spend",
    "revenue",
    "conversions",
    "platform",
]

NUMERIC_COLUMNS = ["impressions", "clicks", "spend", "revenue", "conversions"]


# ------------------------------------------------------------------
# Smart Column Aliases — maps common Kaggle/external names → our names
# Each key = our required column, values = list of known aliases (lowercase)
# ------------------------------------------------------------------
COLUMN_ALIASES = {
    "campaign name": [
        "campaign_name", "campaign name", "campaign", "campaign_type",
        "campaign_id", "campaign id", "ad_group", "ad group", "ad_name",
        "ad name", "adset_name", "adset name", "campaign_title",
        "campaign title", "name",
    ],
    "date": [
        "date", "day", "report_date", "report date", "start_date",
        "start date", "end_date", "end date", "created_at", "created at",
        "period", "month", "week", "year_month",
    ],
    "impressions": [
        "impressions", "impression", "imps", "views", "ad_views",
        "ad views", "total_impressions", "total impressions", "reach",
    ],
    "clicks": [
        "clicks", "click", "total_clicks", "total clicks", "link_clicks",
        "link clicks", "website_clicks", "website clicks",
    ],
    "spend": [
        "spend", "cost", "total_spend", "total spend", "amount_spent",
        "amount spent", "acquisition_cost", "acquisition cost",
        "campaign_cost", "campaign cost", "ad_spend", "ad spend",
        "budget", "total_cost", "total cost", "media_cost", "media cost",
        "investment", "adspend", "marketing_spend", "marketing spend",
        "cost_per_result", "advertising_cost", "budget_allocated",
    ],
    "revenue": [
        "revenue", "total_revenue", "total revenue", "earnings",
        "income", "sales", "total_sales", "total sales", "value",
        "conversion_value", "conversion value", "purchase_value",
        "purchase value", "gmv", "gross_revenue", "gross revenue",
        "return", "returns", "revenue_generated", "revenue generated",
    ],
    "conversions": [
        "conversions", "conversion", "total_conversions",
        "total conversions", "leads", "lead", "applications",
        "application", "purchases", "purchase", "signups", "sign_ups",
        "sign ups", "registrations", "registration", "actions",
        "results", "installs", "app_installs", "app installs",
        "subscribers", "orders", "total_orders",
    ],
    "platform": [
        "platform", "channel", "channels_used", "channels used",
        "source", "ad_platform", "ad platform", "network",
        "traffic_source", "traffic source", "medium", "publisher",
        "ad_network", "ad network", "marketing_channel",
        "marketing channel", "source_medium", "device", "social_network",
    ],
}


def auto_map_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Automatically detect and rename columns to match the dashboard schema.

    Uses fuzzy alias matching: for each required column, scans the
    DataFrame's columns against a curated list of known aliases.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame with potentially non-standard column names.

    Returns
    -------
    tuple[pd.DataFrame, dict]
        (renamed_df, mapping) where mapping shows {original → standard}.
        Only columns that were actually renamed are included in mapping.
    """
    df = df.copy()
    # Normalise: strip whitespace, lowercase
    df.columns = df.columns.str.strip().str.lower()

    existing_cols = set(df.columns)
    rename_map = {}  # old_name → new_standard_name

    for standard_name, aliases in COLUMN_ALIASES.items():
        # Skip if the standard name already exists
        if standard_name in existing_cols:
            continue

        # Search aliases for a match
        for alias in aliases:
            if alias in existing_cols and alias != standard_name:
                rename_map[alias] = standard_name
                existing_cols.discard(alias)
                existing_cols.add(standard_name)
                break

    if rename_map:
        df = df.rename(columns=rename_map)

    return df, rename_map


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def load_file(uploaded_file) -> pd.DataFrame:
    """
    Read an uploaded CSV or XLSX file into a pandas DataFrame.

    Parameters
    ----------
    uploaded_file : st.UploadedFile
        File object from st.file_uploader.

    Returns
    -------
    pd.DataFrame or None
        Raw DataFrame if parsing succeeds, None otherwise.
    """
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            st.error("Unsupported file type. Please upload a CSV or XLSX file.")
            return None

        # Normalise column names: strip whitespace, lowercase
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None


def validate_columns(df: pd.DataFrame) -> list:
    """
    Check that all required columns exist in the DataFrame.

    Returns
    -------
    list
        Names of any missing required columns (empty list = all present).
    """
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]


def run_quality_checks(df: pd.DataFrame) -> dict:
    """
    Run a comprehensive data-quality audit on the raw DataFrame.

    Returns a dict with counts and flagged row indices so the UI can
    let the user decide how to handle each issue category.

    Keys returned
    -------------
    missing_values : dict   — column → count of nulls
    duplicate_idx  : Index  — indices of duplicate rows
    clicks_gt_imp  : Index  — rows where Clicks > Impressions
    negative_vals  : Index  — rows with any negative numeric value
    bad_dates      : Index  — rows where Date could not be parsed
    total_rows     : int
    """
    report = {}

    # --- Missing / null values in numeric columns ---
    missing = {}
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            n = df[col].isna().sum()
            if n > 0:
                missing[col] = int(n)
    report["missing_values"] = missing

    # --- Duplicate rows (same Campaign Name + Date + Platform) ---
    dup_cols = ["campaign name", "date", "platform"]
    if all(c in df.columns for c in dup_cols):
        dup_mask = df.duplicated(subset=dup_cols, keep="first")
        report["duplicate_idx"] = df.index[dup_mask]
    else:
        report["duplicate_idx"] = pd.Index([])

    # --- Clicks > Impressions (impossible) ---
    if {"clicks", "impressions"}.issubset(df.columns):
        mask = df["clicks"] > df["impressions"]
        # Only flag where both values are non-null
        mask = mask & df["clicks"].notna() & df["impressions"].notna()
        report["clicks_gt_imp"] = df.index[mask]
    else:
        report["clicks_gt_imp"] = pd.Index([])

    # --- Negative values in numeric columns ---
    neg_mask = pd.Series(False, index=df.index)
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            neg_mask = neg_mask | (df[col] < 0)
    report["negative_vals"] = df.index[neg_mask]

    # --- Unparseable dates ---
    if "date" in df.columns:
        parsed = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        report["bad_dates"] = df.index[parsed.isna() & df["date"].notna()]
    else:
        report["bad_dates"] = pd.Index([])

    report["total_rows"] = len(df)
    return report


def clean_data(
    df: pd.DataFrame,
    drop_duplicates: bool = True,
    fill_missing_zero: bool = True,
) -> pd.DataFrame:
    """
    Apply cleaning steps to produce analysis-ready data.

    Parameters
    ----------
    drop_duplicates : bool
        If True, remove duplicate rows (keep first occurrence).
    fill_missing_zero : bool
        If True, fill NaN in numeric columns with 0; otherwise drop rows.

    Returns
    -------
    pd.DataFrame
        Cleaned copy of the input.
    """
    df = df.copy()

    # 1. Parse dates (try dayfirst=True for DD/MM/YYYY formats)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        # Drop rows where date could not be parsed
        df = df.dropna(subset=["date"])

    # 2. Handle missing numeric values
    if fill_missing_zero:
        for col in NUMERIC_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    else:
        df = df.dropna(subset=[c for c in NUMERIC_COLUMNS if c in df.columns])

    # 3. Remove rows with negative values in numeric columns
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df = df[df[col] >= 0]

    # 4. Remove impossible rows (Clicks > Impressions)
    if {"clicks", "impressions"}.issubset(df.columns):
        df = df[df["clicks"] <= df["impressions"]]

    # 5. Drop duplicates
    if drop_duplicates:
        dup_cols = ["campaign name", "date", "platform"]
        if all(c in df.columns for c in dup_cols):
            df = df.drop_duplicates(subset=dup_cols, keep="first")

    # 6. Reset index for a clean sequential index
    df = df.reset_index(drop=True)

    return df

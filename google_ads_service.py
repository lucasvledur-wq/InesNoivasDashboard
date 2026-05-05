import os
from datetime import date, timedelta

import pandas as pd
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

load_dotenv()

CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "6778012588")


def _get_client() -> GoogleAdsClient:
    credentials = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", CUSTOMER_ID),
        "use_proto_plus": True,
    }
    return GoogleAdsClient.load_from_dict(credentials)


def _date_range(days: int) -> tuple[str, str]:
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def fetch_campaign_metrics(days: int) -> pd.DataFrame:
    client = _get_client()
    service = client.get_service("GoogleAdsService")
    start, end = _date_range(days)

    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.cost_per_conversion,
            metrics.conversions_from_interactions_rate,
            metrics.search_impression_share,
            metrics.interactions
        FROM campaign
        WHERE segments.date BETWEEN '{start}' AND '{end}'
            AND campaign.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """

    rows = []
    response = service.search_stream(customer_id=CUSTOMER_ID, query=query)
    for batch in response:
        for row in batch.results:
            cost = row.metrics.cost_micros / 1_000_000
            rows.append({
                "Campaign ID": row.campaign.id,
                "Campaign": row.campaign.name,
                "Status": row.campaign.status.name,
                "Type": row.campaign.advertising_channel_type.name,
                "Impressions": row.metrics.impressions,
                "Clicks": row.metrics.clicks,
                "CTR (%)": round(row.metrics.ctr * 100, 2),
                "CPC (R$)": round(row.metrics.average_cpc / 1_000_000, 2),
                "Cost (R$)": round(cost, 2),
                "Conversions": round(row.metrics.conversions, 1),
                "Conv. Value (R$)": round(row.metrics.conversions_value, 2),
                "Cost/Conv (R$)": round(row.metrics.cost_per_conversion / 1_000_000, 2) if row.metrics.conversions > 0 else 0,
                "Conv. Rate (%)": round(row.metrics.conversions_from_interactions_rate * 100, 2),
                "Impr. Share (%)": round((row.metrics.search_impression_share or 0) * 100, 1),
                "Interactions": row.metrics.interactions,
            })

    return pd.DataFrame(rows) if rows else pd.DataFrame()


def fetch_daily_metrics(days: int) -> pd.DataFrame:
    client = _get_client()
    service = client.get_service("GoogleAdsService")
    start, end = _date_range(days)

    query = f"""
        SELECT
            segments.date,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE segments.date BETWEEN '{start}' AND '{end}'
            AND campaign.status != 'REMOVED'
        ORDER BY segments.date ASC
    """

    rows = []
    response = service.search_stream(customer_id=CUSTOMER_ID, query=query)
    for batch in response:
        for row in batch.results:
            rows.append({
                "Date": row.segments.date,
                "Impressions": row.metrics.impressions,
                "Clicks": row.metrics.clicks,
                "Cost (R$)": row.metrics.cost_micros / 1_000_000,
                "Conversions": row.metrics.conversions,
                "Conv. Value (R$)": row.metrics.conversions_value,
            })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.groupby("Date", as_index=False).sum()
    df["CTR (%)"] = (df["Clicks"] / df["Impressions"].replace(0, 1) * 100).round(2)
    df["CPC (R$)"] = (df["Cost (R$)"] / df["Clicks"].replace(0, 1)).round(2)
    df["Cost (R$)"] = df["Cost (R$)"].round(2)
    df["Conv. Value (R$)"] = df["Conv. Value (R$)"].round(2)
    return df


def fetch_campaign_daily(days: int) -> pd.DataFrame:
    client = _get_client()
    service = client.get_service("GoogleAdsService")
    start, end = _date_range(days)

    query = f"""
        SELECT
            segments.date,
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM campaign
        WHERE segments.date BETWEEN '{start}' AND '{end}'
            AND campaign.status != 'REMOVED'
        ORDER BY segments.date ASC
    """

    rows = []
    response = service.search_stream(customer_id=CUSTOMER_ID, query=query)
    for batch in response:
        for row in batch.results:
            rows.append({
                "Date": row.segments.date,
                "Campaign": row.campaign.name,
                "Impressions": row.metrics.impressions,
                "Clicks": row.metrics.clicks,
                "Cost (R$)": round(row.metrics.cost_micros / 1_000_000, 2),
                "Conversions": round(row.metrics.conversions, 1),
            })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

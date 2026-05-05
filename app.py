import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_service import (
    load_campaigns, load_adgroups,
    load_ga4_pages, load_ga4_daily, load_ga4_channels,
    load_ads_daily, load_keywords,
)

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Inês Noivas Eternity | Dashboard",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme colors
# ---------------------------------------------------------------------------
GOLD = "#d4af37"
NAVY = "#1a1a2e"
BLUE = "#0f3460"
LIGHT_BLUE = "#16213e"
RED = "#e74c3c"
GREEN = "#27ae60"

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    .main .block-container {{ padding-top: 1.5rem; }}
    .dashboard-header {{
        background: linear-gradient(135deg, {NAVY} 0%, {LIGHT_BLUE} 50%, {BLUE} 100%);
        padding: 2rem 2.5rem; border-radius: 16px; margin-bottom: 1.5rem; color: white;
    }}
    .dashboard-header h1 {{
        font-family: 'Playfair Display', serif; font-size: 2.2rem; margin: 0; color: {GOLD};
    }}
    .dashboard-header p {{
        font-family: 'Inter', sans-serif; font-size: 0.95rem; color: #b8c5d6; margin: 0.3rem 0 0 0;
    }}
    .metric-card {{
        background: white; border: 1px solid #e8e8e8; border-radius: 12px;
        padding: 1.1rem 1.2rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}
    .metric-card .label {{
        font-family: 'Inter', sans-serif; font-size: 0.72rem; font-weight: 500;
        color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;
    }}
    .metric-card .value {{
        font-family: 'Inter', sans-serif; font-size: 1.6rem; font-weight: 700;
        color: {NAVY}; margin-top: 0.15rem;
    }}
    .metric-card .value.gold {{ color: {GOLD}; }}
    .metric-card .value.red {{ color: {RED}; }}
    .metric-card .value.green {{ color: {GREEN}; }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {NAVY} 0%, {LIGHT_BLUE} 100%);
    }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    .section-title {{
        font-family: 'Playfair Display', serif; font-size: 1.4rem; color: {NAVY};
        border-bottom: 2px solid {GOLD}; padding-bottom: 0.5rem; margin: 1.5rem 0 1rem 0;
    }}
    .insight-box {{
        background: #f8f9fa; border-left: 4px solid {GOLD}; padding: 0.8rem 1.2rem;
        border-radius: 0 8px 8px 0; margin: 0.5rem 0; font-family: 'Inter', sans-serif;
        font-size: 0.9rem; color: #333;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="dashboard-header">
    <h1>Inês Noivas Eternity</h1>
    <p>Google Ads + GA4 Dashboard &nbsp;|&nbsp; Conta 677-801-2588 &nbsp;|&nbsp; Geração de Leads</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Configurações")
    period = st.radio(
        "Período de análise",
        options=[7, 14, 30, 90],
        format_func=lambda x: f"Últimos {x} dias",
        index=2,
    )
    st.markdown("---")
    st.markdown("**Conta:** 677-801-2588")
    st.markdown("**Cliente:** Inês Noivas Eternity")
    st.markdown("**Tipo:** Geração de Leads")
    st.markdown("**GA4 Property:** 453035485")
    st.markdown("---")
    st.markdown("*Dados atualizados via Zapier*")


def metric_html(label, value, style=""):
    cls = f"value {style}" if style else "value"
    return f'<div class="metric-card"><div class="label">{label}</div><div class="{cls}">{value}</div></div>'


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
campaigns_df = load_campaigns(period)
adgroups_df = load_adgroups(period)
ga4_pages_df = load_ga4_pages(period)
ga4_daily_df = load_ga4_daily(period)
ga4_channels_df = load_ga4_channels(period)
ads_daily_df = load_ads_daily(period)
keywords_df = load_keywords(30)

if campaigns_df.empty:
    st.warning(f"Nenhum dado de campanhas encontrado para {period} dias. Execute o refresh de dados via Claude Code.")
    st.info("""
    **Como atualizar os dados:**
    No Claude Code, peça: *"Atualizar dados da dashboard Inês Noivas para X dias"*
    Os dados serão puxados via Zapier e salvos localmente.
    """)
    st.stop()

# =========================================================================
# SECTION 1: KPI CARDS — Google Ads
# =========================================================================
active_campaigns = campaigns_df[campaigns_df["Status"] != "REMOVED"]
total_cost = active_campaigns["Cost (R$)"].sum()
total_clicks = active_campaigns["Clicks"].sum()
total_impressions = active_campaigns["Impressions"].sum()
total_conversions = active_campaigns["Conversions"].sum()
avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
avg_cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
cost_per_lead = (total_cost / total_conversions) if total_conversions > 0 else 0
active_count = len(active_campaigns[active_campaigns["Impressions"] > 0])

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.markdown(metric_html("Investimento", f"R$ {total_cost:,.2f}"), unsafe_allow_html=True)
with col2:
    st.markdown(metric_html("Leads (Conv.)", f"{total_conversions:,.1f}", "gold"), unsafe_allow_html=True)
with col3:
    st.markdown(metric_html("Custo por Lead", f"R$ {cost_per_lead:,.2f}", "gold"), unsafe_allow_html=True)
with col4:
    st.markdown(metric_html("Cliques", f"{total_clicks:,}"), unsafe_allow_html=True)
with col5:
    st.markdown(metric_html("CTR", f"{avg_ctr:.2f}%"), unsafe_allow_html=True)
with col6:
    st.markdown(metric_html("CPC Médio", f"R$ {avg_cpc:,.2f}"), unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.markdown(metric_html("Impressões", f"{total_impressions:,}"), unsafe_allow_html=True)
with col2:
    st.markdown(metric_html("Campanhas Ativas", f"{active_count}"), unsafe_allow_html=True)
with col3:
    if not ga4_daily_df.empty and "Sessions" in ga4_daily_df.columns:
        total_sessions = ga4_daily_df["Sessions"].sum()
        st.markdown(metric_html("Sessões (GA4)", f"{total_sessions:,}"), unsafe_allow_html=True)
    else:
        st.markdown(metric_html("Sessões (GA4)", "—"), unsafe_allow_html=True)
with col4:
    if not ga4_daily_df.empty and "Users" in ga4_daily_df.columns:
        total_users = ga4_daily_df["Users"].sum()
        st.markdown(metric_html("Usuários (GA4)", f"{total_users:,}"), unsafe_allow_html=True)
    else:
        st.markdown(metric_html("Usuários (GA4)", "—"), unsafe_allow_html=True)
with col5:
    if not ga4_daily_df.empty and "Engagement Rate (%)" in ga4_daily_df.columns:
        avg_engagement = ga4_daily_df["Engagement Rate (%)"].mean()
        st.markdown(metric_html("Engajamento", f"{avg_engagement:.1f}%", "green"), unsafe_allow_html=True)
    else:
        st.markdown(metric_html("Engajamento", "—"), unsafe_allow_html=True)
with col6:
    if not ga4_daily_df.empty and "Bounce Rate (%)" in ga4_daily_df.columns:
        avg_bounce = ga4_daily_df["Bounce Rate (%)"].mean()
        color = "red" if avg_bounce > 35 else "green"
        st.markdown(metric_html("Bounce Rate", f"{avg_bounce:.1f}%", color), unsafe_allow_html=True)
    else:
        st.markdown(metric_html("Bounce Rate", "—"), unsafe_allow_html=True)

# =========================================================================
# SECTION 2: IMPRESSION SHARE ANALYSIS
# =========================================================================
is_cols = ["Impr. Share (%)", "Lost IS Budget (%)", "Lost IS Rank (%)"]
has_is_data = all(c in campaigns_df.columns for c in is_cols)

if has_is_data:
    st.markdown('<div class="section-title">Parcela de Impressões (Search & PMax)</div>', unsafe_allow_html=True)

    is_data = active_campaigns[active_campaigns["Impr. Share (%)"].notna()].copy()
    if not is_data.empty:
        col1, col2 = st.columns([3, 2])

        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=is_data["Campaign"], x=is_data["Impr. Share (%)"],
                name="Parcela de Impressões", marker_color=GOLD, orientation="h",
            ))
            fig.add_trace(go.Bar(
                y=is_data["Campaign"], x=is_data["Lost IS Budget (%)"],
                name="Perdida (Orçamento)", marker_color=RED, orientation="h",
            ))
            fig.add_trace(go.Bar(
                y=is_data["Campaign"], x=is_data["Lost IS Rank (%)"],
                name="Perdida (Class./Rank)", marker_color="#95a5a6", orientation="h",
            ))
            fig.update_layout(
                barmode="stack", template="plotly_white",
                height=300, margin=dict(t=10, b=30, l=10),
                legend=dict(orientation="h", y=1.15),
                xaxis=dict(title="% das Impressões Disponíveis", range=[0, 105]),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            is_table = is_data[["Campaign", "Impr. Share (%)", "Lost IS Budget (%)", "Lost IS Rank (%)"]].copy()
            if "Top IS (%)" in is_data.columns:
                is_table["Top IS (%)"] = is_data["Top IS (%)"]
            if "Abs. Top IS (%)" in is_data.columns:
                is_table["Abs. Top IS (%)"] = is_data["Abs. Top IS (%)"]
            st.dataframe(is_table, use_container_width=True, hide_index=True)

        for _, row in is_data.iterrows():
            name = row["Campaign"]
            lost_rank = row.get("Lost IS Rank (%)", 0) or 0
            lost_budget = row.get("Lost IS Budget (%)", 0) or 0
            is_share = row.get("Impr. Share (%)", 0) or 0

            if lost_rank > 50:
                st.markdown(
                    f'<div class="insight-box"><strong>{name}:</strong> Perdendo <b>{lost_rank:.0f}%</b> '
                    f'de impressões por classificação. Considere aumentar lances ou melhorar Quality Score.</div>',
                    unsafe_allow_html=True)
            if lost_budget > 10:
                st.markdown(
                    f'<div class="insight-box"><strong>{name}:</strong> Perdendo <b>{lost_budget:.0f}%</b> '
                    f'de impressões por orçamento. Considere aumentar o budget diário.</div>',
                    unsafe_allow_html=True)

# =========================================================================
# SECTION 3: CAMPAIGN PERFORMANCE TABLE
# =========================================================================
st.markdown('<div class="section-title">Performance por Campanha</div>', unsafe_allow_html=True)

display_cols = [
    "Campaign", "Impressions", "Clicks", "CTR (%)", "CPC (R$)",
    "Cost (R$)", "Conversions", "Cost/Conv (R$)", "Conv. Rate (%)",
    "Impr. Share (%)", "Lost IS Budget (%)", "Lost IS Rank (%)",
]
available_cols = [c for c in display_cols if c in active_campaigns.columns]

format_dict = {
    "Impressions": "{:,.0f}", "Clicks": "{:,.0f}", "CTR (%)": "{:.2f}%",
    "CPC (R$)": "R$ {:.2f}", "Cost (R$)": "R$ {:.2f}", "Conversions": "{:.1f}",
    "Cost/Conv (R$)": "R$ {:.2f}", "Conv. Rate (%)": "{:.2f}%",
    "Impr. Share (%)": "{:.1f}%", "Lost IS Budget (%)": "{:.1f}%",
    "Lost IS Rank (%)": "{:.1f}%",
}
active_format = {k: v for k, v in format_dict.items() if k in available_cols}

st.dataframe(
    active_campaigns[available_cols].style.format(active_format, na_rep="—"),
    use_container_width=True, height=300, hide_index=True,
)

# =========================================================================
# SECTION 4: AD GROUP PERFORMANCE (Search depth)
# =========================================================================
if not adgroups_df.empty:
    st.markdown('<div class="section-title">Performance por Grupo de Anúncios</div>', unsafe_allow_html=True)

    ag_cols = ["Ad Group", "Impressions", "Clicks", "CTR (%)", "CPC (R$)",
               "Cost (R$)", "Conversions", "Cost/Conv (R$)", "Conv. Rate (%)"]
    ag_available = [c for c in ag_cols if c in adgroups_df.columns]

    col1, col2 = st.columns([3, 2])
    with col1:
        st.dataframe(
            adgroups_df[ag_available].sort_values("Conversions", ascending=False).style.format({
                "Impressions": "{:,.0f}", "Clicks": "{:,.0f}", "CTR (%)": "{:.2f}%",
                "CPC (R$)": "R$ {:.2f}", "Cost (R$)": "R$ {:.2f}", "Conversions": "{:.1f}",
                "Cost/Conv (R$)": "R$ {:.2f}", "Conv. Rate (%)": "{:.2f}%",
            }, na_rep="—"),
            use_container_width=True, hide_index=True,
        )
    with col2:
        fig = px.bar(
            adgroups_df.sort_values("Conversions", ascending=True),
            x="Conversions", y="Ad Group", orientation="h",
            color="Cost/Conv (R$)",
            color_continuous_scale=[[0, GREEN], [0.5, GOLD], [1, RED]],
        )
        fig.update_layout(
            height=300, margin=dict(t=10, b=30), template="plotly_white",
            yaxis_title="", xaxis_title="Conversões (Leads)",
            coloraxis_colorbar_title="CPA (R$)",
        )
        st.plotly_chart(fig, use_container_width=True)

# =========================================================================
# SECTION 5: DAILY TRENDS — Google Ads
# =========================================================================
st.markdown('<div class="section-title">Tendência Diária — Google Ads</div>', unsafe_allow_html=True)

if not ads_daily_df.empty:
    tab1, tab2, tab3 = st.tabs(["Investimento, Leads & Custo/Lead", "Cliques & Impressões", "CTR & CPC"])

    daily_ads = ads_daily_df.copy()

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=daily_ads["Date"], y=daily_ads["Cost (R$)"],
            name="Investimento (R$)", marker_color=NAVY, opacity=0.6,
            yaxis="y",
            hovertemplate="Investimento: R$ %{y:,.2f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=daily_ads["Date"], y=daily_ads["Conversions"],
            name="Leads", line=dict(color=GOLD, width=3),
            yaxis="y2",
            hovertemplate="Leads: %{y:.1f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=daily_ads["Date"], y=daily_ads["Cost/Lead (R$)"],
            name="Custo/Lead (R$)", line=dict(color=RED, width=2, dash="dot"),
            yaxis="y2",
            hovertemplate="Custo/Lead: R$ %{y:.2f}<extra></extra>",
        ))
        fig.update_layout(
            template="plotly_white", height=380, margin=dict(t=20, b=40),
            yaxis=dict(title="Investimento (R$)", tickprefix="R$ ", side="left"),
            yaxis2=dict(title="Leads / Custo por Lead", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=daily_ads["Date"], y=daily_ads["Impressions"],
            name="Impressões", marker_color=NAVY, opacity=0.5,
            yaxis="y",
            hovertemplate="Impressões: %{y:,.0f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=daily_ads["Date"], y=daily_ads["Clicks"],
            name="Cliques", line=dict(color=GOLD, width=3),
            yaxis="y2",
            hovertemplate="Cliques: %{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            template="plotly_white", height=380, margin=dict(t=20, b=40),
            yaxis=dict(title="Impressões", side="left"),
            yaxis2=dict(title="Cliques", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_ads["Date"], y=daily_ads["CTR (%)"],
            name="CTR (%)", line=dict(color=GOLD, width=3),
            yaxis="y",
            hovertemplate="CTR: %{y:.2f}%<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=daily_ads["Date"], y=daily_ads["CPC (R$)"],
            name="CPC (R$)", line=dict(color=BLUE, width=2),
            yaxis="y2",
            hovertemplate="CPC: R$ %{y:.2f}<extra></extra>",
        ))
        fig.update_layout(
            template="plotly_white", height=380, margin=dict(t=20, b=40),
            yaxis=dict(title="CTR (%)", ticksuffix="%", side="left"),
            yaxis2=dict(title="CPC (R$)", tickprefix="R$ ", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig, use_container_width=True)

# =========================================================================
# SECTION 6: DISTRIBUTION CHARTS
# =========================================================================
st.markdown('<div class="section-title">Distribuição de Investimento & Leads</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    pie_data = active_campaigns[active_campaigns["Cost (R$)"] > 0]
    fig = px.pie(
        pie_data, values="Cost (R$)", names="Campaign",
        color_discrete_sequence=[GOLD, NAVY, BLUE, "#27ae60", "#e74c3c", "#9b59b6"],
        hole=0.45,
    )
    fig.update_layout(height=350, margin=dict(t=20, b=20))
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        active_campaigns[active_campaigns["Conversions"] > 0].sort_values("Conversions", ascending=True),
        x="Conversions", y="Campaign", orientation="h",
        color="Cost/Conv (R$)",
        color_continuous_scale=[[0, GREEN], [0.5, GOLD], [1, RED]],
    )
    fig.update_layout(
        height=350, margin=dict(t=20, b=20), template="plotly_white",
        yaxis_title="", xaxis_title="Leads (Conversões)",
        coloraxis_colorbar_title="CPA",
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================================================================
# SECTION 7: GA4 — PAGE PERFORMANCE
# =========================================================================
if not ga4_pages_df.empty:
    st.markdown('<div class="section-title">Performance por Página (GA4)</div>', unsafe_allow_html=True)

    has_events = "Whatsapp LP" in ga4_pages_df.columns
    page_fmt = {
        "Pageviews": "{:,.0f}",
        "Avg. Session (s)": "{:.0f}s",
    }
    if has_events:
        page_fmt["Whatsapp LP"] = "{:,.0f}"
        page_fmt["Generate Lead"] = "{:,.0f}"
    page_cols = ["Page", "Pageviews", "Avg. Session (s)"]
    if has_events:
        page_cols += ["Whatsapp LP", "Generate Lead"]
    page_cols_available = [c for c in page_cols if c in ga4_pages_df.columns]

    col1, col2 = st.columns([3, 2])
    with col1:
        st.dataframe(
            ga4_pages_df[page_cols_available].sort_values("Pageviews", ascending=False).style.format(
                {k: v for k, v in page_fmt.items() if k in page_cols_available}, na_rep="—"
            ),
            use_container_width=True, hide_index=True,
        )

    with col2:
        if has_events:
            events_chart = ga4_pages_df[ga4_pages_df["Whatsapp LP"] > 0].sort_values("Whatsapp LP", ascending=True)
            if not events_chart.empty:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=events_chart["Page"], x=events_chart["Whatsapp LP"],
                    name="Whatsapp LP", marker_color=GREEN, orientation="h",
                ))
                if events_chart["Generate Lead"].sum() > 0:
                    fig.add_trace(go.Bar(
                        y=events_chart["Page"], x=events_chart["Generate Lead"],
                        name="Generate Lead", marker_color=GOLD, orientation="h",
                    ))
                fig.update_layout(
                    barmode="group", height=300, margin=dict(t=10, b=30),
                    template="plotly_white", yaxis_title="", xaxis_title="Eventos",
                    legend=dict(orientation="h", y=1.1),
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.bar(
                ga4_pages_df.sort_values("Pageviews", ascending=True),
                x="Pageviews", y="Page", orientation="h",
                color_discrete_sequence=[GOLD],
            )
            fig.update_layout(
                height=300, margin=dict(t=10, b=30), template="plotly_white",
                yaxis_title="", xaxis_title="Pageviews",
            )
            st.plotly_chart(fig, use_container_width=True)

# =========================================================================
# SECTION 8: GA4 — CHANNEL MIX
# =========================================================================
if not ga4_channels_df.empty:
    st.markdown('<div class="section-title">Mix de Canais (GA4)</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(
            ga4_channels_df, values="Sessions", names="Channel",
            color_discrete_sequence=[GOLD, NAVY, BLUE, GREEN, RED, "#9b59b6", "#f39c12"],
            hole=0.45,
        )
        fig.update_layout(height=320, margin=dict(t=20, b=20))
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        ch_cols = ["Channel", "Sessions", "Users"]
        if "Whatsapp LP" in ga4_channels_df.columns:
            ch_cols += ["Whatsapp LP", "Generate Lead"]
        ch_cols += [c for c in ["Engagement Rate (%)", "Avg. Session (s)"]
                    if c in ga4_channels_df.columns]
        ch_available = [c for c in ch_cols if c in ga4_channels_df.columns]
        ch_fmt = {"Engagement Rate (%)": "{:.1f}%", "Avg. Session (s)": "{:.1f}s"}
        st.dataframe(
            ga4_channels_df[ch_available].sort_values("Sessions", ascending=False).style.format(
                {k: v for k, v in ch_fmt.items() if k in ch_available}, na_rep="—"
            ),
            use_container_width=True, hide_index=True,
        )

# =========================================================================
# SECTION 9: KEYWORDS — Top Converting Search Terms
# =========================================================================
if not keywords_df.empty:
    st.markdown('<div class="section-title">Palavras-chave com Mais Conversões (Google Ads — 30d)</div>', unsafe_allow_html=True)

    kw_display = keywords_df[keywords_df["Conversões"] > 0].copy()
    if not kw_display.empty:
        col1, col2 = st.columns([3, 2])
        with col1:
            kw_cols = ["Palavra-chave", "Conversões", "Cliques", "CTR (%)", "CPC (R$)",
                       "Custo (R$)", "Custo/Conv (R$)", "Taxa Conv (%)"]
            kw_available = [c for c in kw_cols if c in kw_display.columns]
            st.dataframe(
                kw_display[kw_available].sort_values("Conversões", ascending=False).style.format({
                    "Conversões": "{:.1f}", "Cliques": "{:,.0f}", "CTR (%)": "{:.2f}%",
                    "CPC (R$)": "R$ {:.2f}", "Custo (R$)": "R$ {:.2f}",
                    "Custo/Conv (R$)": "R$ {:.2f}", "Taxa Conv (%)": "{:.2f}%",
                }, na_rep="—"),
                use_container_width=True, hide_index=True,
            )

        with col2:
            top_kw = kw_display.nlargest(10, "Conversões")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=top_kw["Palavra-chave"], x=top_kw["Conversões"],
                orientation="h", marker_color=GOLD,
                text=[f'{v:.1f}' for v in top_kw["Conversões"]],
                textposition="auto",
                hovertemplate="<b>%{y}</b><br>Conversões: %{x:.1f}<extra></extra>",
            ))
            fig.update_layout(
                height=400, margin=dict(t=10, b=30, l=10), template="plotly_white",
                yaxis=dict(autorange="reversed"),
                xaxis=dict(title="Conversões (Leads)"),
            )
            st.plotly_chart(fig, use_container_width=True)

# =========================================================================
# SECTION 10: ANÁLISE ESPECIALISTA — PPC Senior LeadGen B2C
# =========================================================================
st.markdown('<div class="section-title">Análise & Recomendações — PPC Sênior</div>', unsafe_allow_html=True)

# ── Calcular métricas consolidadas para análise ──
_c = campaigns_df if not campaigns_df.empty else pd.DataFrame()

def _s(df, col, agg="sum"):
    if df.empty or col not in df.columns: return 0
    return df[col].sum() if agg == "sum" else df[col].mean()

total_cost    = _s(_c, "Cost (R$)")
total_leads   = _s(_c, "Conversions")
total_clicks  = _s(_c, "Clicks")
total_imp     = _s(_c, "Impressions")
cpa_geral     = total_cost / total_leads if total_leads > 0 else 0
ctr_geral     = (total_clicks / total_imp * 100) if total_imp > 0 else 0
cpc_geral     = total_cost / total_clicks if total_clicks > 0 else 0

# IS de Search (só campanhas Search com IS)
_search = _c[_c["Impr. Share (%)"].notna()] if not _c.empty and "Impr. Share (%)" in _c.columns else pd.DataFrame()
avg_is   = _search["Impr. Share (%)"].mean() if not _search.empty else None
avg_rank = _search["Lost IS Rank (%)"].mean() if not _search.empty and "Lost IS Rank (%)" in _search.columns else None
avg_bud  = _search["Lost IS Budget (%)"].mean() if not _search.empty and "Lost IS Budget (%)" in _search.columns else None

# GA4 canais — Whatsapp LP total
_ch = ga4_channels_df if not ga4_channels_df.empty else pd.DataFrame()
total_wpp = _s(_ch, "Whatsapp LP")
total_gl  = _s(_ch, "Generate Lead")
top_ch    = _ch.iloc[0]["Channel"] if not _ch.empty else "—"

# GA4 páginas — melhor página
_pg = ga4_pages_df if not ga4_pages_df.empty else pd.DataFrame()
best_page = _pg.iloc[0]["Page"] if not _pg.empty else "—"

# ── Insights dinâmicos ──
insights  = []
tests     = []
alerts    = []

if not _c.empty:
    # 1. CPA
    if cpa_geral > 0:
        if cpa_geral < 15:
            insights.append(f"**CPA de R$ {cpa_geral:.2f}** está excelente para leadgen de alto ticket (vestidos de noiva). Escale o orçamento com confiança.")
        elif cpa_geral < 30:
            insights.append(f"**CPA de R$ {cpa_geral:.2f}** está saudável. Foco em aumentar volume sem sacrificar eficiência.")
        else:
            alerts.append(f"**CPA de R$ {cpa_geral:.2f}** está elevado. Priorize otimização de landing page e negative keywords antes de escalar.")

    # 2. Impression Share
    if avg_is is not None:
        if avg_is < 20:
            alerts.append(f"**IS Search médio de {avg_is:.0f}%** é muito baixo — você está perdendo mais de 80% das impressões elegíveis.")
        if avg_rank and avg_rank > 60:
            alerts.append(f"**{avg_rank:.0f}% do IS perdido é por Rank** (qualidade/lance). Revisar Ad Strength, Quality Score e lances das campanhas Search é prioritário.")
        if avg_bud and avg_bud > 15:
            alerts.append(f"**{avg_bud:.0f}% do IS perdido é por Orçamento** — aumentar budget das campanhas Search pode capturar leads adicionais com o mesmo CPA.")

    # 3. PMax
    pmax = _c[_c["Campaign"].str.contains("Pmax|PMax|pmax", na=False)]
    if not pmax.empty:
        pmax_leads = pmax["Conversions"].sum()
        pmax_cost  = pmax["Cost (R$)"].sum()
        pmax_cpa   = pmax_cost / pmax_leads if pmax_leads > 0 else 0
        insights.append(f"**PMax** gerou {pmax_leads:.0f} leads a R$ {pmax_cpa:.2f} CPA. {'Excelente eficiência — considere aumentar o orçamento.' if pmax_cpa < cpa_geral else 'CPA acima da média — revise os sinais de audiência e assets.'}")

    # 4. Demand Gen
    dg = _c[_c["Campaign"].str.contains("demand|Demand|DG|YT", na=False)]
    if not dg.empty:
        dg_leads = dg["Conversions"].sum()
        dg_cost  = dg["Cost (R$)"].sum()
        dg_cpa   = dg_cost / dg_leads if dg_leads > 0 else 0
        insights.append(f"**Demand Gen / YT Retargeting** trouxe {dg_leads:.0f} leads a R$ {dg_cpa:.2f} CPA. {'Forte para retargeting — audiência qualificada convertendo bem.' if dg_cpa < 25 else 'CPA de topo de funil — avalie se o volume justifica o investimento vs Search.'}")

    # 5. CTR Search
    if ctr_geral < 6:
        alerts.append(f"**CTR médio de {ctr_geral:.1f}%** — anúncios podem estar pouco relevantes. Teste novos headlines com provas sociais (ex: '+ de 500 noivas atendidas', 'Atendimento personalizado').")
    elif ctr_geral > 10:
        insights.append(f"**CTR de {ctr_geral:.1f}%** excelente — os anúncios estão altamente relevantes para as buscas.")

# 6. Canais GA4
if not _ch.empty:
    if total_wpp > 0:
        insights.append(f"**{total_wpp:.0f} cliques no WhatsApp** são o principal CTA — garanta que o número está ativo, com mensagem automática de boas-vindas e tempo de resposta < 5 min.")
    cross = _ch[_ch["Channel"] == "Cross-network"]
    if not cross.empty:
        cross_sessions = cross.iloc[0]["Sessions"]
        total_sessions = _ch["Sessions"].sum()
        cross_pct = cross_sessions / total_sessions * 100 if total_sessions > 0 else 0
        if cross_pct > 40:
            insights.append(f"**Cross-network representa {cross_pct:.0f}% das sessões** — PMax e Demand Gen estão dominando o tráfego. Monitore a qualidade das sessões (tempo + engajamento).")

# ── Testes recomendados ──
tests = [
    ("🧪 Teste de Headlines com Prova Social", "Crie variações com '+ de X noivas atendidas', 'Coleção exclusiva SP', 'Vestidos sob medida em até 48h'. Headlines emocionais tendem a converter melhor em alto ticket B2C."),
    ("🧪 Segmentação por Intenção de Casamento", "Adicione audiences de 'Casamento em 6 meses' e 'Recentemente noiva' como observation layers no Search. Use como signal no PMax para alimentar o modelo."),
    ("🧪 Extensão de Imagem nas Campanhas Search", "Adicione imagens dos vestidos como assets nas campanhas Search ativas. Aumenta CTR em mobile e diferencia dos concorrentes."),
    ("🧪 Bid Strategy — Target CPA vs Maximize Conversions", "Se o volume de conversões > 30/mês por campanha, migre para Target CPA com valor 10-15% acima do CPA atual. Dê 2 semanas de fase de aprendizado."),
    ("🧪 Negative Keywords — Intenção de Compra Própria", "Adicione negative: 'aluguel', 'usado', 'segunda mão', 'barato', 'simples', 'grávida', 'debutante' para filtrar tráfego sem intenção premium."),
    ("🧪 Landing Page — A/B Teste de CTA", "Teste CTA 'Agendar visita' vs 'Falar com consultora' vs 'Ver coleção'. CTAs de baixo comprometimento tendem a converter mais no topo do funil."),
    ("🧪 Remarketing Dinâmico com Produto", "Configure feed de produtos com os vestidos (imagem + preço + categoria). Use no Demand Gen para exibir o vestido que a usuária visualizou — personalização aumenta taxa de retorno."),
    ("🧪 Call Extensions em Horário Comercial", "Ative extensão de chamada Seg-Sáb 10h-18h. Leads que ligam diretamente têm taxa de fechamento muito maior que leads digitais."),
]

# ── Layout ──
# Alertas
if alerts:
    st.markdown("#### ⚠️ Pontos de Atenção")
    for a in alerts:
        st.markdown(f"""
        <div style="background:#fff8e1;border-left:4px solid #d4af37;padding:0.7rem 1rem;border-radius:6px;margin-bottom:0.5rem;font-family:'Inter',sans-serif;font-size:0.88rem;">
        {a}
        </div>""", unsafe_allow_html=True)

# Insights positivos
if insights:
    st.markdown("#### ✅ Destaques do Período")
    for ins in insights:
        st.markdown(f"""
        <div style="background:#f0faf4;border-left:4px solid #27ae60;padding:0.7rem 1rem;border-radius:6px;margin-bottom:0.5rem;font-family:'Inter',sans-serif;font-size:0.88rem;">
        {ins}
        </div>""", unsafe_allow_html=True)

# Testes
st.markdown("#### 🔬 Testes Recomendados para o Próximo Período")
cols_t = st.columns(2)
for i, (title, desc) in enumerate(tests):
    with cols_t[i % 2]:
        st.markdown(f"""
        <div style="background:white;border:1px solid #e8e8e8;border-radius:10px;padding:0.9rem 1rem;margin-bottom:0.8rem;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
        <div style="font-family:'Inter',sans-serif;font-weight:600;font-size:0.85rem;color:#1a1a2e;margin-bottom:0.3rem;">{title}</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.8rem;color:#555;">{desc}</div>
        </div>""", unsafe_allow_html=True)

# =========================================================================
# FOOTER
# =========================================================================
st.markdown("---")
st.caption(
    f"Dashboard Inês Noivas Eternity | Google Ads 677-801-2588 + GA4 453035485 | "
    f"Período: Últimos {period} dias | Dados via Zapier MCP"
)

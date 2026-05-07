import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_service import (
    load_campaigns, load_adgroups,
    load_ga4_pages, load_ga4_daily, load_ga4_channels,
    load_ads_daily, load_keywords, load_meta, load_meta_creatives,
)

st.set_page_config(
    page_title="Inês Noivas Eternity | Dashboard",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded",
)

GOLD = "#d4af37"
NAVY = "#1a1a2e"
BLUE = "#0f3460"
LIGHT_BLUE = "#16213e"
RED = "#e74c3c"
GREEN = "#27ae60"
META_BLUE = "#1877F2"
META_PINK = "#E1306C"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    .main .block-container {{ padding-top: 1rem; max-width: 1400px; }}
    .dashboard-header {{
        background: linear-gradient(135deg, {NAVY} 0%, {LIGHT_BLUE} 50%, {BLUE} 100%);
        padding: 1.6rem 2rem; border-radius: 14px; margin-bottom: 1rem; color: white;
    }}
    .dashboard-header h1 {{
        font-family: 'Playfair Display', serif; font-size: 2rem; margin: 0; color: {GOLD};
    }}
    .dashboard-header p {{
        font-family: 'Inter', sans-serif; font-size: 0.9rem; color: #b8c5d6; margin: 0.25rem 0 0 0;
    }}
    .kpi {{
        background: white; border: 1px solid #ebebeb; border-radius: 12px;
        padding: 1rem 1.1rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        height: 100%;
    }}
    .kpi .kpi-label {{
        font-family: 'Inter', sans-serif; font-size: 0.7rem; font-weight: 600;
        color: #9ca3af; text-transform: uppercase; letter-spacing: 0.6px;
    }}
    .kpi .kpi-value {{
        font-family: 'Inter', sans-serif; font-size: 1.55rem; font-weight: 700;
        color: {NAVY}; margin-top: 0.1rem; line-height: 1.2;
    }}
    .kpi .kpi-sub {{
        font-family: 'Inter', sans-serif; font-size: 0.72rem; color: #9ca3af; margin-top: 0.1rem;
    }}
    .kpi.gold .kpi-value {{ color: {GOLD}; }}
    .kpi.green .kpi-value {{ color: {GREEN}; }}
    .kpi.red .kpi-value {{ color: {RED}; }}
    .kpi.meta .kpi-value {{ color: {META_BLUE}; }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {NAVY} 0%, {LIGHT_BLUE} 100%);
    }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    .sec {{
        font-family: 'Playfair Display', serif; font-size: 1.25rem; color: {NAVY};
        border-bottom: 2px solid {GOLD}; padding-bottom: 0.4rem; margin: 1.4rem 0 0.8rem 0;
    }}
    .alert-box {{
        background:#fff8e1; border-left:4px solid {GOLD}; padding:0.65rem 1rem;
        border-radius:0 8px 8px 0; margin:0.4rem 0;
        font-family:'Inter',sans-serif; font-size:0.85rem; color:#333;
    }}
    .ok-box {{
        background:#f0faf4; border-left:4px solid {GREEN}; padding:0.65rem 1rem;
        border-radius:0 8px 8px 0; margin:0.4rem 0;
        font-family:'Inter',sans-serif; font-size:0.85rem; color:#333;
    }}
    .test-card {{
        background:white; border:1px solid #e8e8e8; border-radius:10px;
        padding:0.85rem 1rem; margin-bottom:0.7rem;
        box-shadow:0 2px 6px rgba(0,0,0,0.04);
    }}
    .test-card .t-title {{
        font-family:'Inter',sans-serif; font-weight:600; font-size:0.82rem; color:{NAVY}; margin-bottom:0.25rem;
    }}
    .test-card .t-desc {{
        font-family:'Inter',sans-serif; font-size:0.78rem; color:#666;
    }}
    .no-data {{
        background:#f8f9fa; border:1px dashed #dee2e6; border-radius:10px;
        padding:2rem; text-align:center; font-family:'Inter',sans-serif; color:#6c757d;
    }}
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div class="dashboard-header">
    <h1>Inês Noivas Eternity</h1>
    <p>Dashboard de Performance &nbsp;|&nbsp; Google Ads · GA4 · Meta &nbsp;|&nbsp; Geração de Leads</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### Período")
    period = st.radio(
        "Analisar os últimos:",
        options=[7, 14, 30, 90],
        format_func=lambda x: f"{x} dias",
        index=2,
    )
    st.markdown("---")
    st.markdown("**Cliente:** Inês Noivas Eternity")
    st.markdown("**Google Ads:** 677-801-2588")
    st.markdown("**GA4:** 453035485")
    st.markdown("---")
    st.markdown("*Dados via Zapier MCP*")


def kpi(label, value, style="", sub=""):
    sub_html = f"<div class='kpi-sub'>{sub}</div>" if sub else ""
    return f'<div class="kpi {style}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{sub_html}</div>'


def sec(title):
    st.markdown(f'<div class="sec">{title}</div>', unsafe_allow_html=True)


# ── Load data ──
campaigns_df   = load_campaigns(period)
adgroups_df    = load_adgroups(period)
ga4_pages_df   = load_ga4_pages(period)
ga4_daily_df   = load_ga4_daily(period)
ga4_channels_df = load_ga4_channels(period)
ads_daily_df   = load_ads_daily(period)
keywords_df        = load_keywords(period)
meta_df            = load_meta(period)
meta_creatives_df  = load_meta_creatives(period)

# ── Main tabs ──
tab_google, tab_ga4, tab_meta = st.tabs([
    "📊  Google Ads",
    "🌐  GA4 — Site",
    "📱  Meta (Instagram & Facebook)",
])


# =============================================================================
# TAB 1 — GOOGLE ADS
# =============================================================================
with tab_google:

    if campaigns_df.empty:
        st.markdown('<div class="no-data"><b>Sem dados para este período.</b><br>Peça ao Claude Code: <i>"Atualize os dados do dashboard"</i></div>', unsafe_allow_html=True)
        st.stop()

    active = campaigns_df[campaigns_df["Status"] != "REMOVED"]
    total_cost   = active["Cost (R$)"].sum()
    total_leads  = active["Conversions"].sum()
    total_clicks = active["Clicks"].sum()
    total_imp    = active["Impressions"].sum()
    cpl          = total_cost / total_leads if total_leads > 0 else 0
    ctr          = total_clicks / total_imp * 100 if total_imp > 0 else 0
    cpc          = total_cost / total_clicks if total_clicks > 0 else 0

    # ── KPIs ──
    c = st.columns(6)
    c[0].markdown(kpi("💰 Investimento",   f"R$ {total_cost:,.0f}"),        unsafe_allow_html=True)
    c[1].markdown(kpi("🎯 Leads",           f"{total_leads:,.0f}", "gold"),  unsafe_allow_html=True)
    c[2].markdown(kpi("💡 Custo por Lead",  f"R$ {cpl:,.2f}", "gold"),       unsafe_allow_html=True)
    c[3].markdown(kpi("🖱️ Cliques",         f"{total_clicks:,}"),            unsafe_allow_html=True)
    c[4].markdown(kpi("📈 CTR",             f"{ctr:.1f}%"),                  unsafe_allow_html=True)
    c[5].markdown(kpi("💲 CPC Médio",       f"R$ {cpc:,.2f}"),               unsafe_allow_html=True)

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    # ── Parcela de Impressões ──
    is_data = active[active["Impr. Share (%)"].notna()].copy() if "Impr. Share (%)" in active.columns else pd.DataFrame()
    if not is_data.empty:
        sec("Parcela de Impressões — quantas buscas estamos aparecendo?")
        st.caption("Mostra, das pessoas que buscaram no Google, em quantas (%) aparecemos. O restante são oportunidades perdidas.")

        col1, col2 = st.columns([3, 2])
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(y=is_data["Campaign"], x=is_data["Impr. Share (%)"],
                name="Aparecemos ✅", marker_color=GREEN, orientation="h"))
            fig.add_trace(go.Bar(y=is_data["Campaign"], x=is_data.get("Lost IS Budget (%)", 0),
                name="Perdido (orçamento) 💰", marker_color=GOLD, orientation="h"))
            fig.add_trace(go.Bar(y=is_data["Campaign"], x=is_data.get("Lost IS Rank (%)", 0),
                name="Perdido (qualidade/lance) ⚠️", marker_color="#d1d5db", orientation="h"))
            fig.update_layout(barmode="stack", template="plotly_white",
                height=260, margin=dict(t=10, b=20, l=10),
                legend=dict(orientation="h", y=1.18),
                xaxis=dict(title="% das buscas", range=[0, 105]))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(
                is_data[["Campaign","Impr. Share (%)","Lost IS Budget (%)","Lost IS Rank (%)"]].style.format({
                    "Impr. Share (%)": "{:.0f}%", "Lost IS Budget (%)": "{:.0f}%", "Lost IS Rank (%)": "{:.0f}%"
                }, na_rep="—"),
                use_container_width=True, hide_index=True, height=260,
            )

    # ── Campanhas ──
    sec("Performance por Campanha")
    camp_cols = ["Campaign","Cost (R$)","Conversions","Cost/Conv (R$)","Clicks","CTR (%)","CPC (R$)","Impressions"]
    camp_available = [c for c in camp_cols if c in active.columns]
    st.dataframe(
        active[camp_available].sort_values("Conversions", ascending=False).style.format({
            "Cost (R$)": "R$ {:.2f}", "Conversions": "{:.1f}", "Cost/Conv (R$)": "R$ {:.2f}",
            "Clicks": "{:,.0f}", "CTR (%)": "{:.1f}%", "CPC (R$)": "R$ {:.2f}", "Impressions": "{:,.0f}",
        }, na_rep="—"),
        use_container_width=True, hide_index=True, height=220,
    )

    # ── Grupos de Anúncios ──
    if not adgroups_df.empty:
        sec("Performance por Grupo de Anúncios")
        ag_cols = ["Ad Group","Campaign","Cost (R$)","Conversions","Cost/Conv (R$)","Clicks","CTR (%)","CPC (R$)"]
        ag_av = [c for c in ag_cols if c in adgroups_df.columns]
        col1, col2 = st.columns([3, 2])
        with col1:
            st.dataframe(
                adgroups_df[ag_av].sort_values("Conversions", ascending=False).style.format({
                    "Cost (R$)": "R$ {:.2f}", "Conversions": "{:.1f}", "Cost/Conv (R$)": "R$ {:.2f}",
                    "Clicks": "{:,.0f}", "CTR (%)": "{:.1f}%", "CPC (R$)": "R$ {:.2f}",
                }, na_rep="—"),
                use_container_width=True, hide_index=True,
            )
        with col2:
            fig = px.bar(
                adgroups_df.sort_values("Conversions", ascending=True),
                x="Conversions", y="Ad Group", orientation="h",
                color="Cost/Conv (R$)", color_continuous_scale=[[0, GREEN],[0.5, GOLD],[1, RED]],
            )
            fig.update_layout(height=280, margin=dict(t=10,b=20), template="plotly_white",
                yaxis_title="", xaxis_title="Leads gerados", coloraxis_colorbar_title="R$/Lead")
            st.plotly_chart(fig, use_container_width=True)

    # ── Keywords ──
    if not keywords_df.empty:
        sec("Palavras-chave que mais geraram leads")
        kw_display = keywords_df[keywords_df["Conversões"] > 0].copy() if "Conversões" in keywords_df.columns else pd.DataFrame()
        if not kw_display.empty:
            col1, col2 = st.columns([3, 2])
            with col1:
                kw_cols = ["Palavra-chave","Conversões","Cliques","CTR (%)","CPC (R$)","Custo (R$)","Custo/Conv (R$)"]
                kw_av = [c for c in kw_cols if c in kw_display.columns]
                st.dataframe(
                    kw_display[kw_av].sort_values("Conversões", ascending=False).style.format({
                        "Conversões": "{:.1f}", "Cliques": "{:,.0f}", "CTR (%)": "{:.1f}%",
                        "CPC (R$)": "R$ {:.2f}", "Custo (R$)": "R$ {:.2f}", "Custo/Conv (R$)": "R$ {:.2f}",
                    }, na_rep="—"),
                    use_container_width=True, hide_index=True,
                )
            with col2:
                top10 = kw_display.nlargest(10, "Conversões")
                fig = go.Figure(go.Bar(
                    y=top10["Palavra-chave"], x=top10["Conversões"], orientation="h",
                    marker_color=GOLD, text=[f'{v:.0f}' for v in top10["Conversões"]], textposition="auto",
                ))
                fig.update_layout(height=350, margin=dict(t=10,b=20,l=10), template="plotly_white",
                    yaxis=dict(autorange="reversed"), xaxis_title="Leads")
                st.plotly_chart(fig, use_container_width=True)

    # ── Tendência Diária ──
    if not ads_daily_df.empty:
        sec("Tendência Diária")
        daily = ads_daily_df.copy()
        t1, t2, t3 = st.tabs(["Investimento & Leads", "Cliques & Impressões", "CTR & CPC"])

        with t1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=daily["Date"], y=daily["Cost (R$)"],
                name="Investimento (R$)", marker_color=NAVY, opacity=0.55, yaxis="y",
                hovertemplate="R$ %{y:,.2f}<extra></extra>"))
            fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Conversions"],
                name="Leads", line=dict(color=GOLD, width=3), yaxis="y2",
                hovertemplate="%{y:.0f} leads<extra></extra>"))
            if "Cost/Lead (R$)" in daily.columns:
                fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Cost/Lead (R$)"],
                    name="Custo/Lead", line=dict(color=RED, width=2, dash="dot"), yaxis="y2",
                    hovertemplate="R$ %{y:.2f}<extra></extra>"))
            fig.update_layout(template="plotly_white", height=340, margin=dict(t=20,b=30),
                yaxis=dict(title="Investimento (R$)", tickprefix="R$ "),
                yaxis2=dict(overlaying="y", side="right", title="Leads / Custo/Lead"),
                legend=dict(orientation="h", y=1.12))
            st.plotly_chart(fig, use_container_width=True)

        with t2:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=daily["Date"], y=daily["Impressions"],
                name="Impressões", marker_color=NAVY, opacity=0.45, yaxis="y"))
            fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Clicks"],
                name="Cliques", line=dict(color=GOLD, width=3), yaxis="y2"))
            fig.update_layout(template="plotly_white", height=340, margin=dict(t=20,b=30),
                yaxis=dict(title="Impressões"), yaxis2=dict(overlaying="y", side="right", title="Cliques"),
                legend=dict(orientation="h", y=1.12))
            st.plotly_chart(fig, use_container_width=True)

        with t3:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily["Date"], y=daily["CTR (%)"],
                name="CTR (%)", line=dict(color=GOLD, width=3), yaxis="y"))
            fig.add_trace(go.Scatter(x=daily["Date"], y=daily["CPC (R$)"],
                name="CPC (R$)", line=dict(color=BLUE, width=2), yaxis="y2"))
            fig.update_layout(template="plotly_white", height=340, margin=dict(t=20,b=30),
                yaxis=dict(title="CTR (%)", ticksuffix="%"),
                yaxis2=dict(title="CPC (R$)", tickprefix="R$ ", overlaying="y", side="right"),
                legend=dict(orientation="h", y=1.12))
            st.plotly_chart(fig, use_container_width=True)

    # ── Análise & Recomendações ──
    sec("Destaques & Recomendações")

    _c = active.copy()
    cpa_g = total_cost / total_leads if total_leads > 0 else 0
    insights, alerts, tests = [], [], []

    if cpa_g > 0:
        if cpa_g < 15:
            insights.append(f"<b>Custo por lead de R$ {cpa_g:.2f}</b> — excelente para vestidos de noiva. Podemos aumentar o investimento com segurança.")
        elif cpa_g < 30:
            insights.append(f"<b>Custo por lead de R$ {cpa_g:.2f}</b> — saudável. Foco em aumentar volume mantendo eficiência.")
        else:
            alerts.append(f"<b>Custo por lead de R$ {cpa_g:.2f}</b> — acima do ideal. Recomendo revisar os anúncios e a página de destino antes de aumentar o investimento.")

    if not is_data.empty:
        avg_is = is_data["Impr. Share (%)"].mean()
        avg_rank = is_data["Lost IS Rank (%)"].mean() if "Lost IS Rank (%)" in is_data.columns else 0
        avg_bud = is_data["Lost IS Budget (%)"].mean() if "Lost IS Budget (%)" in is_data.columns else 0
        if avg_is < 25:
            alerts.append(f"<b>Estamos aparecendo em apenas {avg_is:.0f}% das buscas elegíveis</b> — há muito espaço para crescer captando mais leads com o mesmo público.")
        if avg_rank and avg_rank > 60:
            alerts.append(f"<b>{avg_rank:.0f}% das impressões perdidas são por qualidade/lance</b> — melhorar os anúncios pode aumentar muito o volume de leads sem aumentar custo.")
        if avg_bud and avg_bud > 15:
            alerts.append(f"<b>{avg_bud:.0f}% das impressões perdidas são por orçamento</b> — aumentar o budget diário pode capturar mais leads a um CPA similar.")

    pmax = _c[_c["Campaign"].str.contains("Pmax|PMax|pmax", na=False)]
    if not pmax.empty and pmax["Conversions"].sum() > 0:
        pc = pmax["Cost (R$)"].sum() / pmax["Conversions"].sum()
        insights.append(f"<b>PMax gerou {pmax['Conversions'].sum():.0f} leads a R$ {pc:.2f} cada</b> — {'ótima eficiência, considere aumentar o orçamento.' if pc < cpa_g else 'custo acima da média, vale revisar os criativos.'}")

    dg = _c[_c["Campaign"].str.contains("demand|Demand|YT", na=False)]
    if not dg.empty and dg["Conversions"].sum() > 0:
        dc = dg["Cost (R$)"].sum() / dg["Conversions"].sum()
        insights.append(f"<b>Remarketing (YouTube/Demand Gen) gerou {dg['Conversions'].sum():.0f} leads a R$ {dc:.2f}</b> — {'recuperando visitantes com boa eficiência.' if dc < 30 else 'avalie se o volume justifica o investimento.'}")

    if ctr < 5:
        alerts.append(f"<b>CTR de {ctr:.1f}%</b> — os anúncios podem estar pouco chamativos. Teste textos com provas sociais como '500+ noivas atendidas' ou 'Coleção exclusiva SP'.")

    tests = [
        ("🧪 Textos com provas sociais", "Teste variações de anúncio com '+ de 500 noivas atendidas', 'Coleção exclusiva SP' e 'Atendimento personalizado'. Textos emocionais convertem melhor para compras de alto valor."),
        ("🧪 Audiências por momento de vida", "Adicione públicos como 'Noivou recentemente' e 'Casamento em 6 meses' nas campanhas. Quem está próximo ao casamento tem urgência maior."),
        ("🧪 Imagens dos vestidos nos anúncios Search", "Adicione fotos dos vestidos como extensão de imagem nas campanhas de busca. Diferencia dos concorrentes e aumenta o clique."),
        ("🧪 Meta junto ao Google Search", "Testar anúncios no Instagram/Facebook sincronizados com Google pode aumentar lembrança de marca e reduzir o custo por lead total."),
        ("🧪 Filtrar público sem perfil de compra", "Adicione palavras-chave negativas: 'aluguel', 'usado', 'barato', 'debutante'. Isso concentra o orçamento em quem quer comprar."),
        ("🧪 Teste de CTA na página do site", "Teste 'Agendar visita' vs 'Falar com consultora' como botão principal. CTAs de baixo comprometimento costumam converter mais."),
    ]

    if alerts:
        st.markdown("##### ⚠️ Pontos de Atenção")
        for a in alerts:
            st.markdown(f'<div class="alert-box">{a}</div>', unsafe_allow_html=True)

    if insights:
        st.markdown("##### ✅ Destaques do Período")
        for i in insights:
            st.markdown(f'<div class="ok-box">{i}</div>', unsafe_allow_html=True)

    st.markdown("##### 🔬 Testes Recomendados para o Próximo Período")
    cols_t = st.columns(2)
    for i, (title, desc) in enumerate(tests):
        with cols_t[i % 2]:
            st.markdown(f'<div class="test-card"><div class="t-title">{title}</div><div class="t-desc">{desc}</div></div>', unsafe_allow_html=True)


# =============================================================================
# TAB 2 — GA4 (SITE)
# =============================================================================
with tab_ga4:

    if ga4_daily_df.empty and ga4_channels_df.empty and ga4_pages_df.empty:
        st.markdown('<div class="no-data"><b>Sem dados de GA4 para este período.</b><br>Peça ao Claude Code: <i>"Atualize os dados do dashboard"</i></div>', unsafe_allow_html=True)
    else:
        # ── KPIs ──
        if not ga4_daily_df.empty:
            tot_sessions  = ga4_daily_df["Sessions"].sum() if "Sessions" in ga4_daily_df.columns else 0
            tot_users     = ga4_daily_df["Users"].sum() if "Users" in ga4_daily_df.columns else 0
            avg_eng       = ga4_daily_df["Engagement Rate (%)"].mean() if "Engagement Rate (%)" in ga4_daily_df.columns else 0
            avg_bounce    = ga4_daily_df["Bounce Rate (%)"].mean() if "Bounce Rate (%)" in ga4_daily_df.columns else 0
            avg_session_s = ga4_daily_df["Avg. Session (s)"].mean() if "Avg. Session (s)" in ga4_daily_df.columns else 0
            session_fmt   = f"{int(avg_session_s // 60)}m {int(avg_session_s % 60)}s" if avg_session_s > 0 else "—"

            c = st.columns(5)
            c[0].markdown(kpi("👥 Visitas ao Site", f"{tot_sessions:,}", sub="sessões no período"), unsafe_allow_html=True)
            c[1].markdown(kpi("🙋 Pessoas Únicas", f"{tot_users:,}", sub="usuários distintos"), unsafe_allow_html=True)
            c[2].markdown(kpi("⏱️ Tempo Médio", session_fmt, sub="por sessão"), unsafe_allow_html=True)
            c[3].markdown(kpi("💬 Engajamento", f"{avg_eng:.0f}%", "green" if avg_eng > 60 else "",
                sub="ficaram e interagiram"), unsafe_allow_html=True)
            c[4].markdown(kpi("🚪 Saíram Sem Interagir", f"{avg_bounce:.0f}%",
                "red" if avg_bounce > 40 else "green", sub="bounce rate médio"), unsafe_allow_html=True)

        # ── Performance por Página ──
        if not ga4_pages_df.empty:
            sec("Performance por Página — onde as pessoas convertem?")
            st.caption("Whatsapp LP = cliques no botão de WhatsApp da página. Generate Lead = formulário de lead preenchido.")

            has_ev = "Whatsapp LP" in ga4_pages_df.columns
            has_sess = "Avg. Session (s)" in ga4_pages_df.columns
            col1, col2 = st.columns([3, 2])
            with col1:
                pg_fmt = {"Pageviews": "{:,.0f}"}
                pg_cols = ["Page","Pageviews"]
                if has_sess:
                    pg_cols.append("Avg. Session (s)")
                    pg_fmt["Avg. Session (s)"] = "{:.0f}s"
                if has_ev:
                    pg_cols += ["Whatsapp LP","Generate Lead"]
                    pg_fmt.update({"Whatsapp LP": "{:,.0f}", "Generate Lead": "{:,.0f}"})
                pg_av = [c for c in pg_cols if c in ga4_pages_df.columns]
                st.dataframe(
                    ga4_pages_df[pg_av].sort_values("Pageviews", ascending=False).style.format(
                        {k: v for k, v in pg_fmt.items() if k in pg_av}, na_rep="—"),
                    use_container_width=True, hide_index=True,
                )
            with col2:
                if has_sess:
                    sess_data = ga4_pages_df[ga4_pages_df["Avg. Session (s)"] > 0].sort_values("Avg. Session (s)", ascending=True).tail(10)
                    if not sess_data.empty:
                        fig = go.Figure(go.Bar(
                            y=sess_data["Page"], x=sess_data["Avg. Session (s)"], orientation="h",
                            marker_color=BLUE,
                            text=[f"{int(v//60)}m{int(v%60)}s" for v in sess_data["Avg. Session (s)"]],
                            textposition="auto",
                        ))
                        fig.update_layout(height=300, margin=dict(t=10,b=20,l=10), template="plotly_white",
                            xaxis_title="Tempo médio (s)", yaxis_title="")
                        st.plotly_chart(fig, use_container_width=True)
                elif has_ev:
                    ev_ch = ga4_pages_df[ga4_pages_df["Whatsapp LP"] > 0].sort_values("Whatsapp LP", ascending=True)
                    if not ev_ch.empty:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(y=ev_ch["Page"], x=ev_ch["Whatsapp LP"],
                            name="WhatsApp", marker_color=GREEN, orientation="h"))
                        if ev_ch["Generate Lead"].sum() > 0:
                            fig.add_trace(go.Bar(y=ev_ch["Page"], x=ev_ch["Generate Lead"],
                                name="Lead (form)", marker_color=GOLD, orientation="h"))
                        fig.update_layout(barmode="group", height=280, margin=dict(t=10,b=20),
                            template="plotly_white", legend=dict(orientation="h", y=1.1),
                            xaxis_title="Conversões")
                        st.plotly_chart(fig, use_container_width=True)

        # ── Mix de Canais ──
        if not ga4_channels_df.empty:
            sec("De onde vêm as visitas?")
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(ga4_channels_df, values="Sessions", names="Channel", hole=0.45,
                    color_discrete_sequence=[GOLD, NAVY, BLUE, GREEN, RED, "#9b59b6", "#f39c12"])
                fig.update_layout(height=300, margin=dict(t=20, b=20))
                fig.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                ch_cols = ["Channel","Sessions","Users"]
                if "Whatsapp LP" in ga4_channels_df.columns:
                    ch_cols += ["Whatsapp LP","Generate Lead"]
                ch_av = [c for c in ch_cols if c in ga4_channels_df.columns]
                ch_fmt = {}
                if "Engagement Rate (%)" in ga4_channels_df.columns:
                    ch_av.append("Engagement Rate (%)")
                    ch_fmt["Engagement Rate (%)"] = "{:.0f}%"
                st.dataframe(
                    ga4_channels_df[ch_av].sort_values("Sessions", ascending=False).style.format(ch_fmt, na_rep="—"),
                    use_container_width=True, hide_index=True, height=300,
                )


# =============================================================================
# TAB 3 — META
# =============================================================================
with tab_meta:

    if meta_df.empty:
        st.markdown("""
        <div class="no-data">
            <div style="font-size:2rem;margin-bottom:0.5rem">📱</div>
            <b style="font-size:1rem">Dados do Meta ainda não conectados</b><br><br>
            Para ativar esta aba, peça ao Claude Code:<br>
            <i>"Adicione os dados do Meta Ads ao dashboard"</i><br><br>
            <div style="font-size:0.82rem;color:#9ca3af;margin-top:0.5rem">
            Métricas que serão exibidas quando conectado:<br>
            Investimento · Impressões · Alcance · CTR · Cliques no Link ·<br>
            Custo por Mensagem no WhatsApp · Custo por Visita ao Perfil · Seguidores Novos
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── KPIs Meta ──
        def _m(col): return meta_df[col].sum() if col in meta_df.columns else 0
        def _ma(col): return meta_df[col].mean() if col in meta_df.columns else 0

        meta_cost   = _m("Investimento (R$)")
        meta_imp    = _m("Impressões")
        meta_reach  = _m("Alcance")
        meta_clicks = _m("Cliques no Link")
        meta_ctr    = _ma("CTR (%)")
        meta_cpc    = meta_cost / meta_clicks if meta_clicks > 0 else 0
        meta_msgs   = _m("Mensagens WhatsApp")
        meta_cpm    = meta_cost / meta_msgs if meta_msgs > 0 else 0
        meta_prof   = _m("Visitas ao Perfil")
        meta_cpp    = meta_cost / meta_prof if meta_prof > 0 else 0
        meta_follow = _m("Seguidores Novos")
        meta_cpf    = meta_cost / meta_follow if meta_follow > 0 else 0

        c = st.columns(5)
        c[0].markdown(kpi("💰 Investimento", f"R$ {meta_cost:,.0f}", "meta"), unsafe_allow_html=True)
        c[1].markdown(kpi("👁️ Impressões", f"{meta_imp:,.0f}", sub="vezes exibido"), unsafe_allow_html=True)
        c[2].markdown(kpi("🎯 Alcance", f"{meta_reach:,.0f}", sub="pessoas únicas"), unsafe_allow_html=True)
        c[3].markdown(kpi("💬 Mensagens WhatsApp", f"{meta_msgs:,.0f}", "gold"), unsafe_allow_html=True)
        c[4].markdown(kpi("💲 Custo/Mensagem", f"R$ {meta_cpm:.2f}" if meta_msgs > 0 else "—", "gold", sub="por conversa iniciada"), unsafe_allow_html=True)

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

        c = st.columns(4)
        c[0].markdown(kpi("🖱️ Cliques no Link", f"{meta_clicks:,.0f}", sub=f"R$ {meta_cpc:.2f} por clique"), unsafe_allow_html=True)
        c[1].markdown(kpi("📈 CTR", f"{meta_ctr:.1f}%", sub="taxa de clique no link"), unsafe_allow_html=True)
        c[2].markdown(kpi("📸 Visitas ao Perfil", f"{meta_prof:,.0f}", sub=f"R$ {meta_cpp:.2f} por visita"), unsafe_allow_html=True)
        c[3].markdown(kpi("➕ Curtidas / Engajamento", f"{meta_follow:,.0f}", "green", sub="novas curtidas na página"), unsafe_allow_html=True)

        # ── Performance por Conjunto de Anúncios ──
        if "Conjunto" in meta_df.columns:
            sec("Performance por Conjunto de Anúncios")
            sum_cols = [c for c in ["Investimento (R$)","Impressões","Alcance","Cliques no Link",
                                    "Mensagens WhatsApp","Visitas ao Perfil","Seguidores Novos","Engajamento"]
                        if c in meta_df.columns]
            meta_grouped = meta_df.groupby("Conjunto")[sum_cols].sum().reset_index()
            if "Cliques no Link" in meta_grouped.columns and "Impressões" in meta_grouped.columns:
                meta_grouped["CTR (%)"] = (meta_grouped["Cliques no Link"] / meta_grouped["Impressões"] * 100).round(2)
            meta_fmt = {"Investimento (R$)": "R$ {:.2f}", "CTR (%)": "{:.1f}%",
                        "Impressões": "{:,.0f}", "Alcance": "{:,.0f}",
                        "Cliques no Link": "{:,.0f}", "Mensagens WhatsApp": "{:,.0f}",
                        "Visitas ao Perfil": "{:,.0f}", "Engajamento": "{:,.0f}"}
            disp_cols = ["Conjunto"] + [c for c in ["Investimento (R$)","Impressões","Alcance","CTR (%)","Cliques no Link",
                                                     "Mensagens WhatsApp","Visitas ao Perfil","Engajamento"]
                                        if c in meta_grouped.columns]
            st.dataframe(
                meta_grouped[disp_cols].sort_values("Investimento (R$)", ascending=False).style.format(
                    {k: v for k, v in meta_fmt.items() if k in meta_grouped.columns}, na_rep="—"),
                use_container_width=True, hide_index=True,
            )

        # ── Tendência Diária Meta ──
        if "Data" in meta_df.columns and "Investimento (R$)" in meta_df.columns:
            sec("Tendência Diária — Meta")
            daily_meta = meta_df.groupby("Data")[["Investimento (R$)","Cliques no Link","Mensagens WhatsApp"]].sum().reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=daily_meta["Data"], y=daily_meta["Investimento (R$)"],
                name="Investimento", marker_color=META_BLUE, opacity=0.55, yaxis="y"))
            if "Mensagens WhatsApp" in daily_meta.columns:
                fig.add_trace(go.Scatter(x=daily_meta["Data"], y=daily_meta["Mensagens WhatsApp"],
                    name="Mensagens WhatsApp", line=dict(color=META_PINK, width=3), yaxis="y2"))
            fig.update_layout(template="plotly_white", height=320, margin=dict(t=20,b=30),
                yaxis=dict(title="Investimento (R$)", tickprefix="R$ "),
                yaxis2=dict(title="Mensagens", overlaying="y", side="right"),
                legend=dict(orientation="h", y=1.12))
            st.plotly_chart(fig, use_container_width=True)

        # ── Criativos que Melhor Performaram ──
        if not meta_creatives_df.empty:
            sec("Criativos que Melhor Performaram")
            st.caption("Anúncios com mais mensagens WhatsApp iniciadas no período — os criativos que realmente convertem.")
            sum_cols_cr = [c for c in ["Investimento (R$)","Impressões","Alcance","Cliques no Link",
                                       "Mensagens WhatsApp","Engajamento"] if c in meta_creatives_df.columns]
            cr_grouped = meta_creatives_df.groupby("Anúncio")[sum_cols_cr].sum().reset_index()
            if "Investimento (R$)" in cr_grouped.columns and "Mensagens WhatsApp" in cr_grouped.columns:
                cr_grouped["Custo/Mensagem (R$)"] = (
                    cr_grouped["Investimento (R$)"] / cr_grouped["Mensagens WhatsApp"].replace(0, float("nan"))
                ).round(2)
            if "Cliques no Link" in cr_grouped.columns and "Impressões" in cr_grouped.columns:
                cr_grouped["CTR (%)"] = (cr_grouped["Cliques no Link"] / cr_grouped["Impressões"].replace(0, float("nan")) * 100).round(2)

            cr_display = cr_grouped[cr_grouped["Mensagens WhatsApp"] > 0].sort_values("Mensagens WhatsApp", ascending=False).head(15)

            col1, col2 = st.columns([3, 2])
            with col1:
                cr_cols = ["Anúncio","Mensagens WhatsApp","Custo/Mensagem (R$)","Investimento (R$)","Impressões","CTR (%)","Engajamento"]
                cr_av = [c for c in cr_cols if c in cr_display.columns]
                cr_fmt = {"Mensagens WhatsApp": "{:.0f}", "Custo/Mensagem (R$)": "R$ {:.2f}",
                          "Investimento (R$)": "R$ {:.2f}", "Impressões": "{:,.0f}", "CTR (%)": "{:.1f}%",
                          "Engajamento": "{:,.0f}"}
                st.dataframe(
                    cr_display[cr_av].style.format({k: v for k, v in cr_fmt.items() if k in cr_av}, na_rep="—"),
                    use_container_width=True, hide_index=True,
                )
            with col2:
                if not cr_display.empty:
                    top8 = cr_display.head(8).copy()
                    top8["Anúncio_short"] = top8["Anúncio"].str[-40:]
                    fig = go.Figure(go.Bar(
                        y=top8["Anúncio_short"], x=top8["Mensagens WhatsApp"], orientation="h",
                        marker_color=META_PINK, text=top8["Mensagens WhatsApp"].astype(int).astype(str),
                        textposition="auto",
                    ))
                    fig.update_layout(height=320, margin=dict(t=10,b=20,l=10), template="plotly_white",
                        yaxis=dict(autorange="reversed"), xaxis_title="Mensagens iniciadas")
                    st.plotly_chart(fig, use_container_width=True)

        # ── Destaques & Recomendações Meta ──
        sec("Destaques & Recomendações — Meta")
        meta_insights, meta_alerts, meta_tests = [], [], []

        if meta_cost > 0 and meta_msgs > 0:
            cpm_val = meta_cost / meta_msgs
            if cpm_val < 10:
                meta_insights.append(f"<b>Custo por mensagem de R$ {cpm_val:.2f}</b> — excelente para o segmento de noivas. Escalar investimento pode gerar volume maior a custo similar.")
            elif cpm_val < 25:
                meta_insights.append(f"<b>Custo por mensagem de R$ {cpm_val:.2f}</b> — saudável. Foco em testar criativos para reduzir ainda mais.")
            else:
                meta_alerts.append(f"<b>Custo por mensagem de R$ {cpm_val:.2f}</b> — acima do ideal. Revisar criativos e públicos pode reduzir significativamente.")

        if meta_ctr > 0:
            if meta_ctr > 3:
                meta_insights.append(f"<b>CTR de {meta_ctr:.1f}%</b> — acima da média do setor. Os criativos estão gerando interesse real.")
            elif meta_ctr < 1:
                meta_alerts.append(f"<b>CTR de {meta_ctr:.1f}%</b> — baixo. Os criativos precisam de revisão — teste imagens dos vestidos com provas sociais.")

        if meta_reach > 0 and meta_imp > 0:
            freq = meta_imp / meta_reach
            if freq > 5:
                meta_alerts.append(f"<b>Frequência média de {freq:.1f}x</b> — o público está saturado. Expandir audiências ou renovar criativos evita fadiga.")
            elif freq < 2:
                meta_insights.append(f"<b>Frequência de {freq:.1f}x</b> — audiência fresca, há espaço para aumentar o orçamento sem saturar.")

        meta_tests = [
            ("🧪 Vídeos curtos de vestidos (Reels)", "Teste criativos de 15-30s mostrando os vestidos em movimento. Reels têm CPM mais barato e alto engajamento para moda nupcial."),
            ("🧪 Depoimentos de noivas", "Anúncios com noivas reais contando sua experiência geram alta confiança e reduzem o custo por mensagem."),
            ("🧪 Oferta de consulta gratuita", "CTA 'Agende sua visita gratuita' com urgência limitada (ex.: 'apenas 5 vagas') pode aumentar a taxa de conversão em cliques para mensagem."),
            ("🧪 Público lookalike de clientes", "Criar lookalike a partir da lista de clientes que fecharam negócio tende a ser mais eficiente que lookalike de visitantes do site."),
        ]

        if meta_alerts:
            st.markdown("##### ⚠️ Pontos de Atenção")
            for a in meta_alerts:
                st.markdown(f'<div class="alert-box">{a}</div>', unsafe_allow_html=True)

        if meta_insights:
            st.markdown("##### ✅ Destaques do Período")
            for i in meta_insights:
                st.markdown(f'<div class="ok-box">{i}</div>', unsafe_allow_html=True)

        st.markdown("##### 🔬 Testes Recomendados")
        cols_mt = st.columns(2)
        for i, (title, desc) in enumerate(meta_tests):
            with cols_mt[i % 2]:
                st.markdown(f'<div class="test-card"><div class="t-title">{title}</div><div class="t-desc">{desc}</div></div>', unsafe_allow_html=True)

# ── Footer ──
st.markdown("---")
st.caption(f"Dashboard Inês Noivas Eternity · Google Ads 677-801-2588 · GA4 453035485 · Últimos {period} dias · Dados via Zapier MCP")

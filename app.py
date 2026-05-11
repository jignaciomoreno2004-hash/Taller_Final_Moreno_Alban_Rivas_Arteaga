# ─── Librerías ───────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ─── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    layout="wide", 
    page_title="Marketing Intelligence Dashboard", 
    page_icon="chart_with_upwards_trend"
)

# ─── Paleta corporativa ───────────────────────────────────────────────────────
PALETTE = {
    "vino":        "#7B2D8B",   # violeta vino
    "dorado":      "#C9962B",   # dorado
    "coral":       "#E05C4B",   # coral
    "verde":       "#3A8C6E",   # verde
    "gris_claro":  "#D6D6D6",   # gris claro
    "gris_oscuro": "#4A4A4A",   # gris oscuro
    "fondo":       "#FAFAF8",   # blanco cálido
}

# ─── Carga y limpieza de datos ────────────────────────────────────────────────
@st.cache_data
def load_data():
    # Carga con ruta relativa
    df = pd.read_csv("marketing_campaign.csv", sep="\t" if "\t" in open("marketing_campaign.csv").read(1024) else ",")
    
    # 1. Eliminar nulos en Income
    df = df.dropna(subset=["Income"])
    
    # 2. Transformaciones
    df["Age"] = 2024 - df["Year_Birth"]
    df["TotalKids"] = df["Kidhome"] + df["Teenhome"]
    df["TotalSpend"] = (
        df["MntWines"] + df["MntFruits"] + df["MntMeatProducts"] + 
        df["MntFishProducts"] + df["MntSweetProducts"] + df["MntGoldProds"]
    )
    df["TotalCampaigns"] = (
        df["AcceptedCmp1"] + df["AcceptedCmp2"] + df["AcceptedCmp3"] + 
        df["AcceptedCmp4"] + df["AcceptedCmp5"] + df["Response"]
    )
    
    # 3. Unificar Marital_Status
    df["Marital_Status"] = df["Marital_Status"].replace({
        "YOLO": "Single", "Alone": "Single", "Absurd": "Single"
    })
    
    # 4. Columna TieneHijos
    df["TieneHijos"] = df["TotalKids"].apply(lambda x: "Sin hijos" if x == 0 else "Con hijos")
    
    return df

df_raw = load_data()

# ─── Sidebar — Filtros globales ───────────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("Filtros de Segmentación")
    st.markdown("---")
    
    # Educación
    edu_options = sorted(df_raw["Education"].unique())
    selected_edu = st.multiselect("Nivel Educativo", options=edu_options, default=edu_options)
    
    # Estado Civil
    marital_options = sorted(df_raw["Marital_Status"].unique())
    # Filtrar solo los solicitados explícitamente si existen
    wanted_marital = ["Married", "Together", "Single", "Divorced", "Widow"]
    marital_options = [m for m in marital_options if m in wanted_marital]
    selected_marital = st.multiselect("Estado Civil", options=marital_options, default=marital_options)
    
    # Hijos
    selected_kids = st.slider("Número de Hijos (TotalKids)", 0, 3, (0, 3))
    
    # Ingreso
    min_inc = int(df_raw["Income"].min())
    max_inc = int(df_raw["Income"].max())
    selected_income = st.slider("Rango de Ingreso Anual", min_inc, max_inc, (min_inc, max_inc))
    
    st.markdown("---")
    st.caption("ADM-3083 — Herramientas y Visualización")

# Aplicar filtros
mask = (
    (df_raw["Education"].isin(selected_edu)) &
    (df_raw["Marital_Status"].isin(selected_marital)) &
    (df_raw["TotalKids"] >= selected_kids[0]) & (df_raw["TotalKids"] <= selected_kids[1]) &
    (df_raw["Income"] >= selected_income[0]) & (df_raw["Income"] <= selected_income[1])
)
df = df_raw[mask].copy()

# ─── Header Principal ─────────────────────────────────────────────────────────
st.title("Marketing Intelligence Dashboard")
st.markdown("### Inteligencia de Marketing y Segmentación de Clientes")
st.markdown("---")

# ─── KPIs — Fila superior ─────────────────────────────────────────────────────
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.metric("Total de Clientes", f"{len(df):,}")
with col_kpi2:
    resp_rate = df["Response"].mean() * 100
    st.metric("Tasa de Respuesta", f"{resp_rate:.1f}%")
with col_kpi3:
    avg_wine = df["MntWines"].mean()
    st.metric("Gasto Promedio Vinos", f"${avg_wine:.0f}")
with col_kpi4:
    avg_gold = df["MntGoldProds"].mean()
    st.metric("Gasto Promedio Gold", f"${avg_gold:.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Acto 1 — ¿Quién es el cliente de alto valor? ─────────────────────────────
st.header("Acto 1 — Perfil Demográfico del Valor")
st.markdown("""
En este primer acto exploramos cómo el nivel educativo y el estado civil definen el potencial de consumo. 
Buscamos identificar los clusters demográficos que lideran el gasto en las categorías más rentables.
""")

col1, col2 = st.columns(2)

with col1:
    # Gráfico 1: Vinos por Educación
    orden_edu = ["Basic", "2n Cycle", "Graduation", "Master", "PhD"]
    g1_data = df.groupby("Education")["MntWines"].mean().reindex(orden_edu).dropna().reset_index()
    
    fig1 = px.bar(
        g1_data,
        x="MntWines",
        y="Education",
        orientation="h",
        title="A mayor nivel educativo, el gasto en vinos se multiplica por 56x",
        color="MntWines",
        color_continuous_scale=[PALETTE["gris_claro"], PALETTE["vino"]],
        template="plotly_white",
        text_auto=".0f"
    )
    fig1.update_layout(
        plot_bgcolor=PALETTE["fondo"], paper_bgcolor=PALETTE["fondo"],
        font=dict(color=PALETTE["gris_oscuro"]),
        coloraxis_showscale=False, xaxis_title="Gasto Promedio en Vinos ($)", yaxis_title=None
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.info("**Insight:** Los clientes con PhD gastan significativamente más, consolidando la educación como el predictor más fuerte de consumo premium.")

with col2:
    # Gráfico 2: Vinos y Gold por Estado Civil
    g2_data = df.groupby("Marital_Status")[["MntWines", "MntGoldProds"]].mean().sort_values("MntWines", ascending=False).reset_index()
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=g2_data["Marital_Status"], y=g2_data["MntWines"],
        name="Vinos", marker_color=PALETTE["vino"]
    ))
    fig2.add_trace(go.Bar(
        x=g2_data["Marital_Status"], y=g2_data["MntGoldProds"],
        name="Gold", marker_color=PALETTE["dorado"]
    ))
    
    fig2.update_layout(
        title="Clientes sin pareja lideran el gasto en productos premium",
        barmode="group", template="plotly_white",
        plot_bgcolor=PALETTE["fondo"], paper_bgcolor=PALETTE["fondo"],
        font=dict(color=PALETTE["gris_oscuro"]),
        xaxis_title=None, yaxis_title="Gasto Promedio ($)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.info("**Insight:** Los segmentos 'Widow' y 'Divorced' muestran un ticket promedio superior en vinos, sugiriendo una mayor renta disponible para lujo personal.")

# ─── Acto 2 — ¿La familia frena el consumo premium? ───────────────────────────
st.markdown("---")
st.header("Acto 2 — Impacto de la Composición Familiar")
st.markdown("""
El análisis familiar revela una tensión directa entre la presencia de dependientes y el gasto en productos de placer. 
Cruzamos la demografía con el ingreso para entender si el freno es económico o de priorización.
""")

col3, col4 = st.columns([1, 1.2])

with col3:
    # Gráfico 3: Vinos por TotalKids
    g3_data = df.groupby("TotalKids")["MntWines"].mean().reset_index()
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=g3_data["TotalKids"], y=g3_data["MntWines"],
        mode="lines+markers+text",
        line=dict(color=PALETTE["vino"], width=4),
        fill="tozeroy",
        fillcolor="rgba(123, 45, 139, 0.12)",
        text=[f"${v:.0f}" for v in g3_data["MntWines"]],
        textposition="top center",
        name="Gasto en Vinos"
    ))
    
    fig3.update_layout(
        title="Cada hijo adicional reduce el gasto en vinos hasta en un 71%",
        template="plotly_white",
        plot_bgcolor=PALETTE["fondo"], paper_bgcolor=PALETTE["fondo"],
        font=dict(color=PALETTE["gris_oscuro"]),
        xaxis=dict(tickvals=[0,1,2,3], title="Número total de hijos"),
        yaxis_title="Promedio Gasto Vinos ($)"
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.info("**Insight:** La caída es drástica al pasar de 0 a 1 hijo. El cliente sin hijos es el target ideal para categorías de alto margen.")

with col4:
    # Gráfico 4: Scatter Income vs Spend
    # Excluir outliers top 1% Income
    p99 = df["Income"].quantile(0.99)
    df_scatter = df[df["Income"] < p99].copy()
    
    df_scatter["Comp. Familiar"] = df_scatter["TotalKids"].apply(
        lambda x: "Sin hijos" if x == 0 else ("1 hijo" if x == 1 else "2+ hijos")
    )
    
    fig4 = px.scatter(
        df_scatter,
        x="Income", y="TotalSpend",
        color="Comp. Familiar",
        color_discrete_map={
            "Sin hijos": PALETTE["vino"],
            "1 hijo":    PALETTE["dorado"],
            "2+ hijos":  PALETTE["coral"]
        },
        title="Ingreso alto + sin hijos = el cliente de alto valor ideal",
        labels={"Income": "Ingreso Anual", "TotalSpend": "Gasto Total"},
        template="plotly_white",
        opacity=0.6
    )
    
    fig4.update_layout(
        plot_bgcolor=PALETTE["fondo"], paper_bgcolor=PALETTE["fondo"],
        font=dict(color=PALETTE["gris_oscuro"]),
        xaxis_tickformat="$"
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.info("**Insight:** A igual nivel de ingreso, el cluster 'Sin hijos' (violeta) se sitúa consistentemente por encima del resto en gasto total.")

# ─── Acto 3 — ¿Por dónde llegamos al cliente ideal? ───────────────────────────
st.markdown("---")
st.header("Acto 3 — Estrategia de Canal y Campañas")
st.markdown("""
Finalmente, analizamos los puntos de contacto. ¿Dónde compra nuestro cliente ideal y qué tan propenso es 
a aceptar nuestras ofertas? Estos hallazgos definen la asignación táctica del presupuesto.
""")

col5, col6 = st.columns(2)

with col5:
    # Gráfico 5: Canales por TieneHijos
    canales = ["NumWebPurchases", "NumStorePurchases", "NumCatalogPurchases", "NumDealsPurchases"]
    g5_data = df.groupby("TieneHijos")[canales].mean().reset_index()
    g5_melted = g5_data.melt(id_vars="TieneHijos", var_name="Canal", value_name="Promedio")
    
    # Traducir nombres de canales
    canal_map = {
        "NumWebPurchases": "Web", "NumStorePurchases": "Tienda", 
        "NumCatalogPurchases": "Catálogo", "NumDealsPurchases": "Ofertas"
    }
    g5_melted["Canal"] = g5_melted["Canal"].map(canal_map)
    
    fig5 = px.bar(
        g5_melted,
        x="Canal", y="Promedio",
        color="TieneHijos",
        barmode="group",
        title="El catálogo es clave para el cliente sin hijos",
        color_discrete_map={"Sin hijos": PALETTE["vino"], "Con hijos": PALETTE["gris_claro"]},
        template="plotly_white",
        text_auto=".1f"
    )
    fig5.update_layout(
        plot_bgcolor=PALETTE["fondo"], paper_bgcolor=PALETTE["fondo"],
        font=dict(color=PALETTE["gris_oscuro"]),
        yaxis_title="Compras Promedio"
    )
    st.plotly_chart(fig5, use_container_width=True)
    st.info("**Insight:** El canal Catálogo es ignorado por familias, pero es 2.7x más efectivo para clientes sin hijos.")

with col6:
    # Gráfico 6: Respuesta por Educación y TieneHijos
    g6_data = df.groupby(["Education", "TieneHijos"])["Response"].mean().reset_index()
    g6_data["Response %"] = g6_data["Response"] * 100
    # Ordenar Educación
    g6_data["Education"] = pd.Categorical(g6_data["Education"], categories=orden_edu, ordered=True)
    g6_data = g6_data.sort_values("Education")
    
    avg_total_resp = df["Response"].mean() * 100
    
    fig6 = px.bar(
        g6_data,
        x="Education", y="Response %",
        color="TieneHijos",
        barmode="group",
        title="PhD y sin hijos: 2.4x más propensos a aceptar campañas",
        color_discrete_map={"Sin hijos": PALETTE["verde"], "Con hijos": PALETTE["gris_claro"]},
        template="plotly_white",
        text_auto=".1f"
    )
    
    # Línea de referencia
    fig6.add_hline(
        y=avg_total_resp, line_dash="dot", line_color=PALETTE["coral"],
        annotation_text=f"Promedio: {avg_total_resp:.1f}%", annotation_position="top right"
    )
    
    fig6.update_layout(
        plot_bgcolor=PALETTE["fondo"], paper_bgcolor=PALETTE["fondo"],
        font=dict(color=PALETTE["gris_oscuro"]),
        yaxis_title="Tasa de Respuesta (%)"
    )
    st.plotly_chart(fig6, use_container_width=True)
    st.info("**Insight:** El segmento PhD sin hijos es el 'Early Adopter' por excelencia, con tasas de respuesta que duplican la media.")

# ─── Conclusión Final ─────────────────────────────────────────────────────────
st.markdown("---")
st.header("Resumen Estratégico y Recomendaciones")

st.markdown("""
| Acto | Dimensión | Hallazgo Estratégico |
| :--- | :--- | :--- |
| **Acto 1** | **Demografía** | El nivel **PhD** es el motor del gasto en vinos (56x vs básico). |
| **Acto 2** | **Familia** | La ausencia de hijos dispara el **TotalSpend** a igual nivel de ingreso. |
| **Acto 3** | **Canales** | El **Catálogo** y el segmento **PhD sin hijos** ofrecen el mejor ROI por respuesta. |

### Recomendaciones:
1. **Priorización:** Concentrar esfuerzos de productos Premium en clientes con Master/PhD sin hijos.
2. **Canal Táctico:** Revitalizar la inversión en catálogos físicos y digitales dirigidos al cluster de alto valor.
3. **Incentivos:** Para el segmento con hijos, la única vía de entrada efectiva son las **Ofertas/Deals**; no intentar vender premium a precio full.
4. **Fidelización:** El PhD sin hijos responde al 36% de las campañas; es el cliente más receptivo a nuevos lanzamientos.
""")

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Proyecto Final — ADM-3083 | Moreno · Albán · Rivas · Arteaga")

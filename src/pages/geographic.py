import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from typing import Dict, Any
import numpy as np

from src.utils import (Page, ChartGenerator, UIComponents, FilterManager, format_number, validate_data,
                       get_cities_list, filter_data_by_cities)
from src.nm.analytics import  Analytics
from src.state import StateManager, DashboardState


class GeographicPage(Page):
    """Página de Visão Geral do Ecossistema Têxtil"""

    def render(self, data: Dict[str, Any]):
        """Renderiza a página de visão geral"""
        Analytics.log_event("page_view", {"page": "overview"})
        StateManager.increment_page_view("Visão Geral")

        st.markdown('<h2 class="page-header">🏠 Visão Geral do Ecossistema Têxtil</h2>',
                    unsafe_allow_html=True)

        # Validar dados
        # if not self._validate_data(data):
        #     st.error("❌ Erro no carregamento dos dados. Verifique os arquivos necessários.")
        #     return

        # Carregar dados
        df_economic = data['economicos']
        df_social = data['sociais']
        df_environmental = data['ambientais']
        df_innovation = data['inovacao']

        # Filtros globais
        filtered_data = self._render_global_filters(data)

        # Layout principal
        self._render_main_overview(filtered_data)

        # Mapa interativo
        self._render_interactive_map(filtered_data)

        # Painel de métricas consolidadas
        self._render_consolidated_metrics(filtered_data)

        # Comparativo entre cidades
        self._render_city_comparison(filtered_data)

    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Valida se todos os dados necessários estão disponíveis"""
        required_keys = ['economicos', 'sociais', 'ambientais', 'inovacao']
        return all(key in data and validate_data(data[key]) for key in required_keys)

    def _render_global_filters(self, data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Renderiza filtros globais e retorna dados filtrados"""
        st.markdown("### 🎛️ Filtros")

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            # Filtro de cidades
            all_cities = get_cities_list(data['economicos'])
            default_cities = ["Santa Cruz do Capibaribe", "Caruaru", "Toritama"]
            selected_cities = st.multiselect(
                "🏘️ Selecione as cidades:",
                options=all_cities,
                default=[city for city in default_cities if city in all_cities],
                key="overview_cities_filter"
            )

            Analytics.log_event("filter_applied",
                                {"filter_type": "cities", "selected": selected_cities})

        with col2:
            # Filtro de indicador para o mapa
            map_indicators = {
                "Faturamento Anual (Milhões)": "faturamento_anual_milhoes",
                "Empresas Formais": "empresas_formais",
                "Empresas Informais": "empresas_informais",
                "Empregos Diretos": "empregos_diretos",
                "População": "populacao",
                "PIB per capita": "pib_per_capita"
            }

            selected_indicator = st.selectbox(
                "📊 Indicador para o mapa:",
                options=list(map_indicators.keys()),
                index=0,
                key="overview_map_indicator"
            )

            Analytics.log_event("filter_applied",
                                {"filter_type": "map_indicator", "selected": selected_indicator})

        with col3:
            # Botão de resetar filtros
            if st.button("🔄 Resetar Filtros", key="overview_reset_filters"):
                Analytics.log_event("filters_reset", {"page": "overview"})
                st.rerun()

        # Aplicar filtros aos dados
        filtered_data = {}
        for key, df in data.items():
            filtered_data[key] = filter_data_by_cities(df.cidade, selected_cities)

        # Adicionar indicador selecionado ao estado
        filtered_data['selected_indicator'] = map_indicators[selected_indicator]
        filtered_data['selected_indicator_name'] = selected_indicator

        return filtered_data

    def _render_main_overview(self, data: Dict[str, pd.DataFrame]):
        """Renderiza visão geral principal"""
        st.markdown("---")
        st.markdown("### 📈 Resumo Executivo")

        df_economic = data['economicos']

        if df_economic.empty:
            st.warning("⚠️ Nenhum dado disponível para as cidades selecionadas.")
            return

        # Métricas principais em cards
        col1, col2, col3, col4 = st.columns(4)

        total_companies = df_economic['empresas_formais'].sum() + df_economic['empresas_informais'].sum()
        total_jobs = df_economic['empregos_diretos'].sum()
        total_revenue = df_economic['faturamento_anual_milhoes'].sum()
        avg_exports = df_economic['exportacao_percentual'].mean()

        with col1:
            UIComponents.metric_card(
                "🏢 Total de Empresas",
                format_number(total_companies),
                f"{len(df_economic)} cidades selecionadas"
            )

        with col2:
            UIComponents.metric_card(
                "👥 Empregos Diretos",
                format_number(total_jobs),
                "Em empresas formais e informais"
            )

        with col3:
            UIComponents.metric_card(
                "💰 Faturamento Total",
                f"R$ {format_number(total_revenue, decimal_places=1)}M",
                "Bilhões em receita anual"
            )

        with col4:
            UIComponents.metric_card(
                "🌍 Exportação Média",
                f"{avg_exports:.1f}%",
                "Da produção total"
            )

    def _render_interactive_map(self, data: Dict[str, pd.DataFrame]):
        """Renderiza mapa interativo do polo têxtil"""
        st.markdown("---")
        st.markdown("### 🗺️ Mapa Interativo do Polo Têxtil")

        df_economic = data['economic']

        if df_economic.empty:
            st.info("ℹ️ Selecione pelo menos uma cidade para visualizar o mapa.")
            return

        # Coordenadas das principais cidades (aproximadas)
        city_coordinates = {
            "Santa Cruz do Capibaribe": [-7.95, -36.20],
            "Caruaru": [-8.28, -35.97],
            "Toritama": [-8.01, -36.05],
            "Surubim": [-7.83, -35.76],
            "Vertentes": [-7.90, -35.98]
        }

        # Criar mapa centrado na região
        center_lat = -8.08
        center_lon = -36.02
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

        # Adicionar marcadores para cada cidade
        indicator_col = data['selected_indicator']
        indicator_name = data['selected_indicator_name']

        # Normalizar valores para tamanho dos círculos
        if indicator_col in df_economic.columns:
            values = df_economic[indicator_col].values
            min_val, max_val = values.min(), values.max()

            for _, row in df_economic.iterrows():
                cidade = row['cidade']
                if cidade in city_coordinates:
                    lat, lon = city_coordinates[cidade]
                    value = row[indicator_col]

                    # Calcular tamanho do círculo (entre 10 e 50)
                    if max_val > min_val:
                        normalized_size = 15 + 35 * (value - min_val) / (max_val - min_val)
                    else:
                        normalized_size = 25

                    # Criar popup com informações
                    popup_content = f"""
                    <div style='width: 200px'>
                        <h4>{cidade}</h4>
                        <b>{indicator_name}:</b> {format_number(value)}<br>
                        <b>População:</b> {format_number(row['populacao'])}<br>
                        <b>Empresas Formais:</b> {format_number(row['empresas_formais'])}<br>
                        <b>Empresas Informais:</b> {format_number(row['empresas_informais'])}<br>
                        <b>PIB per capita:</b> R$ {format_number(row['pib_per_capita'])}
                    </div>
                    """

                    # Adicionar marcador
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=normalized_size,
                        popup=folium.Popup(popup_content, max_width=250),
                        color='blue',
                        fill=True,
                        fillColor='lightblue',
                        fillOpacity=0.6,
                        weight=2
                    ).add_to(m)

                    # Adicionar label com nome da cidade
                    folium.Marker(
                        location=[lat, lon],
                        icon=folium.DivIcon(
                            html=f'<div style="font-size: 12px; font-weight: bold; text-align: center; margin-top: 30px;">{cidade}</div>',
                            icon_size=(100, 20),
                            icon_anchor=(50, 0)
                        )
                    ).add_to(m)

        # Exibir mapa
        col1, col2 = st.columns([3, 1])

        with col1:
            map_data = st_folium(m, width=700, height=400)

            Analytics.log_event("map_interaction", {
                "indicator": indicator_name,
                "cities_count": len(df_economic)
            })

        with col2:
            st.markdown("#### 📋 Legenda")
            st.markdown(f"**Indicador:** {indicator_name}")
            st.markdown("**Tamanho dos círculos:** Proporcional ao valor do indicador selecionado")
            st.markdown("**Interação:** Clique nos círculos para ver detalhes")

            # Estatísticas do indicador
            if indicator_col in df_economic.columns:
                st.markdown("#### 📊 Estatísticas")
                values = df_economic[indicator_col]
                st.write(f"**Máximo:** {format_number(values.max())}")
                st.write(f"**Mínimo:** {format_number(values.min())}")
                st.write(f"**Média:** {format_number(values.mean())}")

    def _render_consolidated_metrics(self, data: Dict[str, pd.DataFrame]):
        """Renderiza painel de métricas consolidadas"""
        st.markdown("---")
        st.markdown("### 📊 Métricas Consolidadas")

        df_economic = data['economic']
        df_social = data['social']

        if df_economic.empty:
            return

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de distribuição formal vs informal
            formal = df_economic['empresas_formais'].sum()
            informal = df_economic['empresas_informais'].sum()

            fig_pie = go.Figure(data=[go.Pie(
                labels=['Empresas Formais', 'Empresas Informais'],
                values=[formal, informal],
                hole=0.4,
                marker_colors=['#2E86AB', '#A23B72']
            )])

            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=12
            )

            fig_pie.update_layout(
                title="Distribuição: Formal vs Informal",
                font=dict(size=14),
                showlegend=True,
                height=400
            )

            st.plotly_chart(fig_pie, use_container_width=True)

            Analytics.log_event("chart_view", {"chart_type": "formal_informal_pie"})

        with col2:
            # Gráfico de faturamento por cidade
            fig_bar = px.bar(
                df_economic,
                x='cidade',
                y='faturamento_anual_milhoes',
                title='Faturamento por Cidade (R$ Milhões)',
                color='faturamento_anual_milhoes',
                color_continuous_scale='Blues'
            )

            fig_bar.update_layout(
                xaxis_title="Cidade",
                yaxis_title="Faturamento (R$ Milhões)",
                xaxis_tickangle=-45,
                height=400
            )

            st.plotly_chart(fig_bar, use_container_width=True)

            Analytics.log_event("chart_view", {"chart_type": "revenue_by_city"})

        # Métricas sociais
        st.markdown("#### 🌍 Indicadores Sociais Consolidados")

        if not df_social.empty:
            col3, col4, col5, col6 = st.columns(4)

            with col3:
                avg_idh = df_social['idh'].mean()
                UIComponents.metric_card("📈 IDH Médio", f"{avg_idh:.3f}", "Índice de Desenvolvimento Humano")

            with col4:
                avg_poverty = df_social['taxa_pobreza'].mean()
                UIComponents.metric_card("📉 Taxa de Pobreza", f"{avg_poverty:.1f}%", "Média das cidades")

            with col5:
                avg_dropout = df_social['evasao_escolar'].mean()
                UIComponents.metric_card("🎓 Evasão Escolar", f"{avg_dropout:.1f}%", "Média das cidades")

            with col6:
                avg_internet = df_social['acesso_internet'].mean()
                UIComponents.metric_card("💻 Acesso à Internet", f"{avg_internet:.1f}%", "Média das cidades")

    def _render_city_comparison(self, data: Dict[str, pd.DataFrame]):
        """Renderiza comparativo entre cidades"""
        st.markdown("---")
        st.markdown("### 🏘️ Comparativo entre Cidades")

        df_economic = data['economic']

        if len(df_economic) < 2:
            st.info("ℹ️ Selecione pelo menos 2 cidades para visualizar comparações.")
            return

        # Seletor de métricas para comparação
        comparison_metrics = {
            "População": "populacao",
            "Empresas Formais": "empresas_formais",
            "Empresas Informais": "empresas_informais",
            "Empregos Diretos": "empregos_diretos",
            "Faturamento (R$ Milhões)": "faturamento_anual_milhoes",
            "Exportação (%)": "exportacao_percentual",
            "PIB per capita": "pib_per_capita"
        }

        selected_metrics = st.multiselect(
            "📊 Selecione as métricas para comparação:",
            options=list(comparison_metrics.keys()),
            default=["Faturamento (R$ Milhões)", "Empregos Diretos", "PIB per capita"],
            key="overview_comparison_metrics"
        )

        if selected_metrics:
            Analytics.log_event("comparison_metrics_selected",
                                {"metrics": selected_metrics})

            # Criar gráfico de barras agrupadas
            metric_columns = [comparison_metrics[metric] for metric in selected_metrics]

            # Preparar dados para o gráfico
            df_melted = df_economic.melt(
                id_vars=['cidade'],
                value_vars=metric_columns,
                var_name='Métrica',
                value_name='Valor'
            )

            # Mapear nomes das colunas para nomes amigáveis
            metric_name_map = {v: k for k, v in comparison_metrics.items()}
            df_melted['Métrica'] = df_melted['Métrica'].map(metric_name_map)

            fig_comparison = px.bar(
                df_melted,
                x='cidade',
                y='Valor',
                color='Métrica',
                barmode='group',
                title='Comparativo entre Cidades - Métricas Selecionadas',
                height=500
            )

            fig_comparison.update_layout(
                xaxis_title="Cidade",
                yaxis_title="Valor",
                xaxis_tickangle=-45,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            st.plotly_chart(fig_comparison, use_container_width=True)

            # Tabela detalhada
            st.markdown("#### 📋 Dados Detalhados")

            display_df = df_economic[['cidade'] + metric_columns].copy()
            display_df.columns = ['Cidade'] + selected_metrics

            # Formatar números para melhor visualização
            for col in selected_metrics:
                if col in ['Faturamento (R$ Milhões)', 'PIB per capita']:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}")
                elif col == 'Exportação (%)':
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}%")
                else:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:,}")

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Botão de exportação
            col_export1, col_export2 = st.columns([1, 3])

            with col_export1:
                if st.button("📥 Exportar Dados", key="overview_export"):
                    Analytics.log_event("export_data",
                                        {"data_type": "city_comparison",
                                         "cities_count": len(df_economic),
                                         "metrics_count": len(selected_metrics)})

                    csv_data = display_df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv_data.encode('utf-8'),
                        file_name=f'comparativo_cidades_{len(df_economic)}_cidades.csv',
                        mime='text/csv'
                    )

    def write(self):
        """Método de compatibilidade com a interface Page"""
        # Este método seria chamado pelo sistema de páginas
        # mas como estamos usando render(), não é necessário implementar
        pass


# Função utilitária para carregar a página
def load_overview_page():
    """Carrega e renderiza a página de overview"""
    return GeographicPage()
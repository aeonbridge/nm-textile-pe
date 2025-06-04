import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

from src.utils import (Page, ChartGenerator, UIComponents, FilterManager, format_number, validate_data, \
                       get_cities_list, filter_data_by_cities)
from src.state import StateManager, DashboardState

from src.nm.analytics import  Analytics

class OverviewPage(Page):
    """Página de Visão Geral do Ecossistema Têxtil"""

    def render(self, data: Dict[str, Any]):
        """Renderiza a página de visão geral"""
        Analytics.log_event("page_view", {"page": "overview"})
        StateManager.increment_page_view("Visão Geral")

        st.markdown('<h2 class="page-header">🏠 Visão Geral do Ecossistema Têxtil</h2>',
                    unsafe_allow_html=True)

        # Filtros globais
        self._render_global_filters(data)

        # Métricas principais
        self._render_key_metrics(data)

        # Layout principal
        col1, col2 = st.columns([2, 1])

        with col1:
            self._render_geographic_section(data)
            self._render_indicators_tabs(data)

        with col2:
            self._render_summary_section(data)
            self._render_insights_section(data)

    def _render_global_filters(self, data: Dict[str, Any]):
        """Renderiza filtros globais"""
        with st.expander("🎛️ Filtro cidades", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                # Filtro de cidades
                cities = get_cities_list(None) #['Santa Cruz do Capibaribe', 'Caruaru', 'Toritama']
                if cities:
                    selected_cities = FilterManager.create_city_filter(
                        cities,
                        key="overview_city_filter"
                    )
                    StateManager.update_state(selected_cities=selected_cities)

            with col2:
                # Opções de visualização
                show_details = st.checkbox(
                    "Mostrar detalhes adicionais",
                    value=StateManager.get_state().show_details,
                    key="overview_show_details"
                )
                StateManager.update_state(show_details=show_details)

    def _render_key_metrics(self, data: Dict[str, Any]):
        """Renderiza métricas principais"""
        st.subheader("📊 Indicadores-Chave")

        # Filtrar dados pelas cidades selecionadas
        state = StateManager.get_state()
        df_econ = filter_data_by_cities(data.get('economicos'), state.selected_cities)

        if df_econ is not None and not df_econ.empty:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                total_pop = df_econ['populacao'].sum() if 'populacao' in df_econ.columns else 0
                UIComponents.create_metric_card(
                    "População Total",
                    format_number(total_pop, "thousands")
                )

            with col2:
                total_empresas = 0
                if 'empresas_formais' in df_econ.columns and 'empresas_informais' in df_econ.columns:
                    total_empresas = df_econ['empresas_formais'].sum() + df_econ['empresas_informais'].sum()
                UIComponents.create_metric_card(
                    "Total de Empresas",
                    format_number(total_empresas, "thousands")
                )

            with col3:
                total_faturamento = df_econ[
                    'faturamento_anual_milhoes'].sum() if 'faturamento_anual_milhoes' in df_econ.columns else 0
                UIComponents.create_metric_card(
                    "Faturamento Anual (M)",
                    format_number(total_faturamento, "currency_millions")
                )

            with col4:
                total_empregos = df_econ['empregos_diretos'].sum() if 'empregos_diretos' in df_econ.columns else 0
                UIComponents.create_metric_card(
                    "Empregos Diretos",
                    format_number(total_empregos, "thousands")
                )
        else:
            st.warning("Dados econômicos não disponíveis para as cidades selecionadas.")

    def _render_geographic_section(self, data: Dict[str, Any]):
        """Renderiza seção geográfica"""
        st.subheader("📍 Distribuição Geográfica")

        state = StateManager.get_state()
        df_econ = filter_data_by_cities(data.get('economicos'), state.selected_cities)

        if df_econ is not None and not df_econ.empty:
            map_fig = ChartGenerator.create_geographic_map(df_econ)
            if map_fig:
                st.plotly_chart(map_fig, use_container_width=True)

                if state.show_details:
                    with st.expander("📋 Dados do Mapa"):
                        st.dataframe(df_econ[['cidade', 'populacao', 'faturamento_anual_milhoes', 'empregos_diretos']])
            else:
                st.info("Mapa geográfico não disponível.")
        else:
            st.warning("Dados não disponíveis para visualização geográfica.")

    def _render_indicators_tabs(self, data: Dict[str, Any]):
        """Renderiza abas de indicadores"""
        st.subheader("📈 Panorama de Indicadores")

        tabs = st.tabs(["Econômicos", "Sociais", "Ambientais", "Inovação"])

        with tabs[0]:
            self._render_economic_indicators(data)

        with tabs[1]:
            self._render_social_indicators(data)

        with tabs[2]:
            self._render_environmental_indicators(data)

        with tabs[3]:
            self._render_innovation_indicators(data)

    def _render_economic_indicators(self, data: Dict[str, Any]):
        """Renderiza indicadores econômicos"""
        state = StateManager.get_state()
        df = filter_data_by_cities(data.get('economicos'), state.selected_cities)

        if df is not None and not df.empty:
            # Gráfico de barras comparativo
            economic_cols = ['empresas_formais', 'empresas_informais', 'empregos_diretos']
            valid_cols = [col for col in economic_cols if col in df.columns]

            if valid_cols:
                fig = ChartGenerator.create_comparison_bar_chart(
                    df, 'cidade', valid_cols,
                    "Indicadores Econômicos por Cidade"
                )
                st.plotly_chart(fig, use_container_width=True)

            # Gráfico de participação no faturamento
            if 'faturamento_anual_milhoes' in df.columns:
                fig_pie = ChartGenerator.create_pie_chart(
                    df, 'faturamento_anual_milhoes', 'cidade',
                    "Participação no Faturamento Total"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Dados econômicos não disponíveis.")

    def _render_social_indicators(self, data: Dict[str, Any]):
        """Renderiza indicadores sociais"""
        state = StateManager.get_state()
        df = filter_data_by_cities(data.get('sociais'), state.selected_cities)

        if df is not None and not df.empty:
            # Gráfico radar para comparação multidimensional
            social_cols = ['idh', 'acesso_internet', 'mulheres_empreendedoras']
            valid_cols = [col for col in social_cols if col in df.columns]

            if valid_cols:
                fig = ChartGenerator.create_radar_chart(
                    df, valid_cols, 'cidade',
                    "Comparação de Indicadores Sociais"
                )
                st.plotly_chart(fig, use_container_width=True)

            # Gráfico de barras para indicadores problemáticos
            problem_cols = ['taxa_pobreza', 'evasao_escolar', 'trabalho_infantil']
            valid_problem_cols = [col for col in problem_cols if col in df.columns]

            if valid_problem_cols:
                fig_problems = ChartGenerator.create_comparison_bar_chart(
                    df, 'cidade', valid_problem_cols,
                    "Indicadores de Desafios Sociais"
                )
                st.plotly_chart(fig_problems, use_container_width=True)
        else:
            st.info("Dados sociais não disponíveis.")

    def _render_environmental_indicators(self, data: Dict[str, Any]):
        """Renderiza indicadores ambientais"""
        state = StateManager.get_state()
        df = filter_data_by_cities(data.get('ambientais'), state.selected_cities)

        if df is not None and not df.empty:
            # Gráfico de consumo de água e tratamento
            water_cols = ['consumo_agua_m3_dia', 'efluentes_tratados_percentual']
            valid_cols = [col for col in water_cols if col in df.columns]

            if valid_cols:
                fig = ChartGenerator.create_comparison_bar_chart(
                    df, 'cidade', valid_cols,
                    "Indicadores de Recursos Hídricos"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados ambientais em preparação.")

    def _render_innovation_indicators(self, data: Dict[str, Any]):
        """Renderiza indicadores de inovação"""
        state = StateManager.get_state()
        df = filter_data_by_cities(data.get('inovacao'), state.selected_cities)

        if df is not None and not df.empty:
            # Gráfico de investimento e adoção digital
            innov_cols = ['investimento_inovacao_percentual', 'empresas_com_ecommerce', 'adocao_tecnologias_digitais']
            valid_cols = [col for col in innov_cols if col in df.columns]

            if valid_cols:
                fig = ChartGenerator.create_comparison_bar_chart(
                    df, 'cidade', valid_cols,
                    "Indicadores de Inovação e Digitalização"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados de inovação em preparação.")

    def _render_summary_section(self, data: Dict[str, Any]):
        """Renderiza seção de resumo"""
        st.subheader("📋 Resumo Executivo")

        state = StateManager.get_state()

        # Análise dinâmica baseada nos dados
        insights = self._generate_insights(data, state.selected_cities)

        for insight in insights:
            st.markdown(f"""
            <div class="insight-box">
            <strong>{insight['title']}</strong><br>
            {insight['description']}
            </div>
            """, unsafe_allow_html=True)

    def _render_insights_section(self, data: Dict[str, Any]):
        """Renderiza seção de insights"""
        st.subheader("💡 Insights e Oportunidades")

        # Ranking das cidades
        self._render_city_ranking(data)

        # Alertas e recomendações
        self._render_alerts(data)

    def _generate_insights(self, data: Dict[str, Any], selected_cities: list) -> list:
        """Gera insights baseados nos dados"""
        insights = []

        df_econ = filter_data_by_cities(data.get('economicos'), selected_cities)
        df_social = filter_data_by_cities(data.get('sociais'), selected_cities)

        if df_econ is not None and not df_econ.empty:
            # Insight sobre informalidade
            if 'taxa_informalidade' in df_econ.columns:
                avg_informal = df_econ['taxa_informalidade'].mean()
                insights.append({
                    'title': '📊 Taxa de Informalidade',
                    'description': f'A taxa média de informalidade nas cidades selecionadas é de {avg_informal:.1f}%. Toritama apresenta o maior desafio neste indicador.'
                })

        if df_social is not None and not df_social.empty:
            # Insight sobre empreendedorismo feminino
            if 'mulheres_empreendedoras' in df_social.columns:
                avg_women = df_social['mulheres_empreendedoras'].mean()
                insights.append({
                    'title': '👩‍💼 Empreendedorismo Feminino',
                    'description': f'Em média, {avg_women:.1f}% dos empreendedores são mulheres, destacando o papel central das mulheres no ecossistema têxtil.'
                })

        return insights

    def _render_city_ranking(self, data: Dict[str, Any]):
        """Renderiza ranking das cidades"""
        st.markdown("🏆 **Ranking das Cidades**")

        state = StateManager.get_state()
        df_econ = filter_data_by_cities(data.get('economicos'), state.selected_cities)

        if df_econ is not None and not df_econ.empty and 'faturamento_anual_milhoes' in df_econ.columns:
            ranking = df_econ.sort_values('faturamento_anual_milhoes', ascending=False)

            for i, (_, row) in enumerate(ranking.iterrows(), 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                st.markdown(
                    f"{medal} **{row['cidade']}** - {format_number(row['faturamento_anual_milhoes'], 'currency_millions')}")

    def _render_alerts(self, data: Dict[str, Any]):
        """Renderiza alertas e recomendações"""
        st.markdown("⚠️ **Alertas e Recomendações**")

        state = StateManager.get_state()
        df_social = filter_data_by_cities(data.get('sociais'), state.selected_cities)

        if df_social is not None and not df_social.empty:
            # Alerta sobre evasão escolar
            if 'evasao_escolar' in df_social.columns:
                high_evasion = df_social[df_social['evasao_escolar'] > 30]
                if not high_evasion.empty:
                    cities = ', '.join(high_evasion['cidade'].tolist())
                    st.markdown(f"""
                    <div class="warning-box">
                    <strong>🚨 Alta Evasão Escolar:</strong> {cities} apresenta(m) taxa de evasão escolar superior a 30%, requerendo atenção prioritária.
                    </div>
                    """, unsafe_allow_html=True)

        # Recomendação geral
        st.markdown("""
        <div class="success-box">
        <strong>✅ Recomendação:</strong> Foque em iniciativas de formalização gradual e fortalecimento da educação técnica para potencializar o desenvolvimento do polo.
        </div>
        """, unsafe_allow_html=True)
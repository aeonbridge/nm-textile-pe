import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, List
import random

from src.utils.page_utils import Page, ChartGenerator, UIComponents, FilterManager, format_number, validate_data, \
    get_cities_list, filter_data_by_cities
from src.nm.analytics import  Analytics

from src.state import StateManager


class IndicatorsPage(Page):
    """Página de Análise de Indicadores"""

    def render(self, data: Dict[str, Any]):
        """Renderiza a página de análise de indicadores"""
        Analytics.log_event("page_view", {"page": "indicators"})
        StateManager.increment_page_view("Análise de Indicadores")

        st.markdown('<h2 class="page-header">📊 Análise de Indicadores</h2>',
                    unsafe_allow_html=True)

        # Filtros específicos da página
        self._render_page_filters(data)

        # Seleção de tipo de análise
        analysis_type = st.selectbox(
            "Tipo de Análise:",
            ["Comparativo entre Cidades", "Evolução Temporal (Simulada)", "Análise Multidimensional", "Benchmarking"],
            key="indicators_analysis_type"
        )

        if analysis_type == "Comparativo entre Cidades":
            self._render_comparative_analysis(data)
        elif analysis_type == "Evolução Temporal (Simulada)":
            self._render_temporal_analysis(data)
        elif analysis_type == "Análise Multidimensional":
            self._render_multidimensional_analysis(data)
        elif analysis_type == "Benchmarking":
            self._render_benchmarking_analysis(data)

    def _render_page_filters(self, data: Dict[str, Any]):
        """Renderiza filtros específicos da página"""
        with st.expander("🎛️ Filtros de Análise", expanded=True):
            col1, col2, col3 = st.columns(3)

            filter_key =  random.randint(1000,10000)

            with col1:
                # Filtro de cidades
                cities = get_cities_list(None)
                selected_cities = FilterManager.create_city_filter(
                    cities,
                    key="indicators_city_filter"+str(filter_key)
                )
                StateManager.update_state(selected_cities=selected_cities)

            with col2:
                # Filtro de categorias de indicadores
                categories = ["Econômicos", "Sociais", "Ambientais", "Inovação"]
                selected_categories = st.multiselect(
                    "Categorias de Indicadores:",
                    options=categories,
                    default=categories,
                    key="indicators_categories"+str(filter_key)
                )

            with col3:
                # Opções de visualização
                normalize_data = st.checkbox(
                    "Normalizar dados (0-100)",
                    value=False,
                    key="indicators_normalize"+str(filter_key)
                )

                show_percentiles = st.checkbox(
                    "Mostrar percentis",
                    value=False,
                    key="indicators_percentiles"+str(filter_key)
                )

        return selected_categories, normalize_data, show_percentiles

    def _render_comparative_analysis(self, data: Dict[str, Any]):
        """Renderiza análise comparativa entre cidades"""
        st.subheader("🏙️ Análise Comparativa entre Cidades")

        selected_categories, normalize_data, show_percentiles = self._render_page_filters(data)
        state = StateManager.get_state()

        # Tabs para cada categoria
        if "Econômicos" in selected_categories:
            with st.expander("💰 Indicadores Econômicos", expanded=True):
                self._render_economic_comparison(data, state.selected_cities, normalize_data)

        if "Sociais" in selected_categories:
            with st.expander("👥 Indicadores Sociais", expanded=True):
                self._render_social_comparison(data, state.selected_cities, normalize_data)

        if "Ambientais" in selected_categories:
            with st.expander("🌍 Indicadores Ambientais", expanded=True):
                self._render_environmental_comparison(data, state.selected_cities, normalize_data)

        if "Inovação" in selected_categories:
            with st.expander("💡 Indicadores de Inovação", expanded=True):
                self._render_innovation_comparison(data, state.selected_cities, normalize_data)

    def _render_economic_comparison(self, data: Dict[str, Any], selected_cities: List[str], normalize_data: bool):
        """Renderiza comparação de indicadores econômicos"""
        df = filter_data_by_cities(data.get('economicos'), selected_cities)

        if df is None or df.empty:
            st.warning("Dados econômicos não disponíveis.")
            return

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de barras - Empresas
            enterprise_cols = ['empresas_formais', 'empresas_informais']
            valid_cols = [col for col in enterprise_cols if col in df.columns]

            if valid_cols:
                df_viz = self._prepare_data_for_viz(df, valid_cols, normalize_data)
                fig = ChartGenerator.create_comparison_bar_chart(
                    df_viz, 'cidade', valid_cols,
                    "Empresas Formais vs Informais"
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gráfico de dispersão - PIB vs Empregos
            if 'pib_per_capita' in df.columns and 'empregos_diretos' in df.columns:
                fig = px.scatter(
                    df,
                    x='pib_per_capita',
                    y='empregos_diretos',
                    size='populacao' if 'populacao' in df.columns else None,
                    color='cidade',
                    title="PIB per capita vs Empregos Diretos",
                    labels={
                        'pib_per_capita': 'PIB per capita (R$)',
                        'empregos_diretos': 'Empregos Diretos'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)

        # Tabela detalhada
        if st.checkbox("Mostrar dados detalhados", key="econ_details"):
            st.dataframe(df)
            UIComponents.create_download_button(df, "indicadores_economicos.csv", label="📥 Download CSV")

    def _render_social_comparison(self, data: Dict[str, Any], selected_cities: List[str], normalize_data: bool):
        """Renderiza comparação de indicadores sociais"""
        df = filter_data_by_cities(data.get('sociais'), selected_cities)

        if df is None or df.empty:
            st.warning("Dados sociais não disponíveis.")
            return

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico radar - Indicadores positivos
            positive_cols = ['idh', 'acesso_internet', 'mulheres_empreendedoras', 'jovens_empreendedores']
            valid_pos_cols = [col for col in positive_cols if col in df.columns]

            if valid_pos_cols:
                fig = ChartGenerator.create_radar_chart(
                    df, valid_pos_cols, 'cidade',
                    "Indicadores Sociais Positivos"
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gráfico de barras - Indicadores problemáticos
            problem_cols = ['taxa_pobreza', 'evasao_escolar', 'trabalho_infantil']
            valid_prob_cols = [col for col in problem_cols if col in df.columns]

            if valid_prob_cols:
                df_viz = self._prepare_data_for_viz(df, valid_prob_cols, normalize_data)
                fig = ChartGenerator.create_comparison_bar_chart(
                    df_viz, 'cidade', valid_prob_cols,
                    "Indicadores de Desafios Sociais"
                )
                st.plotly_chart(fig, use_container_width=True)

        # Análise de correlação
        self._render_correlation_analysis(df, "Sociais")

    def _render_environmental_comparison(self, data: Dict[str, Any], selected_cities: List[str], normalize_data: bool):
        """Renderiza comparação de indicadores ambientais"""
        df = filter_data_by_cities(data.get('ambientais'), selected_cities)

        if df is None or df.empty:
            st.info("Dados ambientais em preparação.")
            return

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de água
            water_cols = ['consumo_agua_m3_dia', 'efluentes_tratados_percentual', 'reuso_agua_percentual']
            valid_cols = [col for col in water_cols if col in df.columns]

            if valid_cols:
                df_viz = self._prepare_data_for_viz(df, valid_cols, normalize_data)
                fig = ChartGenerator.create_comparison_bar_chart(
                    df_viz, 'cidade', valid_cols,
                    "Gestão de Recursos Hídricos"
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gráfico de lavanderias
            if 'lavanderias_quantidade' in df.columns and 'lavanderias_licenciadas_percentual' in df.columns:
                fig = px.scatter(
                    df,
                    x='lavanderias_quantidade',
                    y='lavanderias_licenciadas_percentual',
                    color='cidade',
                    size='consumo_agua_m3_dia' if 'consumo_agua_m3_dia' in df.columns else None,
                    title="Lavanderias: Quantidade vs Licenciamento",
                    labels={
                        'lavanderias_quantidade': 'Quantidade de Lavanderias',
                        'lavanderias_licenciadas_percentual': '% Licenciadas'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)

    def _render_innovation_comparison(self, data: Dict[str, Any], selected_cities: List[str], normalize_data: bool):
        """Renderiza comparação de indicadores de inovação"""
        df = filter_data_by_cities(data.get('inovacao'), selected_cities)

        if df is None or df.empty:
            st.info("Dados de inovação em preparação.")
            return

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de investimento e adoção
            innov_cols = ['investimento_inovacao_percentual', 'adocao_tecnologias_digitais', 'empresas_com_ecommerce']
            valid_cols = [col for col in innov_cols if col in df.columns]

            if valid_cols:
                df_viz = self._prepare_data_for_viz(df, valid_cols, normalize_data)
                fig = ChartGenerator.create_comparison_bar_chart(
                    df_viz, 'cidade', valid_cols,
                    "Investimento e Adoção Tecnológica"
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gráfico de startups e marcas próprias
            brand_cols = ['marcas_proprias_percentual', 'design_proprio_percentual', 'startups_relacionadas']
            valid_brand_cols = [col for col in brand_cols if col in df.columns]

            if valid_brand_cols:
                df_viz = self._prepare_data_for_viz(df, valid_brand_cols, normalize_data)
                fig = ChartGenerator.create_comparison_bar_chart(
                    df_viz, 'cidade', valid_brand_cols,
                    "Inovação em Produtos e Negócios"
                )
                st.plotly_chart(fig, use_container_width=True)

    def _render_temporal_analysis(self, data: Dict[str, Any]):
        """Renderiza análise temporal simulada"""
        st.subheader("📈 Evolução Temporal (Simulada)")
        st.info("Esta análise utiliza dados simulados para demonstrar como seria a evolução temporal dos indicadores.")

        # Seletor de indicador para análise temporal
        indicator_options = {
            "Faturamento Anual": ("economicos", "faturamento_anual_milhoes"),
            "Taxa de Informalidade": ("economicos", "taxa_informalidade"),
            "IDH": ("sociais", "idh"),
            "Evasão Escolar": ("sociais", "evasao_escolar"),
            "Investimento em Inovação": ("inovacao", "investimento_inovacao_percentual")
        }

        selected_indicator = st.selectbox(
            "Selecione o indicador:",
            options=list(indicator_options.keys()),
            key="temporal_indicator"
        )

        # Gerar dados temporais simulados
        years = list(range(2020, 2026))
        df_temporal = self._generate_temporal_data(data, indicator_options[selected_indicator], years)

        if df_temporal is not None:
            # Gráfico de linha temporal
            fig = px.line(
                df_temporal,
                x='ano',
                y='valor',
                color='cidade',
                markers=True,
                title=f"Evolução de {selected_indicator} (2020-2025)",
                labels={'valor': selected_indicator, 'ano': 'Ano'}
            )

            # Adicionar linha de tendência
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

            # Análise de crescimento
            self._render_growth_analysis(df_temporal, selected_indicator)

    def _render_multidimensional_analysis(self, data: Dict[str, Any]):
        """Renderiza análise multidimensional"""
        st.subheader("🎯 Análise Multidimensional")

        state = StateManager.get_state()

        # Seleção de dimensões para análise
        col1, col2 = st.columns(2)

        with col1:
            dimension_x = st.selectbox(
                "Dimensão X:",
                ["PIB per capita", "Taxa de Informalidade", "IDH", "Investimento em Inovação"],
                key="multi_dim_x"
            )

        with col2:
            dimension_y = st.selectbox(
                "Dimensão Y:",
                ["Empregos Diretos", "Evasão Escolar", "Acesso à Internet", "Empresas com E-commerce"],
                key="multi_dim_y"
            )

        # Mapeamento de dimensões para dados
        dimension_mapping = {
            "PIB per capita": ("economicos", "pib_per_capita"),
            "Taxa de Informalidade": ("economicos", "taxa_informalidade"),
            "IDH": ("sociais", "idh"),
            "Investimento em Inovação": ("inovacao", "investimento_inovacao_percentual"),
            "Empregos Diretos": ("economicos", "empregos_diretos"),
            "Evasão Escolar": ("sociais", "evasao_escolar"),
            "Acesso à Internet": ("sociais", "acesso_internet"),
            "Empresas com E-commerce": ("inovacao", "empresas_com_ecommerce")
        }

        # Criar gráfico multidimensional
        df_multi = self._create_multidimensional_dataframe(data, dimension_mapping, dimension_x, dimension_y)

        if df_multi is not None:
            fig = px.scatter(
                df_multi,
                x='dim_x',
                y='dim_y',
                color='cidade',
                size='populacao' if 'populacao' in df_multi.columns else None,
                hover_name='cidade',
                title=f"{dimension_x} vs {dimension_y}",
                labels={'dim_x': dimension_x, 'dim_y': dimension_y}
            )

            # Adicionar linha de tendência
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

            # Análise de quadrantes
            self._render_quadrant_analysis(df_multi, dimension_x, dimension_y)

    def _render_benchmarking_analysis(self, data: Dict[str, Any]):
        """Renderiza análise de benchmarking"""
        st.subheader("🏆 Análise de Benchmarking")

        # Criar índice composto para ranking
        composite_index = self._calculate_composite_index(data)

        if composite_index is not None:
            # Gráfico de ranking
            fig = px.bar(
                composite_index.sort_values('indice_composto', ascending=True),
                x='indice_composto',
                y='cidade',
                orientation='h',
                title="Índice Composto de Desenvolvimento",
                labels={'indice_composto': 'Índice Composto', 'cidade': 'Cidade'}
            )
            st.plotly_chart(fig, use_container_width=True)

            # Análise detalhada por dimensão
            self._render_dimensional_breakdown(composite_index)

    def _prepare_data_for_viz(self, df: pd.DataFrame, columns: List[str], normalize: bool) -> pd.DataFrame:
        """Prepara dados para visualização"""
        df_viz = df.copy()

        if normalize:
            for col in columns:
                if col in df_viz.columns:
                    min_val = df_viz[col].min()
                    max_val = df_viz[col].max()
                    if max_val > min_val:
                        df_viz[col] = ((df_viz[col] - min_val) / (max_val - min_val)) * 100

        return df_viz

    def _render_correlation_analysis(self, df: pd.DataFrame, category: str):
        """Renderiza análise de correlação"""
        if st.checkbox(f"Mostrar correlações - {category}", key=f"corr_{category.lower()}"):
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if 'cidade' in numeric_cols:
                numeric_cols.remove('cidade')

            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()

                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    aspect="auto",
                    title=f"Matriz de Correlação - {category}",
                    color_continuous_scale="RdBu"
                )
                st.plotly_chart(fig, use_container_width=True)

    def _generate_temporal_data(self, data: Dict[str, Any], indicator_info: tuple, years: List[int]) -> pd.DataFrame:
        """Gera dados temporais simulados"""
        category, column = indicator_info
        df_base = data.get(category)

        if df_base is None or column not in df_base.columns:
            return None

        temporal_data = []

        for _, row in df_base.iterrows():
            cidade = row['cidade']
            base_value = row[column]

            for year in years:
                # Simular variação temporal com tendência e ruído
                if year == 2025:  # Valor atual
                    value = base_value
                else:
                    # Adicionar tendência e variação aleatória
                    trend = (year - 2025) * np.random.uniform(-0.02, 0.03)  # -2% a +3% por ano
                    noise = np.random.uniform(-0.05, 0.05)  # ±5% de ruído
                    value = base_value * (1 + trend + noise)

                temporal_data.append({
                    'cidade': cidade,
                    'ano': year,
                    'valor': value
                })

        return pd.DataFrame(temporal_data)

    def _render_growth_analysis(self, df_temporal: pd.DataFrame, indicator: str):
        """Renderiza análise de crescimento"""
        with st.expander("📊 Análise de Crescimento"):
            # Calcular crescimento por cidade
            growth_data = []
            for cidade in df_temporal['cidade'].unique():
                city_data = df_temporal[df_temporal['cidade'] == cidade].sort_values('ano')
                start_value = city_data.iloc[0]['valor']
                end_value = city_data.iloc[-1]['valor']
                growth_rate = ((end_value - start_value) / start_value) * 100

                growth_data.append({
                    'cidade': cidade,
                    'crescimento_percentual': growth_rate,
                    'valor_inicial': start_value,
                    'valor_final': end_value
                })

            growth_df = pd.DataFrame(growth_data)

            # Gráfico de crescimento
            fig = px.bar(
                growth_df,
                x='cidade',
                y='crescimento_percentual',
                title=f"Taxa de Crescimento - {indicator} (2020-2025)",
                labels={'crescimento_percentual': 'Crescimento (%)'}
            )
            st.plotly_chart(fig, use_container_width=True)

    def _create_multidimensional_dataframe(self, data: Dict[str, Any], mapping: Dict, dim_x: str,
                                           dim_y: str) -> pd.DataFrame:
        """Cria dataframe para análise multidimensional"""
        category_x, column_x = mapping[dim_x]
        category_y, column_y = mapping[dim_y]

        df_x = data.get(category_x)
        df_y = data.get(category_y)

        if df_x is None or df_y is None:
            return None

        # Merge dos dataframes
        df_merged = pd.merge(df_x[['cidade', column_x]], df_y[['cidade', column_y]], on='cidade')
        df_merged['dim_x'] = df_merged[column_x]
        df_merged['dim_y'] = df_merged[column_y]

        # Adicionar população se disponível
        if 'populacao' in df_x.columns:
            df_merged['populacao'] = df_x['populacao']

        return df_merged

    def _render_quadrant_analysis(self, df_multi: pd.DataFrame, dim_x: str, dim_y: str):
        """Renderiza análise de quadrantes"""
        with st.expander("🎯 Análise de Quadrantes"):
            # Calcular medianas para dividir quadrantes
            median_x = df_multi['dim_x'].median()
            median_y = df_multi['dim_y'].median()

            # Classificar cidades por quadrante
            for _, row in df_multi.iterrows():
                cidade = row['cidade']
                x_val = row['dim_x']
                y_val = row['dim_y']

                if x_val >= median_x and y_val >= median_y:
                    quadrant = "🟢 Alto desempenho em ambas dimensões"
                elif x_val >= median_x and y_val < median_y:
                    quadrant = f"🟡 Alto {dim_x}, baixo {dim_y}"
                elif x_val < median_x and y_val >= median_y:
                    quadrant = f"🟡 Baixo {dim_x}, alto {dim_y}"
                else:
                    quadrant = "🔴 Baixo desempenho em ambas dimensões"

                st.markdown(f"**{cidade}**: {quadrant}")

    def _calculate_composite_index(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Calcula índice composto para benchmarking"""
        # Selecionar indicadores-chave
        key_indicators = [
            ("economicos", "pib_per_capita", 1),  # Positivo
            ("economicos", "taxa_informalidade", -1),  # Negativo
            ("sociais", "idh", 1),  # Positivo
            ("sociais", "evasao_escolar", -1),  # Negativo
            ("inovacao", "investimento_inovacao_percentual", 1)  # Positivo
        ]

        composite_data = []
        cities = get_cities_list(None)

        for cidade in cities:
            city_score = 0
            valid_indicators = 0

            for category, column, weight in key_indicators:
                df = data.get(category)
                if df is not None and column in df.columns:
                    city_data = df[df['cidade'] == cidade]
                    if not city_data.empty:
                        value = city_data[column].iloc[0]
                        # Normalizar e aplicar peso
                        normalized = self._normalize_indicator(df[column], value, weight > 0)
                        city_score += normalized * abs(weight)
                        valid_indicators += 1

            if valid_indicators > 0:
                composite_data.append({
                    'cidade': cidade,
                    'indice_composto': city_score / valid_indicators,
                    'indicadores_validos': valid_indicators
                })

        return pd.DataFrame(composite_data) if composite_data else None

    def _normalize_indicator(self, series: pd.Series, value: float, is_positive: bool) -> float:
        """Normaliza indicador para índice composto"""
        min_val = series.min()
        max_val = series.max()

        if max_val == min_val:
            return 50  # Valor neutro se não há variação

        normalized = ((value - min_val) / (max_val - min_val)) * 100

        # Inverter se indicador é negativo (menor é melhor)
        if not is_positive:
            normalized = 100 - normalized

        return normalized

    def _render_dimensional_breakdown(self, composite_index: pd.DataFrame):
        """Renderiza breakdown dimensional do índice composto"""
        with st.expander("📋 Detalhamento por Dimensões"):
            st.markdown("""
            **Componentes do Índice Composto:**
            - 📈 PIB per capita (peso positivo)
            - 📉 Taxa de informalidade (peso negativo)
            - 👥 IDH (peso positivo)
            - 🎓 Evasão escolar (peso negativo)
            - 💡 Investimento em inovação (peso positivo)
            """)

            st.dataframe(composite_index)
            UIComponents.create_download_button(
                composite_index,
                "ranking_composite.csv",
                label="📥 Download Ranking"
            )
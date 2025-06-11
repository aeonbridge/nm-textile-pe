import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
import random

from src.utils.page_utils import (Page, ChartGenerator, UIComponents, FilterManager, format_number, validate_data,
                       get_cities_list, filter_data_by_cities)
from src.nm.analytics import Analytics
from src.state import StateManager


class InteractiveAnalysisPage(Page):
    """Página de Análise Interativa Avançada"""

    def __init__(self):
        # Inicializar dados de sessão se não existirem
        if 'simulation_data' not in st.session_state:
            st.session_state.simulation_data = {}
        if 'comparison_cities' not in st.session_state:
            st.session_state.comparison_cities = []
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []

    def render(self, data: Dict[str, Any]):
        """Renderiza a página de análise interativa"""
        Analytics.log_event("page_view", {"page": "interactive_analysis"})
        StateManager.increment_page_view("Análise Interativa")

        st.markdown('<h2 class="page-header">🚀 Laboratório de Análise Interativa</h2>',
                    unsafe_allow_html=True)

        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px; color: white;">
        <h3>🔬 Explore, Compare e Simule</h3>
        <p>Este laboratório permite análises avançadas, simulações de cenários e comparações dinâmicas 
        para insights profundos sobre o ecossistema têxtil.</p>
        </div>
        """, unsafe_allow_html=True)

        # Carregar e preparar dados
        if not self._validate_basic_data(data):
            st.error("❌ Dados insuficientes para análises interativas.")
            return

        # Menu de análises
        analysis_mode = self._render_analysis_menu()

        # Renderizar análise selecionada
        if analysis_mode == "🎯 Análise Comparativa Dinâmica":
            self._render_dynamic_comparison_analysis(data)
        elif analysis_mode == "🔮 Simulador de Cenários":
            self._render_scenario_simulator(data)
        elif analysis_mode == "🎲 Explorador de Correlações":
            self._render_correlation_explorer(data)
        elif analysis_mode == "📊 Dashboard Personalizado":
            self._render_custom_dashboard(data)
        elif analysis_mode == "🌐 Análise de Rede Interativa":
            self._render_network_analysis(data)
        elif analysis_mode == "📈 Predictor de Tendências":
            self._render_trend_predictor(data)

    def _validate_basic_data(self, data: Dict[str, Any]) -> bool:
        """Valida se os dados básicos estão disponíveis"""
        required_keys = ['economicos', 'sociais']
        return all(key in data and not data[key].empty for key in required_keys)

    def _render_analysis_menu(self) -> str:
        """Renderiza menu de seleção de análises"""
        st.markdown("### 🎛️ Escolha sua Análise")
        
        analysis_options = [
            "🎯 Análise Comparativa Dinâmica",
            "🔮 Simulador de Cenários", 
            "🎲 Explorador de Correlações",
            "📊 Dashboard Personalizado",
            "🌐 Análise de Rede Interativa",
            "📈 Predictor de Tendências"
        ]

        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_analysis = st.selectbox(
                "Selecione o tipo de análise:",
                options=analysis_options,
                key="analysis_mode_selector"
            )

        with col2:
            if st.button("🔄 Nova Análise", key="reset_analysis"):
                # Limpar dados da sessão
                for key in ['simulation_data', 'comparison_cities', 'custom_metrics']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

        Analytics.log_event("analysis_mode_selected", {"mode": selected_analysis})
        return selected_analysis

    def _render_dynamic_comparison_analysis(self, data: Dict[str, Any]):
        """Análise comparativa dinâmica entre cidades"""
        st.markdown("---")
        st.markdown("## 🎯 Análise Comparativa Dinâmica")
        
        # Combinar datasets
        df_combined = self._combine_all_datasets(data)
        
        # Interface de seleção dinâmica
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Seletor de cidades para comparação
            available_cities = df_combined['cidade'].unique().tolist()
            selected_cities = st.multiselect(
                "🏘️ Cidades para Comparar:",
                options=available_cities,
                default=available_cities[:3] if len(available_cities) >= 3 else available_cities,
                key="comparison_cities_selector"
            )

        with col2:
            # Seletor de dimensões de análise
            analysis_dimensions = {
                "💰 Econômica": ['faturamento_anual_milhoes', 'pib_per_capita', 'empresas_totais'],
                "👥 Social": ['idh', 'taxa_pobreza', 'acesso_internet'], 
                "🌱 Ambiental": ['efluentes_tratados_percentual', 'energia_renovavel_percentual'],
                "🚀 Inovação": ['investimento_inovacao_percentual', 'empresas_com_ecommerce']
            }
            
            selected_dimension = st.selectbox(
                "📐 Dimensão de Análise:",
                options=list(analysis_dimensions.keys()),
                key="analysis_dimension"
            )

        with col3:
            # Tipo de visualização
            viz_types = {
                "📊 Barras Comparativas": "bar",
                "🕸️ Radar Multidimensional": "radar",
                "🎯 Scatter Matrix": "scatter_matrix",
                "📈 Séries Temporais": "time_series"
            }
            
            viz_type = st.selectbox(
                "📈 Tipo de Visualização:",
                options=list(viz_types.keys()),
                key="viz_type_selector"
            )

        if selected_cities:
            # Filtrar dados pelas cidades selecionadas
            df_filtered = df_combined[df_combined['cidade'].isin(selected_cities)]
            metrics = analysis_dimensions[selected_dimension]
            available_metrics = [m for m in metrics if m in df_filtered.columns]

            if available_metrics:
                # Renderizar visualização baseada na seleção
                if viz_types[viz_type] == "bar":
                    self._render_dynamic_bar_comparison(df_filtered, available_metrics, selected_cities)
                elif viz_types[viz_type] == "radar":
                    self._render_radar_comparison(df_filtered, available_metrics, selected_cities)
                elif viz_types[viz_type] == "scatter_matrix":
                    self._render_scatter_matrix(df_filtered, available_metrics, selected_cities)
                elif viz_types[viz_type] == "time_series":
                    self._render_simulated_time_series(df_filtered, available_metrics, selected_cities)

                # Insights automáticos
                self._render_automatic_insights(df_filtered, available_metrics, selected_cities)

    def _render_dynamic_bar_comparison(self, df: pd.DataFrame, metrics: List[str], cities: List[str]):
        """Renderiza comparação dinâmica em barras"""
        st.markdown("#### 📊 Comparação Dinâmica")
        
        # Normalizar dados para comparação
        df_normalized = df.copy()
        for metric in metrics:
            if metric in df.columns:
                df_normalized[f"{metric}_norm"] = (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min()) * 100

        # Criar visualização interativa
        fig = go.Figure()

        colors = px.colors.qualitative.Set1
        
        for i, metric in enumerate(metrics):
            if f"{metric}_norm" in df_normalized.columns:
                fig.add_trace(go.Bar(
                    name=metric.replace('_', ' ').title(),
                    x=df_normalized['cidade'],
                    y=df_normalized[f"{metric}_norm"],
                    marker_color=colors[i % len(colors)],
                    hovertemplate=f"<b>{metric.replace('_', ' ').title()}</b><br>" +
                                  "Cidade: %{x}<br>" +
                                  "Score Normalizado: %{y:.1f}<br>" +
                                  "Valor Original: %{customdata}<br>" +
                                  "<extra></extra>",
                    customdata=df_normalized[metric]
                ))

        fig.update_layout(
            title="Comparação Multidimensional (Valores Normalizados 0-100)",
            xaxis_title="Cidades",
            yaxis_title="Score Normalizado",
            barmode='group',
            height=500,
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Controles interativos de peso
        st.markdown("#### ⚖️ Ajuste de Pesos para Score Composto")
        weights = {}
        weight_cols = st.columns(len(metrics))
        
        for i, metric in enumerate(metrics):
            with weight_cols[i]:
                weights[metric] = st.slider(
                    f"{metric.replace('_', ' ').title()}",
                    min_value=0.0,
                    max_value=2.0,
                    value=1.0,
                    step=0.1,
                    key=f"weight_{metric}"
                )

        # Calcular score composto com pesos
        if any(weights.values()):
            df_weighted = df_normalized.copy()
            weighted_score = 0
            total_weight = 0
            
            for metric, weight in weights.items():
                if f"{metric}_norm" in df_weighted.columns and weight > 0:
                    weighted_score += df_weighted[f"{metric}_norm"] * weight
                    total_weight += weight
            
            if total_weight > 0:
                df_weighted['score_composto'] = weighted_score / total_weight
                
                # Gráfico do score composto
                fig_composite = px.bar(
                    df_weighted.sort_values('score_composto', ascending=False),
                    x='score_composto',
                    y='cidade',
                    orientation='h',
                    title="🏆 Ranking por Score Composto Personalizado",
                    color='score_composto',
                    color_continuous_scale='Viridis'
                )
                
                fig_composite.update_layout(height=300)
                st.plotly_chart(fig_composite, use_container_width=True)

    def _render_scenario_simulator(self, data: Dict[str, Any]):
        """Simulador de cenários interativo"""
        st.markdown("---")
        st.markdown("## 🔮 Simulador de Cenários")
        
        df_combined = self._combine_all_datasets(data)
        
        # Interface do simulador
        st.markdown("### 🎛️ Configure seu Cenário")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleção de cidade base
            base_city = st.selectbox(
                "🏘️ Cidade Base para Simulação:",
                options=df_combined['cidade'].unique(),
                key="base_city_simulator"
            )
            
            # Horizonte temporal
            time_horizon = st.selectbox(
                "⏰ Horizonte de Simulação:",
                options=["📅 1 ano", "📅 3 anos", "📅 5 anos", "📅 10 anos"],
                key="time_horizon"
            )
            
        with col2:
            # Tipo de cenário
            scenario_type = st.selectbox(
                "📈 Tipo de Cenário:",
                options=[
                    "🚀 Crescimento Acelerado",
                    "📊 Crescimento Moderado", 
                    "⚖️ Cenário Conservador",
                    "⚠️ Cenário de Crise",
                    "🎯 Cenário Personalizado"
                ],
                key="scenario_type"
            )

        # Parâmetros de simulação
        if scenario_type == "🎯 Cenário Personalizado":
            st.markdown("#### 🎚️ Parâmetros Personalizados")
            
            param_cols = st.columns(4)
            
            simulation_params = {}
            with param_cols[0]:
                simulation_params['economic_growth'] = st.slider(
                    "💰 Crescimento Econômico (%/ano)", -10, 50, 5, 1, key="econ_growth"
                )
                
            with param_cols[1]:
                simulation_params['innovation_factor'] = st.slider(
                    "🚀 Fator Inovação", 0.5, 3.0, 1.0, 0.1, key="innovation_factor"
                )
                
            with param_cols[2]:
                simulation_params['sustainability_improvement'] = st.slider(
                    "🌱 Melhoria Ambiental (%/ano)", -5, 20, 2, 1, key="sustainability"
                )
                
            with param_cols[3]:
                simulation_params['social_development'] = st.slider(
                    "👥 Desenvolvimento Social (%/ano)", -5, 15, 3, 1, key="social_dev"
                )
        else:
            # Parâmetros predefinidos por tipo de cenário
            simulation_params = self._get_predefined_scenario_params(scenario_type)

        # Executar simulação
        if st.button("🚀 Executar Simulação", key="run_simulation"):
            simulated_data = self._run_scenario_simulation(
                df_combined, base_city, time_horizon, simulation_params
            )
            
            # Armazenar na sessão
            st.session_state.simulation_data = simulated_data
            
            Analytics.log_event("scenario_simulation", {
                "base_city": base_city,
                "scenario_type": scenario_type,
                "time_horizon": time_horizon
            })

        # Exibir resultados da simulação
        if 'simulation_data' in st.session_state and st.session_state.simulation_data:
            self._render_simulation_results(st.session_state.simulation_data)

    def _render_correlation_explorer(self, data: Dict[str, Any]):
        """Explorador de correlações interativo"""
        st.markdown("---")
        st.markdown("## 🎲 Explorador de Correlações")
        
        df_combined = self._combine_all_datasets(data)
        numeric_cols = df_combined.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remover colunas não relevantes
        exclude_cols = ['lat', 'lon']
        numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        if len(numeric_cols) < 2:
            st.warning("Dados insuficientes para análise de correlações.")
            return

        # Interface de exploração
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Seleção de variáveis
            selected_vars = st.multiselect(
                "📊 Variáveis para Análise:",
                options=numeric_cols,
                default=numeric_cols[:8] if len(numeric_cols) >= 8 else numeric_cols,
                key="correlation_vars"
            )
            
        with col2:
            # Método de correlação
            correlation_method = st.selectbox(
                "🔢 Método de Correlação:",
                options=["pearson", "spearman", "kendall"],
                key="correlation_method"
            )
            
        with col3:
            # Filtro de força de correlação
            min_correlation = st.slider(
                "🎯 Correlação Mínima:",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1,
                key="min_correlation"
            )

        if selected_vars and len(selected_vars) >= 2:
            # Calcular matriz de correlação
            corr_matrix = df_combined[selected_vars].corr(method=correlation_method)
            
            # Visualização da matriz de correlação
            self._render_interactive_correlation_matrix(corr_matrix, min_correlation)
            
            # Análise de correlações fortes
            self._render_strong_correlations_analysis(corr_matrix, min_correlation, selected_vars)
            
            # Explorador de relações específicas
            self._render_relationship_explorer(df_combined, selected_vars)

    def _render_custom_dashboard(self, data: Dict[str, Any]):
        """Dashboard personalizável pelo usuário"""
        st.markdown("---")
        st.markdown("## 📊 Dashboard Personalizado")
        
        # Construtor de dashboard
        st.markdown("### 🔧 Construtor de Dashboard")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 📝 Configurações")
            
            # Layout do dashboard
            dashboard_layout = st.selectbox(
                "📐 Layout:",
                options=["2 colunas", "3 colunas", "1 coluna principal + lateral", "Grid 2x2"],
                key="dashboard_layout"
            )
            
            # Seleção de widgets
            available_widgets = [
                "📊 Gráfico de Barras",
                "📈 Gráfico de Linhas", 
                "🥧 Gráfico de Pizza",
                "🔢 Métricas Numéricas",
                "🗺️ Mapa de Calor",
                "📋 Tabela de Dados",
                "🎯 Gauge Chart",
                "🌐 Gráfico de Rede"
            ]
            
            selected_widgets = st.multiselect(
                "🧩 Widgets para Incluir:",
                options=available_widgets,
                default=available_widgets[:4],
                key="dashboard_widgets"
            )
            
            # Tema do dashboard
            dashboard_theme = st.selectbox(
                "🎨 Tema:",
                options=["🌅 Claro", "🌙 Escuro", "🌈 Colorido", "📊 Profissional"],
                key="dashboard_theme"
            )
            
            if st.button("🔄 Gerar Dashboard", key="generate_dashboard"):
                st.session_state.custom_dashboard_config = {
                    'layout': dashboard_layout,
                    'widgets': selected_widgets,
                    'theme': dashboard_theme
                }
                st.rerun()
        
        with col2:
            # Área de preview do dashboard
            if 'custom_dashboard_config' in st.session_state:
                self._render_custom_dashboard_preview(data, st.session_state.custom_dashboard_config)
            else:
                st.info("👈 Configure seu dashboard e clique em 'Gerar Dashboard' para ver o preview.")

    def _render_network_analysis(self, data: Dict[str, Any]):
        """Análise de rede interativa"""
        st.markdown("---")
        st.markdown("## 🌐 Análise de Rede Interativa")
        
        # Criar rede baseada em similaridades entre cidades
        df_combined = self._combine_all_datasets(data)
        
        # Interface de configuração da rede
        col1, col2, col3 = st.columns(3)
        
        with col1:
            network_metric = st.selectbox(
                "📏 Métrica para Conexões:",
                options=[
                    "💰 Similaridade Econômica",
                    "👥 Similaridade Social",
                    "🌱 Similaridade Ambiental",
                    "🚀 Similaridade em Inovação",
                    "🔄 Similaridade Geral"
                ],
                key="network_metric"
            )
            
        with col2:
            similarity_threshold = st.slider(
                "🎯 Threshold de Similaridade:",
                min_value=0.1,
                max_value=0.9,
                value=0.6,
                step=0.1,
                key="similarity_threshold"
            )
            
        with col3:
            network_layout = st.selectbox(
                "🕸️ Layout da Rede:",
                options=["spring", "circular", "kamada_kawai", "random"],
                key="network_layout"
            )

        # Gerar e visualizar rede
        network_data = self._generate_similarity_network(df_combined, network_metric, similarity_threshold)
        self._render_interactive_network(network_data, network_layout)

    def _render_trend_predictor(self, data: Dict[str, Any]):
        """Preditor de tendências com análise temporal"""
        st.markdown("---")
        st.markdown("## 📈 Predictor de Tendências")
        
        # Simular dados históricos e projeções
        df_combined = self._combine_all_datasets(data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_city = st.selectbox(
                "🏘️ Cidade para Análise:",
                options=df_combined['cidade'].unique(),
                key="trend_city"
            )
            
            target_metric = st.selectbox(
                "📊 Métrica para Previsão:",
                options=[
                    "faturamento_anual_milhoes",
                    "empresas_totais", 
                    "empregos_diretos",
                    "idh",
                    "investimento_inovacao_percentual"
                ],
                key="trend_metric"
            )
            
        with col2:
            prediction_years = st.slider(
                "📅 Anos para Previsão:",
                min_value=1,
                max_value=10,
                value=5,
                key="prediction_years"
            )
            
            confidence_level = st.selectbox(
                "📊 Nível de Confiança:",
                options=["90%", "95%", "99%"],
                key="confidence_level"
            )

        if st.button("🔮 Gerar Previsão", key="generate_prediction"):
            # Gerar dados históricos simulados e previsão
            historical_data, prediction_data = self._generate_trend_prediction(
                df_combined, target_city, target_metric, prediction_years
            )
            
            # Visualizar tendência e previsão
            self._render_trend_visualization(historical_data, prediction_data, target_metric, target_city)

    # Métodos auxiliares para as análises

    def _combine_all_datasets(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Combina todos os datasets disponíveis"""
        df_base = data['economicos'].copy()
        
        # Adicionar empresas totais
        if 'empresas_formais' in df_base.columns and 'empresas_informais' in df_base.columns:
            df_base['empresas_totais'] = df_base['empresas_formais'] + df_base['empresas_informais']
        
        # Mesclar outros datasets
        for key in ['sociais', 'ambientais', 'inovacao']:
            if key in data and not data[key].empty:
                df_base = df_base.merge(data[key], on='cidade', how='left', suffixes=('', f'_{key}'))
        
        return df_base

    def _render_radar_comparison(self, df: pd.DataFrame, metrics: List[str], cities: List[str]):
        """Renderiza comparação em radar chart"""
        # Normalizar dados
        df_norm = df.copy()
        for metric in metrics:
            if metric in df.columns:
                df_norm[metric] = (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min())

        fig = go.Figure()
        colors = px.colors.qualitative.Set1

        for i, city in enumerate(cities):
            city_data = df_norm[df_norm['cidade'] == city]
            if not city_data.empty:
                values = [city_data[metric].iloc[0] if metric in city_data.columns else 0 for metric in metrics]
                values.append(values[0])  # Fechar o radar
                
                labels = [metric.replace('_', ' ').title() for metric in metrics]
                labels.append(labels[0])
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=labels,
                    fill='toself',
                    name=city,
                    line_color=colors[i % len(colors)]
                ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            title="🕸️ Comparação Multidimensional (Radar)",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_automatic_insights(self, df: pd.DataFrame, metrics: List[str], cities: List[str]):
        """Gera insights automáticos baseados nos dados"""
        st.markdown("#### 🧠 Insights Automáticos")
        
        insights = []
        
        for metric in metrics:
            if metric in df.columns:
                max_city = df.loc[df[metric].idxmax(), 'cidade']
                min_city = df.loc[df[metric].idxmin(), 'cidade']
                max_val = df[metric].max()
                min_val = df[metric].min()
                
                if max_val != min_val:
                    diff_percent = ((max_val - min_val) / min_val) * 100
                    insights.append(
                        f"📊 **{metric.replace('_', ' ').title()}**: "
                        f"{max_city} lidera com {format_number(max_val)}, "
                        f"{diff_percent:.1f}% superior a {min_city}"
                    )

        for insight in insights[:3]:  # Mostrar apenas os 3 primeiros
            st.markdown(f"• {insight}")

    def _get_predefined_scenario_params(self, scenario_type: str) -> Dict[str, float]:
        """Retorna parâmetros predefinidos para tipos de cenário"""
        scenarios = {
            "🚀 Crescimento Acelerado": {
                'economic_growth': 15,
                'innovation_factor': 2.0,
                'sustainability_improvement': 8,
                'social_development': 10
            },
            "📊 Crescimento Moderado": {
                'economic_growth': 5,
                'innovation_factor': 1.2,
                'sustainability_improvement': 3,
                'social_development': 4
            },
            "⚖️ Cenário Conservador": {
                'economic_growth': 2,
                'innovation_factor': 1.0,
                'sustainability_improvement': 1,
                'social_development': 2
            },
            "⚠️ Cenário de Crise": {
                'economic_growth': -5,
                'innovation_factor': 0.8,
                'sustainability_improvement': -2,
                'social_development': -1
            }
        }
        return scenarios.get(scenario_type, scenarios["📊 Crescimento Moderado"])

    def _run_scenario_simulation(self, df: pd.DataFrame, base_city: str, time_horizon: str, params: Dict[str, float]) -> Dict[str, Any]:
        """Executa simulação de cenário"""
        years = int(time_horizon.split()[0])
        city_data = df[df['cidade'] == base_city].iloc[0].to_dict()
        
        # Simular evolução ao longo dos anos
        simulation_results = []
        
        for year in range(years + 1):
            year_data = {'year': 2024 + year}
            
            for key, value in city_data.items():
                if isinstance(value, (int, float)) and key != 'cidade':
                    # Aplicar crescimento/mudança baseado nos parâmetros
                    if 'faturamento' in key or 'pib' in key:
                        growth_rate = params['economic_growth'] / 100
                    elif 'inovacao' in key or 'ecommerce' in key:
                        growth_rate = params['innovation_factor'] - 1
                    elif 'ambiental' in key or 'energia' in key:
                        growth_rate = params['sustainability_improvement'] / 100
                    elif 'idh' in key or 'pobreza' in key:
                        growth_rate = params['social_development'] / 100
                    else:
                        growth_rate = params['economic_growth'] / 200  # Crescimento mais conservador
                    
                    # Aplicar variabilidade aleatória
                    random_factor = 1 + random.uniform(-0.1, 0.1)
                    year_data[key] = value * ((1 + growth_rate) ** year) * random_factor
            
            simulation_results.append(year_data)
        
        return {
            'base_city': base_city,
            'scenario_params': params,
            'results': simulation_results
        }

    def _render_simulation_results(self, simulation_data: Dict[str, Any]):
        """Renderiza resultados da simulação"""
        st.markdown("#### 📊 Resultados da Simulação")
        
        results_df = pd.DataFrame(simulation_data['results'])
        base_city = simulation_data['base_city']
        
        # Métricas principais para visualizar
        key_metrics = [
            'faturamento_anual_milhoes',
            'empresas_totais', 
            'empregos_diretos',
            'idh'
        ]
        
        available_metrics = [m for m in key_metrics if m in results_df.columns]
        
        if available_metrics:
            # Gráfico de evolução temporal
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[metric.replace('_', ' ').title() for metric in available_metrics[:4]],
                vertical_spacing=0.1
            )
            
            for i, metric in enumerate(available_metrics[:4]):
                row = (i // 2) + 1
                col = (i % 2) + 1
                
                fig.add_trace(
                    go.Scatter(
                        x=results_df['year'],
                        y=results_df[metric],
                        mode='lines+markers',
                        name=metric.replace('_', ' ').title(),
                        line=dict(width=3)
                    ),
                    row=row, col=col
                )
            
            fig.update_layout(
                title=f"🔮 Projeção para {base_city}",
                height=600,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela de resultados
            st.markdown("#### 📋 Dados Detalhados da Simulação")
            st.dataframe(results_df.round(2), use_container_width=True)
            
            # Download dos resultados
            csv_data = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Resultados CSV",
                data=csv_data.encode('utf-8'),
                file_name=f'simulacao_{base_city}_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                key="download_simulation"
            )

    def _render_interactive_correlation_matrix(self, corr_matrix: pd.DataFrame, min_correlation: float):
        """Renderiza matriz de correlação interativa"""
        st.markdown("#### 🔥 Matriz de Correlação Interativa")
        
        # Filtrar correlações fracas
        mask = np.abs(corr_matrix) >= min_correlation
        filtered_corr = corr_matrix.where(mask, 0)
        
        fig = go.Figure(data=go.Heatmap(
            z=filtered_corr.values,
            x=filtered_corr.columns,
            y=filtered_corr.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(filtered_corr.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=f"Correlações ≥ {min_correlation}",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def _render_custom_dashboard_preview(self, data: Dict[str, Any], config: Dict[str, Any]):
        """Renderiza preview do dashboard personalizado"""
        st.markdown("#### 📱 Preview do Dashboard")
        
        df_combined = self._combine_all_datasets(data)
        
        # Aplicar layout
        if config['layout'] == "2 colunas":
            col1, col2 = st.columns(2)
            widget_cols = [col1, col2] * (len(config['widgets']) // 2 + 1)
        elif config['layout'] == "3 colunas":
            col1, col2, col3 = st.columns(3)
            widget_cols = [col1, col2, col3] * (len(config['widgets']) // 3 + 1)
        else:
            widget_cols = [st] * len(config['widgets'])
        
        # Renderizar widgets selecionados
        for i, widget in enumerate(config['widgets']):
            with widget_cols[i]:
                if widget == "📊 Gráfico de Barras":
                    fig = px.bar(df_combined, x='cidade', y='faturamento_anual_milhoes', 
                               title="Faturamento por Cidade")
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif widget == "🔢 Métricas Numéricas":
                    total_revenue = df_combined['faturamento_anual_milhoes'].sum()
                    st.metric("💰 Faturamento Total", f"R$ {total_revenue:.1f}M")
                    
                elif widget == "📋 Tabela de Dados":
                    st.dataframe(df_combined.head(), use_container_width=True)

    def _generate_similarity_network(self, df: pd.DataFrame, metric_type: str, threshold: float) -> Dict[str, Any]:
        """Gera rede baseada em similaridades"""
        # Implementação simplificada - retorna dados estruturados para visualização
        cities = df['cidade'].tolist()
        
        # Calcular similaridades (simulado)
        edges = []
        for i, city1 in enumerate(cities):
            for j, city2 in enumerate(cities[i+1:], i+1):
                similarity = random.uniform(0, 1)  # Simulado
                if similarity >= threshold:
                    edges.append({
                        'source': city1,
                        'target': city2,
                        'weight': similarity
                    })
        
        return {
            'nodes': [{'id': city, 'label': city} for city in cities],
            'edges': edges
        }

    def _render_interactive_network(self, network_data: Dict[str, Any], layout: str):
        """Renderiza rede interativa"""
        st.markdown("#### 🕸️ Rede de Similaridades")
        
        if network_data['edges']:
            # Criar visualização de rede simplificada
            fig = go.Figure()
            
            # Adicionar edges
            for edge in network_data['edges']:
                fig.add_trace(go.Scatter(
                    x=[0, 1], y=[0, 1],  # Posições simplificadas
                    mode='lines',
                    line=dict(width=edge['weight']*5),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Adicionar nós
            fig.add_trace(go.Scatter(
                x=[0.5] * len(network_data['nodes']),
                y=list(range(len(network_data['nodes']))),
                mode='markers+text',
                text=[node['label'] for node in network_data['nodes']],
                textposition="middle center",
                marker=dict(size=20, color='lightblue'),
                showlegend=False
            ))
            
            fig.update_layout(
                title="Rede de Conexões entre Cidades",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma conexão forte encontrada com o threshold atual.")

    def _generate_trend_prediction(self, df: pd.DataFrame, city: str, metric: str, years: int):
        """Gera dados históricos simulados e previsão"""
        # Dados históricos simulados (últimos 5 anos)
        current_value = df[df['cidade'] == city][metric].iloc[0]
        
        historical_years = list(range(2019, 2024))
        historical_values = []
        
        # Simular histórico com tendência crescente e variabilidade
        for i, year in enumerate(historical_years):
            base_value = current_value * (0.85 + i * 0.05)  # Crescimento gradual
            noise = random.uniform(-0.1, 0.1) * base_value
            historical_values.append(base_value + noise)
        
        # Previsão futura
        future_years = list(range(2024, 2024 + years + 1))
        future_values = []
        
        growth_rate = 0.05  # 5% ao ano
        for i, year in enumerate(future_years):
            predicted_value = current_value * ((1 + growth_rate) ** i)
            future_values.append(predicted_value)
        
        historical_data = pd.DataFrame({
            'year': historical_years,
            'value': historical_values,
            'type': 'Histórico'
        })
        
        prediction_data = pd.DataFrame({
            'year': future_years,
            'value': future_values,
            'type': 'Previsão'
        })
        
        return historical_data, prediction_data

    def _render_trend_visualization(self, historical_data: pd.DataFrame, prediction_data: pd.DataFrame, 
                                  metric: str, city: str):
        """Renderiza visualização de tendência e previsão"""
        st.markdown("#### 📈 Análise de Tendência e Previsão")
        
        fig = go.Figure()
        
        # Dados históricos
        fig.add_trace(go.Scatter(
            x=historical_data['year'],
            y=historical_data['value'],
            mode='lines+markers',
            name='Dados Históricos',
            line=dict(color='blue', width=3)
        ))
        
        # Previsão
        fig.add_trace(go.Scatter(
            x=prediction_data['year'],
            y=prediction_data['value'],
            mode='lines+markers',
            name='Previsão',
            line=dict(color='red', width=3, dash='dash')
        ))
        
        fig.update_layout(
            title=f"📊 Tendência e Previsão: {metric.replace('_', ' ').title()} - {city}",
            xaxis_title="Ano",
            yaxis_title=metric.replace('_', ' ').title(),
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas da previsão
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current_val = prediction_data['value'].iloc[0]
            st.metric("📊 Valor Atual", f"{current_val:.2f}")
            
        with col2:
            future_val = prediction_data['value'].iloc[-1]
            growth = ((future_val - current_val) / current_val) * 100
            st.metric("🔮 Valor Projetado", f"{future_val:.2f}", f"{growth:.1f}%")
            
        with col3:
            avg_growth = (prediction_data['value'].pct_change().mean()) * 100
            st.metric("📈 Crescimento Médio/Ano", f"{avg_growth:.1f}%")

    def _render_scatter_matrix(self, df: pd.DataFrame, metrics: List[str], cities: List[str]):
        """Renderiza matriz de dispersão"""
        if len(metrics) < 2:
            st.warning("Selecione pelo menos 2 métricas para matriz de dispersão.")
            return
            
        fig = make_subplots(
            rows=len(metrics), cols=len(metrics),
            subplot_titles=[f"{m1} vs {m2}" for m1 in metrics for m2 in metrics]
        )
        
        colors = px.colors.qualitative.Set1
        
        for i, metric1 in enumerate(metrics):
            for j, metric2 in enumerate(metrics):
                if i != j and metric1 in df.columns and metric2 in df.columns:
                    for k, city in enumerate(cities):
                        city_data = df[df['cidade'] == city]
                        if not city_data.empty:
                            fig.add_trace(
                                go.Scatter(
                                    x=city_data[metric1],
                                    y=city_data[metric2],
                                    mode='markers',
                                    name=city,
                                    marker=dict(color=colors[k % len(colors)], size=10),
                                    showlegend=(i==0 and j==1)
                                ),
                                row=i+1, col=j+1
                            )
        
        fig.update_layout(height=600, title="🎯 Matriz de Dispersão")
        st.plotly_chart(fig, use_container_width=True)

    def _render_simulated_time_series(self, df: pd.DataFrame, metrics: List[str], cities: List[str]):
        """Renderiza séries temporais simuladas"""
        st.markdown("#### 📈 Evolução Temporal Simulada")
        
        # Gerar dados temporais simulados
        years = list(range(2020, 2025))
        
        fig = go.Figure()
        colors = px.colors.qualitative.Set1
        
        for i, city in enumerate(cities):
            city_data = df[df['cidade'] == city]
            if not city_data.empty and metrics[0] in city_data.columns:
                base_value = city_data[metrics[0]].iloc[0]
                
                # Simular evolução temporal
                values = []
                for j, year in enumerate(years):
                    growth_factor = 1 + (j * 0.05) + random.uniform(-0.1, 0.1)
                    values.append(base_value * growth_factor)
                
                fig.add_trace(go.Scatter(
                    x=years,
                    y=values,
                    mode='lines+markers',
                    name=city,
                    line=dict(color=colors[i % len(colors)], width=3)
                ))
        
        fig.update_layout(
            title=f"Evolução de {metrics[0].replace('_', ' ').title()}",
            xaxis_title="Ano",
            yaxis_title=metrics[0].replace('_', ' ').title(),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def _render_relationship_explorer(self, df: pd.DataFrame, variables: List[str]):
        """Explorador de relações específicas entre variáveis"""
        st.markdown("#### 🔍 Explorador de Relações Específicas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            x_var = st.selectbox("📊 Variável X:", options=variables, key="x_var_explorer")
        with col2:
            y_var = st.selectbox("📊 Variável Y:", options=variables, key="y_var_explorer", 
                                index=1 if len(variables) > 1 else 0)
        
        if x_var != y_var and x_var in df.columns and y_var in df.columns:
            # Scatter plot interativo
            fig = px.scatter(
                df,
                x=x_var,
                y=y_var,
                color='cidade',
                size=df[variables[0]] if variables[0] in df.columns else None,
                hover_data=['cidade'],
                title=f"🎯 Relação: {x_var.replace('_', ' ').title()} vs {y_var.replace('_', ' ').title()}",
                trendline="ols"
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas da correlação
            correlation = df[x_var].corr(df[y_var])
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("🔗 Correlação", f"{correlation:.3f}")
            with col_stat2:
                strength = "Forte" if abs(correlation) > 0.7 else "Moderada" if abs(correlation) > 0.3 else "Fraca"
                st.metric("💪 Força", strength)
            with col_stat3:
                direction = "Positiva" if correlation > 0 else "Negativa"
                st.metric("🔄 Direção", direction)

    def _render_strong_correlations_analysis(self, corr_matrix: pd.DataFrame, min_correlation: float, variables: List[str]):
        """Análise de correlações fortes"""
        st.markdown("#### 🔥 Correlações Mais Fortes")
        
        # Encontrar correlações fortes
        strong_correlations = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= min_correlation:
                    strong_correlations.append({
                        'Variável 1': corr_matrix.columns[i],
                        'Variável 2': corr_matrix.columns[j],
                        'Correlação': corr_value,
                        'Força': abs(corr_value)
                    })
        
        if strong_correlations:
            strong_corr_df = pd.DataFrame(strong_correlations)
            strong_corr_df = strong_corr_df.sort_values('Força', ascending=False)
            
            # Top 5 correlações
            st.dataframe(
                strong_corr_df.head().round(3),
                use_container_width=True,
                hide_index=True
            )
            
            # Visualização das top correlações
            if len(strong_corr_df) > 0:
                top_corr = strong_corr_df.iloc[0]
                st.markdown(f"**🏆 Correlação Mais Forte:** {top_corr['Variável 1']} ↔ {top_corr['Variável 2']} ({top_corr['Correlação']:.3f})")
        else:
            st.info("Nenhuma correlação forte encontrada com o threshold atual.")

    def write(self):
        """Método de compatibilidade com a interface Page"""
        pass
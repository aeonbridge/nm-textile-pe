import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
import numpy as np

from src.utils.page_utils import (Page, ChartGenerator, UIComponents, FilterManager, format_number, validate_data,
                       get_cities_list, filter_data_by_cities)
from src.nm.analytics import Analytics
from src.state import StateManager


class GeographicMapboxPage(Page):
    """Página de Análise Geográfica com Mapbox"""

    def render(self, data: Dict[str, Any]):
        """Renderiza a página de análise geográfica"""
        Analytics.log_event("page_view", {"page": "geographic_mapbox"})
        StateManager.increment_page_view("Análise Geográfica")

        st.markdown('<h2 class="page-header">🗺️ Análise Geográfica do Polo Têxtil</h2>',
                    unsafe_allow_html=True)

        # Carregar dados
        df_economic = data.get('economicos', pd.DataFrame())
        df_social = data.get('sociais', pd.DataFrame())
        df_environmental = data.get('ambientais', pd.DataFrame())
        df_innovation = data.get('inovacao', pd.DataFrame())

        if df_economic.empty:
            st.warning("⚠️ Dados econômicos não disponíveis. Usando dados simulados.")
            return

        # Filtros globais
        filtered_data = self._render_global_filters(data)

        # Layout principal
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Mapa principal com Mapbox
            self._render_mapbox_visualization(filtered_data)
        
        with col2:
            # Painel de controle e métricas
            self._render_control_panel(filtered_data)

        # Análises geográficas detalhadas
        self._render_geographic_analysis(filtered_data)

        # Comparativo regional
        self._render_regional_comparison(filtered_data)

    def _render_global_filters(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Renderiza filtros globais e retorna dados filtrados"""
        st.markdown("### 🎛️ Configurações de Visualização")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Filtro de cidades
            all_cities = get_cities_list(data['economicos'])
            default_cities = ["Santa Cruz do Capibaribe", "Caruaru", "Toritama"]
            selected_cities = st.multiselect(
                "🏘️ Cidades:",
                options=all_cities,
                default=[city for city in default_cities if city in all_cities],
                key="mapbox_cities_filter"
            )

        with col2:
            # Indicador para tamanho dos marcadores
            size_indicators = {
                "Faturamento (R$ Milhões)": "faturamento_anual_milhoes",
                "Empresas Totais": "empresas_totais", 
                "Empregos Diretos": "empregos_diretos",
                "População": "populacao",
                "PIB per capita": "pib_per_capita"
            }

            size_indicator = st.selectbox(
                "📏 Tamanho dos Marcadores:",
                options=list(size_indicators.keys()),
                index=0,
                key="mapbox_size_indicator"
            )

        with col3:
            # Indicador para cor dos marcadores
            color_indicators = {
                "Taxa de Informalidade": "taxa_informalidade",
                "IDH": "idh",
                "Taxa de Pobreza": "taxa_pobreza",
                "Acesso à Internet": "acesso_internet",
                "Investimento em Inovação": "investimento_inovacao_percentual",
                "Exportação (%)": "exportacao_percentual"
            }

            color_indicator = st.selectbox(
                "🎨 Cor dos Marcadores:",
                options=list(color_indicators.keys()),
                index=0,
                key="mapbox_color_indicator"
            )

        with col4:
            # Estilo do mapa
            map_styles = {
                "🌍 Open Street Map": "open-street-map",
                "🛰️ Satellite": "satellite", 
                "🗺️ Satellite Streets": "satellite-streets",
                "☀️ Light": "light",
                "🌙 Dark": "dark",
                "🏞️ Outdoors": "outdoors"
            }

            map_style = st.selectbox(
                "🎭 Estilo do Mapa:",
                options=list(map_styles.keys()),
                index=0,
                key="mapbox_style"
            )

        # Controles avançados
        st.markdown("#### ⚙️ Configurações Avançadas")
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            # Escala de cores
            color_scales = {
                "🌈 Viridis": "Viridis",
                "🔥 Plasma": "Plasma", 
                "🌊 Blues": "Blues",
                "🍃 Greens": "Greens",
                "🌅 Sunset": "Sunset",
                "❄️ Ice": "ice",
                "🎨 Turbo": "Turbo"
            }
            
            color_scale = st.selectbox(
                "🎨 Escala de Cores:",
                options=list(color_scales.keys()),
                index=0,
                key="mapbox_colorscale"
            )
            
        with col6:
            # Opacidade dos marcadores
            marker_opacity = st.slider(
                "🔍 Transparência:",
                min_value=0.3,
                max_value=1.0,
                value=0.8,
                step=0.1,
                key="mapbox_opacity"
            )
            
        with col7:
            # Tamanho mínimo/máximo dos marcadores
            size_range = st.slider(
                "📐 Faixa de Tamanho:",
                min_value=10,
                max_value=100,
                value=(20, 60),
                step=5,
                key="mapbox_size_range"
            )
            
        with col8:
            # Símbolo dos marcadores
            marker_symbols = {
                "⭕ Círculo": "circle",
                "📍 Marcador": "marker", 
                "⭐ Estrela": "star",
                "💎 Diamante": "diamond",
                "⬜ Quadrado": "square"
            }
            
            marker_symbol = st.selectbox(
                "🎯 Símbolo:",
                options=list(marker_symbols.keys()),
                index=0,
                key="mapbox_symbol"
            )

        # Aplicar filtros aos dados
        filtered_data = {}
        for key, df in data.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                filtered_data[key] = filter_data_by_cities(df, selected_cities)

        # Adicionar configurações de visualização
        filtered_data['config'] = {
            'size_indicator': size_indicators[size_indicator],
            'size_indicator_name': size_indicator,
            'color_indicator': color_indicators.get(color_indicator),
            'color_indicator_name': color_indicator,
            'map_style': map_styles[map_style],
            'color_scale': color_scales[color_scale],
            'marker_opacity': marker_opacity,
            'size_range': size_range,
            'marker_symbol': marker_symbols[marker_symbol]
        }

        # Combinar dados para visualização
        if all(key in filtered_data for key in ['economicos', 'sociais']):
            combined_df = self._combine_datasets(filtered_data)
            filtered_data['combined'] = combined_df

        Analytics.log_event("geographic_filters_applied", {
            "cities_count": len(selected_cities),
            "size_indicator": size_indicator,
            "color_indicator": color_indicator,
            "map_style": map_style
        })

        return filtered_data

    def _combine_datasets(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Combina datasets para visualização unificada"""
        df_econ = data['economicos'].copy()
        df_social = data.get('sociais', pd.DataFrame())
        df_env = data.get('ambientais', pd.DataFrame())
        df_innov = data.get('inovacao', pd.DataFrame())

        # Adicionar colunas calculadas
        if 'empresas_formais' in df_econ.columns and 'empresas_informais' in df_econ.columns:
            df_econ['empresas_totais'] = df_econ['empresas_formais'] + df_econ['empresas_informais']

        # Mesclar com dados sociais
        if not df_social.empty:
            df_econ = df_econ.merge(df_social, on='cidade', how='left', suffixes=('', '_social'))

        # Mesclar com dados ambientais
        if not df_env.empty:
            df_econ = df_econ.merge(df_env, on='cidade', how='left', suffixes=('', '_env'))

        # Mesclar com dados de inovação
        if not df_innov.empty:
            df_econ = df_econ.merge(df_innov, on='cidade', how='left', suffixes=('', '_innov'))

        return df_econ

    def _render_mapbox_visualization(self, data: Dict[str, Any]):
        """Renderiza visualização principal com Mapbox"""
        st.markdown("#### 🗺️ Visualização Geográfica Interativa")

        if 'combined' not in data:
            st.warning("Dados insuficientes para visualização geográfica.")
            return

        df = data['combined']
        config = data['config']

        # Coordenadas das cidades do polo têxtil
        city_coordinates = {
            'Santa Cruz do Capibaribe': {'lat': -7.9557, 'lon': -36.2085},
            'Caruaru': {'lat': -8.2837, 'lon': -35.9761},
            'Toritama': {'lat': -8.0108, 'lon': -36.0564},
            'Surubim': {'lat': -7.8312, 'lon': -35.7642},
            'Vertentes': {'lat': -7.9033, 'lon': -35.9789}
        }

        # Adicionar coordenadas ao DataFrame
        df['lat'] = df['cidade'].map(lambda x: city_coordinates.get(x, {}).get('lat', -8.1))
        df['lon'] = df['cidade'].map(lambda x: city_coordinates.get(x, {}).get('lon', -36.0))

        # Preparar dados para o mapa
        size_col = config['size_indicator']
        color_col = config['color_indicator']

        # Criar hover template personalizado
        hover_template = "<b>%{customdata[0]}</b><br><br>"
        
        # Adicionar métricas principais ao hover
        metrics_to_show = [
            ('População', 'populacao'),
            ('Empresas Totais', 'empresas_totais'),
            ('Faturamento (R$ M)', 'faturamento_anual_milhoes'),
            ('Empregos Diretos', 'empregos_diretos'),
            ('PIB per capita (R$)', 'pib_per_capita')
        ]

        customdata_cols = ['cidade']
        for label, col in metrics_to_show:
            if col in df.columns:
                customdata_cols.append(col)
                hover_template += f"{label}: %{{customdata[{len(customdata_cols)-1}]}}<br>"

        hover_template += "<extra></extra>"

        # Preparar dados customizados para hover
        customdata = df[customdata_cols].values

        # Criar o mapa
        fig = go.Figure()

        # Configurar propriedades dos marcadores com base nas configurações
        marker_props = dict(
            size=self._normalize_sizes(df[size_col], config['size_range'][0], config['size_range'][1]) if size_col in df.columns else 25,
            sizemode='diameter',
            opacity=config['marker_opacity'],
            symbol=config['marker_symbol']
        )
        
        # Configurar cores se indicador de cor está disponível
        if color_col and color_col in df.columns:
            color_values = df[color_col]
            marker_props.update({
                'color': color_values,
                'colorscale': config['color_scale'],
                'showscale': True,
                'colorbar': dict(
                    title=dict(
                        text=config['color_indicator_name'],
                        font=dict(size=12)
                    ),
                    thickness=15,
                    len=0.7,
                    x=1.02,
                    xanchor="left",
                    tickfont=dict(size=10)
                ),
                'cmin': color_values.min(),
                'cmax': color_values.max(),
                'reversescale': False
            })
        else:
            # Cores categóricas para cada cidade
            city_colors = {
                'Santa Cruz do Capibaribe': '#FF6B6B',
                'Caruaru': '#4ECDC4', 
                'Toritama': '#45B7D1',
                'Surubim': '#96CEB4',
                'Vertentes': '#FFEAA7'
            }
            marker_props['color'] = [city_colors.get(city, '#74B9FF') for city in df['cidade']]

        # Adicionar marcadores principais
        fig.add_trace(go.Scattermapbox(
            lat=df['lat'],
            lon=df['lon'],
            mode='markers+text',
            marker=marker_props,
            text=df['cidade'],
            textposition="bottom center",
            textfont=dict(size=10, color="black"),
            customdata=customdata,
            hovertemplate=hover_template,
            name="Cidades do Polo",
            showlegend=False
        ))

        # Adicionar linhas conectando cidades próximas para mostrar relações regionais
        if len(df) > 1:
            connections = [
                ('Santa Cruz do Capibaribe', 'Toritama'),
                ('Caruaru', 'Santa Cruz do Capibaribe'),
                ('Surubim', 'Caruaru')
            ]
            
            for city1, city2 in connections:
                city1_data = df[df['cidade'] == city1]
                city2_data = df[df['cidade'] == city2]
                
                if not city1_data.empty and not city2_data.empty:
                    fig.add_trace(go.Scattermapbox(
                        lat=[city1_data['lat'].iloc[0], city2_data['lat'].iloc[0]],
                        lon=[city1_data['lon'].iloc[0], city2_data['lon'].iloc[0]],
                        mode='lines',
                        line=dict(width=2, color='rgba(128,128,128,0.3)'),
                        hoverinfo='skip',
                        showlegend=False,
                        name="Conexões Regionais"
                    ))

        # Configurar layout do mapa
        mapbox_config = dict(
            style=config['map_style'],
            center=dict(lat=-8.1, lon=-36.0),
            zoom=8.5,
            bearing=0,
            pitch=0
        )
        
        # Adicionar token do Mapbox apenas se disponível
        try:
            mapbox_token = st.secrets.get("MAPBOX_TOKEN", "")
            if mapbox_token:
                mapbox_config['accesstoken'] = mapbox_token
        except:
            pass  # Usar estilo padrão sem token
        
        fig.update_layout(
            title=dict(
                text=f"🗺️ Polo Têxtil de Pernambuco<br><sub>{config['size_indicator_name']} vs {config['color_indicator_name']}</sub>",
                x=0.5,
                font=dict(size=16, family="Arial, sans-serif"),
                pad=dict(t=20)
            ),
            mapbox=mapbox_config,
            height=600,
            margin=dict(r=80, t=60, l=0, b=0),
            showlegend=False,
            font=dict(family="Arial, sans-serif")
        )

        st.plotly_chart(fig, use_container_width=True)

        # Legenda informativa abaixo do mapa
        with st.expander("ℹ️ Como interpretar o mapa", expanded=False):
            col_legend1, col_legend2, col_legend3 = st.columns(3)
            
            with col_legend1:
                st.markdown("**📏 Tamanho dos Marcadores**")
                st.write(f"Representa: {config['size_indicator_name']}")
                if size_col in df.columns:
                    values = df[size_col]
                    st.write(f"• Máximo: {format_number(values.max())}")
                    st.write(f"• Mínimo: {format_number(values.min())}")
                    st.write(f"• Faixa de tamanho: {config['size_range'][0]}-{config['size_range'][1]}px")
                
            with col_legend2:
                st.markdown(f"**🎨 Cor dos Marcadores**")
                st.write(f"Representa: {config['color_indicator_name']}")
                if color_col and color_col in df.columns:
                    color_values = df[color_col]
                    st.write(f"• Máximo: {format_number(color_values.max())}")
                    st.write(f"• Mínimo: {format_number(color_values.min())}")
                    st.write(f"• Escala: {config['color_scale']}")
                else:
                    st.write("• Cores fixas por cidade")
                    
            with col_legend3:
                st.markdown("**🎯 Interação**")
                st.write("• **Hover**: Passe o mouse sobre os marcadores para ver detalhes")
                st.write("• **Zoom**: Use o scroll para aproximar/afastar")
                st.write("• **Pan**: Arraste para mover o mapa")
                st.write(f"• **Símbolo**: {config['marker_symbol']}")
                st.write(f"• **Transparência**: {config['marker_opacity']:.1%}")

        Analytics.log_event("mapbox_view", {
            "cities_count": len(df),
            "size_indicator": config['size_indicator_name'],
            "color_indicator": config['color_indicator_name'],
            "map_style": config['map_style'],
            "marker_symbol": config['marker_symbol']
        })

    def _normalize_sizes(self, values: pd.Series, min_size: int = 15, max_size: int = 50) -> pd.Series:
        """Normaliza valores para tamanhos de marcadores"""
        if values.max() == values.min():
            return pd.Series([(min_size + max_size) / 2] * len(values))
        
        normalized = min_size + (values - values.min()) / (values.max() - values.min()) * (max_size - min_size)
        return normalized

    def _render_control_panel(self, data: Dict[str, Any]):
        """Renderiza painel de controle e métricas"""
        st.markdown("#### 📊 Resumo Executivo")

        if 'combined' not in data:
            return

        df = data['combined']
        config = data['config']

        # Métricas principais
        total_cities = len(df)
        total_population = df['populacao'].sum() if 'populacao' in df.columns else 0
        total_companies = df['empresas_totais'].sum() if 'empresas_totais' in df.columns else 0
        total_revenue = df['faturamento_anual_milhoes'].sum() if 'faturamento_anual_milhoes' in df.columns else 0

        st.metric("🏘️ Cidades", total_cities)
        st.metric("👥 População", format_number(total_population))
        st.metric("🏢 Empresas", format_number(total_companies))
        st.metric("💰 Faturamento", f"R$ {format_number(total_revenue)}M")

        st.markdown("---")

        # Estatísticas do indicador de tamanho
        size_col = config['size_indicator']
        if size_col in df.columns:
            st.markdown(f"**📏 {config['size_indicator_name']}**")
            values = df[size_col]
            st.write(f"Máximo: {format_number(values.max())}")
            st.write(f"Mínimo: {format_number(values.min())}")
            st.write(f"Média: {format_number(values.mean())}")

        st.markdown("---")

        # Estatísticas do indicador de cor
        color_col = config['color_indicator']
        if color_col and color_col in df.columns:
            st.markdown(f"**🎨 {config['color_indicator_name']}**")
            color_values = df[color_col]
            st.write(f"Máximo: {format_number(color_values.max())}")
            st.write(f"Mínimo: {format_number(color_values.min())}")
            st.write(f"Média: {format_number(color_values.mean())}")

        st.markdown("---")

        # Botão de exportação
        if st.button("📥 Exportar Dados Geográficos", key="export_geo_data"):
            Analytics.log_event("export_data", {"type": "geographic_analysis"})
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data.encode('utf-8'),
                file_name=f'analise_geografica_{len(df)}_cidades.csv',
                mime='text/csv',
                key="download_geo_csv"
            )

    def _render_geographic_analysis(self, data: Dict[str, Any]):
        """Renderiza análises geográficas detalhadas"""
        st.markdown("---")
        st.markdown("### 📈 Análises Geográficas Detalhadas")

        if 'combined' not in data:
            return

        df = data['combined']

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de correlação geográfica
            self._render_correlation_analysis(df)

        with col2:
            # Ranking das cidades
            self._render_city_ranking(df)

        # Análise de densidade territorial
        self._render_density_analysis(df)

    def _render_correlation_analysis(self, df: pd.DataFrame):
        """Renderiza análise de correlação entre indicadores"""
        st.markdown("#### 🔗 Correlação entre Indicadores")

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if 'lat' in numeric_cols:
            numeric_cols.remove('lat')
        if 'lon' in numeric_cols:
            numeric_cols.remove('lon')

        if len(numeric_cols) >= 2:
            # Calcular matriz de correlação
            corr_matrix = df[numeric_cols].corr()

            # Criar heatmap de correlação
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_matrix.values, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))

            fig.update_layout(
                title="Matriz de Correlação dos Indicadores",
                height=400,
                xaxis_title="",
                yaxis_title=""
            )

            st.plotly_chart(fig, use_container_width=True)

            Analytics.log_event("correlation_analysis_view", {"indicators_count": len(numeric_cols)})

    def _render_city_ranking(self, df: pd.DataFrame):
        """Renderiza ranking das cidades"""
        st.markdown("#### 🏆 Ranking das Cidades")

        # Critérios para ranking
        ranking_criteria = {
            "Econômico": ["faturamento_anual_milhoes", "pib_per_capita", "empresas_totais"],
            "Social": ["idh", "acesso_internet"],
            "Ambiental": ["efluentes_tratados_percentual", "energia_renovavel_percentual"],
            "Inovação": ["investimento_inovacao_percentual", "empresas_com_ecommerce"]
        }

        selected_criterion = st.selectbox(
            "Critério de ranking:",
            options=list(ranking_criteria.keys()),
            key="ranking_criterion"
        )

        criteria_cols = ranking_criteria[selected_criterion]
        available_cols = [col for col in criteria_cols if col in df.columns]

        if available_cols:
            # Calcular score composto (média normalizada)
            df_ranking = df.copy()
            for col in available_cols:
                # Normalizar entre 0 e 1
                df_ranking[f"{col}_norm"] = (df_ranking[col] - df_ranking[col].min()) / (df_ranking[col].max() - df_ranking[col].min())

            norm_cols = [f"{col}_norm" for col in available_cols]
            df_ranking['score_composto'] = df_ranking[norm_cols].mean(axis=1)

            # Ordenar por score
            df_ranking = df_ranking.sort_values('score_composto', ascending=False)

            # Criar gráfico de ranking
            fig = px.bar(
                df_ranking,
                x='score_composto',
                y='cidade',
                orientation='h',
                title=f'Ranking {selected_criterion}',
                color='score_composto',
                color_continuous_scale='Viridis'
            )

            fig.update_layout(
                xaxis_title="Score Composto",
                yaxis_title="",
                height=300,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

            # Mostrar top 3
            st.markdown("**🥇 Top 3:**")
            for i, (_, row) in enumerate(df_ranking.head(3).iterrows()):
                medal = ["🥇", "🥈", "🥉"][i]
                st.write(f"{medal} {row['cidade']} - Score: {row['score_composto']:.3f}")

    def _render_density_analysis(self, df: pd.DataFrame):
        """Renderiza análise de densidade territorial"""
        st.markdown("#### 🗺️ Análise de Densidade Territorial")

        if 'populacao' in df.columns and 'empresas_totais' in df.columns:
            col1, col2 = st.columns(2)

            with col1:
                # Densidade populacional vs empresarial
                fig = px.scatter(
                    df,
                    x='populacao',
                    y='empresas_totais',
                    size='faturamento_anual_milhoes' if 'faturamento_anual_milhoes' in df.columns else None,
                    color='cidade',
                    title='Densidade: População vs Empresas',
                    hover_data=['cidade']
                )

                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Eficiência territorial (faturamento por empresa)
                if 'faturamento_anual_milhoes' in df.columns:
                    df['faturamento_por_empresa'] = df['faturamento_anual_milhoes'] / df['empresas_totais']
                    
                    fig = px.bar(
                        df.sort_values('faturamento_por_empresa', ascending=True),
                        x='faturamento_por_empresa',
                        y='cidade',
                        orientation='h',
                        title='Faturamento por Empresa (R$ M)',
                        color='faturamento_por_empresa',
                        color_continuous_scale='Blues'
                    )

                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)

    def _render_regional_comparison(self, data: Dict[str, Any]):
        """Renderiza comparativo regional"""
        st.markdown("---")
        st.markdown("### 🌍 Comparativo Regional")

        if 'combined' not in data:
            return

        df = data['combined']

        # Agrupar cidades por região (baseado na proximidade geográfica)
        regions = {
            'Norte': ['Santa Cruz do Capibaribe', 'Toritama'],
            'Centro': ['Caruaru', 'Surubim'],
            'Sul': ['Vertentes']
        }

        # Criar mapeamento cidade -> região
        city_to_region = {}
        for region, cities in regions.items():
            for city in cities:
                city_to_region[city] = region

        df['regiao'] = df['cidade'].map(city_to_region).fillna('Outras')

        # Agregar dados por região
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        exclude_cols = ['lat', 'lon']
        numeric_cols = [col for col in numeric_cols if col not in exclude_cols]

        if numeric_cols:
            df_regional = df.groupby('regiao')[numeric_cols].agg(['sum', 'mean']).round(2)

            # Gráfico comparativo regional
            col1, col2 = st.columns(2)

            with col1:
                # Seletor de métrica
                metric_options = ['populacao', 'empresas_totais', 'faturamento_anual_milhoes', 'empregos_diretos']
                available_metrics = [m for m in metric_options if m in numeric_cols]

                if available_metrics:
                    selected_metric = st.selectbox(
                        "Métrica para comparação regional:",
                        options=available_metrics,
                        key="regional_metric"
                    )

                    # Gráfico de barras por região
                    regional_data = df_regional[(selected_metric, 'sum')].reset_index()
                    regional_data.columns = ['regiao', selected_metric]

                    fig = px.bar(
                        regional_data,
                        x='regiao',
                        y=selected_metric,
                        title=f'{selected_metric.replace("_", " ").title()} por Região',
                        color=selected_metric,
                        color_continuous_scale='Viridis'
                    )

                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Tabela de dados regionais
                st.markdown("**📊 Dados Regionais Consolidados**")
                
                # Preparar tabela para exibição
                display_metrics = ['populacao', 'empresas_totais', 'faturamento_anual_milhoes']
                available_display = [m for m in display_metrics if m in numeric_cols]

                if available_display:
                    regional_summary = df_regional[[(m, 'sum') for m in available_display]]
                    regional_summary.columns = [m.replace('_', ' ').title() for m in available_display]
                    
                    st.dataframe(regional_summary, use_container_width=True)

        Analytics.log_event("regional_comparison_view", {"regions_count": len(regions)})
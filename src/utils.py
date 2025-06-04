import string
import random

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


class Page(ABC):
    """Classe base para páginas do dashboard"""

    @abstractmethod
    def render(self, data: Dict[str, Any]):
        """Renderiza a página com os dados fornecidos"""
        pass


class DataLoader:
    """Classe para carregar e gerenciar dados"""

    @staticmethod
    @st.cache_data
    def load_csv_safe(filepath: str, encoding: str = 'utf-8') -> Optional[pd.DataFrame]:
        """Carrega arquivo CSV com tratamento de erro"""
        try:
            return pd.read_csv(filepath, encoding=encoding)
        except FileNotFoundError:
            st.warning(f"Arquivo {filepath} não encontrado")
            return None
        except Exception as e:
            st.error(f"Erro ao carregar {filepath}: {str(e)}")
            return None

    @staticmethod
    @st.cache_data
    def load_json_safe(filepath: str, encoding: str = 'utf-8') -> Optional[Dict]:
        """Carrega arquivo JSON com tratamento de erro"""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return json.load(f)
        except FileNotFoundError:
            st.warning(f"Arquivo {filepath} não encontrado")
            return None
        except Exception as e:
            st.error(f"Erro ao carregar {filepath}: {str(e)}")
            return None


class ChartGenerator:
    """Classe para gerar visualizações"""

    @staticmethod
    def create_comparison_bar_chart(
            df: pd.DataFrame,
            x_col: str,
            y_cols: List[str],
            title: str = "",
            color_sequence: List[str] = None
    ) -> go.Figure:
        """Cria gráfico de barras comparativo"""
        fig = go.Figure()

        colors = color_sequence or px.colors.qualitative.Set2

        for i, col in enumerate(y_cols):
            if col in df.columns:
                fig.add_trace(go.Bar(
                    name=col.replace('_', ' ').title(),
                    x=df[x_col],
                    y=df[col],
                    marker_color=colors[i % len(colors)]
                ))

        fig.update_layout(
            title=title,
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title="Valor",
            barmode='group',
            height=400,
            showlegend=True
        )

        return fig

    @staticmethod
    def create_pie_chart(
            df: pd.DataFrame,
            values_col: str,
            names_col: str,
            title: str = ""
    ) -> go.Figure:
        """Cria gráfico de pizza"""
        fig = px.pie(
            df,
            values=values_col,
            names=names_col,
            title=title,
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)

        return fig

    @staticmethod
    def create_radar_chart(
            df: pd.DataFrame,
            categories: List[str],
            entity_col: str,
            title: str = ""
    ) -> go.Figure:
        """Cria gráfico radar para comparação multidimensional"""
        fig = go.Figure()

        colors = px.colors.qualitative.Set1

        for i, entity in enumerate(df[entity_col].unique()):
            entity_data = df[df[entity_col] == entity]

            values = []
            for cat in categories:
                if cat in entity_data.columns:
                    values.append(entity_data[cat].iloc[0])
                else:
                    values.append(0)

            # Fechar o radar
            values.append(values[0])
            categories_radar = categories + [categories[0]]

            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories_radar,
                fill='toself',
                name=entity,
                line_color=colors[i % len(colors)]
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max([df[cat].max() for cat in categories if cat in df.columns])]
                )
            ),
            title=title,
            showlegend=True,
            height=500
        )

        return fig

    @staticmethod
    def create_geographic_map(
            df: pd.DataFrame,
            lat_col: str = None,
            lon_col: str = None,
            size_col: str = None,
            color_col: str = None,
            hover_data: List[str] = None,
            title: str = "Mapa Geográfico do Polo Têxtil de Pernambuco"
    ) -> go.Figure:
        """
        Cria mapa geográfico interativo das cidades do polo têxtil

        Args:
            df: DataFrame com dados das cidades
            lat_col: Coluna com latitude (opcional, usa coordenadas pré-definidas)
            lon_col: Coluna com longitude (opcional, usa coordenadas pré-definidas)
            size_col: Coluna para definir tamanho dos marcadores
            color_col: Coluna para definir cor dos marcadores
            hover_data: Colunas adicionais para mostrar no hover
            title: Título do mapa

        Returns:
            go.Figure: Figura do mapa interativo
        """

        # Coordenadas das principais cidades do polo têxtil de Pernambuco
        city_coordinates = {
            'Santa Cruz do Capibaribe': {'lat': -7.9557, 'lon': -36.2085},
            'Caruaru': {'lat': -8.2837, 'lon': -35.9761},
            'Toritama': {'lat': -8.0108, 'lon': -36.0564},
            'Polo Têxtil PE': {'lat': -8.1, 'lon': -36.0}  # Centro aproximado do polo
        }

        # Criar cópia do DataFrame para não modificar o original
        df_map = df.copy()

        # Se não foram fornecidas colunas de coordenadas, usar coordenadas pré-definidas
        if lat_col is None or lon_col is None:
            # Adicionar coordenadas baseadas no nome da cidade
            df_map['latitude'] = df_map['cidade'].map(lambda x: city_coordinates.get(x, {}).get('lat', -8.1))
            df_map['longitude'] = df_map['cidade'].map(lambda x: city_coordinates.get(x, {}).get('lon', -36.0))
            lat_col = 'latitude'
            lon_col = 'longitude'

        # Preparar dados para hover
        hover_template = "<b>%{text}</b><br>"
        hover_template += "Latitude: %{lat:.4f}<br>"
        hover_template += "Longitude: %{lon:.4f}<br>"

        if hover_data:
            for col in hover_data:
                if col in df_map.columns:
                    hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{hover_data.index(col)}]}}<br>"

        hover_template += "<extra></extra>"

        # Configurar tamanho dos marcadores
        marker_size = 20  # Tamanho padrão
        if size_col and size_col in df_map.columns:
            # Normalizar tamanhos para uma faixa adequada (10-50)
            size_values = df_map[size_col]
            min_size, max_size = 15, 60
            normalized_sizes = min_size + (size_values - size_values.min()) / (
                        size_values.max() - size_values.min()) * (max_size - min_size)
            marker_size = normalized_sizes

        # Configurar cores dos marcadores
        marker_color = 'blue'  # Cor padrão
        if color_col and color_col in df_map.columns:
            marker_color = df_map[color_col]

        # Preparar dados customizados para hover
        customdata = None
        if hover_data:
            customdata = df_map[hover_data].values

        # Criar o mapa
        fig = go.Figure()

        # Adicionar marcadores das cidades
        fig.add_trace(go.Scattermapbox(
            lat=df_map[lat_col],
            lon=df_map[lon_col],
            mode='markers',
            marker=dict(
                size=marker_size,
                color=marker_color,
                colorscale='Viridis' if color_col else None,
                showscale=True if color_col else False,
                colorbar=dict(title=color_col.replace('_', ' ').title() if color_col else '') if color_col else None,
                sizemode='diameter'
            ),
            text=df_map['cidade'],
            customdata=customdata,
            hovertemplate=hover_template,
            name="Cidades do Polo"
        ))

        # Configurar layout do mapa
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16)
            ),
            mapbox=dict(
                style='open-street-map',
                center=dict(
                    lat=-8.1,  # Centro aproximado do polo têxtil
                    lon=-36.0
                ),
                zoom=8.5
            ),
            height=600,
            margin=dict(r=0, t=40, l=0, b=0),
            showlegend=False
        )

        return fig

    @staticmethod
    def create_choropleth_map(
            df: pd.DataFrame,
            locations_col: str,
            values_col: str,
            title: str = "Mapa Coroplético",
            color_scale: str = "Blues"
    ) -> go.Figure:
        """
        Cria mapa coroplético (preenchimento por região)

        Args:
            df: DataFrame com dados
            locations_col: Coluna com identificadores de localização
            values_col: Coluna com valores para colorir o mapa
            title: Título do mapa
            color_scale: Escala de cores

        Returns:
            go.Figure: Figura do mapa coroplético
        """

        fig = px.choropleth(
            df,
            locations=locations_col,
            color=values_col,
            hover_name=locations_col,
            color_continuous_scale=color_scale,
            title=title
        )

        fig.update_layout(
            height=500,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='equirectangular'
            )
        )

        return fig


class FilterManager:
    """Classe para gerenciar filtros do dashboard"""

    @staticmethod
    def create_city_filter(cities: List[str], key: str = "city_filter") -> List[str]:
        """Cria filtro de seleção múltipla para cidades"""
        return st.multiselect(
            "Selecione as cidades:",
            options=cities,
            default=cities,
            key=key
        )

    @staticmethod
    def create_date_range_filter(key: str = "date_filter") -> tuple:
        """Cria filtro de intervalo de datas"""
        start_date = st.date_input(
            "Data inicial:",
            value=datetime.date.today() - datetime.timedelta(days=365),
            key=f"{key}_start"
        )
        end_date = st.date_input(
            "Data final:",
            value=datetime.date.today(),
            key=f"{key}_end"
        )
        return start_date, end_date

    @staticmethod
    def create_numeric_range_filter(
            min_val: float,
            max_val: float,
            step: float = 1.0,
            label: str = "Intervalo:",
            key: str = "numeric_filter"
    ) -> tuple:
        """Cria filtro de intervalo numérico"""
        return st.slider(
            label,
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            step=step,
            key=key
        )


class UIComponents:
    """Componentes de interface reutilizáveis"""

    @staticmethod
    def create_metric_card(title: str, value: str, delta: Optional[str] = None):
        """Cria cartão de métrica"""
        st.metric(label=title, value=value, delta=delta)

    @staticmethod
    def create_info_expander(title: str, content: str):
        """Cria expansor de informações"""
        with st.expander(title):
            st.markdown(content)

    @staticmethod
    def create_download_button(
            data: Any,
            filename: str,
            mime_type: str = "text/csv",
            label: str = "Download"
    ):
        """Cria botão de download"""
        if isinstance(data, pd.DataFrame):
            csv = data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=label,
                data=csv,
                file_name=filename,
                mime=mime_type
            )
        else:
            st.download_button(
                label=label,
                data=str(data),
                file_name=filename,
                mime=mime_type
            )


def add_custom_css():
    """Adiciona CSS customizado"""
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 2rem;
            font-weight: bold;
            color: #FF6B35;
            text-align: center;
            margin-bottom: 2rem;
        }

        .metric-container {
            background-color: #F0F2F6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }

        .insight-box {
            background-color: #E3F2FD;
            padding: 1rem;
            border-left: 4px solid #2196F3;
            margin: 1rem 0;
        }

        .warning-box {
            background-color: #FFF3E0;
            padding: 1rem;
            border-left: 4px solid #FF9800;
            margin: 1rem 0;
        }

        .sidebar .sidebar-content {
            background-color: #FAFAFA;
        }

        .stPlotlyChart {
            border: 1px solid #E0E0E0;
            border-radius: 0.5rem;
            padding: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def format_number(num: float, format_type: str = "thousands") -> str:
    """Formata números para exibição"""
    if format_type == "thousands":
        return f"{num:,.0f}"
    elif format_type == "currency":
        return f"R$ {num:,.2f}"
    elif format_type == "percentage":
        return f"{num:.1f}%"
    else:
        return str(num)


def validate_data(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """Valida se o DataFrame possui as colunas necessárias"""
    if df is None:
        return False
    return all(col in df.columns for col in required_columns)

def get_cities_list(df: pd.DataFrame, city_column: str = "cidade") -> List[str]:
    """Obtém lista única de cidades de um DataFrame"""
    if df is None or city_column not in df.columns:
        return ['Santa Cruz do Capibaribe', 'Caruaru', 'Toritama']
    return sorted(df[city_column].unique().tolist())


def filter_data_by_cities(df: pd.DataFrame, selected_cities: List[str], city_column: str = "cidade") -> pd.DataFrame:
    """Filtra DataFrame pelas cidades selecionadas"""
    if df is None or not selected_cities:
        return df

    if city_column not in df.columns:
        return df

    return df[df[city_column].isin(selected_cities)]


def create_priority_matrix_chart(df: pd.DataFrame, x_col: str, y_col: str, size_col: str = None,
                                 color_col: str = None, text_col: str = None, title: str = "") -> go.Figure:
    """Cria gráfico de matriz de priorização (dispersão)"""
    fig = go.Figure()

    # Se não há coluna de cor, usar valores do eixo x
    if color_col is None:
        color_col = x_col

    # Se não há coluna de tamanho, usar valores constantes
    if size_col is None:
        sizes = [10] * len(df)
    else:
        sizes = df[size_col] * 2  # Multiplica por 2 para melhor visualização

    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='markers+text',
        marker=dict(
            size=sizes,
            color=df[color_col] if color_col in df.columns else df[x_col],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Valor")
        ),
        text=df[text_col] if text_col and text_col in df.columns else "",
        textposition="middle center",
        hovertemplate="<b>%{text}</b><br>" +
                      f"{x_col}: %{{x}}<br>" +
                      f"{y_col}: %{{y}}<br>" +
                      "<extra></extra>"
    ))

    fig.update_layout(
        title=title,
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title(),
        height=500,
        showlegend=False
    )

    return fig



def generate_user_id(length=6):
    characters = string.ascii_letters + string.digits  # a-zA-Z0-9
    return ''.join(random.choices(characters, k=length))
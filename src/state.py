import streamlit as st
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, date
import json
from src.utils.page_utils import (generate_user_id)


@dataclass
class DashboardState:
    """Classe para gerenciar o estado do dashboard"""

    # Filtros globais
    selected_cities: List[str] = field(default_factory=lambda: ['Santa Cruz do Capibaribe', 'Caruaru', 'Toritama'])
    date_range: Optional[tuple] = None
    active_page: str = "🏠 Visão Geral"

    # Estado dos dados
    data_loaded: bool = False
    last_update: Optional[datetime] = None

    # Configurações de visualização
    chart_theme: str = "plotly"
    show_details: bool = True

    # Analytics
    session_start: Optional[datetime] = None
    page_views: Dict[str, int] = field(default_factory=dict)

    # Filtros específicos de páginas
    indicators_filters: Dict[str, Any] = field(default_factory=dict)
    network_filters: Dict[str, Any] = field(default_factory=dict)
    risks_filters: Dict[str, Any] = field(default_factory=dict)
    opportunities_filters: Dict[str, Any] = field(default_factory=dict)

    try:
        if st.session_state.user_id is None:
            st.session_state["user_id"] = generate_user_id()
    except:
        st.session_state["user_id"] = generate_user_id()

    def __post_init__(self):
        if self.session_start is None:
            self.session_start = datetime.now()


class StateManager:
    """Gerenciador central do estado da aplicação"""

    @staticmethod
    def initialize_state():
        """Inicializa o estado da aplicação"""
        if 'dashboard_state' not in st.session_state:
            st.session_state.dashboard_state = DashboardState()

        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {
                'theme': 'light',
                'language': 'pt-BR',
                'notifications': True,
                'auto_refresh': False,
                'default_chart_height': 400,
                'show_data_sources': True
            }

        if 'cache_data' not in st.session_state:
            st.session_state.cache_data = {}

        if 'filters' not in st.session_state:
            st.session_state.filters = {
                'global': {},
                'page_specific': {}
            }

        if 'selected_entities' not in st.session_state:
            st.session_state.selected_entities = {
                'actors': [],
                'opportunities': [],
                'risks': []
            }

    @staticmethod
    def get_state() -> DashboardState:
        """Obtém o estado atual"""
        StateManager.initialize_state()
        return st.session_state.dashboard_state

    @staticmethod
    def update_state(**kwargs):
        """Atualiza o estado com novos valores"""
        StateManager.initialize_state()
        state = st.session_state.dashboard_state

        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)

    @staticmethod
    def get_user_preferences() -> Dict[str, Any]:
        """Obtém preferências do usuário"""
        StateManager.initialize_state()
        return st.session_state.user_preferences

    @staticmethod
    def update_user_preferences(**kwargs):
        """Atualiza preferências do usuário"""
        StateManager.initialize_state()
        for key, value in kwargs.items():
            st.session_state.user_preferences[key] = value

    @staticmethod
    def get_filters() -> Dict[str, Any]:
        """Obtém filtros atuais"""
        StateManager.initialize_state()
        return st.session_state.filters

    @staticmethod
    def update_filters(filter_type: str, **kwargs):
        """Atualiza filtros específicos"""
        StateManager.initialize_state()
        if filter_type not in st.session_state.filters:
            st.session_state.filters[filter_type] = {}

        for key, value in kwargs.items():
            st.session_state.filters[filter_type][key] = value

    @staticmethod
    def increment_page_view(page_name: str):
        """Incrementa contador de visualizações de página"""
        state = StateManager.get_state()
        if page_name in state.page_views:
            state.page_views[page_name] += 1
        else:
            state.page_views[page_name] = 1

    @staticmethod
    def get_selected_entities(entity_type: str) -> List[str]:
        """Obtém entidades selecionadas por tipo"""
        StateManager.initialize_state()
        return st.session_state.selected_entities.get(entity_type, [])

    @staticmethod
    def update_selected_entities(entity_type: str, entities: List[str]):
        """Atualiza entidades selecionadas"""
        StateManager.initialize_state()
        st.session_state.selected_entities[entity_type] = entities

    @staticmethod
    def clear_filters():
        """Limpa todos os filtros"""
        StateManager.initialize_state()
        st.session_state.filters = {
            'global': {},
            'page_specific': {}
        }

    @staticmethod
    def export_state() -> Dict[str, Any]:
        """Exporta estado atual para JSON"""
        StateManager.initialize_state()
        return {
            'dashboard_state': st.session_state.dashboard_state.__dict__,
            'user_preferences': st.session_state.user_preferences,
            'filters': st.session_state.filters,
            'selected_entities': st.session_state.selected_entities
        }

    @staticmethod
    def import_state(state_dict: Dict[str, Any]):
        """Importa estado de um dicionário"""
        StateManager.initialize_state()

        if 'user_preferences' in state_dict:
            st.session_state.user_preferences.update(state_dict['user_preferences'])

        if 'filters' in state_dict:
            st.session_state.filters.update(state_dict['filters'])

        if 'selected_entities' in state_dict:
            st.session_state.selected_entities.update(state_dict['selected_entities'])


class SessionManager:
    """Gerenciador de sessão e persistência"""

    @staticmethod
    def get_session_info() -> Dict[str, Any]:
        """Obtém informações da sessão atual"""
        StateManager.initialize_state()
        state = StateManager.get_state()

        return {
            'session_duration': datetime.now() - state.session_start if state.session_start else None,
            'pages_visited': len(state.page_views),
            'total_page_views': sum(state.page_views.values()),
            'most_visited_page': max(state.page_views.items(), key=lambda x: x[1])[0] if state.page_views else None,
            'data_loaded': state.data_loaded,
            'last_update': state.last_update
        }

    @staticmethod
    def reset_session():
        """Reseta a sessão atual"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        StateManager.initialize_state()

    @staticmethod
    def save_session_to_cache(key: str):
        """Salva estado da sessão no cache"""
        StateManager.initialize_state()
        st.session_state.cache_data[key] = StateManager.export_state()

    @staticmethod
    def load_session_from_cache(key: str) -> bool:
        """Carrega estado da sessão do cache"""
        StateManager.initialize_state()
        if key in st.session_state.cache_data:
            StateManager.import_state(st.session_state.cache_data[key])
            return True
        return False
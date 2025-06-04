import streamlit as st
from typing import Dict, Any, List, Optional
from src.utils import Page, UIComponents, FilterManager, format_number
from src.state import StateManager
from src.nm.people_network import EcosystemNetworkRenderer

from src.nm.analytics import  Analytics


class NetworkPageV2(Page):
    """Página de Rede de Atores"""

    def render(self, data: Dict[str, Any]):
        """Renderiza a página de rede de atores"""
        Analytics.log_event("page_view", {"page": "network"})
        StateManager.increment_page_view("Rede de Atores")

        st.markdown('<h2 class="page-header">🔄 Rede de Agentes-Chave e Relacionamentos</h2>',
                    unsafe_allow_html=True)

        renderer = EcosystemNetworkRenderer()

        # Verificar se dados da ontologia estão disponíveis
        ontology_data = data.get('ontologia')
        if not ontology_data:
            st.warning("Dados da ontologia não estão disponíveis.")
            return

        renderer.load_json_ontology(json_data=ontology_data, root_node = 'textile_ecosystem_network_ontology')

        renderer.create_network_map()
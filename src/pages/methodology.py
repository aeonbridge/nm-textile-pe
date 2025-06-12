import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Any

from src.nm.analytics import  Analytics
from src.utils.page_utils import (Page)
from src.state import StateManager
from src.utils.cards import render_comments_section


class MethodologyPage(Page):
    def render(self, data: Dict[str, Any]):
        Analytics.log_event("page_view", {"page": "methodology"})
        StateManager.increment_page_view("Metodologia")
        methodology_content = data.get("methodology")
        if not methodology_content:
            st.warning("Página indisponível")
            return

        # Create split layout: iframe on left (3/5), comments on right (2/5)
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("📋 Framework Metodológico")
            components.html(methodology_content, height=800, scrolling=True)
        
        with col2:
            # Add centralized comment section for methodology items with hierarchical structure
            methodology_items = {
                "Framework Metodológico": {
                    "fase_1": "Fase 1: Contextualize & Frame",
                    "fase_2": "Fase 2: Model & Hypothesize", 
                    "fase_3": "Fase 3: Assess & Define",
                    "fase_4": "Fase 4: Implement & Monitor",
                    "fase_5": "Fase 5: Analyze & Refine",
                    "fase_6": "Fase 6: Validate & Adjust",
                    "fase_7": "Fase 7: Decide & Continue"
                },
                "Dashboard": {
                    "metricas_qualidade": "Métricas de Qualidade",
                    "metricas_processo": "Métricas de Processo",
                    "indicadores_performance": "Indicadores de Performance",
                    "analise_rede": "Análise de Rede"
                },
                "Análise Metodológica": "Análise Metodológica",
                "Implementação": "Implementação",
                "Validação": "Validação"
            }
            
            render_comments_section(methodology_items, "methodology")

        st.link_button(url="/static/kb/methodology/The_Phygital_Scientist_AIM.pdf", label="AIM", type="secondary")
        st.link_button(url="/static/kb/methodology/SPA_15.pdf", label="SPA")
        st.link_button(url="/static/kb/methodology/SPA_15_refs.pdf", label="SPA Refs", )
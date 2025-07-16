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

        # Initialize framework expansion state
        if "expand_framework" not in st.session_state:
            st.session_state.expand_framework = False
        
        # Add expand/collapse button for Framework Metodológico
        if st.button(
            f"{'📏 Comprimir Framework' if st.session_state.expand_framework else '🔍 Expandir Framework'}", 
            key="toggle_framework_expand",
            use_container_width=True
        ):
            st.session_state.expand_framework = not st.session_state.expand_framework
            st.rerun()
        
        # Create dynamic layout based on expansion state
        if st.session_state.expand_framework:
            # Expanded layout: framework takes full width
            st.subheader("📋 Framework Metodológico (Expandido)")
            components.html(methodology_content, height=1000, scrolling=True)
            
            # Comments section below when expanded
            st.markdown("---")
        else:
            # Normal split layout: iframe on left (3/5), comments on right (2/5)
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.subheader("📋 Framework Metodológico")
                components.html(methodology_content, height=800, scrolling=True)
        
        # Comments section - either in col2 (normal) or below (expanded)
        if not st.session_state.expand_framework:
            with col2:
                # Add toggle button for comments visibility
                if "show_comments" not in st.session_state:
                    st.session_state.show_comments = True
                
                # Toggle button with icon
                if st.button(
                    f"{'🙈 Ocultar Comentários' if st.session_state.show_comments else '👁️ Mostrar Comentários'}", 
                    key="toggle_comments",
                    use_container_width=True
                ):
                    st.session_state.show_comments = not st.session_state.show_comments
                    st.rerun()
                
                # Only render comments section if toggle is enabled
                if st.session_state.show_comments:
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
                else:
                    st.info("💬 Comentários estão ocultos. Use o botão acima para mostrá-los.")
        else:
            # Comments section below when framework is expanded
            # Add toggle button for comments visibility
            if "show_comments" not in st.session_state:
                st.session_state.show_comments = True
            
            # Toggle button with icon
            if st.button(
                f"{'🙈 Ocultar Comentários' if st.session_state.show_comments else '👁️ Mostrar Comentários'}", 
                key="toggle_comments_expanded",
                use_container_width=True
            ):
                st.session_state.show_comments = not st.session_state.show_comments
                st.rerun()
            
            # Only render comments section if toggle is enabled
            if st.session_state.show_comments:
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
            else:
                st.info("💬 Comentários estão ocultos. Use o botão acima para mostrá-los.")

        st.link_button(url="/static/kb/methodology/The_Phygital_Scientist_AIM.pdf", label="AIM", type="secondary")
        st.link_button(url="/static/kb/methodology/SPA_15.pdf", label="SPA")
        st.link_button(url="/static/kb/methodology/SPA_15_refs.pdf", label="SPA Refs", )
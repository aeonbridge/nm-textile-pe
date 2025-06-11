import streamlit as st
from typing import Dict, Any

from src.nm.analytics import Analytics
from src.utils.page_utils import Page
from src.state import StateManager
from src.utils.cards import InteractiveCard, create_phase_card


class CardDemoPage(Page):
    def render(self, data: Dict[str, Any]):
        Analytics.log_event("page_view", {"page": "card_demo"})
        StateManager.increment_page_view("Card Demo")
        
        st.title("🃏 Interactive Cards Demo")
        st.markdown("Demonstração dos cartões interativos com flip e comentários integrados ao Supabase.")
        
        # Create columns for cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Fase 1: Contextualize & Frame")
            
            # Create sample content for phase 1
            phase1_content = {
                "🎯 Entrada via CDL Regional": [
                    "Workshop alinhamento CDL (2 dias)",
                    "Identificação 5-7 empresários-chave",
                    "Protocolo apresentação pesquisa"
                ],
                "🗺️ Mapeamento Contextual": [
                    "Entrevistas agentes indicados (1h30)",
                    "Análise infraestrutura figital",
                    "Redes sociais/organizacionais"
                ],
                "📊 Objetivos SMART-er": [
                    "20-30 insights validados",
                    "15-20 agentes-chave engajados",
                    "12 meses de cronograma"
                ]
            }
            
            card1 = create_phase_card(1, "FASE 1: CONTEXTUALIZE & FRAME", phase1_content)
            card1.render()
        
        with col2:
            st.subheader("Fase 2: Model & Hypothesize")
            
            # Create sample content for phase 2
            phase2_content = {
                "🕸️ Modelo de Rede": [
                    "Mapeamento relações agentes",
                    "Fluxos informação/influência",
                    "Gatekeepers e conectores"
                ],
                "💡 Modelo de Insights": [
                    "Framework captura via workshops",
                    "Sistema categorização temática",
                    "Validação colaborativa"
                ],
                "🔬 Hipóteses Focadas": [
                    "H1: Workshops → insights acionáveis",
                    "H2: Validação cruzada (+40% qualidade)",
                    "H3: Co-criação (>70% endorsement)"
                ]
            }
            
            card2 = create_phase_card(2, "FASE 2: MODEL & HYPOTHESIZE", phase2_content)
            card2.render()
        
        # Add a third card for custom content demo
        st.subheader("Custom Card Example")
        
        custom_card = InteractiveCard(
            card_id="custom_demo",
            title="🚀 Custom Card Demo",
            content="""
            <h4>📋 Features</h4>
            <ul>
                <li>Click to flip and see comments</li>
                <li>Add your own comments</li>
                <li>Comments stored in Supabase</li>
                <li>Session-based authorship</li>
            </ul>
            
            <h4>💡 Usage</h4>
            <ul>
                <li>Hover to see interaction hints</li>
                <li>Click anywhere on card to flip</li>
                <li>Use Ctrl+Enter in textarea for quick submit</li>
                <li>Comments persist across sessions</li>
            </ul>
            """,
            color="#9f7aea",
            height=500
        )
        custom_card.render()
        
        # Instructions
        st.markdown("---")
        st.markdown("""
        ### 📖 Como usar os cartões:
        
        1. **Visualizar conteúdo**: O cartão mostra o conteúdo principal na frente
        2. **Ver comentários**: Clique no cartão para virar e ver os comentários
        3. **Adicionar comentário**: Digite na caixa de texto e clique em "Adicionar Comentário"
        4. **Fechar comentários**: Clique no botão "✕ Fechar" para voltar ao conteúdo
        5. **Indicador de comentários**: O número no canto superior direito mostra quantos comentários existem
        
        ### 🔧 Recursos técnicos:
        
        - ✅ **Flip animation**: Animação suave de rotação 3D
        - ✅ **Comment system**: Integração completa com Supabase
        - ✅ **Session management**: Identificação por sessão
        - ✅ **Responsive design**: Adaptável a diferentes tamanhos de tela
        - ✅ **Keyboard shortcuts**: Ctrl+Enter para envio rápido
        - ✅ **Visual feedback**: Indicadores visuais e animações
        """)
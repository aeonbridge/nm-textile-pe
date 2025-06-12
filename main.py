import streamlit as st
import sys
from pathlib import Path
from streamlit import sidebar

from src.pages.methodology import MethodologyPage

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from src.nm.analytics import Analytics
from src.nm.data_loader import DataLoader
from src.state import StateManager
from src.pages.overview import OverviewPage
from src.pages.indicators import IndicatorsPage
from src.pages.geographic_mapbox import GeographicMapboxPage
from src.pages.interactive_analysis import InteractiveAnalysisPage
from src.pages.network_v2 import NetworkPageV2
from src.pages.risks import RisksPage
from src.pages.opportunities import OpportunitiesPage
from src.pages.card_demo import CardDemoPage
from src.nm.feedback import create_feedback_section
from src.auth import require_authentication, AuthManager

# IMPORTANTE: Verificar autenticação antes de qualquer configuração
require_authentication()

# Configuração da página principal (só executa se autenticado)
st.set_page_config(
    page_title="Dashboard Ecossistema Têxtil PE",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Aplicar CSS customizado
# add_custom_css()

# Inicializar estado
StateManager.initialize_state()


class DashboardApp:
    """Classe principal do dashboard"""

    def __init__(self):
        # Initialize session state for navigation
        if "selected_page_card" not in st.session_state:
            st.session_state.selected_page_card = None
            
        # Definir as páginas como objetos st.Page para usar com st.navigation
        self.page_configs = {
            "visao_geral": {"title": "Visão Geral", "icon": "🏠", "description": "Panorama geral do ecossistema têxtil"},
            "methodology": {"title": "Methodology", "icon": "📋", "description": "Metodologia e framework de análise utilizado"},
            "rede_agentes": {"title": "Rede de Agentes-chave", "icon": "🕸️", "description": "Mapeamento de stakeholders e suas interações"},
            "analise_riscos": {"title": "Análise de Riscos", "icon": "⚠️", "description": "Identificação e avaliação de riscos sistêmicos"},
            "oportunidades": {"title": "Identificação de Oportunidades", "icon": "💡", "description": "Descoberta de oportunidades de crescimento"},
            "indicadores": {"title": "Análise de Indicadores", "icon": "📊", "description": "Métricas econômicas, sociais e ambientais"},
            "geografica": {"title": "Análise Geográfica", "icon": "🗺️", "description": "Distribuição espacial e mapas interativos"},
            "laboratorio": {"title": "Laboratório Interativo", "icon": "🚀", "description": "Simulações e análises personalizadas"},
            "card_demo": {"title": "Demo Cards", "icon": "🃏", "description": "Demonstração de cartões interativos com st.dialog"},
        }
        
        # Create st.Page objects for navigation
        self.nav_pages = {
            "visao_geral": st.Page(self._render_overview, title="🏠 Visão Geral", icon="🏠"),
            "methodology": st.Page(self._render_methodology, title="📋 Methodology", icon="📋"),
            "rede_agentes": st.Page(self._render_network, title="🕸️ Rede de Agentes-chave", icon="🕸️"),
            "analise_riscos": st.Page(self._render_risks, title="⚠️ Análise de Riscos", icon="⚠️"),
            "oportunidades": st.Page(self._render_opportunities, title="💡 Identificação de Oportunidades", icon="💡"),
            "indicadores": st.Page(self._render_indicators, title="📊 Análise de Indicadores", icon="📊"),
            "geografica": st.Page(self._render_geographic, title="🗺️ Análise Geográfica", icon="🗺️"),
            "laboratorio": st.Page(self._render_interactive, title="🚀 Laboratório Interativo", icon="🚀"),
            "card_demo": st.Page(self._render_card_demo, title="🃏 Demo Cards", icon="🃏"),
        }
        
        # Manter instâncias das páginas para compatibilidade
        self.pages = {
            "visao_geral": OverviewPage(),
            "methodology": MethodologyPage(),
            "rede_agentes": NetworkPageV2(),
            "analise_riscos": RisksPage(),
            "oportunidades": OpportunitiesPage(),
            "indicadores": IndicatorsPage(),
            "geografica": GeographicMapboxPage(),
            "laboratorio": InteractiveAnalysisPage(),
            "card_demo": CardDemoPage(),
        }
        
        self.data = None

    def load_data(self):
        """Carrega todos os dados necessários"""
        if self.data is None:
            with st.spinner("Carregando dados..."):
                self.data = self._load_all_datasets()
        return self.data

    def _load_all_datasets(self):
        """Carrega todos os datasets"""
        data = {}

        # Carregar CSVs
        csv_files = {
            'economicos': 'indicadores_economicos.csv',
            'sociais': 'indicadores_sociais.csv',
            'ambientais': 'indicadores_ambientais.csv',
            'inovacao': 'indicadores_inovacao.csv'
        }

        for key, filename in csv_files.items():
            filepath = f"static/datasets/{filename}"
            data[key] = DataLoader.load_csv_safe(filepath)
            if data[key] is None:
                data[key] = self._create_dummy_data(key)

        # Carregar JSONs
        json_files = [
            'ontologia_ecossistema_textil_ptbr.json'
        ]

        for filename in json_files:
            filepath = f"static/datasets/{filename}"
            json_data = DataLoader.load_json_safe(filepath)
            if json_data:
                data['ontologia'] = json_data
                break

        filepath = f"static/methodology/aim/board_aim_framework-fluid-version.html"
        data['methodology'] = DataLoader.load_file(filepath)
        filepath = f"static/js/controls.js"
        data['controls'] = DataLoader.load_file(filepath)

        return data

    def _create_dummy_data(self, data_type):
        """Cria dados simulados quando arquivos não estão disponíveis"""
        import pandas as pd

        cities = ['Santa Cruz do Capibaribe', 'Caruaru', 'Toritama']

        if data_type == 'economicos':
            return pd.DataFrame({
                'cidade': cities,
                'populacao': [107500, 365000, 44000],
                'empresas_formais': [1200, 2500, 450],
                'empresas_informais': [4800, 7500, 1550],
                'taxa_informalidade': [39.8, 23.9, 57.3],
                'empregos_diretos': [45000, 85000, 25000],
                'faturamento_anual_milhoes': [1800, 2200, 1600],
                'exportacao_percentual': [5, 8, 3],
                'pib_per_capita': [12500, 18700, 14300]
            })

        elif data_type == 'sociais':
            return pd.DataFrame({
                'cidade': cities,
                'idh': [0.648, 0.677, 0.618],
                'taxa_pobreza': [28.5, 22.1, 35.2],
                'taxa_extrema_pobreza': [12.3, 8.7, 15.8],
                'evasao_escolar': [32.5, 24.8, 38.7],
                'trabalho_infantil': [18.7, 12.5, 24.3],
                'acesso_internet': [65.3, 72.8, 58.7],
                'mulheres_empreendedoras': [58.2, 52.4, 62.5],
                'jovens_empreendedores': [42.5, 38.2, 48.7]
            })

        elif data_type == 'ambientais':
            return pd.DataFrame({
                'cidade': cities,
                'consumo_agua_m3_dia': [3200, 4500, 2800],
                'efluentes_tratados_percentual': [35.2, 58.7, 22.5],
                'residuos_solidos_ton_mes': [450, 780, 320],
                'energia_renovavel_percentual': [15.3, 22.1, 8.7],
                'reuso_agua_percentual': [12.5, 18.3, 8.2],
                'poluicao_rios_indice': [7.8, 6.2, 8.9],
                'lavanderias_quantidade': [25, 35, 70],
                'lavanderias_licenciadas_percentual': [45.2, 62.8, 28.6]
            })

        elif data_type == 'inovacao':
            return pd.DataFrame({
                'cidade': cities,
                'investimento_inovacao_percentual': [2.8, 4.2, 1.5],
                'empresas_com_ecommerce': [18.5, 27.3, 12.4],
                'adocao_tecnologias_digitais': [35.2, 48.6, 28.7],
                'marcas_proprias_percentual': [22.4, 35.8, 18.2],
                'design_proprio_percentual': [15.7, 28.4, 12.1],
                'capacitacao_digital_percentual': [28.5, 42.1, 19.3],
                'acesso_credito_inovacao': [6.2, 8.7, 4.1],
                'startups_relacionadas': [8, 28, 3]
            })

        return pd.DataFrame()

    def _render_overview(self):
        """Render overview page"""
        data = self.load_data()
        self.pages["visao_geral"].render(data)
    
    def _render_methodology(self):
        """Render methodology page"""
        data = self.load_data()
        self.pages["methodology"].render(data)
    
    def _render_network(self):
        """Render network analysis page"""
        data = self.load_data()
        self.pages["rede_agentes"].render(data)
    
    def _render_risks(self):
        """Render risks analysis page"""
        data = self.load_data()
        self.pages["analise_riscos"].render(data)
    
    def _render_opportunities(self):
        """Render opportunities page"""
        data = self.load_data()
        self.pages["oportunidades"].render(data)
    
    def _render_indicators(self):
        """Render indicators analysis page"""
        data = self.load_data()
        self.pages["indicadores"].render(data)
    
    def _render_geographic(self):
        """Render geographic analysis page"""
        data = self.load_data()
        self.pages["geografica"].render(data)
    
    def _render_interactive(self):
        """Render interactive laboratory page"""
        data = self.load_data()
        self.pages["laboratorio"].render(data)
    
    def _render_card_demo(self):
        """Render card demo page"""
        data = self.load_data()
        self.pages["card_demo"].render(data)

    def render_header(self):
        user_info = AuthManager.get_user_info()
        if user_info["is_logged_in"]:
            # Get user display name and picture
            user_display = AuthManager.get_user_display_name()
            user_picture = user_info.get("picture")

            profile_html = ""
            if user_picture and user_picture.strip():
                # Show profile picture with name - complete HTML in one block
                profile_html = f"""
                                <img src="{user_picture}" 
                                     style="width: 80px; height: 80px; border-radius: 50%; 
                                            object-fit: cover; border: 1px solid #ddd;" 
                                     alt="Profile"/>
                            """
            else:
                # Show fallback - complete HTML in one block
                profile_html = f"""
                                <div style="width: 30px; height: 30px; border-radius: 50%; 
                                           background: #f0f0f0; display: flex; align-items: center; 
                                           justify-content: center; font-size: 14px; border: 1px solid #ddd;">👤</div>
                                <span style="font-size: 14px; font-weight: 500; color: #333;">{user_display}</span>
                            """

            #"""Renderiza o cabeçalho principal"""
            st.html(f"""
            
            <h1 class="main-header">{profile_html} 📊 Dashboard Ecossistema Têxtil de Pernambuco</h1>
            """)

            # Informações contextuais
            header = f"""
            <div class="insight-box">
            <strong>💡 Sobre este Dashboard:</strong> Ferramenta interativa para apoiar stakeholders 
            na compreensão do ambiente, análise de tendências e tomada de decisão no ecossistema têxtil de Pernambuco.
            </div>
            """
            st.html(header)

    def render_user_profile(self):
        """Renderiza o perfil do usuário no topo da página"""
        # Renderizar o perfil do usuário
        AuthManager.render_logout_button()
    
    def render_medium_cards_top(self):
        """Renderiza cards médios no topo quando uma página está ativa"""
        current_page = getattr(st.session_state, "current_page", None)
        
        if current_page:
            self.render_header()
            st.html('<div class="cards-medium">')
            
            # Cards médios em linha horizontal
            cols = st.columns(len(self.page_configs))
            
            for i, (page_key, config) in enumerate(self.page_configs.items()):
                with cols[i]:
                    button_label = f"{config['icon']} {config['title']}"
                    
                    if st.button(button_label, key=f"top_card_{page_key}", 
                               type="primary" if current_page == page_key else "secondary",
                               help=f"Acessar {config['title']}",
                               use_container_width=True):
                        st.session_state.current_page = page_key
                        st.rerun()
            
            st.html('</div>')
            st.divider()

    def render_analysis_cards(self):
        """Renderiza cards para seleção das análises usando st.navigation"""
        # Verificar se já temos uma página ativa via navigation
        current_page = getattr(st.session_state, "current_page", None)
        
        st.html("<h2>🎯 Escolha uma Análise </h2>")
        
        # CSS para cards aesthetic uniformes
        st.html("""
        <style>
        /* Estilo para cards grandes (formato carta de baralho vertical aesthetic) */
        .cards-large .stButton > button {
            border: 1px solid rgba(0, 0, 0, 0.1) !important;
            border-radius: 16px !important;
            padding: 24px 20px !important;
            margin: 12px !important;
            text-align: center !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
            background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.1) !important;
            width: 100% !important;
            height: 280px !important;
            min-height: 280px !important;
            max-height: 280px !important;
            aspect-ratio: 5/7 !important;
            color: #374151 !important;
            font-weight: 600 !important;
            white-space: pre-line !important;
            word-wrap: break-word !important;
            line-height: 1.5 !important;
            font-size: 14px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .cards-large .stButton > button::before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            background: linear-gradient(145deg, transparent 0%, rgba(102, 126, 234, 0.02) 100%) !important;
            opacity: 0 !important;
            transition: opacity 0.3s ease !important;
        }
        
        .cards-large .stButton > button:hover {
            border-color: rgba(102, 126, 234, 0.3) !important;
            transform: translateY(-4px) scale(1.02) !important;
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15), 0 4px 12px rgba(0, 0, 0, 0.1) !important;
            background: linear-gradient(145deg, #ffffff 0%, #f0f4ff 100%) !important;
        }
        
        .cards-large .stButton > button:hover::before {
            opacity: 1 !important;
        }
        
        .cards-large .stButton > button:active {
            transform: translateY(-2px) scale(1.01) !important;
            transition: all 0.2s ease !important;
        }
        
        .cards-large .stButton > button[kind="primary"] {
            border-color: rgba(102, 126, 234, 0.4) !important;
            background: linear-gradient(145deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            transform: translateY(-4px) !important;
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.25), 0 4px 12px rgba(118, 75, 162, 0.2) !important;
        }
        
        /* Estilo para cards médios no topo (formato retangular vertical reduzido) */
        .cards-medium .stButton > button {
            border: 1px solid rgba(0, 0, 0, 0.08) !important;
            border-radius: 12px !important;
            padding: 12px 10px !important;
            margin: 6px !important;
            text-align: center !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%) !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04) !important;
            width: 100% !important;
            height: 112px !important;
            min-height: 112px !important;
            max-height: 112px !important;
            aspect-ratio: 5/7 !important;
            color: #374151 !important;
            font-weight: 600 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            font-size: 12px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            position: relative !important;
            flex-direction: column !important;
        }
        
        .cards-medium .stButton > button:hover {
            border-color: rgba(102, 126, 234, 0.2) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.12), 0 2px 6px rgba(0, 0, 0, 0.08) !important;
            background: linear-gradient(145deg, #ffffff 0%, #f0f4ff 100%) !important;
        }
        
        .cards-medium .stButton > button[kind="primary"] {
            border-color: rgba(102, 126, 234, 0.3) !important;
            background: linear-gradient(145deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2), 0 2px 6px rgba(118, 75, 162, 0.15) !important;
        }
        
        /* Layout responsivo e aesthetic */
        .main .block-container {
            max-width: 1400px !important;
            padding-top: 2rem !important;
        }
        
        /* Garantir tamanhos uniformes */
        .cards-large, .cards-medium {
            display: flex !important;
            align-items: stretch !important;
        }
        
        .cards-large > div, .cards-medium > div {
            display: flex !important;
            align-items: stretch !important;
        }
        
        /* Estilo para ícones nos cards retangulares verticais */
        .cards-large .stButton > button {
            flex-direction: column !important;
            gap: 12px !important;
        }
        
        .cards-large .stButton > button span:first-child {
            font-size: 3rem !important;
            line-height: 1 !important;
            display: block !important;
        }
        
        .cards-medium .stButton > button span:first-child {
            font-size: 1.8rem !important;
            line-height: 1 !important;
            margin-bottom: 4px !important;
        }
        
        /* Garantir estrutura vertical consistente */
        .cards-large .stButton > button > div,
        .cards-medium .stButton > button > div {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            height: 100% !important;
            gap: 8px !important;
        }
        </style>
        """)
        
        # Determinar se deve mostrar cards minimizados
        show_minimized = current_page is not None
        
        # Container com classe CSS apropriada
        container_class = "cards-medium" if show_minimized else "cards-large"
        st.html(f'<div class="{container_class}">')
        
        # Configurar colunas baseado no estado
        if show_minimized:
            # Cards médios em linha horizontal no topo
            num_cols = len(self.page_configs)
            cols = st.columns(num_cols)
        else:
            # Cards grandes em grid 4x2 (4 colunas, 2 linhas) formato carta de baralho vertical
            cols = st.columns(4)
            # Adicionar espaçamento extra para cards retangulares verticais
            st.html('<div style="margin-bottom: 2rem;"></div>')
        
        # Renderizar cards como botões estilizados
        for i, (page_key, config) in enumerate(self.page_configs.items()):
            col_index = i if show_minimized else i % 4
            
            with cols[col_index]:
                # Criar label simples para o botão
                if show_minimized:
                    button_label = f"{config['icon']} {config['title']}"
                else:
                    button_label = f"{config['icon']}\n{config['title']}"
                
                # Botão clicável estilizado como card
                if st.button(button_label, key=f"card_{page_key}", 
                           type="primary" if current_page == page_key else "secondary",
                           help=f"Acessar {config['description']}",
                           use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()
        
        # Fechar container
        st.html('</div>')

    def render_sidebar(self):
        """Render simplified sidebar with feedback only"""
        with sidebar:
            st.title("🧭 Dashboard Têxtil PE")
            
            # Add a home button to reset to card view
            if st.button("🏠 Voltar ao Início", use_container_width=True):
                st.session_state.current_page = None
                st.rerun()
            
            # Logout button
            if st.button("🚪 Sair", key="logout_btn",
                         help=f"Sair",
                         type="secondary",
                         use_container_width=True):
                AuthManager.logout()
                st.rerun()
            st.divider()

            # Show current page if any
            current_page = getattr(st.session_state, "current_page", None)
            if current_page and current_page in self.page_configs:
                config = self.page_configs[current_page]
                st.markdown(f"**Página Atual:** {config['icon']} {config['title']}")
                st.divider()

            create_feedback_section()



    def run(self):
        """Executa a aplicação principal com cards no topo"""
        # Registrar carregamento da página
        Analytics.log_event("app_start")

        # Renderizar perfil do usuário no topo
        self.render_user_profile()
        
        # Renderizar sidebar sempre (colapsado)
        self.render_sidebar()
        
        # Renderizar cards médios no topo quando página ativa
        self.render_medium_cards_top()

        # Verificar página atual
        current_page = getattr(st.session_state, "current_page", None)
        
        if current_page and current_page in self.pages:
            # Renderizar página selecionada diretamente
            data = self.load_data()
            try:
                self.pages[current_page].render(data)
            except Exception as e:
                st.error(f"Erro ao carregar página: {str(e)}")
                st.exception(e)
        else:
            # Renderizar cabeçalho e cards quando nenhuma página está ativa
            self.render_header()
            
            # Mostrar cards de navegação grandes
            self.render_analysis_cards()
            
            # Mostrar informações de boas-vindas
            st.divider()
            st.html("<h2> 👋 Bem-vindo ao Dashboard Ecossistema Têxtil PE</h2>")
            st.info("Selecione uma análise acima para começar a explorar os dados.")

        # Analytics na sidebar para modo admin
        query_params = st.query_params
        admin_mode = query_params.get("admin") == "on"
        if admin_mode:
            self._render_analytics_sidebar()

    def _render_analytics_sidebar(self):
        """Renderiza estatísticas de uso na sidebar"""
        with st.sidebar.expander("📈 Estatísticas de Uso"):
            session_id = Analytics.get_session_id()
            st.text(f"Sessão: {session_id[:8]}...")

            # Contadores de visitas
            if "visit_count" not in st.session_state:
                st.session_state.visit_count = 0
            st.session_state.visit_count += 1
            st.text(f"Visitas: {st.session_state.visit_count}")

            # Estado atual
            state = StateManager.get_state()
            st.text(f"Página ativa: {state.active_page}")

            if st.button("🔄 Recarregar Dados", key="reload_data"):
                self.data = None
                st.rerun()


if __name__ == "__main__":
    # Initialize user identifier (will use email if authenticated, fallback to generated ID)
    try:
        if "user_id" not in st.session_state:
            st.session_state["user_id"] = Analytics.generate_user_id()
    except:
        st.session_state["user_id"] = Analytics.generate_user_id()

    app = DashboardApp()
    app.run()
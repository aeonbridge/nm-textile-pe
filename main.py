import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from streamlit import sidebar

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from src.nm.analytics import Analytics
from src.nm.data_loader import DataLoader
from src.state import StateManager
from src.pages.overview import OverviewPage
from src.pages.indicators import IndicatorsPage
from src.pages.network_v2 import NetworkPageV2
from src.pages.risks import RisksPage
from src.pages.opportunities import OpportunitiesPage
from src.nm.feedback import create_feedback_section

# Configuração da página principal
st.set_page_config(
    page_title="Dashboard Ecossistema Têxtil PE",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar CSS customizado
# add_custom_css()

# Inicializar estado
StateManager.initialize_state()


class DashboardApp:
    """Classe principal do dashboard"""

    def __init__(self):
        self.pages = {
            "🏠 Visão Geral": OverviewPage(),
            #"🗺️ Visão Geográfica": GeographicPage(),
            "📊 Análise de Indicadores": IndicatorsPage(),
            "🕸️  Rede de Agentes-chave": NetworkPageV2(),
            "⚠️ Análise de Riscos": RisksPage(),
            "💡 Identificação de Oportunidades": OpportunitiesPage()
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

    def render_header(self):
        """Renderiza o cabeçalho principal"""
        st.markdown('<h1 class="main-header">📊 Dashboard Ecossistema Têxtil de Pernambuco</h1>',
                    unsafe_allow_html=True)

        # Informações contextuais
        st.markdown("""
        <div class="insight-box">
        <strong>💡 Sobre este Dashboard:</strong> Ferramenta interativa para apoiar stakeholders 
        na compreensão do ambiente, análise de tendências e tomada de decisão no ecossistema têxtil de Pernambuco.
        </div>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        with sidebar:
            st.title("🧭 Navegação")

            # Menu de páginas
            selected_page = st.selectbox(
                "Selecione uma análise:",
                options=list(self.pages.keys()),
                index=0,
                key="page_selector"
            )

            self.render_header()

            create_feedback_section()

            # Registrar evento de navegação
            Analytics.log_event("page_navigation", {
                "page": selected_page,
                "timestamp": str(pd.Timestamp.now())
            })

            # Atualizar estado
            state = StateManager.get_state()
            state.active_page = selected_page



            return selected_page



    def run(self):
        """Executa a aplicação principal"""
        # Registrar carregamento da página
        Analytics.log_event("app_start")

        # Renderizar interface
        #self.render_header()
        selected_page = self.render_sidebar()

        # Carregar dados
        data = self.load_data()

        # Renderizar página selecionada
        if selected_page in self.pages:
            try:
                self.pages[selected_page].render(data)
            except Exception as e:
                st.error(f"Erro ao carregar página: {str(e)}")
                st.exception(e)

        # Analytics na sidebar
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
    try:
        if st.session_state.user_id is None:
            st.session_state["user_id"] = Analytics.generate_user_id()
    except:
        st.session_state["user_id"] = Analytics.generate_user_id()

    app = DashboardApp()
    app.run()
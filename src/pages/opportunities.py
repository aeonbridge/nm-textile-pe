import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional

from src.utils.page_utils import Page, UIComponents, FilterManager, format_number, ChartGenerator
from src.state import StateManager

from src.nm.analytics import  Analytics


class OpportunitiesPage(Page):
    """Página de Identificação de Oportunidades"""

    def render(self, data: Dict[str, Any]):
        """Renderiza a página de identificação de oportunidades"""
        Analytics.log_event("page_view", {"page": "opportunities"})
        StateManager.increment_page_view("Identificação de Oportunidades")

        st.markdown('<h2 class="page-header">💡 Identificação de Oportunidades</h2>',
                    unsafe_allow_html=True)

        # Carregar dados de oportunidades
        opportunities_data = self._load_opportunities_data()

        # Filtros da página
        filtered_opportunities = self._render_page_filters(opportunities_data)

        # Layout principal
        col1, col2 = st.columns([2, 1])

        with col1:
            self._render_opportunities_matrix(filtered_opportunities)
            self._render_opportunities_by_category(filtered_opportunities)

        with col2:
            self._render_priority_opportunities(filtered_opportunities, data)
            self._render_stakeholder_recommendations(filtered_opportunities, data)

    def _load_opportunities_data(self) -> List[Dict[str, Any]]:
        """Carrega dados de oportunidades estruturadas"""
        return [
            {
                "id": "opp_001",
                "categoria": "Transformação Digital",
                "oportunidade": "Plataforma Digital Escalonada",
                "descricao": "Implementação de plataforma digital com níveis progressivos para inclusão de pequenos produtores",
                "cidade": ["Santa Cruz do Capibaribe", "Caruaru", "Toritama"],
                "segmento": "Geral",
                "impacto": "Alto",
                "viabilidade": "Média",
                "impacto_valor": 4,
                "viabilidade_valor": 3,
                "valor_prioridade": 12,
                "horizonte": "Curto prazo (1-2 anos)",
                "investimento_estimado": "R$ 5-10 milhões",
                "stakeholders_recomendados": ["Bruno Bezerra", "Cláuston Pacas Silva", "Valmir Ribeiro"]
            },
            {
                "id": "opp_002",
                "categoria": "Sustentabilidade",
                "oportunidade": "Consórcio de Tratamento de Efluentes",
                "descricao": "Sistema compartilhado para tratamento de efluentes das lavanderias de Toritama",
                "cidade": ["Toritama"],
                "segmento": "Lavanderias",
                "impacto": "Muito Alto",
                "viabilidade": "Média",
                "impacto_valor": 5,
                "viabilidade_valor": 3,
                "valor_prioridade": 15,
                "horizonte": "Médio prazo (3-5 anos)",
                "investimento_estimado": "R$ 8-12 milhões",
                "stakeholders_recomendados": ["Douglas Costa", "Sídia Haiut", "Raquel Lyra"]
            },
            {
                "id": "opp_003",
                "categoria": "Educação e Capacitação",
                "oportunidade": "Centro de Excelência em Design",
                "descricao": "Centro integrado de formação em design e moda para agregação de valor",
                "cidade": ["Caruaru"],
                "segmento": "Design e Moda",
                "impacto": "Alto",
                "viabilidade": "Alta",
                "impacto_valor": 4,
                "viabilidade_valor": 4,
                "valor_prioridade": 16,
                "horizonte": "Médio prazo (3-5 anos)",
                "investimento_estimado": "R$ 15-25 milhões",
                "stakeholders_recomendados": ["Newton Montenegro", "Ivania Porto", "Fernando Pimentel"]
            },
            {
                "id": "opp_004",
                "categoria": "Economia Circular",
                "oportunidade": "Sistema de Reaproveitamento de Resíduos",
                "descricao": "Implementação de economia circular para retalhos e sobras têxteis",
                "cidade": ["Santa Cruz do Capibaribe", "Caruaru"],
                "segmento": "Produção",
                "impacto": "Alto",
                "viabilidade": "Média",
                "impacto_valor": 4,
                "viabilidade_valor": 3,
                "valor_prioridade": 12,
                "horizonte": "Médio prazo (3-5 anos)",
                "investimento_estimado": "R$ 3-8 milhões",
                "stakeholders_recomendados": ["José Gomes Filho", "Gilson Belarmino", "Ricardo Cappelli"]
            },
            {
                "id": "opp_005",
                "categoria": "Empreendedorismo Feminino",
                "oportunidade": "Programa de Microcrédito para Mulheres",
                "descricao": "Linha específica de microcrédito e capacitação para empreendedoras do setor",
                "cidade": ["Santa Cruz do Capibaribe", "Caruaru", "Toritama"],
                "segmento": "Facções",
                "impacto": "Alto",
                "viabilidade": "Alta",
                "impacto_valor": 4,
                "viabilidade_valor": 4,
                "valor_prioridade": 16,
                "horizonte": "Curto prazo (1-2 anos)",
                "investimento_estimado": "R$ 10-20 milhões",
                "stakeholders_recomendados": ["Ivania Porto", "Danielle Lago Bruno de Faria",
                                              "Shirley Kelly Monteiro Torres Oliveira"]
            },
            {
                "id": "opp_006",
                "categoria": "Inovação Tecnológica",
                "oportunidade": "Tecnologias de Baixo Consumo Hídrico",
                "descricao": "Desenvolvimento e adoção de tecnologias para redução do consumo de água",
                "cidade": ["Toritama"],
                "segmento": "Lavanderias",
                "impacto": "Muito Alto",
                "viabilidade": "Baixa",
                "impacto_valor": 5,
                "viabilidade_valor": 2,
                "valor_prioridade": 10,
                "horizonte": "Longo prazo (mais de 5 anos)",
                "investimento_estimado": "R$ 20-40 milhões",
                "stakeholders_recomendados": ["Ricardo Cappelli", "Fernando Pimentel", "Mario Cezar de Aguiar"]
            }
        ]

    def _render_page_filters(self, opportunities_data: List[Dict]) -> List[Dict]:
        """Renderiza filtros específicos da página"""
        with st.expander("🎛️ Filtros de Oportunidades", expanded=True):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                # Filtro por categoria
                categories = list(set([opp["categoria"] for opp in opportunities_data]))
                selected_categories = st.multiselect(
                    "Categorias:",
                    options=categories,
                    default=categories,
                    key="opp_categories"
                )

            with col2:
                # Filtro por cidade
                all_cities = []
                for opp in opportunities_data:
                    all_cities.extend(opp["cidade"])
                cities = list(set(all_cities))

                selected_cities = st.multiselect(
                    "Cidades:",
                    options=cities,
                    default=cities,
                    key="opp_cities"
                )

            with col3:
                # Filtro por horizonte temporal
                horizons = list(set([opp["horizonte"] for opp in opportunities_data]))
                selected_horizons = st.multiselect(
                    "Horizonte Temporal:",
                    options=horizons,
                    default=horizons,
                    key="opp_horizons"
                )

            with col4:
                # Filtro por prioridade mínima
                min_priority = st.slider(
                    "Prioridade Mínima:",
                    min_value=1,
                    max_value=25,
                    value=10,
                    key="opp_min_priority"
                )

        # Filtrar oportunidades
        filtered = []
        for opp in opportunities_data:
            # Verificar filtros
            category_match = opp["categoria"] in selected_categories
            city_match = any(city in selected_cities for city in opp["cidade"])
            horizon_match = opp["horizonte"] in selected_horizons
            priority_match = opp["valor_prioridade"] >= min_priority

            if category_match and city_match and horizon_match and priority_match:
                filtered.append(opp)

        return filtered

    def _render_opportunities_matrix(self, opportunities_data: List[Dict]):
        """Renderiza matriz de oportunidades (viabilidade x impacto)"""
        st.subheader("🎯 Matriz de Priorização de Oportunidades")

        if not opportunities_data:
            st.warning("Nenhuma oportunidade encontrada com os filtros selecionados.")
            return

        # Criar DataFrame para plotagem
        df_matrix = pd.DataFrame(opportunities_data)

        # Gráfico de dispersão
        fig = go.Figure()

        # Adicionar pontos por categoria
        categories = df_matrix['categoria'].unique()
        colors = px.colors.qualitative.Set3

        for i, category in enumerate(categories):
            cat_data = df_matrix[df_matrix['categoria'] == category]

            fig.add_trace(go.Scatter(
                x=cat_data['viabilidade_valor'],
                y=cat_data['impacto_valor'],
                mode='markers+text',
                name=category,
                text=cat_data['oportunidade'].str[:20] + '...',
                textposition="top center",
                marker=dict(
                    size=cat_data['valor_prioridade'] * 2,
                    color=colors[i % len(colors)],
                    line=dict(width=2, color='white'),
                    opacity=0.8
                ),
                hovertemplate=(
                        "<b>%{text}</b><br>" +
                        "Viabilidade: %{x}<br>" +
                        "Impacto: %{y}<br>" +
                        "Prioridade: %{marker.size}<br>" +
                        "<extra></extra>"
                )
            ))

        # Adicionar linhas de grade para quadrantes
        fig.add_shape(type="line", x0=0.5, y0=2.5, x1=5.5, y1=2.5,
                      line=dict(color="gray", width=1, dash="dash"))
        fig.add_shape(type="line", x0=2.5, y0=0.5, x1=2.5, y1=5.5,
                      line=dict(color="gray", width=1, dash="dash"))

        # Anotações dos quadrantes
        annotations = [
            dict(x=1.25, y=4.5, text="Alto Impacto<br>Baixa Viabilidade", showarrow=False),
            dict(x=4, y=4.5, text="Alto Impacto<br>Alta Viabilidade", showarrow=False),
            dict(x=1.25, y=1.5, text="Baixo Impacto<br>Baixa Viabilidade", showarrow=False),
            dict(x=4, y=1.5, text="Baixo Impacto<br>Alta Viabilidade", showarrow=False)
        ]

        fig.update_layout(
            title="Matriz de Priorização: Impacto vs Viabilidade",
            xaxis=dict(
                title="Viabilidade",
                range=[0.5, 5.5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=["Muito Baixa", "Baixa", "Média", "Alta", "Muito Alta"]
            ),
            yaxis=dict(
                title="Impacto",
                range=[0.5, 5.5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
            ),
            height=600,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_opportunities_by_category(self, opportunities_data: List[Dict]):
        """Renderiza oportunidades por categoria"""
        st.subheader("📊 Oportunidades por Categoria")

        if not opportunities_data:
            return

        # Análise por categoria
        df_cat = pd.DataFrame(opportunities_data)
        category_analysis = df_cat.groupby('categoria').agg({
            'valor_prioridade': ['mean', 'count'],
            'investimento_estimado': 'first'  # Para mostrar exemplo
        }).round(1)

        category_analysis.columns = ['Prioridade Média', 'Quantidade', 'Investimento Exemplo']
        category_analysis = category_analysis.reset_index()

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de barras - Quantidade por categoria
            fig_count = px.bar(
                category_analysis,
                x='categoria',
                y='Quantidade',
                color='Prioridade Média',
                title="Quantidade e Prioridade Média por Categoria",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_count, use_container_width=True)

        with col2:
            # Análise temporal
            horizon_analysis = df_cat.groupby('horizonte').size().reset_index(name='count')
            fig_horizon = px.pie(
                horizon_analysis,
                values='count',
                names='horizonte',
                title="Distribuição por Horizonte Temporal"
            )
            st.plotly_chart(fig_horizon, use_container_width=True)

    def _render_priority_opportunities(self, opportunities_data: List[Dict], data: Dict[str, Any]):
        """Renderiza oportunidades prioritárias"""
        st.subheader("🏆 Oportunidades Prioritárias")

        if not opportunities_data:
            st.info("Nenhuma oportunidade prioritária encontrada.")
            return

        # Ordenar por prioridade
        sorted_opportunities = sorted(
            opportunities_data,
            key=lambda x: x['valor_prioridade'],
            reverse=True
        )[:5]  # Top 5

        for i, opp in enumerate(sorted_opportunities, 1):
            with st.expander(f"{i}. {opp['oportunidade']} (Prioridade: {opp['valor_prioridade']})"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Categoria:** {opp['categoria']}")
                    st.markdown(f"**Descrição:** {opp['descricao']}")
                    st.markdown(f"**Cidades:** {', '.join(opp['cidade'])}")
                    st.markdown(f"**Segmento:** {opp['segmento']}")
                    st.markdown(f"**Horizonte:** {opp['horizonte']}")
                    st.markdown(f"**Investimento Estimado:** {opp['investimento_estimado']}")

                with col2:
                    st.markdown("**Avaliação:**")
                    st.markdown(f"- Impacto: {opp['impacto']}")
                    st.markdown(f"- Viabilidade: {opp['viabilidade']}")
                    st.markdown(f"- Prioridade: {opp['valor_prioridade']}")

                # Stakeholders recomendados
                st.markdown("**Stakeholders Recomendados:**")
                for stakeholder in opp['stakeholders_recomendados']:
                    st.markdown(f"- {stakeholder}")

    def _render_stakeholder_recommendations(self, opportunities_data: List[Dict], data: Dict[str, Any]):
        """Renderiza recomendações de stakeholders"""
        st.subheader("👥 Stakeholders-Chave por Oportunidade")

        if not opportunities_data:
            return

        # Seletor de oportunidade
        opp_names = [f"{opp['oportunidade']} ({opp['categoria']})" for opp in opportunities_data]

        if opp_names:
            selected_opp_index = st.selectbox(
                "Selecione uma oportunidade:",
                range(len(opp_names)),
                format_func=lambda x: opp_names[x],
                key="stakeholder_opp_selection"
            )

            selected_opp = opportunities_data[selected_opp_index]

            st.markdown(f"### {selected_opp['oportunidade']}")

            # Informações da oportunidade
            st.markdown(f"**Descrição:** {selected_opp['descricao']}")
            st.markdown(f"**Investimento:** {selected_opp['investimento_estimado']}")
            st.markdown(f"**Horizonte:** {selected_opp['horizonte']}")

            # Stakeholders recomendados com detalhes
            st.markdown("### 🎯 Stakeholders Recomendados para Discussão")

            for stakeholder in selected_opp['stakeholders_recomendados']:
                # Buscar informações do stakeholder na ontologia
                stakeholder_info = self._get_stakeholder_info(stakeholder, data)

                if stakeholder_info:
                    with st.expander(f"👤 {stakeholder}"):
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.markdown(f"**Cargo:** {stakeholder_info.get('position', 'N/A')}")
                            st.markdown(f"**Cidade:** {stakeholder_info.get('main_city', 'N/A')}")
                            st.markdown(f"**Área de Atuação:** {stakeholder_info.get('activity_area', 'N/A')}")
                            st.markdown(f"**Tipo de Liderança:** {stakeholder_info.get('leadership_type', 'N/A')}")

                        with col2:
                            relevance = stakeholder_info.get('relevance_degree', 'N/A')
                            st.metric("Relevância", f"{relevance}/10" if relevance != 'N/A' else 'N/A')

                            impact_scale = stakeholder_info.get('impact_scale', 'N/A')
                            st.markdown(f"**Escala:** {impact_scale}")

                        # Justificativa da recomendação
                        justification = self._generate_stakeholder_justification(selected_opp, stakeholder_info)
                        st.markdown(f"**Por que este stakeholder?** {justification}")
                else:
                    st.markdown(f"- **{stakeholder}** (informações detalhadas não disponíveis)")

            # Próximos passos sugeridos
            st.markdown("### 📋 Próximos Passos Sugeridos")
            next_steps = self._generate_next_steps(selected_opp)
            for step in next_steps:
                st.markdown(f"- {step}")

    def _get_stakeholder_info(self, stakeholder_name: str, data: Dict[str, Any]) -> Optional[Dict]:
        """Busca informações de um stakeholder específico"""
        ontology_data = data.get('ontologia')
        if not ontology_data:
            return None

        # Extrair dados dos atores
        try:
            if 'textile_ecosystem_network_ontology' in ontology_data:
                actors = ontology_data['textile_ecosystem_network_ontology'].get('nodes', [])
            elif 'ontologia_pessoas_ecossistema_textil_pernambuco' in ontology_data:
                actors = ontology_data['ontologia_pessoas_ecossistema_textil_pernambuco'].get('nos', [])
            else:
                return None

            # Buscar por nome
            for actor in actors:
                if actor.get('name', '') == stakeholder_name:
                    attrs = actor.get('attributes', {})
                    return {
                        'name': actor.get('name', ''),
                        'position': actor.get('position', ''),
                        'main_city': attrs.get('main_city', ''),
                        'activity_area': attrs.get('activity_area', ''),
                        'leadership_type': attrs.get('leadership_type', ''),
                        'relevance_degree': attrs.get('relevance_degree', ''),
                        'impact_scale': attrs.get('impact_scale', ''),
                        'main_contribution': attrs.get('main_contribution', '')
                    }

            return None

        except Exception:
            return None

    def _generate_stakeholder_justification(self, opportunity: Dict, stakeholder_info: Dict) -> str:
        """Gera justificativa para recomendação do stakeholder"""
        justifications = []

        # Baseado na área de atuação
        if 'digital' in opportunity['categoria'].lower() and 'digital' in stakeholder_info.get('activity_area',
                                                                                               '').lower():
            justifications.append("expertise em transformação digital")

        # Baseado na cidade
        stakeholder_city = stakeholder_info.get('main_city', '')
        if stakeholder_city in opportunity.get('cidade', []):
            justifications.append(f"atuação em {stakeholder_city}")

        # Baseado no tipo de liderança
        leadership = stakeholder_info.get('leadership_type', '')
        if 'Governamental' in leadership and 'sustentabilidade' in opportunity['categoria'].lower():
            justifications.append("capacidade de articulação de políticas públicas")
        elif 'Empresarial' in leadership and 'empreendedorismo' in opportunity['categoria'].lower():
            justifications.append("experiência em desenvolvimento empresarial")
        elif 'Associativa' in leadership:
            justifications.append("capacidade de mobilização setorial")

        # Baseado na relevância
        relevance = stakeholder_info.get('relevance_degree', 0)
        if isinstance(relevance, (int, float)) and relevance >= 8:
            justifications.append("alta relevância no ecossistema")

        if not justifications:
            justifications.append("expertise relevante para a oportunidade")

        return ", ".join(justifications)

    def _generate_next_steps(self, opportunity: Dict) -> List[str]:
        """Gera próximos passos para uma oportunidade"""
        category = opportunity['categoria']

        if 'Digital' in category:
            return [
                "Realizar workshop de alinhamento com stakeholders-chave",
                "Mapear necessidades específicas dos usuários finais",
                "Desenvolver prototótipo funcional mínimo",
                "Estabelecer cronograma de implementação faseada",
                "Definir métricas de sucesso e monitoramento"
            ]
        elif 'Sustentabilidade' in category:
            return [
                "Realizar estudo de viabilidade técnica e ambiental",
                "Articular parcerias público-privadas",
                "Desenvolver modelo de governança compartilhada",
                "Estabelecer marcos regulatórios necessários",
                "Criar plano de financiamento sustentável"
            ]
        elif 'Educação' in category:
            return [
                "Mapear demandas de capacitação no setor",
                "Desenvolver currículo adaptado às necessidades locais",
                "Estabelecer parcerias com instituições de ensino",
                "Criar programa piloto de formação",
                "Definir sistema de certificação e reconhecimento"
            ]
        elif 'Empreendedorismo' in category:
            return [
                "Realizar diagnóstico das necessidades das empreendedoras",
                "Desenvolver produtos financeiros específicos",
                "Criar programa de mentoria e acompanhamento",
                "Estabelecer rede de apoio e suporte",
                "Definir indicadores de impacto social"
            ]
        else:
            return [
                "Realizar reunião de alinhamento inicial",
                "Desenvolver plano detalhado de implementação",
                "Identificar recursos e fontes de financiamento",
                "Estabelecer cronograma e marcos de entrega",
                "Definir governança e responsabilidades"
            ]


# Criar uma página de riscos básica para completar a estrutura
class RisksPage(Page):
    """Página de Análise de Riscos"""

    def render(self, data: Dict[str, Any]):
        """Renderiza a página de análise de riscos"""
        Analytics.log_event("page_view", {"page": "risks"})
        StateManager.increment_page_view("Análise de Riscos")

        st.markdown('<h2 class="page-header">⚠️ Análise de Riscos</h2>',
                    unsafe_allow_html=True)

        st.info("Esta página está em desenvolvimento e conterá análise detalhada de riscos da cadeia de valor.")

        # Placeholder para estrutura de riscos
        risk_categories = {
            "🏢 Riscos Econômicos": [
                "Concorrência com produtos importados",
                "Dependência de intermediários",
                "Volatilidade de preços de insumos",
                "Sazonalidade acentuada"
            ],
            "👥 Riscos Sociais": [
                "Trabalho infantil",
                "Precarização do trabalho",
                "Evasão escolar",
                "Desigualdade de gênero"
            ],
            "🌍 Riscos Ambientais": [
                "Escassez hídrica",
                "Poluição de recursos hídricos",
                "Pressão regulatória ambiental",
                "Gestão inadequada de resíduos"
            ],
            "💻 Riscos Tecnológicos": [
                "Exclusão da transformação digital",
                "Obsolescência tecnológica",
                "Dependência de plataformas externas",
                "Resistência cultural à digitalização"
            ]
        }

        # Layout em abas
        tabs = st.tabs(list(risk_categories.keys()))

        for i, (category, risks) in enumerate(risk_categories.items()):
            with tabs[i]:
                st.subheader(category)

                for risk in risks:
                    with st.expander(f"⚠️ {risk}"):
                        st.markdown(f"""
                        **Descrição:** Análise detalhada do risco "{risk}" será implementada.

                        **Impacto Potencial:** Alto/Médio/Baixo

                        **Probabilidade:** Alta/Média/Baixa

                        **Medidas de Mitigação:** A serem definidas

                        **Stakeholders Afetados:** Lista dos atores impactados
                        """)

        # Matriz de riscos placeholder
        st.subheader("🎯 Matriz de Riscos")
        st.info("Matriz de probabilidade vs impacto será implementada com dados reais dos riscos mapeados.")

        # Plano de contingência
        st.subheader("📋 Planos de Contingência")
        st.info("Planos de resposta a riscos críticos serão desenvolvidos em colaboração com stakeholders.")
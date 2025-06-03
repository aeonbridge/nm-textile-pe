import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from typing import Dict, Any, List, Optional

from src.utils import Page, Analytics, UIComponents, FilterManager, format_number
from src.state import StateManager


class NetworkPage(Page):
    """Página de Rede de Atores"""

    def render(self, data: Dict[str, Any]):
        """Renderiza a página de rede de atores"""
        Analytics.log_event("page_view", {"page": "network"})
        StateManager.increment_page_view("Rede de Atores")

        st.markdown('<h2 class="page-header">🔄 Rede de Atores e Relacionamentos</h2>',
                    unsafe_allow_html=True)

        # Verificar se dados da ontologia estão disponíveis
        ontology_data = data.get('ontologia')
        if not ontology_data:
            st.warning("Dados da ontologia não estão disponíveis.")
            self._render_placeholder_content()
            return

        # Extrair dados da ontologia
        actors_data = self._extract_actors_data(ontology_data)
        if not actors_data:
            st.warning("Não foi possível extrair dados dos atores.")
            return

        # Filtros da página
        filtered_actors = self._render_page_filters(actors_data)

        # Layout principal
        col1, col2 = st.columns([2, 1])

        with col1:
            self._render_network_visualization(filtered_actors, ontology_data)
            self._render_network_analysis(filtered_actors)

        with col2:
            self._render_actor_details(filtered_actors)
            self._render_network_stats(filtered_actors)

    def _extract_actors_data(self, ontology_data: Dict[str, Any]) -> Optional[List[Dict]]:
        """Extrai dados dos atores da ontologia"""
        try:
            # Tentar diferentes estruturas de ontologia
            if 'textile_ecosystem_network_ontology' in ontology_data:
                return ontology_data['textile_ecosystem_network_ontology'].get('nodes', [])
            elif 'ontologia_pessoas_ecossistema_textil_pernambuco' in ontology_data:
                return ontology_data['ontologia_pessoas_ecossistema_textil_pernambuco'].get('nos', [])
            elif 'nodes' in ontology_data:
                return ontology_data['nodes']
            elif 'nos' in ontology_data:
                return ontology_data['nos']
            else:
                return None
        except Exception as e:
            st.error(f"Erro ao extrair dados dos atores: {str(e)}")
            return None

    def _render_page_filters(self, actors_data: List[Dict]) -> List[Dict]:
        """Renderiza filtros específicos da página"""
        with st.expander("🎛️ Filtros de Rede", expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                # Filtro por tipo de liderança
                leadership_types = list(set([
                    actor.get('attributes', {}).get('leadership_type', 'Não especificado')
                    for actor in actors_data
                ]))

                selected_leadership = st.multiselect(
                    "Tipo de Liderança:",
                    options=leadership_types,
                    default=leadership_types,
                    key="network_leadership_filter"
                )

            with col2:
                # Filtro por cidade
                cities = list(set([
                    actor.get('attributes', {}).get('main_city', 'Não especificado')
                    for actor in actors_data
                ]))

                selected_cities = st.multiselect(
                    "Cidade:",
                    options=cities,
                    default=cities,
                    key="network_city_filter"
                )

            with col3:
                # Filtro por relevância mínima
                relevance_values = [
                    actor.get('attributes', {}).get('relevance_degree', 0)
                    for actor in actors_data
                    if isinstance(actor.get('attributes', {}).get('relevance_degree'), (int, float))
                ]

                if relevance_values:
                    min_relevance = st.slider(
                        "Relevância Mínima:",
                        min_value=int(min(relevance_values)),
                        max_value=int(max(relevance_values)),
                        value=int(min(relevance_values)),
                        key="network_relevance_filter"
                    )
                else:
                    min_relevance = 0

        # Filtrar atores
        filtered_actors = []
        for actor in actors_data:
            attrs = actor.get('attributes', {})

            # Verificar filtros
            leadership_match = attrs.get('leadership_type', 'Não especificado') in selected_leadership
            city_match = attrs.get('main_city', 'Não especificado') in selected_cities
            relevance_match = attrs.get('relevance_degree', 0) >= min_relevance

            if leadership_match and city_match and relevance_match:
                filtered_actors.append(actor)

        return filtered_actors

    def _render_network_visualization(self, actors_data: List[Dict], ontology_data: Dict[str, Any]):
        """Renderiza visualização da rede"""
        st.subheader("🕸️ Visualização da Rede")

        if len(actors_data) < 2:
            st.warning("Dados insuficientes para visualização da rede.")
            return

        # Criar grafo NetworkX
        G = self._create_networkx_graph(actors_data, ontology_data)

        if G.number_of_nodes() == 0:
            st.warning("Nenhum nó disponível para visualização.")
            return

        # Visualização com Plotly
        self._render_plotly_network(G)

        # Opções de exportação
        if st.button("📥 Exportar Rede (GraphML)", key="export_network"):
            try:
                nx.write_graphml(G, "network_export.graphml")
                st.success("Rede exportada como 'network_export.graphml'")
            except Exception as e:
                st.error(f"Erro ao exportar: {str(e)}")

    def _create_networkx_graph(self, actors_data: List[Dict], ontology_data: Dict[str, Any]) -> nx.Graph:
        """Cria grafo NetworkX a partir dos dados"""
        G = nx.Graph()

        # Adicionar nós
        for actor in actors_data:
            actor_id = actor.get('id', actor.get('name', ''))
            if actor_id:
                attrs = actor.get('attributes', {})
                G.add_node(
                    actor_id,
                    name=actor.get('name', ''),
                    position=actor.get('position', ''),
                    city=attrs.get('main_city', ''),
                    leadership_type=attrs.get('leadership_type', ''),
                    relevance=attrs.get('relevance_degree', 0),
                    impact_scale=attrs.get('impact_scale', '')
                )

        # Adicionar arestas se disponíveis
        edges = self._extract_edges_data(ontology_data)
        if edges:
            actor_ids = [actor.get('id', actor.get('name', '')) for actor in actors_data]

            for edge in edges:
                source = edge.get('source', edge.get('origem', ''))
                target = edge.get('target', edge.get('destino', ''))

                if source in actor_ids and target in actor_ids:
                    edge_attrs = edge.get('attributes', {})
                    G.add_edge(
                        source,
                        target,
                        relationship=edge.get('type', ''),
                        intensity=edge_attrs.get('intensity', edge_attrs.get('intensidade', '')),
                        context=edge_attrs.get('context', edge_attrs.get('contexto', ''))
                    )

        return G

    def _extract_edges_data(self, ontology_data: Dict[str, Any]) -> Optional[List[Dict]]:
        """Extrai dados das arestas da ontologia"""
        try:
            if 'textile_ecosystem_network_ontology' in ontology_data:
                return ontology_data['textile_ecosystem_network_ontology'].get('edges', [])
            elif 'ontologia_pessoas_ecossistema_textil_pernambuco' in ontology_data:
                return ontology_data['ontologia_pessoas_ecossistema_textil_pernambuco'].get('arestas', [])
            elif 'edges' in ontology_data:
                return ontology_data['edges']
            elif 'arestas' in ontology_data:
                return ontology_data['arestas']
            else:
                return []
        except Exception:
            return []

    def _render_plotly_network(self, G: nx.Graph):
        """Renderiza rede usando Plotly"""
        # Calcular layout
        pos = nx.spring_layout(G, k=1, iterations=50)

        # Preparar dados para plotly
        edge_x = []
        edge_y = []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        # Criar trace das arestas
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        # Preparar dados dos nós
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            node_data = G.nodes[node]
            node_text.append(f"{node_data.get('name', node)}<br>{node_data.get('position', '')}")
            node_size.append(max(10, node_data.get('relevance', 5) * 3))

            # Cor baseada no tipo de liderança
            leadership = node_data.get('leadership_type', '')
            color_map = {
                'Associativa': '#FF6B6B',
                'Política': '#4ECDC4',
                'Empresarial': '#45B7D1',
                'Governamental': '#96CEB4',
                'Técnica': '#FFEAA7'
            }
            node_color.append(color_map.get(leadership.split(' e ')[0], '#DDA0DD'))

        # Criar trace dos nós
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[name.split('<br>')[0] for name in node_text],
            hovertext=node_text,
            textposition="middle center",
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            )
        )

        # Criar figura
        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title="Rede de Atores do Ecossistema Têxtil",
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            annotations=[dict(
                                text="Tamanho dos nós representa a relevância. Cores representam tipos de liderança.",
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.005, y=-0.002,
                                xanchor='left', yanchor='bottom',
                                font=dict(size=12)
                            )],
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            height=600
                        ))

        st.plotly_chart(fig, use_container_width=True)

    def _render_network_analysis(self, actors_data: List[Dict]):
        """Renderiza análise da rede"""
        st.subheader("📊 Análise da Rede")

        # Análise por tipo de liderança
        leadership_analysis = self._analyze_by_leadership(actors_data)

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de distribuição por tipo de liderança
            if leadership_analysis:
                fig = px.pie(
                    values=list(leadership_analysis.values()),
                    names=list(leadership_analysis.keys()),
                    title="Distribuição por Tipo de Liderança"
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Análise por cidade
            city_analysis = self._analyze_by_city(actors_data)
            if city_analysis:
                fig = px.bar(
                    x=list(city_analysis.keys()),
                    y=list(city_analysis.values()),
                    title="Atores por Cidade",
                    labels={'x': 'Cidade', 'y': 'Número de Atores'}
                )
                st.plotly_chart(fig, use_container_width=True)

        # Análise de relevância
        self._render_relevance_analysis(actors_data)

    def _render_actor_details(self, actors_data: List[Dict]):
        """Renderiza detalhes do ator selecionado"""
        st.subheader("👤 Detalhes do Ator")

        # Campo de busca
        search_term = st.text_input(
            "Buscar ator por nome:",
            key="network_search",
            placeholder="Digite o nome do ator..."
        )

        # Filtrar atores pela busca
        if search_term:
            filtered_actors = [
                actor for actor in actors_data
                if search_term.lower() in actor.get('name', '').lower()
            ]

            if filtered_actors:
                st.success(f"Encontrados {len(filtered_actors)} resultados.")
            else:
                st.warning("Nenhum ator encontrado.")
                return
        else:
            filtered_actors = actors_data

        if not filtered_actors:
            st.info("Nenhum ator disponível com os filtros atuais.")
            return

        # Ordenar por relevância
        sorted_actors = sorted(
            filtered_actors,
            key=lambda x: x.get('attributes', {}).get('relevance_degree', 0),
            reverse=True
        )

        # Seleção do ator
        actor_names = [f"{actor.get('name', 'N/A')} ({actor.get('position', 'N/A')})" for actor in sorted_actors]

        if actor_names:
            selected_index = st.selectbox(
                "Selecione um ator:",
                range(len(actor_names)),
                format_func=lambda x: actor_names[x],
                key="network_actor_selection"
            )

            selected_actor = sorted_actors[selected_index]
            self._display_actor_details(selected_actor)

    def _display_actor_details(self, actor: Dict[str, Any]):
        """Exibe detalhes de um ator específico"""
        attrs = actor.get('attributes', {})

        # Nome e posição
        st.markdown(f"### {actor.get('name', 'N/A')}")
        st.markdown(f"**Cargo:** {actor.get('position', 'N/A')}")

        # Foto de perfil se disponível
        photo_url = attrs.get('profile_photo')
        if photo_url and photo_url != "não disponível em fontes abertas":
            try:
                st.image(photo_url, width=200, caption=actor.get('name', ''))
            except:
                pass  # Falha silenciosa se imagem não carregar

        # Informações principais
        info_data = {
            "Cidade Principal": attrs.get('main_city', 'N/A'),
            "Estado": attrs.get('state', 'N/A'),
            "Tipo de Liderança": attrs.get('leadership_type', 'N/A'),
            "Área de Atuação": attrs.get('activity_area', 'N/A'),
            "Grau de Relevância": f"{attrs.get('relevance_degree', 'N/A')}/10",
            "Escala de Impacto": attrs.get('impact_scale', 'N/A')
        }

        # Exibir como tabela
        info_df = pd.DataFrame(list(info_data.items()), columns=["Atributo", "Valor"])
        st.dataframe(info_df, hide_index=True)

        # Contribuição principal
        main_contribution = attrs.get('main_contribution')
        if main_contribution:
            st.markdown(f"**Contribuição Principal:** {main_contribution}")

        # Citação relevante
        quote = attrs.get('relevant_quote')
        if quote:
            st.markdown(f"**Citação Relevante:**")
            st.markdown(f"*\"{quote}\"*")

        # Links de perfil
        linkedin = attrs.get('profile_linkedin')
        instagram = attrs.get('profile_instagram')

        if linkedin and linkedin != "não identificado":
            st.markdown(f"[🔗 LinkedIn]({linkedin})")

        if instagram and instagram != "não identificado":
            st.markdown(f"[📷 Instagram]({instagram})")

    def _render_network_stats(self, actors_data: List[Dict]):
        """Renderiza estatísticas da rede"""
        st.subheader("📈 Estatísticas da Rede")

        # Métricas básicas
        total_actors = len(actors_data)
        st.metric("Total de Atores", total_actors)

        # Relevância média
        relevances = [
            actor.get('attributes', {}).get('relevance_degree', 0)
            for actor in actors_data
            if isinstance(actor.get('attributes', {}).get('relevance_degree'), (int, float))
        ]

        if relevances:
            avg_relevance = sum(relevances) / len(relevances)
            st.metric("Relevância Média", f"{avg_relevance:.1f}/10")

        # Distribuição por escala de impacto
        impact_scales = [
            actor.get('attributes', {}).get('impact_scale', 'N/A')
            for actor in actors_data
        ]

        impact_distribution = {}
        for scale in impact_scales:
            impact_distribution[scale] = impact_distribution.get(scale, 0) + 1

        if impact_distribution:
            st.markdown("**Distribuição por Escala de Impacto:**")
            for scale, count in impact_distribution.items():
                st.markdown(f"- {scale}: {count}")

        # Top atores por relevância
        if relevances:
            top_actors = sorted(
                actors_data,
                key=lambda x: x.get('attributes', {}).get('relevance_degree', 0),
                reverse=True
            )[:5]

            st.markdown("**Top 5 Atores por Relevância:**")
            for i, actor in enumerate(top_actors, 1):
                relevance = actor.get('attributes', {}).get('relevance_degree', 0)
                st.markdown(f"{i}. {actor.get('name', 'N/A')} ({relevance}/10)")

    def _analyze_by_leadership(self, actors_data: List[Dict]) -> Dict[str, int]:
        """Analisa distribuição por tipo de liderança"""
        leadership_count = {}

        for actor in actors_data:
            leadership = actor.get('attributes', {}).get('leadership_type', 'Não especificado')
            leadership_count[leadership] = leadership_count.get(leadership, 0) + 1

        return leadership_count

    def _analyze_by_city(self, actors_data: List[Dict]) -> Dict[str, int]:
        """Analisa distribuição por cidade"""
        city_count = {}

        for actor in actors_data:
            city = actor.get('attributes', {}).get('main_city', 'Não especificado')
            city_count[city] = city_count.get(city, 0) + 1

        return city_count

    def _render_relevance_analysis(self, actors_data: List[Dict]):
        """Renderiza análise de relevância"""
        with st.expander("🎯 Análise de Relevância"):
            relevances = [
                actor.get('attributes', {}).get('relevance_degree', 0)
                for actor in actors_data
                if isinstance(actor.get('attributes', {}).get('relevance_degree'), (int, float))
            ]

            if relevances:
                # Histograma de relevância
                fig = px.histogram(
                    x=relevances,
                    nbins=10,
                    title="Distribuição de Relevância dos Atores",
                    labels={'x': 'Grau de Relevância', 'y': 'Número de Atores'}
                )
                st.plotly_chart(fig, use_container_width=True)

                # Estatísticas
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Mínimo", f"{min(relevances)}/10")

                with col2:
                    st.metric("Média", f"{sum(relevances) / len(relevances):.1f}/10")

                with col3:
                    st.metric("Máximo", f"{max(relevances)}/10")

    def _render_placeholder_content(self):
        """Renderiza conteúdo placeholder quando dados não estão disponíveis"""
        st.info("A visualização da rede de atores requer dados da ontologia do ecossistema.")

        st.markdown("""
        ### 🔄 Rede de Atores - Funcionalidades Planejadas

        Esta página permitirá:

        #### 📊 Visualização Interativa
        - Grafo de rede mostrando conexões entre atores-chave
        - Nós dimensionados por relevância e influência
        - Cores representando tipos de liderança
        - Filtros por cidade, setor e escala de impacto

        #### 🔍 Análise de Atores
        - Busca por atores específicos
        - Perfis detalhados com informações de contato
        - Análise de conexões diretas e indiretas
        - Identificação de intermediadores e conectores-chave

        #### 📈 Métricas de Rede
        - Centralidade e influência de atores
        - Clusters e comunidades
        - Análise de densidade de conexões
        - Identificação de gaps na rede

        #### 💡 Insights Estratégicos
        - Mapeamento de stakeholders por oportunidade
        - Recomendações de articulações
        - Análise de poder e influência
        - Sugestões de parcerias estratégicas
        """)

        # Exemplo de como seria a interface
        st.markdown("### 🎛️ Filtros de Exemplo")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.multiselect(
                "Tipo de Liderança:",
                ["Associativa", "Política", "Empresarial", "Governamental"],
                disabled=True
            )

        with col2:
            st.multiselect(
                "Cidade:",
                ["Santa Cruz do Capibaribe", "Caruaru", "Toritama"],
                disabled=True
            )

        with col3:
            st.slider(
                "Relevância Mínima:",
                min_value=1,
                max_value=10,
                value=5,
                disabled=True
            )

        st.info(
            "💡 **Dica:** Para ver esta funcionalidade em ação, certifique-se de que os arquivos de ontologia estejam disponíveis no diretório `static/datasets/`.")
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple, Optional
import networkx as nx
from src.nm.data_loader import DataLoader

class EcosystemNetworkRenderer:
    """
    A class to render textile ecosystem networks from JSON ontology data.
    Designed for use with Streamlit applications.
    """

    def __init__(self):
        self.graph = None
        self.pos = None
        self.node_data = {}
        self.edge_data = {}
        self.clusters = {}

    def load_json_ontology(self, json_file_path: str = None, json_data: dict = None, root_node: str = None) -> None:
        """
        Load the JSON ontology data from file or dictionary.

        Args:
            json_file_path (str): Path to the JSON file
            json_data (dict): JSON data as dictionary
        """
        if json_file_path:
            data = DataLoader.load_json_safe(json_file_path)
        elif json_data:
            data = json_data
        else:
            raise ValueError("Either json_file_path or json_data must be provided")


        self.ontology_data = data[root_node] if root_node else json_data

        self._process_data()

    def _process_data(self) -> None:
        """Process the ontology data and create NetworkX graph."""
        self.graph = nx.Graph()

        # Process nodes
        for node in self.ontology_data['nodes']:
            node_id = node['id']
            self.graph.add_node(node_id)
            self.node_data[node_id] = node

        # Process edges
        for edge in self.ontology_data['edges']:
            source = edge['source']
            target = edge['target']
            edge_id = edge['id']

            self.graph.add_edge(source, target)
            self.edge_data[edge_id] = edge

        # Process clusters
        try:
            for cluster in self.ontology_data['clusters']:
                self.clusters[cluster['id']] = cluster
        except:
            pass

    def _calculate_layout(self, layout_type: str = 'spring') -> Dict:
        """
        Calculate node positions using various layout algorithms.

        Args:
            layout_type (str): Type of layout ('spring', 'circular', 'random', 'kamada_kawai')

        Returns:
            Dict: Node positions
        """
        if layout_type == 'spring':
            pos = nx.spring_layout(self.graph, k=3, iterations=50, seed=42)
        elif layout_type == 'circular':
            pos = nx.circular_layout(self.graph)
        elif layout_type == 'random':
            pos = nx.random_layout(self.graph, seed=42)
        elif layout_type == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph, k=3, iterations=50, seed=42)

        return pos

    def _get_node_colors_by_attribute(self, attribute: str) -> Tuple[List[str], Dict[str, str]]:
        """
        Get node colors based on a specific attribute.

        Args:
            attribute (str): Attribute to color by ('relevance_degree', 'impact_scale', 'leadership_type', etc.)

        Returns:
            Tuple[List[str], Dict[str, str]]: Colors and color mapping
        """
        values = []
        for node_id in self.graph.nodes():
            node = self.node_data[node_id]
            if attribute in node.get('attributes', {}):
                values.append(node['attributes'][attribute])
            else:
                values.append('Unknown')

        unique_values = list(set(values))
        color_palette = px.colors.qualitative.Set3[:len(unique_values)]

        if len(unique_values) > len(color_palette):
            color_palette = px.colors.qualitative.Plotly[:len(unique_values)]

        color_map = dict(zip(unique_values, color_palette))
        node_colors = [color_map[val] for val in values]

        return node_colors, color_map

    def _create_node_hover_text(self, node_id: str) -> str:
        """Create hover text for nodes."""
        node = self.node_data[node_id]
        attributes = node.get('attributes', {})

        hover_text = f"<b>{node['name']}</b><br>"
        hover_text += f"Posição: {node.get('position', 'N/A')}<br>"
        hover_text += f"Tipo: {node.get('type', 'N/A')}<br>"

        if 'main_city' in attributes:
            hover_text += f"Cidade: {attributes['main_city']}<br>"
        if 'relevance_degree' in attributes:
            hover_text += f"Relevância: {attributes['relevance_degree']}/10<br>"
        if 'impact_scale' in attributes:
            hover_text += f"Escala de impacto: {attributes['impact_scale']}<br>"
        if 'leadership_type' in attributes:
            hover_text += f"Liderança: {attributes['leadership_type']}<br>"
        if 'main_contribution' in attributes:
            hover_text += f"Contribuição: {attributes['main_contribution'][:100]}...<br>"

        # Add profile links if available
        profile_links = []
        if 'profile_linkedin' in attributes and attributes['profile_linkedin'] != "not identified":
            profile_links.append(f"LinkedIn: {attributes['profile_linkedin']}")
        if 'profile_instagram' in attributes and attributes['profile_instagram'] != "not identified":
            profile_links.append(f"Instagram: {attributes['profile_instagram']}")


        return hover_text

    def _create_edge_hover_text(self, edge_data: dict) -> str:
        """Create hover text for edges."""
        hover_text = f"<b>{edge_data['type']}</b><br>"

        attributes = edge_data.get('attributes', {})
        if 'relationship_nature' in attributes:
            hover_text += f"Natureza: {attributes['relationship_nature']}<br>"
        if 'intensity' in attributes:
            hover_text += f"Intensidade: {attributes['intensity']}<br>"
        if 'context' in attributes:
            hover_text += f"Contexto: {attributes['context']}<br>"

        return hover_text

    def render_network(self,
                       layout_type: str = 'spring',
                       color_by: str = 'impact_scale',
                       node_size_by: str = 'relevance_degree',
                       show_edge_labels: bool = True,
                       filter_by_cluster: Optional[str] = None,
                       width: int = 1000,
                       height: int = 800) -> go.Figure:
        """
        Render the network as an interactive Plotly figure.

        Args:
            layout_type (str): Layout algorithm to use
            color_by (str): Attribute to color nodes by
            node_size_by (str): Attribute to size nodes by
            show_edge_labels (bool): Whether to show edge labels
            filter_by_cluster (str): Filter nodes by specific cluster
            width (int): Figure width
            height (int): Figure height

        Returns:
            go.Figure: Plotly figure object
        """
        if self.graph is None:
            st.markdown("No graph data loaded. Call load_json_ontology() first.")
            raise ValueError("No graph data loaded. Call load_json_ontology() first.")

        # Filter by cluster if specified
        if filter_by_cluster and filter_by_cluster in self.clusters:
            cluster_nodes = self.clusters[filter_by_cluster]['nodes']
            subgraph = self.graph.subgraph(cluster_nodes)
            pos = self._calculate_layout(layout_type)
            pos = {node: pos[node] for node in subgraph.nodes() if node in pos}
        else:
            subgraph = self.graph
            pos = self._calculate_layout(layout_type)

        # Get node colors and sizes for the current subgraph
        subgraph_nodes = list(subgraph.nodes())

        # Use consistent color mapping
        self.current_color_map = self._get_consistent_color_mapping(subgraph_nodes, color_by)

        # Get colors for subgraph nodes only
        node_colors = []
        for node_id in subgraph_nodes:
            node = self.node_data[node_id]
            if color_by in node.get('attributes', {}):
                color_value = str(node['attributes'][color_by])
            else:
                color_value = 'Unknown'

            if color_value in self.current_color_map:
                node_colors.append(self.current_color_map[color_value])
            else:
                node_colors.append('#999999')  # Default gray color

        # Get node sizes for subgraph nodes only
        node_sizes = []
        for node_id in subgraph_nodes:
            node = self.node_data[node_id]
            if node_size_by in node.get('attributes', {}):
                size_val = node['attributes'][node_size_by]
                if isinstance(size_val, (int, float)):
                    node_sizes.append(max(10, size_val * 5))  # Scale size
                else:
                    node_sizes.append(20)
            else:
                node_sizes.append(20)

        # Create figure
        fig = go.Figure()

        # Add edges as lines (without hover)
        edge_x = []
        edge_y = []
        for edge in subgraph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='rgba(136,136,136,0.5)'),
            hoverinfo='none',
            mode='lines',
            showlegend=False,
            name='Connections'
        ))

        # Add edge labels/hover at middle points
        edge_mid_x = []
        edge_mid_y = []
        edge_hover_text = []
        edge_labels = []

        for edge in subgraph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            # Calculate middle point
            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2
            edge_mid_x.append(mid_x)
            edge_mid_y.append(mid_y)

            # Find edge data
            edge_data = None
            for edge_id, data in self.edge_data.items():
                if (data['source'] == edge[0] and data['target'] == edge[1]) or \
                        (data['source'] == edge[1] and data['target'] == edge[0]):
                    edge_data = data
                    break

            # Create hover text and label for this edge
            if edge_data:
                hover_text = self._create_edge_hover_text(edge_data)
                source_name = self.node_data[edge[0]]['name']
                target_name = self.node_data[edge[1]]['name']
                full_hover = f"<b>{source_name} ↔ {target_name}</b><br>{hover_text}"
                edge_labels.append(edge_data['type'])
            else:
                source_name = self.node_data[edge[0]]['name']
                target_name = self.node_data[edge[1]]['name']
                full_hover = f"<b>{source_name} ↔ {target_name}</b><br>Conexão"
                edge_labels.append("")

            edge_hover_text.append(full_hover)

        # Add edge hover points (invisible markers at edge midpoints)
        if edge_mid_x:  # Only add if there are edges
            fig.add_trace(go.Scatter(
                x=edge_mid_x,
                y=edge_mid_y,
                mode='markers',
                marker=dict(size=8, color='rgba(0,0,0,0)'),  # Invisible markers
                hoverinfo='text',
                hovertext=edge_hover_text,
                showlegend=False,
                name='Edge Info'
            ))

        # Add nodes
        node_x = [pos[node][0] for node in subgraph.nodes()]
        node_y = [pos[node][1] for node in subgraph.nodes()]
        node_text = [self.node_data[node]['name'] for node in subgraph.nodes()]
        hover_text = [self._create_node_hover_text(node) for node in subgraph.nodes()]

        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=hover_text,
            text=node_text,
            textposition="middle center",
            marker=dict(
                showscale=True,
                colorscale='Viridis',
                color=node_colors,
                size=node_sizes,
                line=dict(width=2, color='DarkSlateGrey')
            ),
            customdata=[node for node in subgraph.nodes()],  # Store node IDs for click events
            name='Actors'
        ))

        # Update layout
        fig.update_layout(
            title=dict(
                text="",
                x=0.5,
                font=dict(size=20)
            ),
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="Visualização iterativa da rede dos atores-chave no ecossistema",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color='#888', size=12)
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            width=width,
            height=height,
            plot_bgcolor='white'
        )

        return fig

    def get_network_statistics(self) -> Dict:
        """Get basic network statistics."""
        if self.graph is None:
            return {}

        stats = {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'avg_clustering': nx.average_clustering(self.graph),
            'num_clusters': len(self.clusters)
        }

        # Centrality measures
        try:
            betweenness = nx.betweenness_centrality(self.graph)
            degree_centrality = nx.degree_centrality(self.graph)

            stats['most_central_actor'] = max(betweenness.items(), key=lambda x: x[1])
            stats['most_connected_actor'] = max(degree_centrality.items(), key=lambda x: x[1])
        except:
            pass

        return stats

    def _create_node_detail_panel(self, node_id: str) -> None:
        """Create a detailed information panel for a selected node."""
        if node_id not in self.node_data:
            st.error("Node not found!")
            return

        node = self.node_data[node_id]
        attributes = node.get('attributes', {})

        st.markdown(f"###")
        # Nome e posição
        st.markdown(f"### {node.get('name', 'N/A')}")
        st.markdown(f"**Cargo:** {node.get('position', 'N/A')}")

        photo, contacts = st.columns(2)

        with photo:
            # Foto de perfil se disponível
            photo_url = node['attributes']['profile_photo']
            if photo_url and photo_url != "não disponível em fontes abertas":
                try:
                    st.image(photo_url, width=150, caption=node['name'])
                except:
                    pass  # Falha silenciosa se imagem não carregar
        with contacts:
            linkedin = attributes.get('profile_linkedin')
            instagram = attributes.get('profile_instagram')

            if linkedin and linkedin != "não identificado":
                st.html(f"<a href={linkedin} target=_blank><img src=app/static/imgs/lkd.png width=20 height=20></a>")

            if instagram and instagram != "não identificado":
                st.html(f"<a href={instagram} target=_blank><img src=app/static/imgs/ig.png width=20 height=20></a>")

        # Informações principais
        attrs = attributes
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

        # Professional Information
        st.markdown("#### 💼 Informações profissionais")

        if 'company' in attributes:
            st.markdown(f"**Empresas:** {attributes['company']}")
        if 'institution' in attributes:
            st.markdown(f"**Instituição:** {attributes['institution']}")
        if 'education' in attributes:
            st.markdown(f"**Educação:** {attributes['education']}")
        if 'activity_area' in attributes:
            st.markdown(f"**Área de atividade:** {attributes['activity_area']}")
        if 'professional_history' in attributes:
            st.markdown(f"**Histórico Profissional:** {attributes['professional_history']}")

        # Leadership & Impact
        st.markdown("#### 🎯 Liderança e Impacto")
        col1, col2 = st.columns(2)

        with col1:
            if 'relevance_degree' in attributes:
                st.metric("Score de Relevância", f"{attributes['relevance_degree']}/10")
            if 'leadership_type' in attributes:
                st.markdown(f"**Tipo de liderança:** {attributes['leadership_type']}")

        with col2:
            if 'impact_scale' in attributes:
                st.markdown(f"**Escala de impacto:** {attributes['impact_scale']}")
            if 'other_positions' in attributes:
                st.markdown(f"**Outras Posições:** {attributes['other_positions']}")

        # Contributions & Quotes
        if 'main_contribution' in attributes:
            st.markdown("#### 🏆 Principais Contribuições")
            st.markdown(f"*{attributes['main_contribution']}*")

        if 'relevant_quote' in attributes:
            st.markdown("#### 💬 Dito por")
            st.info(f'"{attributes["relevant_quote"]}"')

        # Additional Information
        additional_info = {}
        for key, value in attributes.items():
            if key not in ['main_city', 'state', 'country', 'company', 'institution', 'education',
                           'activity_area', 'professional_history', 'relevance_degree', 'leadership_type',
                           'impact_scale', 'other_positions', 'main_contribution', 'relevant_quote',
                           'profile_linkedin', 'profile_instagram', 'profile_photo', 'geolocation']:
                additional_info[key] = value

        if additional_info:
            st.markdown("#### ℹ️ Informações Adicionais")
            for key, value in additional_info.items():
                if value and value != "not identified" and value != "not available in open sources":
                    formatted_key = key.replace('_', ' ').title()

                    # Se for um dicionário (grupos com listas de itens)
                    if isinstance(value, dict):
                        st.markdown(f"**{formatted_key}:**")
                        for group, items in value.items():
                            st.markdown(f"**{group}**")
                            for item in items:
                                st.markdown(f"  - {item}")
                    else:
                        st.markdown(f"**{formatted_key}:** {value}")

    def get_cluster_options(self) -> List[Tuple[str, str]]:
        """Get list of available clusters for filtering."""
        return [(cluster_id, cluster['name']) for cluster_id, cluster in self.clusters.items()]

    def create_network_map(self):
        """Create a complete Streamlit application for the network visualization."""
        # st.set_page_config(page_title="Rede do Ecossistema", layout="wide")

        # st.title("🕸️ Rede do Ecossistema")
        st.markdown("Visualização Iterativo dos atores-chave dentro da rede do ecossistema")

        with st.expander("📊 Estatísticas da rede"):
            stats = self.get_network_statistics()

            # Create columns for metrics
            stat_cols = st.columns(5)
            with stat_cols[0]:
                st.metric("Total de pessoas", stats.get('num_nodes', 0))
            with stat_cols[1]:
                st.metric("Total de conexões", stats.get('num_edges', 0))
            with stat_cols[2]:
                st.metric("Densidade da rede", f"{stats.get('density', 0):.3f}")
            with stat_cols[3]:
                st.metric("Coeficiente de clusterização", f"{stats.get('avg_clustering', 0):.3f}")
            with stat_cols[4]:
                st.metric("Quantidade de clusters", stats.get('num_clusters', 0))

            self.render_network_stats()
            self.render_network_analysis()
            # Análise de relevância
        self._render_relevance_analysis(self.ontology_data.get("nodes"))

        #st.divider()

        # Sidebar controls
        st.markdown("🎛️ Controles de visualização")

        col_controls = st.columns(4)

        with col_controls[0]:
            layout_type = st.selectbox(
                "Layout",
                ['kamada_kawai', 'spring', 'circular', 'random'],
                index=0
            )
        with col_controls[1]:
            color_by = st.selectbox(
                "Colorir por",
                ['main_city', 'impact_scale', 'leadership_type', 'relevance_degree'],
                index=0
            )
        with col_controls[2]:
            node_size_by = st.selectbox(
                "Tamanho por",
                ['relevance_degree', 'impact_scale'],
                index=0
            )
        with col_controls[3]:
            # Cluster filter
            cluster_options = [("all", "Todos atores")] + self.get_cluster_options()
            selected_cluster = st.selectbox(
                "Filtrar por cluster",
                options=[opt[0] for opt in cluster_options],
                format_func=lambda x: dict(cluster_options)[x],
                index=0
            )
            filter_cluster = None if selected_cluster == "all" else selected_cluster
            # Main layout with sidebar for node details
            if 'selected_node' not in st.session_state:
                st.session_state.selected_node = None

        col_map, col_detail = st.columns([3, 1])
        with col_map:
            # Display network
            st.markdown("Legenda cores")
            self.create_color_legend(color_by, filter_cluster)
            fig = self.render_network(
                layout_type=layout_type,
                color_by=color_by,
                node_size_by=node_size_by,
                filter_by_cluster=filter_cluster,
                width=1200,
                height=800
            )

            # Handle click events
            clicked_data = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")
            # Check if a node was clicked
            if clicked_data and 'selection' in clicked_data and 'points' in clicked_data['selection']:
                if clicked_data['selection']['points']:
                    point = clicked_data['selection']['points'][0]
                    if 'customdata' in point:
                        st.session_state.selected_node = point['customdata']


            # with stat_cols[5]:
            #     if 'most_central_actor' in stats:
            #         actor_id, centrality = stats['most_central_actor']
            #         actor_name = self.node_data[actor_id]['name']
            #         st.metric("Ator mais central",
            #                   actor_name[:15] + "..." if len(actor_name) > 15 else actor_name,
            #                   f"{centrality:.3f}")
            #     else:
            #         st.metric("Ator mais central", "N/A", "0.000")
        with col_detail:
            # self.render_filter_actor_details()
            self.create_detail_panel(filter_cluster)



    def create_detail_panel(self, filter_cluster):
        st.info("💡 **Dica:** Clique em qualquer nó da rede para visualizar as informações detalhadas do mesmo!")

        # Create layout for network and details
        if st.session_state.selected_node:
            self._create_node_detail_panel(st.session_state.selected_node)
        else:
            self._create_node_detail_panel("p001")

        st.divider()
        # Display cluster information
        if filter_cluster and filter_cluster in self.clusters:
            st.subheader(f"📋 Cluster: {self.clusters[filter_cluster]['name']}")
            st.write(self.clusters[filter_cluster]['description'])

            cluster_nodes = self.clusters[filter_cluster]['nodes']
            cluster_data = []

            for node_id in cluster_nodes:
                node = self.node_data[node_id]
                attributes = node.get('attributes', {})

                cluster_data.append({
                    'Nome': node['name'],
                    'Posição': node.get('position', 'N/A'),
                    'Cidade': attributes.get('main_city', 'N/A'),
                    'Relevancia': attributes.get('relevance_degree', 'N/A'),
                })

            cluster_df = pd.DataFrame(cluster_data)
            st.dataframe(cluster_df, use_container_width=True)

    def _get_consistent_color_mapping(self, nodes: List[str], color_by: str) -> Dict[str, str]:
        """
        Get consistent color mapping for a given set of nodes and attribute.

        Args:
            nodes: List of node IDs to consider
            color_by: Attribute to color by

        Returns:
            Dict mapping attribute values to colors
        """
        # Get unique values for the color attribute
        color_values = []
        for node_id in nodes:
            node = self.node_data[node_id]
            if color_by in node.get('attributes', {}):
                color_value = str(node['attributes'][color_by])
            else:
                color_value = 'Unknown'
            color_values.append(color_value)

        unique_color_values = sorted(list(set(color_values)))

        # Create consistent color mapping
        color_palette = px.colors.qualitative.Set3
        if len(unique_color_values) > len(color_palette):
            color_palette = color_palette + px.colors.qualitative.Plotly + px.colors.qualitative.Dark24
        while len(unique_color_values) > len(color_palette):
            color_palette = color_palette + color_palette

        color_map = {}
        for i, color_val in enumerate(unique_color_values):
            color_map[color_val] = color_palette[i % len(color_palette)]

        return color_map

    def create_color_legend(self, color_by, filter_cluster):
        # Use the color mapping created in render_network to ensure consistency
        if hasattr(self, 'current_color_map') and self.current_color_map:
            color_map = self.current_color_map
        else:
            # Fallback if color map doesn't exist yet
            if self.graph is not None:
                # Apply cluster filter if specified
                if filter_cluster and filter_cluster in self.clusters:
                    cluster_nodes = self.clusters[filter_cluster]['nodes']
                    legend_nodes = cluster_nodes
                else:
                    legend_nodes = list(self.graph.nodes())

                color_map = self._get_consistent_color_mapping(legend_nodes, color_by)
            else:
                return

        # Display color legend in columns
        legend_cols = st.columns(min(len(color_map), 4))
        for i, (value, color) in enumerate(color_map.items()):
            with legend_cols[i % 4]:
                st.markdown(
                    f'<div style="display: flex; align-items: center; margin-bottom: 5px;"><div style="width: 20px; height: 20px; background-color: {color}; border-radius: 50%; margin-right: 10px;"></div><span style="font-size: 14px;">{value}</span></div>',
                    unsafe_allow_html=True)


    @staticmethod
    def _analyze_by_leadership(actors_data: List[Dict]) -> Dict[str, int]:
        """Analisa distribuição por tipo de liderança"""
        leadership_count = {}

        for actor in actors_data:
            leadership = actor.get('attributes', {}).get('leadership_type', 'Não especificado')
            leadership_count[leadership] = leadership_count.get(leadership, 0) + 1

        return leadership_count

    @staticmethod
    def _analyze_by_city(actors_data: List[Dict]) -> Dict[str, int]:
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

    def render_network_analysis(self):
        """Renderiza análise da rede"""
        # st.subheader("📊 Análise da Rede")

        actors_data = self.ontology_data.get('nodes')

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

    def render_network_stats(self):
        actors_data = self.ontology_data.get('nodes')

        # Relevância média
        relevances = [
            actor.get('attributes', {}).get('relevance_degree', 0)
            for actor in actors_data
            if isinstance(actor.get('attributes', {}).get('relevance_degree'), (int, float))
        ]
        # Distribuição por escala de impacto
        impact_scales = [
            actor.get('attributes', {}).get('impact_scale', 'N/A')
            for actor in actors_data
        ]

        impact, top5 = st.columns(2)

        with impact:
            impact_distribution = {}
            for scale in impact_scales:
                impact_distribution[scale] = impact_distribution.get(scale, 0) + 1

            if impact_distribution:
                st.markdown("**Distribuição por Escala de Impacto:**")
                for scale, count in impact_distribution.items():
                    st.markdown(f"- {scale}: {count}")
        with top5:
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

    def render_filter_actor_details(self):
        actors_data = self.ontology_data.get('nodes')
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

        return selected_actor
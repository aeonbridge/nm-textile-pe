import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional


from src.utils.page_utils import Page, UIComponents, FilterManager, format_number, ChartGenerator
from src.state import StateManager

from src.nm.analytics import  Analytics

class RisksPage(Page):
    """Página de Identificação de Riscos"""

    def render(self, data: Dict[str, Any]):
        Analytics.log_event("page_view", {"page": "risks"})
        StateManager.increment_page_view("Análise de Riscos")

        st.markdown('<h2 class="page-header">⚠️ Análise de Riscos da Cadeia de Valor</h2>',
                    unsafe_allow_html=True)


        # Função para carregar dados de riscos
        @st.cache_data
        def load_risk_data():
            """Carrega dados de riscos baseados no mapeamento detalhado"""

            # Dados dos riscos baseados no documento de mapeamento
            risk_data = [
                # Riscos Críticos (Alta Severidade e Alta Probabilidade)
                {"categoria": "Social", "risco": "Trabalho infantil", "severidade": 5, "probabilidade": 5,
                 "prioridade": "Crítica",
                 "descricao": "Utilização de mão de obra infantil nas facções e unidades produtivas",
                 "stakeholders": "Crianças e adolescentes, famílias, comunidade",
                 "mitigacao": "Fiscalização educativa, alternativas de renda, sensibilização"},

                {"categoria": "Social", "risco": "Precarização do trabalho", "severidade": 5, "probabilidade": 5,
                 "prioridade": "Crítica",
                 "descricao": "Condições inadequadas de trabalho, jornadas excessivas, remuneração insuficiente",
                 "stakeholders": "Costureiras autônomas, trabalhadores informais",
                 "mitigacao": "Formalização gradual, melhoria de condições, fiscalização"},

                {"categoria": "Social", "risco": "Evasão escolar", "severidade": 4, "probabilidade": 5, "prioridade": "Crítica",
                 "descricao": "Abandono da educação formal em favor do trabalho precoce",
                 "stakeholders": "Jovens, comunidade, futuro do polo",
                 "mitigacao": "Educação dual, incentivos à permanência escolar"},

                {"categoria": "Econômico", "risco": "Concorrência com produtos importados", "severidade": 5, "probabilidade": 4,
                 "prioridade": "Crítica",
                 "descricao": "Entrada massiva de produtos têxteis importados de baixo custo",
                 "stakeholders": "Todos os produtores, especialmente pequenas facções",
                 "mitigacao": "Inovação, diferenciação, agregação de valor"},

                {"categoria": "Econômico", "risco": "Dependência de intermediários", "severidade": 4, "probabilidade": 5,
                 "prioridade": "Crítica",
                 "descricao": "Estrutura de mercado com múltiplos intermediários que capturam valor significativo",
                 "stakeholders": "Costureiras autônomas, facções, pequenos produtores",
                 "mitigacao": "Plataformas digitais, cooperação, vendas diretas"},

                {"categoria": "Ambiental", "risco": "Escassez hídrica", "severidade": 5, "probabilidade": 4,
                 "prioridade": "Crítica",
                 "descricao": "Redução da disponibilidade de água para processos produtivos",
                 "stakeholders": "Lavanderias, produtores de jeans, comunidade",
                 "mitigacao": "Tecnologias de economia de água, reuso, captação de chuva"},

                {"categoria": "Ambiental", "risco": "Poluição de recursos hídricos", "severidade": 5, "probabilidade": 4,
                 "prioridade": "Crítica",
                 "descricao": "Contaminação de rios e lençóis freáticos por efluentes não tratados",
                 "stakeholders": "Comunidade, meio ambiente, lavanderias",
                 "mitigacao": "Sistemas de tratamento, fiscalização, cooperação"},

                {"categoria": "Tecnológico", "risco": "Exclusão da transformação digital", "severidade": 4, "probabilidade": 5,
                 "prioridade": "Crítica",
                 "descricao": "Incapacidade de pequenos produtores de acompanhar a digitalização",
                 "stakeholders": "Pequenos produtores, facções, comerciantes tradicionais",
                 "mitigacao": "Inclusão digital, capacitação, tecnologias acessíveis"},

                # Riscos Significativos (Média Severidade e Alta Probabilidade)
                {"categoria": "Econômico", "risco": "Sazonalidade acentuada", "severidade": 3, "probabilidade": 4,
                 "prioridade": "Significativa",
                 "descricao": "Concentração de vendas em períodos específicos",
                 "stakeholders": "Produtores e comerciantes",
                 "mitigacao": "Diversificação de mercados, planejamento estratégico"},

                {"categoria": "Econômico", "risco": "Limitações logísticas", "severidade": 3, "probabilidade": 4,
                 "prioridade": "Significativa",
                 "descricao": "Infraestrutura de transporte deficiente, elevando custos",
                 "stakeholders": "Toda a cadeia, especialmente exportadores",
                 "mitigacao": "Investimento em infraestrutura, logística compartilhada"},

                {"categoria": "Econômico", "risco": "Acesso limitado a crédito", "severidade": 3, "probabilidade": 4,
                 "prioridade": "Significativa",
                 "descricao": "Dificuldade de acesso a financiamento adequado",
                 "stakeholders": "Pequenos e médios produtores, empreendedores jovens",
                 "mitigacao": "Microcrédito, garantias coletivas, formalização"},

                {"categoria": "Social", "risco": "Desigualdade de gênero", "severidade": 3, "probabilidade": 4,
                 "prioridade": "Significativa",
                 "descricao": "Disparidades de remuneração e oportunidades entre homens e mulheres",
                 "stakeholders": "Mulheres trabalhadoras, comunidade",
                 "mitigacao": "Programas de empoderamento feminino, capacitação"},

                {"categoria": "Social", "risco": "Problemas de saúde ocupacional", "severidade": 3, "probabilidade": 4,
                 "prioridade": "Significativa",
                 "descricao": "Doenças e lesões relacionadas ao trabalho",
                 "stakeholders": "Trabalhadores, especialmente costureiras",
                 "mitigacao": "Equipamentos de segurança, ergonomia, prevenção"},

                {"categoria": "Ambiental", "risco": "Gestão inadequada de resíduos sólidos", "severidade": 3,
                 "probabilidade": 4, "prioridade": "Significativa",
                 "descricao": "Descarte inadequado de retalhos, embalagens e outros resíduos",
                 "stakeholders": "Comunidade, meio ambiente, produtores",
                 "mitigacao": "Economia circular, reciclagem, reaproveitamento"},

                {"categoria": "Ambiental", "risco": "Uso de produtos químicos tóxicos", "severidade": 3, "probabilidade": 4,
                 "prioridade": "Significativa",
                 "descricao": "Utilização de corantes, alvejantes e outros produtos nocivos",
                 "stakeholders": "Trabalhadores, comunidade, meio ambiente",
                 "mitigacao": "Produtos alternativos, capacitação, regulamentação"},

                {"categoria": "Tecnológico", "risco": "Resistência cultural à digitalização", "severidade": 3,
                 "probabilidade": 4, "prioridade": "Significativa",
                 "descricao": "Rejeição de novas tecnologias e modelos de negócio digitais",
                 "stakeholders": "Produtores tradicionais, trabalhadores mais velhos",
                 "mitigacao": "Sensibilização, demonstrações práticas, capacitação gradual"},

                {"categoria": "Político", "risco": "Burocracia excessiva", "severidade": 3, "probabilidade": 4,
                 "prioridade": "Significativa",
                 "descricao": "Processos complexos e demorados para licenciamentos",
                 "stakeholders": "Empreendedores, especialmente pequenos",
                 "mitigacao": "Simplificação de processos, balcão único, digitalização"},

                # Alguns riscos moderados para completar o conjunto
                {"categoria": "Econômico", "risco": "Volatilidade de preços de insumos", "severidade": 3, "probabilidade": 3,
                 "prioridade": "Moderada",
                 "descricao": "Flutuações significativas nos preços de tecidos e aviamentos",
                 "stakeholders": "Toda a cadeia produtiva, especialmente pequenos produtores",
                 "mitigacao": "Compras coletivas, contratos de longo prazo, diversificação"},

                {"categoria": "Tecnológico", "risco": "Ciberataques e segurança digital", "severidade": 4, "probabilidade": 2,
                 "prioridade": "Moderada",
                 "descricao": "Vulnerabilidade a ataques cibernéticos em sistemas digitais",
                 "stakeholders": "Empresas digitalizadas, plataforma B2B",
                 "mitigacao": "Segurança digital, backups, treinamento em segurança"},

                {"categoria": "Político", "risco": "Descontinuidade de políticas públicas", "severidade": 4, "probabilidade": 3,
                 "prioridade": "Moderada",
                 "descricao": "Interrupção ou alteração significativa de programas governamentais",
                 "stakeholders": "Beneficiários de programas, instituições implementadoras",
                 "mitigacao": "Diversificação de fontes de apoio, sustentabilidade própria"}
            ]

            return pd.DataFrame(risk_data)


        # Função para calcular valor de risco
        def calculate_risk_value(severidade, probabilidade):
            return severidade * probabilidade


        # Carregar dados
        df_risks = load_risk_data()

        # Calcular valor de risco
        df_risks['valor_risco'] = df_risks.apply(lambda row: calculate_risk_value(row['severidade'], row['probabilidade']),
                                                 axis=1)

        # Sidebar para filtros
        st.header("Filtros de Análise")

        # Filtro por categoria
        categorias = sorted(df_risks['categoria'].unique())
        selected_categories = st.multiselect(
            "Categorias de Risco:",
            options=categorias,
            default=categorias,
            key="risk_categories"
        )

        # Registrar evento de filtro
        if selected_categories != categorias:
            Analytics.log_event("risks-filter_applied",
                                {"selected_values": selected_categories})

        # Filtro por prioridade
        prioridades = ["Crítica", "Significativa", "Moderada"]
        selected_priorities = st.multiselect(
            "Níveis de Prioridade:",
            options=prioridades,
            default=prioridades,
            key="risk_priorities"
        )

        # Registrar evento de filtro
        if selected_priorities != prioridades:
            Analytics.log_event("risks-filter_priorities",
                                {"selected_values": selected_priorities})


        # Filtro por valor mínimo de risco
        min_risk_value = st.slider(
            "Valor Mínimo de Risco:",
            min_value=1,
            max_value=25,
            value=5,
            key="min_risk_value"
        )

        # Registrar evento de filtro
        if "min_risk_value_last" not in st.session_state:
            st.session_state.min_risk_value_last = 5
        if st.session_state.min_risk_value_last != min_risk_value:
            if selected_priorities != prioridades:
                Analytics.log_event("risks-filter_priorities",
                                    {"min_risk_value": min_risk_value})

            st.session_state.min_risk_value_last = min_risk_value

        # Filtrar dados
        df_filtered = df_risks[
            (df_risks['categoria'].isin(selected_categories)) &
            (df_risks['prioridade'].isin(selected_priorities)) &
            (df_risks['valor_risco'] >= min_risk_value)
            ].copy()

        # Layout em colunas
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Matriz de Riscos")

            # Criar matriz de riscos (probabilidade x severidade)
            fig = go.Figure()

            # Definir cores por prioridade
            color_map = {
                'Crítica': '#FF4B4B',
                'Significativa': '#FFA500',
                'Moderada': '#FFD700'
            }

            for prioridade in df_filtered['prioridade'].unique():
                df_priority = df_filtered[df_filtered['prioridade'] == prioridade]

                fig.add_trace(go.Scatter(
                    x=df_priority['probabilidade'],
                    y=df_priority['severidade'],
                    mode='markers',
                    marker=dict(
                        size=[val * 3 for val in df_priority['valor_risco']],
                        color=color_map.get(prioridade, '#1f77b4'),
                        line=dict(width=2, color='white'),
                        opacity=0.8
                    ),
                    text=df_priority['risco'],
                    name=f'Prioridade {prioridade}',
                    hovertemplate="<b>%{text}</b><br>Severidade: %{y}<br>Probabilidade: %{x}<br>Valor de Risco: %{marker.size}<extra></extra>"
                ))

            # Adicionar linhas de grade para os quadrantes
            fig.add_shape(type="line", x0=0.5, y0=3, x1=5.5, y1=3, line=dict(color="gray", width=1, dash="dash"))
            fig.add_shape(type="line", x0=3, y0=0.5, x1=3, y1=5.5, line=dict(color="gray", width=1, dash="dash"))

            # Adicionar anotações para os quadrantes
            fig.add_annotation(x=1.5, y=4.5, text="Alta Severidade<br>Baixa Probabilidade", showarrow=False, font=dict(size=10))
            fig.add_annotation(x=4.5, y=4.5, text="Alta Severidade<br>Alta Probabilidade", showarrow=False, font=dict(size=10))
            fig.add_annotation(x=1.5, y=1.5, text="Baixa Severidade<br>Baixa Probabilidade", showarrow=False,
                               font=dict(size=10))
            fig.add_annotation(x=4.5, y=1.5, text="Baixa Severidade<br>Alta Probabilidade", showarrow=False, font=dict(size=10))

            fig.update_layout(
                title="Matriz de Riscos - Probabilidade vs Severidade",
                xaxis=dict(
                    title="Probabilidade",
                    range=[0.5, 5.5],
                    tickvals=[1, 2, 3, 4, 5],
                    ticktext=["Muito Baixa", "Baixa", "Média", "Alta", "Muito Alta"]
                ),
                yaxis=dict(
                    title="Severidade",
                    range=[0.5, 5.5],
                    tickvals=[1, 2, 3, 4, 5],
                    ticktext=["Muito Baixa", "Baixa", "Média", "Alta", "Muito Alta"]
                ),
                height=600,
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True)

            if selected_priorities != prioridades:
                Analytics.log_event("risks-view_visualization",
                                    {"chart_type": "risk_matrix"})

            # Gráfico de barras por categoria
            category_risk = df_filtered.groupby('categoria')['valor_risco'].agg(['mean', 'count']).reset_index()
            category_risk.columns = ['categoria', 'risco_medio', 'quantidade']

            if not category_risk.empty:
                fig_category = px.bar(
                    category_risk,
                    x='categoria',
                    y='risco_medio',
                    color='risco_medio',
                    text='quantidade',
                    labels={'risco_medio': 'Risco Médio', 'categoria': 'Categoria', 'quantidade': 'Quantidade'},
                    title='Risco Médio por Categoria',
                    color_continuous_scale='Reds'
                )

                fig_category.update_traces(texttemplate='%{text} riscos', textposition='outside')

                st.plotly_chart(fig_category, use_container_width=True)
                Analytics.log_event("risks-view_visualization",
                                    {"chart_type": "risk_by_category"})

        with col2:
            st.subheader("Riscos Prioritários")

            # Ordenar por valor de risco
            df_priority = df_filtered.sort_values(by='valor_risco', ascending=False).head(10)

            for i, risk in df_priority.iterrows():
                with st.expander(f"{risk['risco']} (Risco: {risk['valor_risco']})"):
                    st.markdown(f"**Categoria:** {risk['categoria']}")
                    st.markdown(f"**Prioridade:** {risk['prioridade']}")
                    st.markdown(f"**Severidade:** {risk['severidade']}/5")
                    st.markdown(f"**Probabilidade:** {risk['probabilidade']}/5")
                    st.markdown(f"**Descrição:** {risk['descricao']}")
                    st.markdown(f"**Stakeholders Afetados:** {risk['stakeholders']}")
                    st.markdown(f"**Estratégias de Mitigação:** {risk['mitigacao']}")

            Analytics.log_event("priority_risks",
                                {"count": len(df_priority)})

        # Análise de Clusters de Risco
        st.header("Clusters de Riscos Interconectados")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Cluster Socioambiental")
            st.markdown("""
            **Interconexão:** Escassez hídrica → Poluição de recursos hídricos → Pressão regulatória ambiental → 
            Custos de adequação → Inviabilização de negócios → Desemprego → Pobreza → Trabalho infantil
        
            **Riscos Envolvidos:**
            - Escassez hídrica
            - Poluição de recursos hídricos
            - Trabalho infantil
            - Precarização do trabalho
            """)

        with col2:
            st.subheader("Cluster Digital-Competitivo")
            st.markdown("""
            **Interconexão:** Exclusão digital → Limitado acesso a mercados → Dependência de intermediários → 
            Margens reduzidas → Limitada capacidade de investimento → Obsolescência tecnológica
        
            **Riscos Envolvidos:**
            - Exclusão da transformação digital
            - Dependência de intermediários
            - Concorrência com produtos importados
            - Resistência cultural à digitalização
            """)

        # Mapa de Calor de Riscos por Segmento
        st.subheader("Mapa de Calor de Riscos por Cidade")

        # Simular impacto dos riscos por cidade
        city_risk_data = {
            'Santa Cruz do Capibaribe': {
                'Trabalho infantil': 4.5, 'Precarização do trabalho': 4.2, 'Evasão escolar': 4.0,
                'Escassez hídrica': 3.5, 'Exclusão digital': 4.0, 'Dependência de intermediários': 4.5
            },
            'Caruaru': {
                'Trabalho infantil': 3.0, 'Precarização do trabalho': 3.5, 'Evasão escolar': 3.2,
                'Escassez hídrica': 2.5, 'Exclusão digital': 3.0, 'Dependência de intermediários': 3.2
            },
            'Toritama': {
                'Trabalho infantil': 5.0, 'Precarização do trabalho': 4.8, 'Evasão escolar': 4.5,
                'Escassez hídrica': 5.0, 'Exclusão digital': 4.5, 'Dependência de intermediários': 4.2
            }
        }

        # Converter para DataFrame para o heatmap
        heatmap_data = pd.DataFrame(city_risk_data).T
        heatmap_data = heatmap_data.fillna(0)

        # Criar heatmap
        fig_heatmap = px.imshow(
            heatmap_data.values,
            labels=dict(x="Tipos de Risco", y="Cidades", color="Intensidade do Risco"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            color_continuous_scale="Reds",
            title="Intensidade dos Riscos por Cidade"
        )

        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Tabela detalhada de riscos
        st.subheader("Tabela Detalhada de Riscos")

        # Opções de ordenação
        sort_by = st.selectbox(
            "Ordenar por:",
            options=["valor_risco", "categoria", "prioridade", "severidade", "probabilidade"],
            format_func=lambda x: {
                "valor_risco": "Valor de Risco",
                "categoria": "Categoria",
                "prioridade": "Prioridade",
                "severidade": "Severidade",
                "probabilidade": "Probabilidade"
            }[x],
            key="risk_sort_by"
        )

        sort_ascending = st.checkbox("Ordem Crescente", value=False, key="risk_sort_order")

        # Ordenar e exibir
        df_display = df_filtered.sort_values(by=sort_by, ascending=sort_ascending)

        # Selecionar colunas para exibição
        df_display_table = df_display[["risco", "categoria", "prioridade", "severidade", "probabilidade", "valor_risco"]].copy()

        # Renomear colunas para exibição
        df_display_table.columns = ["Risco", "Categoria", "Prioridade", "Severidade", "Probabilidade", "Valor de Risco"]

        st.dataframe(df_display_table, hide_index=True)

        # Exportar dados
        col1, col2 = st.columns(2)

        with col1:
            # Exportar riscos filtrados
            csv_data = df_filtered.to_csv(index=False).encode('utf-8')
            if st.download_button(
                    label="📥 Exportar Riscos (CSV)",
                    data=csv_data,
                    file_name='analise_riscos_filtrados.csv',
                    mime='text/csv',
                    key="export_risks_csv"
            ):
                Analytics.log_event("export_data",
                                    {"risks": str(len(df_filtered))+"rows"})


        with col2:
            # Exportar relatório de riscos
            report_data = f"""# Relatório de Análise de Riscos - Ecossistema Têxtil de Pernambuco
        
        ## Filtros Aplicados
        - Categorias: {', '.join(selected_categories)}
        - Prioridades: {', '.join(selected_priorities)}
        - Valor Mínimo de Risco: {min_risk_value}
        
        ## Resumo Executivo
        - Total de riscos analisados: {len(df_filtered)}
        - Riscos críticos: {len(df_filtered[df_filtered['prioridade'] == 'Crítica'])}
        - Riscos significativos: {len(df_filtered[df_filtered['prioridade'] == 'Significativa'])}
        - Valor médio de risco: {df_filtered['valor_risco'].mean():.2f}
        
        ## Riscos por Categoria
        {df_filtered.groupby('categoria')['valor_risco'].agg(['count', 'mean']).round(2).to_string()}
        
        ## Recomendações Prioritárias
        Com base na análise, recomenda-se focar inicialmente nos riscos críticos, especialmente:
        1. {df_filtered.nlargest(1, 'valor_risco')['risco'].iloc[0] if len(df_filtered) > 0 else 'N/A'}
        2. Implementar estratégias de mitigação integradas
        3. Monitoramento contínuo dos indicadores de risco
        """

            if st.download_button(
                    label="📥 Exportar Relatório (MD)",
                    data=report_data.encode('utf-8'),
                    file_name='relatorio_analise_riscos.md',
                    mime='text/markdown',
                    key="export_risk_report"
            ):
                Analytics.log_event("export_data",
                                    {"risk_report": "markdown"})

        # Informações adicionais
        st.markdown("""
        ### Sobre a Análise de Riscos
        
        Esta ferramenta permite explorar os principais riscos identificados na cadeia de valor do ecossistema têxtil de Pernambuco, 
        priorizá-los com base em severidade e probabilidade, e desenvolver estratégias de mitigação.
        
        **Metodologia:**
        - **Severidade**: Impacto potencial do risco (1-5)
        - **Probabilidade**: Chance de ocorrência do risco (1-5)
        - **Valor de Risco**: Severidade × Probabilidade
        - **Prioridade**: Classificação baseada no valor de risco
        
        **Dicas de uso:**
        - Utilize os filtros para focar em categorias específicas de risco
        - Analise a matriz de riscos para identificar prioridades de ação
        - Explore os clusters de riscos para entender interconexões
        - Exporte os dados para análises offline e elaboração de planos de mitigação
        
        **Fonte:** Baseado no "Mapeamento de Riscos da Cadeia de Valor do Ecossistema Têxtil em Pernambuco"
        """)
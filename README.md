# Dashboard Interativo Inteligente - Ecossistema Têxtil de Pernambuco

## Estrutura do Projeto

```
dashboard_textil_pe/
├── main.py                          # Aplicação principal
├── src/                            # Código fonte
│   ├── __init__.py
│   ├── utils.py                    # Funções utilitárias
│   └── state.py                    # Gerenciamento de estado
├── pages/                          # Páginas do dashboard
│   ├── __init__.py
│   ├── overview.py                 # Página de visão geral
│   ├── indicators.py               # Análise de indicadores
│   ├── network.py                  # Rede de atores
│   ├── risks.py                    # Análise de riscos
│   └── opportunities.py            # Identificação de oportunidades
├── static/                         # Arquivos estáticos
│   ├── datasets/                   # Datasets
│   │   ├── indicadores_economicos.csv
│   │   ├── indicadores_sociais.csv
│   │   ├── indicadores_ambientais.csv
│   │   ├── indicadores_inovacao.csv
│   │   ├── ontologia_ecossistema_textil_ptbr.json
│   │   └── textile_ecosystem_network_ontology.json
│   └── analytics/                  # Dados de analytics
├── .streamlit/
│   ├── config.toml                 # Configurações do Streamlit
│   └── secrets.toml                # Secrets (não versionado)
└── requirements.txt                # Dependências Python
```

## Instalação e Execução

### 1. Requisitos
```bash
pip install streamlit pandas plotly networkx numpy
```

### 2. Executar o Dashboard
```bash
streamlit run main.py
```

### 3. Acessar
O dashboard estará disponível em `http://localhost:8501`

## Funcionalidades Implementadas

### 🏠 Visão Geral
- **Métricas-chave do ecossistema** com população, empresas, faturamento e empregos
- **Mapa geográfico interativo** mostrando distribuição das cidades
- **Análise comparativa** entre indicadores econômicos, sociais, ambientais e de inovação
- **Filtros globais** por cidade e opções de visualização
- **Insights automáticos** baseados nos dados

### 📊 Análise de Indicadores
- **Análise comparativa entre cidades** com gráficos especializados
- **Evolução temporal simulada** para projeções e tendências
- **Análise multidimensional** com scatter plots interativos
- **Benchmarking** com índice composto de desenvolvimento
- **Correlações** entre diferentes indicadores
- **Análise de quadrantes** para posicionamento estratégico

### 🔄 Rede de Atores
- **Visualização de rede** usando NetworkX e Plotly
- **Perfis detalhados** dos stakeholders com fotos e informações de contato
- **Filtros avançados** por tipo de liderança, cidade e relevância
- **Análise de centralidade** e métricas de rede
- **Busca de atores** específicos
- **Estatísticas da rede** e distribuições

### 💡 Identificação de Oportunidades
- **Matriz de priorização** (impacto vs viabilidade)
- **Oportunidades por categoria** e análise temporal
- **Recomendações de stakeholders** para cada oportunidade
- **Próximos passos** estruturados
- **Filtros** por categoria, cidade e horizonte temporal
- **Detalhamento** de investimentos e justificativas

### ⚠️ Análise de Riscos
- **Estrutura para categorização** de riscos
- **Placeholder para matriz** de probabilidade vs impacto
- **Framework para planos** de contingência
- **Base para integração** com dados reais de riscos

## Analytics e Monitoramento

### Sistema de Analytics Integrado
- **Rastreamento de eventos** de navegação e interação
- **Métricas de uso** por página e funcionalidade
- **Sessões de usuário** com IDs únicos
- **Exportação de dados** analíticos em formato JSONL

### Métricas Coletadas
- Carregamento de páginas
- Navegação entre seções
- Filtros aplicados
- Dados exportados
- Tempo de sessão
- Interações com visualizações

## Tratamento de Dados

### Resiliência a Dados Ausentes
- **Fallback para dados simulados** quando arquivos não estão disponíveis
- **Validação de estruturas** de dados antes do processamento
- **Tratamento de erros** sem quebrar a experiência do usuário
- **Avisos informativos** sobre status dos dados

### Otimização de Performance
- **Cache de dados** com `@st.cache_data`
- **Carregamento lazy** de dados pesados
- **Compressão** de visualizações
- **Estado persistente** entre sessões

## Personalização e Extensibilidade

### Configurações Flexíveis
- **Temas e cores** customizáveis via CSS
- **Filtros dinâmicos** baseados nos dados disponíveis
- **Layouts responsivos** para diferentes tamanhos de tela
- **Exportação** em múltiplos formatos (CSV, JSON, PNG)

### Arquitetura Extensível
- **Classes base** para páginas (`Page`)
- **Utilitários reutilizáveis** (`ChartGenerator`, `FilterManager`)
- **Gerenciamento centralizado** de estado
- **Sistema de plugins** para novas funcionalidades

## Próximos Desenvolvimentos

### Funcionalidades Planejadas
1. **Simulação de cenários** com sliders interativos
2. **Integração com APIs** para dados em tempo real
3. **Sistema de alertas** para indicadores críticos
4. **Relatórios automatizados** em PDF
5. **Dashboard móvel** otimizado
6. **Colaboração** multi-usuário
7. **Integração** com LLMs para insights inteligentes

### Melhorias Técnicas
1. **Base de dados** para persistência
2. **Autenticação** e controle de acesso
3. **API REST** para integração externa
4. **Testes automatizados** para qualidade
5. **Deploy** em cloud com escalabilidade
6. **Monitoramento** de performance em produção

## Suporte e Documentação

### Como Usar
1. **Navegue** pelas páginas usando o menu lateral
2. **Aplique filtros** para focar em dados específicos
3. **Interaja** com visualizações clicando e fazendo hover
4. **Exporte dados** usando os botões de download
5. **Explore** as diferentes análises e insights

### Solução de Problemas
- **Dados não carregam**: Verifique se os arquivos CSV/JSON estão no diretório `static/datasets/`
- **Performance lenta**: Reduza o número de cidades/categorias nos filtros
- **Gráficos não aparecem**: Atualize a página e verifique a conexão com internet
- **Erros de importação**: Instale todas as dependências listadas em `requirements.txt`

### Contribuição
Para contribuir com o projeto:
1. **Fork** o repositório
2. **Crie** uma branch para sua feature
3. **Implemente** suas modificações
4. **Teste** thoroughly
5. **Submeta** um pull request

Este dashboard representa uma ferramenta poderosa para apoiar stakeholders do ecossistema têxtil de Pernambuco na compreensão do ambiente, análise de tendências e tomada de decisões estratégicas baseadas em dados.
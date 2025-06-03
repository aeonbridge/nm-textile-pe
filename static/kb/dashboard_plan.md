# Plano de Dashboard Interativo para o Ecossistema Têxtil de Pernambuco

## Estrutura Geral
O dashboard será organizado em abas separadas, cada uma focada em um aspecto específico do ecossistema têxtil de Pernambuco, com funcionalidades interativas para apoiar a tomada de decisão dos stakeholders.

## Abas e Funcionalidades

### 1. Visão Geral do Ecossistema
- **Mapa geográfico interativo** do polo têxtil de Pernambuco
  - Visualização das três cidades principais (Santa Cruz do Capibaribe, Caruaru, Toritama) e outros municípios
  - Indicadores-chave sobrepostos ao mapa (tamanho dos círculos proporcional ao faturamento/número de empresas)
  - Filtros para selecionar indicadores a serem visualizados
- **Painel de indicadores macro** com métricas consolidadas
  - Totais de empresas, empregos, faturamento
  - Comparativo entre formal e informal
  - Exportações
- **Funcionalidades interativas**:
  - Zoom no mapa
  - Seleção de cidades para detalhamento
  - Exportação de visualizações (PNG, PDF)

### 2. Análise de Indicadores
- **Visualizações comparativas** entre as cidades
  - Gráficos de barras para indicadores econômicos
  - Gráficos de radar para indicadores sociais
  - Gráficos de linha para indicadores ambientais
  - Gráficos de dispersão para indicadores de inovação
- **Funcionalidades interativas**:
  - Filtros por cidade/região
  - Seleção de indicadores específicos
  - Comparação temporal (simulada com projeções)
  - Exportação de dados (CSV)

### 3. Rede de Atores e Relacionamentos
- **Gráfico de rede interativo** baseado na ontologia
  - Visualização de pessoas-chave e suas conexões
  - Tamanho dos nós proporcional ao grau de relevância
  - Cores diferentes para tipos de liderança
- **Painel de detalhes** para cada ator selecionado
  - Informações de perfil
  - Foto (quando disponível)
  - Contribuições principais
  - Conexões diretas
- **Funcionalidades interativas**:
  - Filtros por tipo de liderança, cidade, escala de impacto
  - Busca por atores específicos
  - Ajuste de visualização da rede (expansão/contração)
  - Exportação da rede (PNG, PDF)

### 4. Análise de Riscos da Cadeia de Valor
- **Mapa de calor de riscos** por segmento da cadeia
  - Visualização dos riscos por categoria (ambiental, social, econômico, regulatório)
  - Intensidade do risco representada por cores
- **Tabela detalhada de riscos** com descrições e impactos
- **Funcionalidades interativas**:
  - Filtros por categoria de risco
  - Filtros por segmento da cadeia
  - Ordenação por probabilidade/impacto
  - Exportação de relatório de riscos (PDF)

### 5. Identificação de Oportunidades
- **Painel de oportunidades** por cidade e segmento
  - Visualização de oportunidades identificadas
  - Potencial de impacto estimado
  - Stakeholders recomendados para discussão
- **Matriz de priorização** de oportunidades
  - Eixos de impacto vs. viabilidade
- **Funcionalidades interativas**:
  - Filtros por cidade e segmento
  - Seleção de stakeholders recomendados
  - Simulação de cenários (básico)
  - Exportação de relatório de oportunidades (PDF)

### 6. Simulação de Cenários
- **Ferramenta de simulação** para indicadores-chave
  - Ajuste de parâmetros (investimentos, políticas, etc.)
  - Visualização de impactos projetados
- **Comparativo de cenários** (otimista, realista, pessimista)
- **Funcionalidades interativas**:
  - Controles deslizantes para ajuste de parâmetros
  - Seleção de horizonte temporal
  - Comparação entre cenários
  - Exportação de projeções (CSV, PDF)

### 7. Iteração com Agentes LLM
- **Interface de conversação** com agentes de IA
  - Seleção de diferentes perspectivas ontológicas
  - Escolha de provedores de LLM
  - Histórico de conversas
- **Painel de configuração** de agentes
  - Seleção de modelos específicos
  - Ajuste de parâmetros (temperatura, etc.)
- **Funcionalidades interativas**:
  - Entrada de texto para perguntas/instruções
  - Seleção de contexto específico do ecossistema
  - Exportação de conversas (TXT, PDF)

## Recursos Técnicos Necessários

### Bibliotecas Python
- **Streamlit**: Framework principal para o dashboard
- **Pandas**: Manipulação de dados
- **Plotly**: Visualizações interativas (gráficos, mapas)
- **NetworkX**: Análise e visualização de redes
- **Folium**: Mapas geográficos interativos
- **PyLLM/LangChain**: Integração com modelos de linguagem
- **Matplotlib/Seaborn**: Visualizações estáticas complementares

### Estrutura de Arquivos
- **app.py**: Arquivo principal do Streamlit
- **pages/**: Diretório com arquivos para cada aba
- **utils/**: Funções auxiliares para processamento de dados
- **data/**: Diretório para armazenar os datasets processados
- **models/**: Configurações para integração com LLMs

### Fluxo de Dados
1. Carregamento inicial dos datasets CSV e JSON
2. Processamento e transformação para estruturas adequadas
3. Armazenamento em cache para otimização de performance
4. Renderização das visualizações conforme interação do usuário
5. Exportação de dados/visualizações quando solicitado

## Implementação e Cronograma
1. **Configuração do ambiente Streamlit**
2. **Implementação da estrutura básica e navegação**
3. **Desenvolvimento das visualizações por aba**
4. **Implementação das funcionalidades interativas**
5. **Integração com LLMs para a aba de agentes**
6. **Testes e otimizações**
7. **Documentação e entrega**

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based interactive dashboard for analyzing the textile ecosystem in Pernambuco, Brazil. It provides data visualization and analytics capabilities for stakeholders to understand industry trends, risks, opportunities, and make strategic decisions.

## Development Commands

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard locally
streamlit run main.py

# Access admin analytics (append to URL)
?admin=on
```

### Development Environment
- Local server runs at `http://localhost:8501`
- Streamlit config in `.streamlit/config.toml`
- Secrets (Supabase keys) in `.streamlit/secrets.toml`

## Architecture Overview

### Core Components

**Application Entry Point**: `main.py` contains the `DashboardApp` class that manages routing, state, and data loading with graceful error handling.

**Page System**: Each major feature is implemented as a separate page class in `src/pages/`:
- Network analysis with NetworkX stakeholder relationships
- Risk assessment and opportunity mapping
- Multi-dimensional indicator analysis (economic, social, environmental, innovation)
- Geographic visualization with Mapbox integration
- Interactive analysis laboratory

**State Management**: `src/state.py` provides centralized state management using dataclasses, handling user preferences, filters, and analytics tracking across pages.

**Core Modules** (`src/nm/`):
- `analytics.py`: User behavior tracking with Supabase integration
- `data_loader.py`: Robust CSV/JSON loading with fallback to dummy data
- `people_network.py`: NetworkX-based stakeholder network visualization
- `feedback.py`: User feedback collection system

**Utilities** (`src/utils.py`): Abstract `Page` base class, `ChartGenerator` for Plotly visualizations, `FilterManager` for interactive filtering, and reusable UI components.

### Data Architecture

**Static Data Sources** (`static/datasets/`):
- Indicator CSV files: economic, social, environmental, innovation metrics
- JSON ontologies: ecosystem and stakeholder relationship definitions
- City-specific analyses and comprehensive knowledge base in `static/kb/`

**Analytics**: Local JSONL files (`static/analytics/`) and Supabase database for usage tracking.

## Development Patterns

### Error Handling & Resilience
- All data loading includes fallback to dummy data when files are missing
- Analytics failures are handled silently to not impact user experience
- Safe operations always check for None/empty data before processing

### Performance Optimization
- Extensive use of `@st.cache_data` decorators for expensive operations
- Lazy loading pattern - data loaded only when needed
- Conditional rendering based on data availability

### Code Conventions
- Page classes inherit from abstract `Page` base class in `utils.py`
- Consistent error handling with try/catch blocks and logging
- Type hints used throughout for better code clarity
- Data validation before processing to prevent runtime errors

## Key Technical Considerations

### Dependencies
- Streamlit ~1.45.1 for web framework
- Pandas/NumPy for data manipulation
- Plotly for interactive visualizations
- NetworkX for graph analysis
- Supabase for analytics backend

### Custom Theming
- Custom fonts in `static/theme/fonts/` (Styrene, Fira Code, Tiempos)
- Brand-specific color scheme with earth tones
- Professional typography hierarchy
- Static file serving enabled for custom assets

### Data Flow
- CSV/JSON file-based with robust error handling
- Centralized loading through `DataLoader` class
- State persistence across page navigation
- Real-time analytics collection without blocking UX
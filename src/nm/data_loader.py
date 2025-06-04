import streamlit as st
import pandas as pd
import json
from typing import Dict, Any, Optional, List

class DataLoader:
    """Classe para carregar e gerenciar dados"""

    @staticmethod
    @st.cache_data
    def load_csv_safe(filepath: str, encoding: str = 'utf-8') -> Optional[pd.DataFrame]:
        """Carrega arquivo CSV com tratamento de erro"""
        try:
            return pd.read_csv(filepath, encoding=encoding)
        except FileNotFoundError:
            st.warning(f"Arquivo {filepath} não encontrado")
            return None
        except Exception as e:
            st.error(f"Erro ao carregar {filepath}: {str(e)}")
            return None

    @staticmethod
    @st.cache_data
    def load_json_safe(filepath: str, encoding: str = 'utf-8') -> Optional[Dict]:
        """Carrega arquivo JSON com tratamento de erro"""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return json.load(f)
        except FileNotFoundError:
            st.warning(f"Arquivo {filepath} não encontrado")
            return None
        except Exception as e:
            st.error(f"Erro ao carregar {filepath}: {str(e)}")
            return None
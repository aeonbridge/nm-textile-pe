import streamlit as st
import uuid
import os
from typing import Dict, Any, Optional, List
import json
import datetime

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

class Analytics:
    """Classe para gerenciar analytics"""

    @staticmethod
    def get_session_id() -> str:
        """Obtém ou gera ID de sessão"""
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        return st.session_state.session_id

    @staticmethod
    def log_event(event_type: str, event_data: Optional[Dict] = None, page: str = "unknown"):
        """Registra evento de analytics"""
        try:
            session_id = Analytics.get_session_id()
            timestamp = datetime.datetime.now().isoformat()

            event = {
                "session_id": session_id,
                "timestamp": timestamp,
                "event_type": event_type,
                "page": page,
                "data": event_data or {}
            }

            # Criar diretório se não existir
            analytics_dir = "static/analytics"
            os.makedirs(analytics_dir, exist_ok=True)

            # Salvar evento
            analytics_file = os.path.join(
                analytics_dir,
                f"analytics_{datetime.datetime.now().strftime('%Y%m%d')}.jsonl"
            )
            with open(analytics_file, "a", encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

            Analytics.save_analytics_db(event, page=page)

        except Exception as e:
            # Falha silenciosa em analytics para não impactar UX
            pass

    @staticmethod
    def save_analytics_db(event_data: Optional[Dict] = None, page: str = "unknown"):
        if not SUPABASE_AVAILABLE:
            return False
        try:
            # Check if we have Supabase configuration in Streamlit secrets
            if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
                return False

            # Initialize Supabase client
            supabase: Client = create_client(
                st.secrets["SUPABASE_URL"],
                st.secrets["SUPABASE_KEY"]
            )
            data_to_insert = {
                "source": "textile-pe",
                "session_id": str(uuid.uuid4()),
                "timestamp": datetime.datetime.now().isoformat(),
                "event_type": "generic",
                "page": page,
                "data": event_data,
                "action": "",
                "env" : st.secrets["ENV"],
                "user_id": st.session_state.user_id,
            }

            # Insert into database
            result = supabase.table("analytics").insert(data_to_insert).execute()

            if result.data:
                return True
            else:
                return False
        except Exception as e:
            print(f"Erro ao salvar no Supabase: {str(e)}")
            return False

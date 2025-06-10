import streamlit as st
from typing import Dict, Any

from src.nm.analytics import  Analytics
from src.utils import (Page)
from src.state import StateManager


class MethodologyPage(Page):
    def render(self, data: Dict[str, Any]):
        Analytics.log_event("page_view", {"page": "methodology"})
        StateManager.increment_page_view("Visão Geral")
        methodology_content = data.get("methodology")
        if not methodology_content:
            st.warning("Página indisponível")
            return

        st.html(methodology_content)

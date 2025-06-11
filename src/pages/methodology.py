import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Any

from src.nm.analytics import  Analytics
from src.nm.comments import CommentsManager
from src.utils.page_utils import (Page)
from src.state import StateManager


class MethodologyPage(Page):
    def render(self, data: Dict[str, Any]):
        Analytics.log_event("page_view", {"page": "methodology"})
        StateManager.increment_page_view("Visão Geral")
        methodology_content = data.get("methodology")
        if not methodology_content:
            st.warning("Página indisponível")
            return

        components.html(methodology_content, height=1000, scrolling=True)
        
        # Add comment section
        st.markdown("---")
        CommentsManager.render_comment_section("methodology_framework", "methodology")

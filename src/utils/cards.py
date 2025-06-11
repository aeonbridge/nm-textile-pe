import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict, Any, List
import json

from src.nm.comments import CommentsManager


class InteractiveCard:
    """Custom Streamlit card component with flip functionality and comments"""
    
    def __init__(self, 
                 card_id: str,
                 title: str, 
                 content: str,
                 color: str = "#3182ce",
                 height: int = 600):
        """
        Initialize an interactive card.
        
        Args:
            card_id: Unique identifier for the card
            title: Card title/header
            content: HTML content for the front of the card
            color: Border and header color (hex)
            height: Card height in pixels
        """
        self.card_id = card_id
        self.title = title
        self.content = content
        self.color = color
        self.height = height
        self.session_key = f"card_state_{card_id}"
        
    def render(self) -> None:
        """Render the interactive card component"""
        # Initialize card state
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {
                'flipped': False,
                'comments': [],
                'new_comment': None,
                'show_comment_form': False
            }
        
        # Load comments from Supabase
        comments = CommentsManager.load_comments(self.card_id)
        comment_count = len(comments)
        
        # Generate the HTML for the card
        card_html = self._generate_card_html(comment_count, comments)
        
        # Render the component
        components.html(card_html, height=self.height + 50, scrolling=False)
        
        # Add external comment form that appears when needed
        self._render_external_comment_form()
    
    def _render_external_comment_form(self):
        """Render an external comment form below the card"""
        # Check if user clicked to add comment (we'll detect this via button)
        if st.button(f"💬 Adicionar comentário para {self.title}", key=f"add_comment_btn_{self.card_id}"):
            st.session_state[self.session_key]['show_comment_form'] = True
        
        # Show the comment form if requested
        if st.session_state[self.session_key].get('show_comment_form', False):
            with st.form(key=f"comment_form_{self.card_id}", clear_on_submit=True):
                st.markdown(f"**💬 Adicionar comentário para: {self.title}**")
                comment_text = st.text_area(
                    "Seu comentário:",
                    height=100,
                    placeholder="Digite seu comentário aqui...",
                    key=f"comment_input_{self.card_id}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("💾 Salvar Comentário", type="primary")
                with col2:
                    if st.form_submit_button("❌ Cancelar"):
                        st.session_state[self.session_key]['show_comment_form'] = False
                        st.rerun()
                
                if submitted:
                    if comment_text and comment_text.strip():
                        if CommentsManager.save_comment(self.card_id, comment_text.strip()):
                            st.success("Comentário adicionado com sucesso!")
                            st.session_state[self.session_key]['show_comment_form'] = False
                            st.rerun()
                        else:
                            st.error("Erro ao salvar comentário.")
                    else:
                        st.warning("Por favor, digite um comentário antes de salvar.")
    
    def _handle_js_result(self, result):
        """Handle result from JavaScript component"""
        if isinstance(result, dict) and result.get('type') == 'comment':
            comment_text = result.get('comment', '').strip()
            if comment_text:
                if CommentsManager.save_comment(self.card_id, comment_text):
                    st.success("Comentário adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao salvar comentário.")
    
    def _generate_card_html(self, comment_count: int, comments: List) -> str:
        """Generate the complete HTML for the card"""
        
        # Format comments for JavaScript
        comments_js = json.dumps([{
            'id': comment.id,
            'text': comment.comment,
            'author': comment.author[:8] if comment.author else 'Anônimo',
            'timestamp': comment.created_at
        } for comment in comments])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        {self._get_card_css()}
    </style>
</head>
<body>
    <div class="card-container">
        <div class="interactive-card" data-card-id="{self.card_id}">
            <div class="comment-indicator {'has-comments' if comment_count > 0 else ''}">{comment_count}</div>
            <div class="click-hint">👁️ Clique para ver comentários</div>
            <div class="floating-hint">👆 Clique para ver comentários existentes</div>
            
            <div class="card-inner">
                <!-- Front of card -->
                <div class="card-front">
                    <div class="card-header" style="background-color: {self.color}">
                        {self.title}
                    </div>
                    <div class="card-content">
                        {self.content}
                    </div>
                </div>
                
                <!-- Back of card (comments) -->
                <div class="card-back">
                    <div class="comments-section">
                        <div class="comments-header">
                            <h3 class="comments-title">💬 Comentários</h3>
                            <button class="close-comments" onclick="closeComments()">✕ Fechar</button>
                        </div>
                        <div class="comments-list" id="comments-list">
                            {self._render_comments_html(comments)}
                        </div>
                        <div class="comment-form">
                            <div class="comment-note">
                                <p style="text-align: center; color: #718096; font-style: italic; padding: 20px; background: #f7fafc; border-radius: 8px; margin: 10px 0;">
                                    💡 Para adicionar um novo comentário, clique no botão<br>
                                    <strong>"💬 Adicionar comentário"</strong> abaixo do cartão
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        {self._get_card_javascript(comments_js)}
    </script>
</body>
</html>
        """
        return html
    
    def _render_comments_html(self, comments) -> str:
        """Render comments as HTML"""
        if not comments:
            return '<div class="no-comments">Nenhum comentário ainda. Seja o primeiro!</div>'
        
        comments_html = ""
        for comment in comments:
            author = comment.author[:8] if comment.author else 'Anônimo'
            # Format timestamp if available
            try:
                from datetime import datetime
                if comment.created_at:
                    dt = datetime.fromisoformat(comment.created_at.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%d/%m/%Y %H:%M")
                else:
                    formatted_time = "Data não disponível"
            except:
                formatted_time = "Data não disponível"
            
            comments_html += f'''
            <div class="comment-item">
                <div class="comment-meta">👤 {author} • 📅 {formatted_time}</div>
                <div class="comment-text">{comment.comment}</div>
            </div>
            '''
        
        return comments_html
    
    def _get_card_css(self) -> str:
        """Return the CSS styles for the card"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: transparent;
            margin: 0;
            padding: 10px;
        }
        
        .card-container {
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }
        
        .interactive-card {
            width: 100%;
            max-width: 400px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 3px solid;
            border-color: inherit;
            transition: all 0.6s ease;
            cursor: pointer;
            transform-style: preserve-3d;
            perspective: 1000px;
            position: relative;
            min-height: 500px;
        }
        
        .interactive-card:hover {
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }
        
        .card-inner {
            position: relative;
            width: 100%;
            height: 100%;
            text-align: left;
            transition: transform 0.6s;
            transform-style: preserve-3d;
            min-height: 500px;
        }
        
        .interactive-card.flipped .card-inner {
            transform: rotateY(180deg);
        }
        
        .card-front, .card-back {
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            border-radius: inherit;
            display: flex;
            flex-direction: column;
        }
        
        .card-back {
            transform: rotateY(180deg);
            background: #f8f9fa;
            padding: 20px;
        }
        
        .card-header {
            color: white;
            font-size: 1.1rem;
            font-weight: 700;
            padding: 16px;
            border-radius: 13px 13px 0 0;
            text-align: center;
        }
        
        .card-content {
            padding: 20px;
            flex: 1;
            overflow-y: auto;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        
        .card-content h4 {
            font-weight: 600;
            margin: 12px 0 8px 0;
            color: #2d3748;
        }
        
        .card-content ul {
            margin-left: 20px;
            margin-bottom: 12px;
        }
        
        .card-content li {
            margin-bottom: 6px;
            color: #4a5568;
        }
        
        /* Comment indicator */
        .comment-indicator {
            position: absolute;
            top: 12px;
            right: 12px;
            background: #4299e1;
            color: white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            font-weight: 600;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 10;
        }
        
        .comment-indicator.has-comments {
            opacity: 1;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(66, 153, 225, 0.7); }
            50% { transform: scale(1.1); box-shadow: 0 0 0 6px rgba(66, 153, 225, 0.3); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(66, 153, 225, 0); }
        }
        
        /* Hover hints */
        .click-hint {
            position: absolute;
            bottom: 12px;
            right: 12px;
            background: rgba(66, 153, 225, 0.9);
            color: white;
            padding: 6px 10px;
            border-radius: 16px;
            font-size: 0.7rem;
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.3s ease;
            pointer-events: none;
            z-index: 5;
        }
        
        .interactive-card:hover .click-hint {
            opacity: 1;
            transform: translateY(0);
        }
        
        .floating-hint {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 0.8rem;
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.8);
            transition: all 0.3s ease;
            pointer-events: none;
            z-index: 10;
            text-align: center;
        }
        
        .interactive-card:hover .floating-hint {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
        }
        
        .interactive-card.flipped .floating-hint {
            display: none;
        }
        
        /* Comments section */
        .comments-section {
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        
        .comments-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .comments-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2d3748;
        }
        
        .close-comments {
            background: #e53e3e;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: background 0.3s ease;
        }
        
        .close-comments:hover {
            background: #c53030;
        }
        
        .comments-list {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 16px;
            max-height: 200px;
        }
        
        .comment-item {
            background: white;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 3px solid #4299e1;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .comment-meta {
            font-size: 0.7rem;
            color: #718096;
            margin-bottom: 6px;
        }
        
        .comment-text {
            font-size: 0.8rem;
            color: #2d3748;
            line-height: 1.4;
        }
        
        .no-comments {
            text-align: center;
            color: #718096;
            font-style: italic;
            padding: 30px;
        }
        
        .comment-form {
            display: flex;
            flex-direction: column;
        }
        
        .comment-note {
            padding: 10px;
        }
        """
    
    def _get_card_javascript(self, comments_js: str) -> str:
        """Return the JavaScript for card functionality"""
        return f"""
        let isFlipped = false;
        let comments = {comments_js};
        
        document.addEventListener('DOMContentLoaded', function() {{
            const card = document.querySelector('.interactive-card');
            
            // Card click to flip
            card.addEventListener('click', function(e) {{
                // Don't flip if clicking on buttons or textarea
                if (e.target.tagName === 'BUTTON' || e.target.tagName === 'TEXTAREA') {{
                    return;
                }}
                
                if (!isFlipped) {{
                    flipCard();
                }}
            }});
            
        }});
        
        function flipCard() {{
            const card = document.querySelector('.interactive-card');
            card.classList.add('flipped');
            isFlipped = true;
            
            // Card is now flipped to show comments
        }}
        
        function closeComments() {{
            const card = document.querySelector('.interactive-card');
            card.classList.remove('flipped');
            isFlipped = false;
        }}
        
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        function formatDate(dateString) {{
            try {{
                const date = new Date(dateString);
                const now = new Date();
                const diff = now - date;
                const minutes = Math.floor(diff / 60000);
                const hours = Math.floor(diff / 3600000);
                const days = Math.floor(diff / 86400000);
                
                if (minutes < 1) return 'agora';
                if (minutes < 60) return minutes + 'm atrás';
                if (hours < 24) return hours + 'h atrás';
                return days + 'd atrás';
            }} catch (e) {{
                return 'Data não disponível';
            }}
        }}
        """
    


def create_phase_card(phase_number: int, title: str, content_dict: Dict[str, Any]) -> InteractiveCard:
    """
    Create a card for a methodology phase
    
    Args:
        phase_number: Phase number (1-7)
        title: Phase title
        content_dict: Dictionary with sections and items
    
    Returns:
        InteractiveCard instance
    """
    colors = {
        1: "#e53e3e",
        2: "#dd6b20", 
        3: "#d69e2e",
        4: "#38a169",
        5: "#3182ce",
        6: "#805ad5",
        7: "#d53f8c"
    }
    
    # Generate HTML content from content_dict
    content_html = ""
    for section, items in content_dict.items():
        content_html += f"<h4>{section}</h4><ul>"
        for item in items:
            content_html += f"<li>{item}</li>"
        content_html += "</ul>"
    
    card_id = f"phase-{phase_number}"
    color = colors.get(phase_number, "#3182ce")
    
    return InteractiveCard(
        card_id=card_id,
        title=title,
        content=content_html,
        color=color,
        height=600
    )
import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict, Any, List
import json

from src.nm.comments import CommentsManager


def interactive_card_component(card_id: str, title: str, content: str, comments: List, 
                               color: str = "#3182ce", height: int = 600):
    """
    Create a custom interactive card component following Streamlit best practices.
    
    Args:
        card_id: Unique identifier for the card
        title: Card title/header
        content: HTML content for the front of the card
        comments: List of existing comments
        color: Border and header color (hex)
        height: Card height in pixels
    
    Returns:
        Dictionary containing component interaction data, or None if no interaction
    """
    
    # Format comments for JavaScript (display only)
    comments_js = json.dumps([{
        'id': comment.id,
        'text': comment.comment,
        'author': comment.author[:8] if comment.author else 'Anônimo',
        'timestamp': comment.created_at
    } for comment in comments])
    
    comment_count = len(comments)
    
    # Generate the HTML for the card (display only - no form)
    card_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        {_get_card_css()}
    </style>
</head>
<body>
    <div class="card-container">
        <div class="interactive-card" data-card-id="{card_id}">
            <div class="comment-indicator {'has-comments' if comment_count > 0 else ''}">{comment_count}</div>
            <div class="click-hint">💬 Clique para ver comentários</div>
            
            <div class="card-inner">
                <!-- Front of card -->
                <div class="card-front">
                    <div class="card-header" style="background-color: {color}">
                        {title}
                    </div>
                    <div class="card-content">
                        {content}
                    </div>
                </div>
                
                <!-- Back of card (comments display only) -->
                <div class="card-back">
                    <div class="comments-section">
                        <div class="comments-header">
                            <h3 class="comments-title">💬 Comentários ({comment_count})</h3>
                            <button class="close-comments" onclick="closeComments()">✕ Fechar</button>
                        </div>
                        <div class="comments-list" id="comments-list">
                            {_render_comments_html(comments)}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        {_get_simple_card_javascript()}
    </script>
</body>
</html>
    """
    
    # Render the display-only component
    components.html(card_html, height=height + 50, scrolling=False)
    
    return None


def render_comments_section(available_items: Dict[str, any], page_key: str = ""):
    """
    Render a centralized comments section for multiple items with hierarchical support
    
    Args:
        available_items: Dict with item_id as key and either:
                        - string value for simple items
                        - dict value for hierarchical items (group -> sub-items)
        page_key: Unique key for the page to avoid conflicts
    """
    
    if not available_items:
        return
    
    st.markdown("---")
    st.markdown("## 💬 Sistema de Comentários")
    
    # Check if we have hierarchical structure (groups with sub-items)
    has_hierarchical = any(isinstance(value, dict) for value in available_items.values())
    
    if has_hierarchical:
        # First level: select group
        group_options = list(available_items.keys())
        group_labels = [f"{group_id}" for group_id in group_options]
        
        selected_group_index = st.selectbox(
            "Selecione a categoria:",
            range(len(group_options)),
            format_func=lambda x: group_labels[x],
            key=f"comment_group_selector_{page_key}"
        )
        
        selected_group_id = group_options[selected_group_index]
        selected_group = available_items[selected_group_id]
        
        # Second level: select specific item within group
        if isinstance(selected_group, dict):
            # Add "Geral" option for group-level comments
            sub_items = {"geral": "Comentário Geral"} 
            sub_items.update(selected_group)
            
            sub_options = list(sub_items.keys())
            sub_labels = [f"{sub_items[sub_id]}" for sub_id in sub_options]
            
            selected_sub_index = st.selectbox(
                f"Selecione o item específico em **{selected_group_id}**:",
                range(len(sub_options)),
                format_func=lambda x: sub_labels[x],
                key=f"comment_sub_selector_{page_key}_{selected_group_id}"
            )
            
            selected_sub_id = sub_options[selected_sub_index]
            selected_sub_name = sub_items[selected_sub_id]
            
            # Create unique identifier for comment location
            if selected_sub_id == "geral":
                selected_item_id = selected_group_id
                selected_item_name = selected_group_id
            else:
                selected_item_id = f"{selected_group_id}_{selected_sub_id}"
                selected_item_name = f"{selected_group_id} → {selected_sub_name}"
        else:
            # Simple string value
            selected_item_id = selected_group_id
            selected_item_name = selected_group
    else:
        # Simple flat structure
        item_options = list(available_items.keys())
        item_labels = [f"{available_items[item_id]}" for item_id in item_options]
        
        selected_item_index = st.selectbox(
            "Selecione o item para comentar:",
            range(len(item_options)),
            format_func=lambda x: item_labels[x],
            key=f"comment_item_selector_{page_key}"
        )
        
        selected_item_id = item_options[selected_item_index]
        selected_item_name = available_items[selected_item_id]
    
    # Display existing comments for selected item
    comments = CommentsManager.load_comments(selected_item_id)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 📝 Comentários: {selected_item_name}")
        
        if comments:
            for comment in comments:
                with st.container():
                    # Format timestamp
                    if comment.created_at:
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(comment.created_at.replace('Z', '+00:00'))
                            formatted_time = dt.strftime("%d/%m/%Y %H:%M")
                        except:
                            formatted_time = "Data não disponível"
                    else:
                        formatted_time = "Data não disponível"
                    
                    # Show author (first 8 chars of session ID)
                    author_short = comment.author[:8] if comment.author else "Anônimo"
                    
                    # Comment display
                    st.markdown(f"**👤 {author_short}** • 📅 {formatted_time}")
                    st.markdown(f"> {comment.comment}")
                    st.markdown("---")
        else:
            st.info("Nenhum comentário ainda. Seja o primeiro a comentar!")
    
    with col2:
        st.markdown("### ➕ Adicionar Comentário")
        
        # Comment form
        form_key = f"comment_form_{page_key}_{selected_item_id}"
        input_key = f"comment_input_{page_key}_{selected_item_id}"
        
        with st.form(key=form_key):
            comment_text = st.text_area(
                f"Comentário sobre **{selected_item_name}**:",
                placeholder="Digite seu comentário aqui...",
                height=150,
                key=input_key
            )
            
            submitted = st.form_submit_button("💾 Adicionar Comentário")
            
            if submitted and comment_text.strip():
                if CommentsManager.save_comment(selected_item_id, comment_text.strip()):
                    st.success("Comentário adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao salvar comentário.")
            elif submitted:
                st.warning("Por favor, digite um comentário antes de enviar.")


def _render_comments_html(comments) -> str:
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


def _get_card_css() -> str:
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
        gap: 12px;
    }
    
    .comment-input {
        resize: vertical;
        min-height: 80px;
        padding: 12px;
        border: 2px solid #e2e8f0;
        border-radius: 6px;
        font-size: 0.8rem;
        font-family: inherit;
        transition: border-color 0.3s ease;
    }
    
    .comment-input:focus {
        outline: none;
        border-color: #4299e1;
    }
    
    .comment-submit {
        background: #38a169;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.8rem;
        font-weight: 600;
        transition: background 0.3s ease;
    }
    
    .comment-submit:hover {
        background: #2f855a;
    }
    
    .comment-note {
        text-align: center;
        padding: 20px;
        background: #f7fafc;
        border-radius: 8px;
        margin-top: 16px;
    }
    
    .comment-note p {
        color: #4a5568;
        font-size: 0.9rem;
        margin: 0;
        font-style: italic;
    }
    """


def _get_simple_card_javascript() -> str:
    """Return simplified JavaScript for card display only"""
    return """
    let isFlipped = false;
    
    document.addEventListener('DOMContentLoaded', function() {
        const card = document.querySelector('.interactive-card');
        
        // Card click to flip and show comments
        card.addEventListener('click', function(e) {
            // Don't flip if clicking on buttons
            if (e.target.tagName === 'BUTTON') {
                return;
            }
            
            if (!isFlipped) {
                flipCard();
            }
        });
    });
    
    function flipCard() {
        const card = document.querySelector('.interactive-card');
        card.classList.add('flipped');
        isFlipped = true;
    }
    
    function closeComments() {
        const card = document.querySelector('.interactive-card');
        card.classList.remove('flipped');
        isFlipped = false;
    }
    """


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
        
    def render(self) -> Optional[Dict]:
        """Render the interactive card component using the new function-based approach"""
        # Load comments from Supabase
        comments = CommentsManager.load_comments(self.card_id)
        
        # Use the new function-based component (handles comment saving internally)
        result = interactive_card_component(
            card_id=self.card_id,
            title=self.title,
            content=self.content,
            comments=comments,
            color=self.color,
            height=self.height
        )
        
        return result
    


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
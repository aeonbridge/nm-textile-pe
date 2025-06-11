import streamlit as st
import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from src.nm.analytics import Analytics


@dataclass
class Comment:
    """Data class for comment structure"""
    id: Optional[int] = None
    created_at: Optional[str] = None
    project: str = "st-textile-pe"
    location: Optional[str] = None
    author: Optional[str] = None
    comment: Optional[str] = None


class CommentsManager:
    """Manages comments using Supabase backend"""
    
    @staticmethod
    def _get_supabase_client() -> Optional[Client]:
        """Get Supabase client if available and configured"""
        if not SUPABASE_AVAILABLE:
            return None
            
        try:
            if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
                return None
                
            return create_client(
                st.secrets["SUPABASE_URL"],
                st.secrets["SUPABASE_KEY"]
            )
        except Exception:
            return None
    
    @staticmethod
    def save_comment(location: str, comment_text: str) -> bool:
        """Save a comment to Supabase"""
        if not comment_text.strip():
            return False
            
        supabase = CommentsManager._get_supabase_client()
        if not supabase:
            return False
            
        try:
            # Get current session ID as author
            author = Analytics.get_session_id()
            
            comment_data = {
                "project": "st-textile-pe",
                "location": location,
                "author": author,
                "comment": comment_text.strip()
            }
            
            result = supabase.table("comments").insert(comment_data).execute()
            
            if result.data:
                return True
            else:
                return False
                
        except Exception as e:
            st.error(f"Erro ao salvar comentário: {str(e)}")
            return False
    
    @staticmethod
    def load_comments(location: Optional[str] = None) -> List[Comment]:
        """Load comments from Supabase"""
        supabase = CommentsManager._get_supabase_client()
        if not supabase:
            return []
            
        try:
            query = supabase.table("comments").select("*").eq("project", "st-textile-pe")
            
            if location:
                query = query.eq("location", location)
                
            result = query.order("created_at", desc=True).execute()
            
            if result.data:
                comments = []
                for row in result.data:
                    comment = Comment(
                        id=row.get("id"),
                        created_at=row.get("created_at"),
                        project=row.get("project"),
                        location=row.get("location"),
                        author=row.get("author"),
                        comment=row.get("comment")
                    )
                    comments.append(comment)
                return comments
            else:
                return []
                
        except Exception as e:
            st.error(f"Erro ao carregar comentários: {str(e)}")
            return []
    
    @staticmethod
    def delete_comment(comment_id: int) -> bool:
        """Delete a comment (only for comments from current session)"""
        supabase = CommentsManager._get_supabase_client()
        if not supabase:
            return False
            
        try:
            # Get current session ID
            current_author = Analytics.get_session_id()
            
            # Only allow deletion of comments from current session
            result = supabase.table("comments").delete().eq("id", comment_id).eq("author", current_author).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            st.error(f"Erro ao deletar comentário: {str(e)}")
            return False
    
    @staticmethod
    def render_comment_section(location: str, key_prefix: str = ""):
        """Render a complete comment section with input and display"""
        st.subheader("💬 Comentários")
        
        # Comment input
        with st.form(key=f"comment_form_{key_prefix}_{location}"):
            comment_text = st.text_area(
                "Adicione seu comentário:",
                placeholder="Digite seu comentário aqui...",
                height=100,
                key=f"comment_input_{key_prefix}_{location}"
            )
            
            submitted = st.form_submit_button("💾 Salvar Comentário")
            
            if submitted and comment_text.strip():
                if CommentsManager.save_comment(location, comment_text):
                    st.success("Comentário salvo com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao salvar comentário.")
        
        # Display existing comments
        comments = CommentsManager.load_comments(location)
        
        if comments:
            st.subheader(f"📝 Comentários ({len(comments)})")
            
            for comment in comments:
                with st.container():
                    # Format timestamp
                    if comment.created_at:
                        try:
                            dt = datetime.datetime.fromisoformat(comment.created_at.replace('Z', '+00:00'))
                            formatted_time = dt.strftime("%d/%m/%Y %H:%M")
                        except:
                            formatted_time = "Data não disponível"
                    else:
                        formatted_time = "Data não disponível"
                    
                    # Show author (first 8 chars of session ID)
                    author_short = comment.author[:8] if comment.author else "Anônimo"
                    
                    # Comment header
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.caption(f"👤 {author_short} • 📅 {formatted_time}")
                    
                    # Delete button for own comments
                    current_author = Analytics.get_session_id()
                    if comment.author == current_author:
                        with col2:
                            if st.button("🗑️", key=f"delete_{comment.id}", help="Deletar comentário"):
                                if CommentsManager.delete_comment(comment.id):
                                    st.success("Comentário deletado!")
                                    st.rerun()
                                else:
                                    st.error("Erro ao deletar comentário.")
                    
                    # Comment content
                    st.write(comment.comment)
                    st.divider()
        else:
            st.info("Nenhum comentário ainda. Seja o primeiro a comentar!")
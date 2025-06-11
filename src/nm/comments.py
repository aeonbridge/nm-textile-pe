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
    author_picture: Optional[str] = None
    author_name: Optional[str] = None


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
            # Get user identifier (email if authenticated, session ID as fallback)
            author = Analytics.get_user_identifier()
            
            # Get user picture and name if available
            author_picture = None
            author_name = None
            try:
                if hasattr(st, 'user') and st.user.is_logged_in:
                    if hasattr(st.user, 'picture') and st.user.picture:
                        author_picture = st.user.picture
                    if hasattr(st.user, 'name') and st.user.name:
                        author_name = st.user.name
                        
                    # Debug info (remove in production)
                    if st.secrets.get("ENV") == "dev":
                        st.info(f"🔍 Salvando comentário: author_picture = '{author_picture}', author_name = '{author_name}'")
            except:
                pass
            
            comment_data = {
                "project": "st-textile-pe",
                "location": location,
                "author": author,
                "comment": comment_text.strip(),
                "author_picture": author_picture,
                "author_name": author_name
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
                        comment=row.get("comment"),
                        author_picture=row.get("author_picture"),
                        author_name=row.get("author_name")
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
        """Delete a comment (only for comments from current user)"""
        supabase = CommentsManager._get_supabase_client()
        if not supabase:
            return False
            
        try:
            # Get current user identifier
            current_author = Analytics.get_user_identifier()
            
            # Only allow deletion of comments from current user
            result = supabase.table("comments").delete().eq("id", comment_id).eq("author", current_author).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            st.error(f"Erro ao deletar comentário: {str(e)}")
            return False
    
    @staticmethod
    def render_comment_section(location: str, key_prefix: str = ""):
        """Render a complete comment section with input and display"""
        st.subheader("💬 Comentários")
        
        # Show current user info before comment input
        current_user_picture = None
        current_user_display = "Usuário Anônimo"
        
        # Get current user info
        try:
            if hasattr(st, 'user') and st.user.is_logged_in:
                if hasattr(st.user, 'picture') and st.user.picture:
                    current_user_picture = st.user.picture
                if hasattr(st.user, 'name') and st.user.name:
                    current_user_display = st.user.name
                elif hasattr(st.user, 'email') and st.user.email:
                    current_user_display = st.user.email.split("@")[0]
        except:
            pass
        
        # Comment input with user info
        with st.form(key=f"comment_form_{key_prefix}_{location}"):
            # Show who is commenting
            if current_user_picture:
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <img src="{current_user_picture}" 
                         style="width: 24px; height: 24px; border-radius: 50%; margin-right: 8px; 
                                object-fit: cover; border: 1px solid #e0e0e0;" 
                         alt="Your profile picture"/>
                    <span style="color: #666; font-size: 14px;">Comentando como: <strong>{current_user_display}</strong></span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.caption(f"👤 Comentando como: **{current_user_display}**")
            
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
                    
                    # Format author display - prioritize author_name if available
                    if comment.author_name:
                        # Use the saved full name
                        author_display = comment.author_name
                        author_icon = "👤"
                    elif comment.author and "@" in comment.author:
                        # If it's an email, show just the name part
                        author_display = comment.author.split("@")[0]
                        author_icon = "👤"
                    else:
                        # If it's a session ID, show first 8 chars
                        author_display = comment.author[:8] if comment.author else "Anônimo"
                        author_icon = "🔹"
                    
                    # Comment header with profile picture
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Create a container for profile picture and author info
                        if comment.author_picture and comment.author_picture.strip():
                            # Use HTML for circular profile picture with professional styling
                            st.markdown(f"""
                            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                <img src="{comment.author_picture}" 
                                     style="width: 32px; height: 32px; border-radius: 50%; margin-right: 10px; 
                                            object-fit: cover; border: 2px solid #e0e0e0; 
                                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);" 
                                     alt="Profile picture"/>
                                <div>
                                    <span style="color: #333; font-weight: 500; font-size: 14px;">{author_display}</span>
                                    <br/>
                                    <span style="color: #666; font-size: 12px;">📅 {formatted_time}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Fallback to emoji when no picture
                            st.caption(f"{author_icon} {author_display} • 📅 {formatted_time}")
                            # Debug info (remove in production)
                            if st.secrets.get("ENV") == "dev":
                                st.caption(f"🔍 Debug: author_picture = '{comment.author_picture}'")
                    
                    # Delete button for own comments
                    current_author = Analytics.get_user_identifier()
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
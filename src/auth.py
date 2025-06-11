import streamlit as st
from typing import Optional, Dict, Any

class AuthManager:
    """Authentication manager using Streamlit's native authentication"""
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if current session is authenticated using Streamlit's native authentication"""
        try:
            is_logged_in = st.user.is_logged_in
            
            # Log successful login event (only once per session)
            if is_logged_in and not st.session_state.get("login_logged", False):
                try:
                    from src.nm.analytics import Analytics
                    Analytics.log_event("user_login", {
                        "username": st.user.name or st.user.email,
                        "user_type": "google_oauth_user"
                    })
                    st.session_state.login_logged = True
                except Exception:
                    pass  # Analytics failure shouldn't break authentication
            
            return is_logged_in
        except AttributeError:
            # Fallback to session state if native auth is not available
            return st.session_state.get("authenticated", False)
    
    @staticmethod
    def get_current_user() -> Optional[str]:
        """Get current authenticated username using Streamlit's native authentication"""
        try:
            if st.user.is_logged_in:
                return st.user.name or st.user.email
        except AttributeError:
            # Fallback to session state if native auth is not available
            if st.session_state.get("authenticated", False):
                return st.session_state.get("username")
        return None
    
    @staticmethod
    def get_user_info() -> Dict[str, Any]:
        """Get comprehensive user information"""
        try:
            if st.user.is_logged_in:
                user_data = {
                    "name": getattr(st.user, 'name', None),
                    "email": getattr(st.user, 'email', None),
                    "picture": getattr(st.user, 'picture', None),
                    "is_logged_in": st.user.is_logged_in
                }
                
# Debug info (remove in production)
                # if st.secrets.get("ENV") == "dev":
                #     st.caption(f"🔍 Debug st.user attributes: name='{user_data['name']}', email='{user_data['email']}', picture available={bool(user_data['picture'])}")
                
                return user_data
        except AttributeError:
            # Fallback to session state if native auth is not available
            if st.session_state.get("authenticated", False):
                return {
                    "name": st.session_state.get("username"),
                    "email": None,
                    "picture": None,
                    "is_logged_in": True
                }
        return {
            "name": None,
            "email": None,
            "picture": None,
            "is_logged_in": False
        }
    
    @staticmethod
    def get_user_display_name() -> str:
        """Get a friendly display name for the user"""
        user_info = AuthManager.get_user_info()
        
        # Debug info (remove in production)
        # if st.secrets.get("ENV") == "dev":
        #     st.caption(f"🔍 Debug user_info: {user_info}")
        
        if user_info["is_logged_in"]:
            if user_info["name"] and user_info["name"].strip():
                return user_info["name"]
            elif user_info["email"] and user_info["email"].strip():
                # Extract name from email (part before @)
                return user_info["email"].split("@")[0]
        
        return "Usuário Anônimo"
    
    @staticmethod
    def login() -> None:
        """Initiate authentication flow using Streamlit's native authentication"""
        try:
            # Use Streamlit's native login (this redirects automatically)
            st.login()
                
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            st.info("Please check your authentication configuration in .streamlit/secrets.toml")
    
    @staticmethod
    def logout():
        """Clear authentication session using Streamlit's native authentication"""
        try:
            # Log logout event before clearing session
            if AuthManager.is_authenticated():
                try:
                    from src.nm.analytics import Analytics
                    user_info = AuthManager.get_user_info()
                    Analytics.log_event("user_logout", {
                        "username": user_info.get("name") or user_info.get("email"),
                        "session_duration": AuthManager._calculate_session_duration()
                    })
                except Exception:
                    pass  # Analytics failure shouldn't break logout
            
            # Use Streamlit's native logout
            st.logout()
            
        except AttributeError:
            # Fallback to session state clearing if native auth is not available
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.login_time = None
        except Exception as e:
            st.error(f"Logout error: {str(e)}")
    
    @staticmethod
    def _calculate_session_duration() -> str:
        """Calculate session duration in minutes"""
        try:
            login_time = st.session_state.get('login_time')
            if login_time:
                import pandas as pd
                current_time = pd.Timestamp.now()
                login_timestamp = pd.Timestamp(login_time)
                duration = current_time - login_timestamp
                return str(int(duration.total_seconds() / 60))
        except Exception:
            pass
        return "unknown"
    
    @staticmethod
    def render_login_form() -> bool:
        """Render login interface using Streamlit's native authentication"""
        
        # Mobile-friendly layout - single column on mobile, centered on desktop
        col1, col2, col3 = st.columns([0.5, 3, 0.5])
        
        with col2:
            # Logo and title section
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h1 style="color: white; font-size: clamp(1.5rem, 4vw, 2.2rem); 
                           text-shadow: 2px 2px 4px rgba(0,0,0,0.3); margin-bottom: 0.5rem;">
                    🔐 Acesso ao Dashboard
                </h1>
                <h3 style="color: rgba(255,255,255,0.9); font-size: clamp(1rem, 2.5vw, 1.3rem); 
                           text-shadow: 1px 1px 2px rgba(0,0,0,0.3); font-weight: 400; margin-bottom: 0;">
                    Dashboard Ecossistema Têxtil - PE
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Native authentication container
            with st.container():
                st.markdown("""
                <div style="background: rgba(255, 255, 255, 0.95); padding: 2rem; 
                           border-radius: 12px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2); 
                           backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.3); 
                           text-align: center; margin-bottom: 1rem;">
                    <h4 style="color: #333; margin-bottom: 1rem;">🚀 Entrar no Dashboard</h4>
                    <p style="color: #666; margin-bottom: 1.5rem;">
                        Clique no botão abaixo para fazer login usando a autenticação nativa do Streamlit
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Login button using native authentication
                if st.button("🔑 Fazer Login com Google", use_container_width=True, type="primary"):
                    AuthManager.login()
            
            # Information section
            st.markdown("""
            <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(255,255,255,0.1); 
                        border-radius: 8px; backdrop-filter: blur(10px);">
                <h4 style="color: white; margin-bottom: 0.8rem; font-size: clamp(0.9rem, 2vw, 1.1rem);">
                    ℹ️ Sobre a Autenticação
                </h4>
                <p style="color: rgba(255,255,255,0.9); font-size: clamp(0.8rem, 1.8vw, 0.9rem); line-height: 1.4;">
                    Este dashboard utiliza a autenticação nativa do Streamlit para garantir acesso seguro. 
                    Você será redirecionado para o provedor de identidade configurado.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        return False
    
    @staticmethod
    def render_logout_button():
        """Render user profile as circular photo in top right corner"""
        user_info = AuthManager.get_user_info()
        
        if user_info["is_logged_in"]:
            # Get user display name and picture
            user_display = AuthManager.get_user_display_name()
            user_picture = user_info.get("picture")
            
            # Use columns to position in top right
            col1, col2, col3 = st.columns([6, 2, 2])
            
            with col3:
                if user_picture and user_picture.strip():
                    # Show profile picture with name - complete HTML in one block
                    profile_html = f"""
                    <div style="display: flex; align-items: center; justify-content: flex-end; 
                               background: rgba(255, 255, 255, 0.9); padding: 5px 10px; 
                               border-radius: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                               margin-bottom: 10px; gap: 8px;">
                        <img src="{user_picture}" 
                             style="width: 30px; height: 30px; border-radius: 50%; 
                                    object-fit: cover; border: 1px solid #ddd;" 
                             alt="Profile"/>
                        <span style="font-size: 14px; font-weight: 500; color: #333;">{user_display}</span>
                    </div>
                    """
                    st.markdown(profile_html, unsafe_allow_html=True)
                else:
                    # Show fallback - complete HTML in one block
                    profile_html = f"""
                    <div style="display: flex; align-items: center; justify-content: flex-end; 
                               background: rgba(255, 255, 255, 0.9); padding: 5px 10px; 
                               border-radius: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                               margin-bottom: 10px; gap: 8px;">
                        <div style="width: 30px; height: 30px; border-radius: 50%; 
                                   background: #f0f0f0; display: flex; align-items: center; 
                                   justify-content: center; font-size: 14px; border: 1px solid #ddd;">👤</div>
                        <span style="font-size: 14px; font-weight: 500; color: #333;">{user_display}</span>
                    </div>
                    """
                    st.markdown(profile_html, unsafe_allow_html=True)
                
                # Logout button
                if st.button("🚪 Sair", key="logout_btn", 
                           help=f"Sair ({user_display})", 
                           type="secondary", 
                           use_container_width=True):
                    AuthManager.logout()
                    st.rerun()


def require_authentication():
    """Decorator function to require authentication for dashboard access using native Streamlit auth"""
    if not AuthManager.is_authenticated():
        st.set_page_config(
            page_title="Login - Dashboard Têxtil PE",
            page_icon="🔐",
            layout="centered",
            initial_sidebar_state="collapsed"
        )
        
        # Enhanced mobile-friendly CSS for login page
        st.markdown("""
        <style>
        /* Full viewport optimization */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Remove default padding and optimize for mobile */
        .main .block-container {
            padding: 1rem;
            max-width: 100%;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        /* Button styling - responsive */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: clamp(0.9rem, 2.5vw, 1rem);
            transition: all 0.3s ease;
            width: 100%;
            min-height: 48px; /* Touch-friendly */
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Mobile responsive adjustments */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 0.5rem;
                min-height: 100vh;
            }
        }
        
        /* Landscape mobile optimization */
        @media (max-height: 600px) and (orientation: landscape) {
            .main .block-container {
                padding: 0.5rem;
                justify-content: flex-start;
                padding-top: 1rem;
            }
        }
        
        /* Success/Error message styling */
        .stAlert {
            margin: 1rem 0;
            border-radius: 6px;
            font-size: clamp(0.85rem, 2vw, 0.95rem);
        }
        
        /* Hide Streamlit branding on login page */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
        
        AuthManager.render_login_form()
        st.stop()
    
    return True
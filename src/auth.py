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
        """Render modern split-screen login with textile image"""
        
        # Create columns for split layout
        col1, col2 = st.columns([2.5, 1])
        
        with col1:
            # Image side with custom styling
            st.html("""
            <div style="
                background-image: url('app/static/imgs/2148527962-small.jpg');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                position: relative;
                min-height: 80vh;
                border-radius: 16px;
                overflow: hidden;
                margin-right: 20px;">
                
                <!-- Subtle overlay for depth -->
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: linear-gradient(
                        135deg,
                        rgba(187, 90, 56, 0.1) 0%,
                        rgba(61, 58, 42, 0.05) 50%,
                        transparent 100%
                    );"></div>
                
                <!-- Brand watermark on image -->
                <div style="
                    position: absolute;
                    bottom: 40px;
                    left: 40px;
                    color: rgba(255, 255, 255, 0.9);
                    text-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                    <div style="
                        font-family: 'Styrene B', sans-serif;
                        font-size: 1.8rem;
                        font-weight: 700;
                        margin-bottom: 8px;
                        letter-spacing: -0.5px;">
                        Ecossistema Têxtil
                    </div>
                    <div style="
                        font-family: 'Styrene B', sans-serif;
                        font-size: 1rem;
                        font-weight: 400;
                        opacity: 0.9;">
                        Pernambuco • Analytics Dashboard
                    </div>
                </div>
            </div>
            """)
        
        with col2:
            # Login form side
            st.html("""
            <div style="padding: 0px 0px;">
                <!-- Logo -->
                <div style="text-align: center; margin-bottom: 50px;">
                    
                    <h1 style="
                        font-family: 'Styrene B', sans-serif;
                        font-size: 1.8rem;
                        font-weight: 700;
                        color: #3d3a2a;
                        margin: 0 0 8px 0;
                        letter-spacing: -0.5px;">
                        APL Têxtil - PE 
                    </h1>
                    
                    <div style="
                        font-family: 'Styrene B', sans-serif;
                        font-size: 0.9rem;
                        font-weight: 400;
                        color: #bb5a38;
                        opacity: 0.8;">
                        Analytics & Insights
                    </div>
                </div>
                
                <!-- Login card -->
                
                
                <!-- Features list -->
                <div style="
                    background: rgba(187, 90, 56, 0.05);
                    border: 1px solid rgba(187, 90, 56, 0.1);
                    border-radius: 0.6rem;
                    padding: 24px;
                    margin-bottom: 50px;">
                    
                    <div style="
                        font-family: 'Styrene B', sans-serif;
                        font-size: 0.85rem;
                        font-weight: 600;
                        color: #3d3a2a;
                        margin-bottom: 16px;
                        text-align: center;">
                        💡 Recursos Disponíveis
                    </div>
                    
                    <div style="color: #3d3a2a; font-size: 0.8rem; line-height: 1.8;">
                        <div style="margin-bottom: 8px;">📊 Análise de indicadores</div>
                        <div style="margin-bottom: 8px;">🕸️ Rede de stakeholders</div>
                        <div style="margin-bottom: 8px;">🗺️ Mapeamento geográfico</div>
                        <div style="margin-bottom: 8px;">⚠️ Análise de Riscos</div>
                        <div style="margin-bottom: 8px;">💡 Identificação de Oportunidades</div>
                        <div style="margin-bottom: 8px;">🚀 Laboratório Interativo</div>
                        <div style="margin-bottom: 8px;">📋 Metodologia</div>
                    </div>
                </div>
            </div>
            """)
            
            # Login button - now renders normally in the column
            if st.button("🔑 Fazer Login com Google", use_container_width=True, type="primary"):
                AuthManager.login()

        return False

    
    @staticmethod
    def render_logout_button():
        """Render user profile as circular photo in top right corner"""
        user_info = AuthManager.get_user_info()


def require_authentication():
    """Decorator function to require authentication for dashboard access using native Streamlit auth"""
    if not AuthManager.is_authenticated():
        st.set_page_config(
            page_title="Login - Dashboard Têxtil PE",
            page_icon="🔐",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Clean and elegant CSS following app theme
        st.html("""
        <style>
        /* Textile-inspired background with app theme colors */
        .stApp {
            background: #f4f3ed;
            background-image: 
                radial-gradient(circle at 25% 25%, rgba(187, 90, 56, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, rgba(61, 58, 42, 0.02) 0%, transparent 50%),
                linear-gradient(45deg, rgba(211, 210, 202, 0.1) 0%, transparent 100%);
            background-attachment: fixed;
            min-height: 0vh;
            overflow-x: hidden;
        }
        
        /* Subtle textile pattern overlay */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                repeating-linear-gradient(
                    45deg,
                    transparent,
                    transparent 2px,
                    rgba(211, 210, 202, 0.05) 2px,
                    rgba(211, 210, 202, 0.05) 4px
                ),
                repeating-linear-gradient(
                    -45deg,
                    transparent,
                    transparent 2px,
                    rgba(187, 90, 56, 0.02) 2px,
                    rgba(187, 90, 56, 0.02) 4px
                );
            pointer-events: none;
            z-index: -1;
        }
        
        /* Container styling */
        .main .block-container {
            padding: 2rem 1rem;
            max-width: 100%;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        /* Button styling following theme */
        .stButton > button {
            background: #bb5a38 !important;
            color: #f4f3ed !important;
            border: 2px solid #bb5a38 !important;
            padding: 1rem 2rem !important;
            border-radius: 0.6rem !important;
            font-family: 'Styrene B', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            min-height: 56px !important;
            box-shadow: 0 4px 12px rgba(187, 90, 56, 0.2) !important;
            letter-spacing: 0.5px !important;
        }
        
        .stButton > button:hover {
            background: #a04d30 !important;
            border-color: #a04d30 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(187, 90, 56, 0.3) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
            transition: all 0.1s ease !important;
        }
        
        /* Mobile responsive design */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem 0.5rem;
                min-height: 100vh;
            }
            
            .stButton > button {
                font-size: 0.9rem !important;
                padding: 0.9rem 1.5rem !important;
            }
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Custom scrollbar with theme colors */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #ecebe3;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #bb5a38;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #a04d30;
        }
        </style>
        """)
        
        AuthManager.render_login_form()
        st.stop()
    
    return True
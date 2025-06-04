import urllib.parse
import streamlit as st
from datetime import datetime

def create_feedback_section():
    """Seção de feedback com envio via WhatsApp corrigido"""
    st.header("💬 Feedback")

    # Área de texto para feedback
    feedback = st.text_area(
        "Seus comentários:",
        height=100,
        placeholder="Compartilhe sua experiência, sugestões ou dúvidas sobre o sistema..."
    )

    categoria = st.selectbox(
        "Categoria do feedback:",
        ["Geral", "Bug/Erro", "Sugestão", "Dúvida", "Elogio", "Crítica"]
    )

    # Número do WhatsApp (substitua pelo seu número)
    WHATSAPP_NUMBER = "14156103695"  # Formato: código do país + DDD + número

    if feedback.strip():  # Só mostrar se há feedback digitado
        # Preparar mensagem
        mensagem_base = f"*Feedback - {categoria}*\n\n{feedback}"

        timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M")
        mensagem_base += f"\n\n_Enviado em: {timestamp}_"

        # Codificar mensagem para URL
        mensagem_codificada = urllib.parse.quote(mensagem_base)

        # Criar URL do WhatsApp
        whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={mensagem_codificada}"

        # Mostrar preview da mensagem
        with st.expander("📱 Preview da mensagem"):
            st.text(mensagem_base)

        # Link direto para WhatsApp
        st.link_button(
            "📱 Enviar via WhatsApp",
            url=whatsapp_url,
            help="Abre o WhatsApp com a mensagem pronta"
        )

    else:
        st.info("💭 Digite seu feedback acima para gerar o link do WhatsApp")

    # Seção de contato alternativo
    st.markdown("---")
    st.markdown("### 📞 Outros canais de contato:")

    st.markdown("""
            **📧 Email:**  
            jwc@cesar.school

            **📱 WhatsApp:**  
            [+1415610-3695](https://wa.me/14156103695?text=Feedback)

            **📍 Localização:**  
            Recife, Pernambuco, BR
            """)

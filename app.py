import streamlit as st
import requests

# Configuração Base da Página
st.set_page_config(page_title="WWIT - Wanna Watchit", layout="centered")

# URL da nossa API FastAPI
API_URL = "http://127.0.0.1:8000"

# --- 1. GERENCIAMENTO DE ESTADO (SPA) ---
if 'page' not in st.session_state:
    st.session_state.page = 'home' # Telas: 'home', 'resultados', 'admin'
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None

def navigate_to(page_name):
    """Função para trocar a tela atual e recarregar a interface."""
    st.session_state.page = page_name
    st.rerun()

# --- 2. MODAL DE LOGIN ---
@st.dialog("Acesso Restrito")
def modal_login():
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Acessar", use_container_width=True):
        if usuario and senha:
            # Envia requisição para a rota de login da API
            resposta = requests.post(f"{API_URL}/login", data={"username": usuario, "password": senha})
            
            if resposta.status_code == 200:
                dados = resposta.json()
                st.session_state.token = dados["access_token"]
                st.session_state.username = usuario
                st.success("Login efetuado com sucesso!")
                st.rerun() # Recarrega a página para atualizar a barra superior
            else:
                st.error("Usuário ou senha incorretos.")
        else:
            st.warning("Preencha todos os campos.")

# --- 3. BARRA DE NAVEGAÇÃO SUPERIOR ---
col1, col2, col3 = st.columns([1, 2, 1], vertical_alignment="center")
with col1:
    if st.button("🏠︎ WWIT", use_container_width=True):
        navigate_to('home')
with col2:
    st.markdown("<h3 style='text-align: center; margin: 0;'>Wanna Watchit</h3>", unsafe_allow_html=True)
with col3:
    if st.session_state.token:
        # Se estiver logado, exibe botão de Sair
        if st.button(f"Sair ({st.session_state.username})", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            navigate_to('home')
    else:
        # Se for visitante, exibe botão de Login
        if st.button("Login", use_container_width=True):
            modal_login()

st.divider()

# --- 4. ROTEAMENTO DE TELAS (SINGLE-PAGE) ---

if st.session_state.page == 'home':
    # --- TELA INICIAL (BUSCA) ---
    st.markdown("<h5 style='text-align: center; color: #bbbbbb;'>O que vamos assistir hoje?</h5>", unsafe_allow_html=True)
    
    # Campo de busca
    busca = st.text_input("Busca", placeholder="Exemplo: Interestelar", label_visibility="collapsed")
    
    # Botões de Ação
    # Se o admin estiver logado, criamos 3 colunas. Se não, 2 colunas.
    if st.session_state.token:
        b1, b2, b3 = st.columns(3)
        with b3:
            if st.button("Restrito", type="primary", use_container_width=True):
                navigate_to('admin')
    else:
        # Colunas com espaçadores laterais para centralizar os 2 botões
        _, b1, b2, _ = st.columns([1, 2, 2, 1])
        
    with b1:
        if st.button("🔍 Buscar", use_container_width=True):
            st.info("A conexão com a rota /obras/buscar será feita na próxima etapa!")
    with b2:
        if st.button("Lista Completa", use_container_width=True):
            st.info("A conexão com a rota /obras será feita na próxima etapa!")

elif st.session_state.page == 'admin':
    # --- TELA RESTRITA (CRUD) ---
    if not st.session_state.token:
        st.error("Acesso negado.")
        if st.button("Voltar"):
            navigate_to('home')
    else:
        st.subheader("Painel Administrativo")
        st.info("Formulários de CRUD serão construídos na próxima etapa.")
        if st.button("Página Inicial"):
            navigate_to('home')
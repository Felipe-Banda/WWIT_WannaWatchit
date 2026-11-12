import streamlit as st
import requests

# Configuração Base da Página
st.set_page_config(page_title="WWIT - Wanna Watchit", layout="centered")

# URL da nossa API FastAPI
API_URL = "http://127.0.0.1:8000"

# --- 1. GERENCIAMENTO DE ESTADO (SPA) ---
if 'resultados' not in st.session_state:
    st.session_state.resultados = []
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
    if st.button("WWIT 🏠︎", type="tertiary"):
        navigate_to('home')
with col2:
    st.markdown("<h3 style='text-align: center; margin: 0;'>Wanna Watchit</h3>", unsafe_allow_html=True)
with col3:
    # Subdivisão: a primeira coluna fica vazia (empurrando), a segunda recebe o botão
    espacador, col_botao = st.columns([1, 1.5])
    
    with col_botao:
        if st.session_state.token:
            # Se estiver logado, exibe botão de Sair
            if st.button(f"Sair", use_container_width=True):
                st.session_state.token = None
                st.session_state.username = None
                navigate_to('home')
        else:
            # Se for visitante, exibe botão de Login
            if st.button("Login", type="primary", use_container_width=True):
                modal_login()

st.divider()

# --- 4. ROTEAMENTO DE TELAS (SINGLE-PAGE) ---

if st.session_state.page == 'home':
    # --- TELA INICIAL (BUSCA) ---
    st.markdown("<h5 style='text-align: center; color: #bbbbbb;'>O que vamos assistir hoje?</h5>", unsafe_allow_html=True)
    
    # Campo de busca
    busca = st.text_input("Busca", placeholder="Exemplo: Interestelar", label_visibility="collapsed")
    
    # Botões de Ação
    if st.session_state.token:
        # VISÃO ADMIN (3 botões)
        _, b1, b2, b3, _ = st.columns([1, 1, 1, 1, 1])
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        
        with b1:
            if st.button("🔍 Buscar"):
                if busca:
                    resposta = requests.get(f"{API_URL}/admin/obras/buscar", params={"titulo": busca}, headers=headers)
                    if resposta.status_code == 200:
                        st.session_state.resultados = resposta.json()
                        navigate_to('resultados')
                    else:
                        st.warning("Nenhuma obra encontrada para esta busca.")
                else:
                    st.warning("Digite um termo para buscar.")
        with b2:
            if st.button("Lista Completa"):
                resposta = requests.get(f"{API_URL}/admin/obras", headers=headers)
                if resposta.status_code == 200:
                    st.session_state.resultados = resposta.json()
                    navigate_to('resultados')
                else:
                    st.error("Falha ao carregar as obras. Verifique se a API está rodando.")
        with b3:
            if st.button("Restrito", type="primary"):
                navigate_to('admin')
    else:
        # VISÃO VISITANTE (2 botões, mesma lógica de API)
        _, b1, b2, _ = st.columns([1.5, 1, 1, 1.5])
        
        with b1:
            if st.button("🔍 Buscar"):
                if busca:
                    resposta = requests.get(f"{API_URL}/obras/buscar", params={"titulo": busca})
                    if resposta.status_code == 200:
                        st.session_state.resultados = resposta.json()
                        navigate_to('resultados')
                    else:
                        st.warning("Nenhuma obra encontrada para esta busca.")
                else:
                    st.warning("Digite um termo para buscar.")
        with b2:
            if st.button("Lista Completa"):
                resposta = requests.get(f"{API_URL}/obras")
                if resposta.status_code == 200:
                    st.session_state.resultados = resposta.json()
                    navigate_to('resultados')
                else:
                    st.error("Falha ao carregar as obras. Verifique se a API está rodando.")    

elif st.session_state.page == 'resultados':
    # --- TELA DE RESULTADOS (CARDS EXPANSÍVEIS) ---
    
    # Botão de retorno à tela de busca
    if st.button("← Voltar"):
        navigate_to('home')
        
    st.markdown("<h4 style='text-align: center; color: #bbbbbb;'>Catálogo de Obras</h4>", unsafe_allow_html=True)
    st.divider()

    if not st.session_state.resultados:
        st.info("Nenhum resultado para exibir.")
    else:
        # Cria a estrutura de grade (3 colunas)
        colunas = st.columns(3)
        
        # Itera sobre os resultados distribuindo-os nas colunas
        for index, obra_resumo in enumerate(st.session_state.resultados):
            col_atual = colunas[index % 3] # Distribui 0, 1, 2, 0, 1, 2...
            
            with col_atual:
                with st.container(border=True):
                    # Título em destaque vem do ObraSearch
                    st.markdown(f"**{obra_resumo['titulo']}**")
                    
                    # Busca os dados completos da obra pelo ID
                    id_obra = obra_resumo['id']
                    req_detalhes = requests.get(f"{API_URL}/obras/{id_obra}")
                    
                    if req_detalhes.status_code == 200:
                        obra_completa = req_detalhes.json()
                        st.caption(f"Autor(a): {obra_completa.get('autor', 'Desconhecido')} | ⭐ {obra_completa.get('nota', 'S/N')}")
                        
                        # Indicador visual de inativo para o admin
                        if st.session_state.token and not obra_completa.get('ativo'):
                            st.error("⚠️ Obra Inativa")
                            
                        with st.expander("Ler Sinopse"):
                            st.write(obra_completa.get('sinopse', 'Nenhuma sinopse cadastrada.'))
                    else:
                        st.caption("Detalhes indisponíveis no momento.")
                    
                    # Se for admin, exibe botões de atalho no rodapé do card
                    if st.session_state.token:
                        st.markdown("<br>", unsafe_allow_html=True) # Espaçamento
                        c_edit, c_status = st.columns(2)
                        with c_edit:
                            if st.button("Editar", key=f"edit_{id_obra}", use_container_width=True):
                                st.info("Integração de edição no próximo passo!")
                        with c_status:
                            if st.button("Status", key=f"status_{id_obra}", use_container_width=True):
                                st.info("Integração de inativação no próximo passo!")

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
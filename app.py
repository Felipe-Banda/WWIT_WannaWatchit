import streamlit as st
import requests
import os

# Configuração Base da Página
st.set_page_config(page_title="WWIT - Wanna Watchit", layout="centered")

# URL da nossa API FastAPI
API_URL = os.getenv('API_URL', 'http://127.0.0.1:8000')

# --- 1. GERENCIAMENTO DE ESTADO (SPA) ---
if 'from_key' not in st.session_state:
    st.session_state.form_key = 0
if 'resultados' not in st.session_state:
    st.session_state.resultados = []
if 'page' not in st.session_state:
    st.session_state.page = 'home' # Telas: 'home', 'resultados', 'admin'
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None
if 'form_data' not in st.session_state:
    st.session_state.form_data = {"titulo": "", "sinopse": "", "autor": "", "nota": 0.0}

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
        # VISÃO ADMIN (2 Linhas)
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        
        # --- LINHA 1: Buscas (Igual ao visitante) ---
        _, b1, b2, _ = st.columns([1.5, 1, 1, 1.5])
        
        with b1:
            if st.button("🔍 Buscar", use_container_width=True):
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
            if st.button("Lista Completa", use_container_width=True):
                resposta = requests.get(f"{API_URL}/admin/obras", headers=headers)
                if resposta.status_code == 200:
                    st.session_state.resultados = resposta.json()
                    navigate_to('resultados')
                else:
                    st.error("Falha ao carregar as obras. Verifique se a API está rodando.")
                    
        # --- LINHA 2: Cadastro (Largura somada de b1 + b2) ---
        _, b_cad, _ = st.columns([1.5, 2, 1.5])
        
        with b_cad:
            if st.button("Cadastrar", type="primary", use_container_width=True):
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
        resultados_ordenados = sorted(st.session_state.resultados, key = lambda x: x['titulo'].lower())
        # Cria a estrutura de grade (3 colunas)
        colunas = st.columns(3)
        
        # Itera sobre os resultados distribuindo-os nas colunas
        for index, obra_resumo in enumerate(resultados_ordenados):
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
                                st.session_state.edit_id = id_obra
                                st.session_state.form_data = {
                                    "titulo": obra_completa.get("titulo", ""),
                                    "sinopse": obra_completa.get("sinopse", ""),
                                    "autor": obra_completa.get("autor", ""),
                                    "nota": obra_completa.get("nota", 0.0)
                                }
                                navigate_to('admin')
                        with c_status:
                            label_status = 'Ativar' if not obra_completa.get('ativo') else 'Inativar'
                            
                            if st.button(label_status, key=f"status_{id_obra}", use_container_width=True):
                                headers = {'Authorization': f'Bearer {st.session_state.token}'}
                                novo_status = not obra_completa.get('ativo')
                                
                                # Consome a rota PUT de status
                                res = requests.put(f"{API_URL}/admin/obras/{id_obra}/status", json={"ativo": novo_status}, headers=headers)
                                
                                if res.status_code == 200:
                                    st.toast(f"Status atualizado com sucesso!")
                                    st.rerun()
                                else:
                                    # Isso vai fazer o erro da API aparecer em vermelho na tela do app!
                                    st.error(f"Erro {res.status_code}: {res.text}")

elif st.session_state.page == 'admin':
    # --- TELA RESTRITA (CRUD) ---
    if not st.session_state.token:
        st.error("Acesso negado.")
        if st.button("Voltar"):
            navigate_to('home')
    else:
        # Define o título da tela baseado na ação
        modo = "✏️ Editar Obra" if st.session_state.edit_id else "➕ Cadastrar Nova Obra"
        st.markdown(f"<h4 style='text-align: center;'>{modo}</h4>", unsafe_allow_html=True)
        st.divider()
        
        # Formulário preenchido com o state (vazio para novo, preenchido para edição)
        col_form1, col_form2 = st.columns([2, 1])
        with col_form1:
            titulo = st.text_input("Título", value=st.session_state.form_data["titulo"], key = f't_{st.session_state.form_key}')
            autor = st.text_input("Autor(a)", value=st.session_state.form_data["autor"], key = f'a_{st.session_state.form_key}')
        with col_form2:
            nota = st.number_input("Nota (0 a 10)", min_value=0.0, max_value=10.0, step=0.1, value=float(st.session_state.form_data["nota"]), key = f'n_{st.session_state.form_key}')
            
        sinopse = st.text_area("Sinopse", value=st.session_state.form_data["sinopse"], height=150, key = f's_{st.session_state.form_key}')
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botões de Ação do Formulário
        c1, c2, c3 = st.columns(3)
        
        with c1:
            if st.button("Limpar", use_container_width=True):
                st.session_state.form_data = {"titulo": "", "sinopse": "", "autor": "", "nota": 0.0}
                st.rerun()
                
        with c2:
            if st.button("Finalizar", type="primary", use_container_width=True):
                if not titulo:
                    st.warning("O campo Título é obrigatório!")
                else:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    payload = {"titulo": titulo, "autor": autor, "nota": nota, "sinopse": sinopse}
                    
                    if st.session_state.edit_id:
                        # Rota PUT (Atualizar)
                        res = requests.put(f"{API_URL}/admin/obras/{st.session_state.edit_id}", json=payload, headers=headers)
                        msg_sucesso = "Obra atualizada com sucesso!"
                    else:
                        # Rota POST (Criar Nova)
                        res = requests.post(f"{API_URL}/admin/obras", json=payload, headers=headers)
                        msg_sucesso = "Obra cadastrada com sucesso!"
                        
                    if res.status_code in [200, 201]:
                        # Usamos toast para a mensagem sobreviver ao recarregamento
                        st.toast(msg_sucesso)
                        # Zera o formulário após sucesso
                        st.session_state.edit_id = None
                        st.session_state.form_data = {"titulo": "", "sinopse": "", "autor": "", "nota": 0.0}
                        # Força a atualização da interface para esvaziar os campos visuais
                        navigate_to('home')
                    else:
                        st.error(f"Erro na operação: {res.json().get('detail', 'Erro desconhecido')}")
                        
        with c3:
            # Substituímos o "Página Inicial" por "Cancelar"
            if st.button("Cancelar", use_container_width=True):
                # Descobre qual era a página anterior com base na ação
                pagina_anterior = 'resultados' if st.session_state.edit_id else 'home'
                
                # Limpa o state para não vazar dados
                st.session_state.edit_id = None
                st.session_state.form_data = {"titulo": "", "sinopse": "", "autor": "", "nota": 0.0}
                
                # Retorna para o local correto
                navigate_to(pagina_anterior)

# --- 5. RODAPÉ ---
st.markdown("<br><br>", unsafe_allow_html=True) # Espaçamento para empurrar o rodapé para baixo
st.markdown(
    """
    <div style='text-align: center; color: #888888; font-size: 0.9em;'>
        Desenvolvido por <a href='https://www.linkedin.com/in/felipe-banda' target='_blank' style='color: #bbbbbb; text-decoration: none; font-weight: bold;'>Felipe Banda</a> <br>
        <em>Wanna Watchit © 2026</em>
    </div>
    """, 
    unsafe_allow_html=True
)
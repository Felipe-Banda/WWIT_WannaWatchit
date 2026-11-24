# 🎬 Wanna Watchit (WWIT)

Um sistema web completo para catalogação e gerenciamento de obras audiovisuais (filmes e séries), desenvolvido com foco em arquitetura de microsserviços, conteinerização e deploy em infraestrutura Cloud (AWS).

Este projeto foi construído para demonstrar habilidades Fullstack (Python) e práticas de DevOps, separando o frontend e o backend em contêineres independentes e orquestrados.

## 🌐 Teste online

O sistema está publicado e pode ser testado agora mesmo:

- **Aplicação (Frontend):** http://13.58.103.151:8501/
- **Documentação da API (Swagger):** http://13.58.103.151:8000/docs

> ⚠️ **Atenção: ambiente público de demonstração**
>
> Para que qualquer pessoa possa explorar a área administrativa, a rota de registro de usuários (`POST /registro`) está **aberta intencionalmente**. Isso significa que:
>
> - Qualquer visitante pode criar uma conta e cadastrar, editar ou inativar obras.
> - Os dados exibidos podem ter sido alterados por outros visitantes e podem ser modificados ou redefinidos a qualquer momento.
> - **Não utilize senhas reais ou dados pessoais** ao criar sua conta de teste.
>
> Em um ambiente de produção, o registro seria restrito (por exemplo, apenas administradores criando novos usuários, ou contas novas sem permissão de administrador).

## 🚀 Funcionalidades

O sistema possui controle de acesso com visões distintas para visitantes e administradores:

**Visão Pública (Visitantes):**
- Busca de obras ativas no catálogo.
- Listagem completa de obras disponíveis.
- Interface limpa e responsiva.

**Visão Restrita (Administradores):**
- Registro e autenticação de usuários com JWT e senhas protegidas com Bcrypt.
- CRUD Completo: Cadastro, edição e inativação (soft delete) de obras.
- Visualização de obras inativas ocultas do público.

## 🛠️ Tecnologias Utilizadas

**Frontend:**
- [Streamlit](https://streamlit.io/) - Construção rápida e reativa de interfaces em Python.
- Componentes visuais personalizados e gerenciamento de estado de sessão.

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) - Criação de APIs robustas, rápidas e tipadas.
- **SQLite** + [SQLAlchemy](https://www.sqlalchemy.org/) (ORM) - Persistência e modelagem de dados.
- Autenticação via tokens JWT.

**DevOps & Infraestrutura:**
- **Docker & Docker Compose** - Conteinerização isolada para API e Frontend.
- **AWS EC2 (Ubuntu)** - Hospedagem em nuvem utilizando instâncias virtuais.
- **Security Groups (AWS)** - Configuração de firewall e liberação de portas customizadas (8000 e 8501).

## ⚙️ Arquitetura e Deploy

O projeto foi empacotado utilizando o Docker Compose (`docker-compose.yml`), garantindo que os serviços conversem através de uma rede interna do Docker.

O deploy foi realizado em uma instância **Amazon EC2 (t2.micro)**, utilizando o sistema operacional Ubuntu. Volumes foram mapeados (`bind mounts`) para garantir a persistência do banco de dados SQLite mesmo após reinicializações do servidor.

## 💻 Como rodar o projeto localmente

**Pré-requisitos:**
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/) e Docker Compose instalados.

**Passo a passo:**

1. Clone este repositório:
```bash
git clone https://github.com/Felipe-Banda/WWIT_WannaWatchit.git
```
2. Acesse o diretório do projeto:
```bash
cd WWIT_WannaWatchit
```
3. Suba os containers utilizando o Docker Compose:
```bash
docker compose up -d --build
```
4. Acesse a aplicação no seu navegador:
   - **Frontend (Interface):** http://localhost:8501
   - **Backend (Documentação):** http://localhost:8000/docs

## 👨‍💻 Desenvolvedor
Desenvolvido por Felipe Banda
- [LinkedIn](https://linkedin.com/in/felipe-banda)
- [GitHub](https://github.com/felipe-banda)
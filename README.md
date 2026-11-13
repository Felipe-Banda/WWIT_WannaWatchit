# 🎬 Wanna Watchit (WWIT)

Um sistema web completo para catalogação e gerenciamento de obras audiovisuais (filmes e séries), desenvolvido com foco em arquitetura de microsserviços, conteinerização e deploy em infraestrutura Cloud (AWS).

Este projeto foi construído para demonstrar habilidades Fullstack (Python) e práticas de DevOps, separando o frontend e o backend em contêineres independentes e orquestrados.

## 🚀 Funcionalidades

O sistema possui controle de acesso com visões distintas para visitantes e administradores:

**Visão Pública (Visitantes):**
- Busca de obras ativas no catálogo.
- Listagem completa de obras disponíveis.
- Interface limpa e responsiva.

**Visão Restrita (Administradores):**
- Autenticação de usuário segura (JWT e Bcrypt).
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

O projeto foi empacotado utilizando `docker-compose`, garantindo que os serviços conversem através de uma rede interna do Docker. 

O deploy foi realizado em uma instância **Amazon EC2 (t2.micro)**, utilizando o sistema operacional Ubuntu. Volumes foram mapeados (`bind mounts`) para garantir a persistência do banco de dados SQLite mesmo após reinicializações do servidor.

## 💻 Como rodar o projeto localmente

**Pré-requisitos:**
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/) e Docker Compose instalados.

**Passo a passo:**

1. Clone este repositório:
```bash
git clone [https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git](https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git)
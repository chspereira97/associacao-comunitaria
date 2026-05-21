# 🏠 Sistema de Gerenciamento de Projetos para Associações Comunitárias

Trabalho da disciplina de **Engenharia de Software** — FATEC   
1º Semestre de 2026

---

## 📌 Sobre o Projeto

Sistema web desenvolvido para gerenciar uma associação comunitária (estudo de caso: **Sociedade Nova Jardim Lapenna**).  
A ONG atende crianças e jovens de 6 a 20 anos em situação de vulnerabilidade social, oferecendo:

- ⚽ Futebol
- 🥋 Judô
- 🎭 Capoeira
- 🎨 Teatro
- 📚 Reforço Escolar

---

## 🛠️ Tecnologias

| Tecnologia | Para que serve |
|------------  ---------------|
| Python 3.13 | Linguagem principal |
| Flask | Framework web |
| SQLAlchemy | ORM (banco de dados) |
| SQLite | Banco de dados |
| Flask-Login | Autenticação de usuários |
| Bootstrap 5 | Interface visual |
| Chart.js | Gráficos dos relatórios |
| Font Awesome | Ícones |

---

## 🚀 Como Rodar o Projeto

```bash
# 1. Clone o repositório
git clone https://github.com/chspereira97/associacao-comunitaria.git

# 2. Entre na pasta
cd associacao-comunitaria

# 3. Crie o ambiente virtual
python -m venv venv

# 4. Ative o ambiente virtual
# Windows:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# 5. Instale as dependências
pip install -r requirements.txt

# 6. Crie o arquivo .env com sua chave secreta
echo SECRET_KEY=sua-chave-aqui > .env
echo DATABASE_URL=sqlite:///instance/sistema.db >> .env

# 7. Rode o sistema
python run.py




📧 admin@associacao.com | 🔑 admin123

# 8. Acesse no navegador
http://localhost:5050

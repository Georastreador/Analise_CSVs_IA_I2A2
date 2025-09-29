# 🚀 Guia de Deploy - CSV Analysis AI

Este guia fornece instruções detalhadas para fazer deploy da aplicação CSV Analysis AI em diferentes plataformas.

## 📋 Pré-requisitos

- Python 3.8+
- Conta no GitHub
- APIs de IA configuradas (OpenAI, Groq, Gemini, ou Claude)

## 🌐 Deploy no GitHub

### 1. Criar Repositório no GitHub

```bash
# 1. Criar repositório no GitHub (via interface web)
# Nome sugerido: csv-analysis-ai

# 2. Inicializar git local
cd /Users/rikardocroce/Desktop/TST1/AnlCSV_V2_Git
git init

# 3. Adicionar arquivos
git add .

# 4. Commit inicial
git commit -m "feat: versão inicial do CSV Analysis AI v2.0"

# 5. Adicionar remote
git remote add origin https://github.com/SEU-USUARIO/csv-analysis-ai.git

# 6. Push inicial
git branch -M main
git push -u origin main
```

### 2. Configurar GitHub Actions

O arquivo `.github/workflows/ci.yml` já está configurado para:
- ✅ Testes automatizados
- ✅ Verificação de código
- ✅ Build do pacote
- ✅ Deploy automático

### 3. Configurar Secrets

No GitHub, vá em **Settings > Secrets and variables > Actions** e adicione:

```
PYPI_API_TOKEN=seu-token-do-pypi
```

## ☁️ Deploy no Streamlit Cloud

### 1. Preparar para Streamlit Cloud

```bash
# 1. Criar requirements.txt otimizado
echo "streamlit>=1.28.0" > requirements.txt
echo "pandas>=1.5.0" >> requirements.txt
echo "plotly>=5.15.0" >> requirements.txt
echo "crewai>=0.1.0" >> requirements.txt
echo "openai>=1.0.0" >> requirements.txt
echo "langchain>=0.1.0" >> requirements.txt
echo "langchain-openai>=0.1.0" >> requirements.txt
echo "langchain-groq>=0.3.8" >> requirements.txt
echo "langchain-google-genai>=2.1.12" >> requirements.txt
echo "langchain-anthropic>=0.3.21" >> requirements.txt
echo "fpdf>=2.5.0" >> requirements.txt
echo "python-docx>=0.8.11" >> requirements.txt
echo "scikit-learn>=1.3.0" >> requirements.txt
echo "seaborn>=0.12.0" >> requirements.txt
echo "matplotlib>=3.7.0" >> requirements.txt
echo "scipy>=1.11.0" >> requirements.txt
```

### 2. Deploy no Streamlit Cloud

1. **Acesse**: [share.streamlit.io](https://share.streamlit.io)
2. **Conecte** sua conta GitHub
3. **Selecione** o repositório `csv-analysis-ai`
4. **Configure**:
   - **Main file path**: `csv_analysis_app_v2.py`
   - **Python version**: 3.11
5. **Adicione secrets**:
   ```
   OPENAI_API_KEY=sk-...
   GROQ_API_KEY=gsk_...
   GOOGLE_API_KEY=...
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### 3. Configurar Streamlit Cloud

Crie `.streamlit/secrets.toml`:

```toml
[api_keys]
openai = "sk-..."
groq = "gsk_..."
google = "..."
anthropic = "sk-ant-..."
```

## 🐳 Deploy com Docker

### 1. Criar Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 8501

# Comando para executar
CMD ["streamlit", "run", "csv_analysis_app_v2.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. Build e Run

```bash
# Build da imagem
docker build -t csv-analysis-ai .

# Executar container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=sk-... \
  -e GROQ_API_KEY=gsk_... \
  csv-analysis-ai
```

### 3. Docker Compose

```yaml
version: '3.8'
services:
  csv-analysis-ai:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## ☁️ Deploy no Heroku

### 1. Preparar para Heroku

```bash
# 1. Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Criar app
heroku create csv-analysis-ai

# 4. Configurar variáveis
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set GROQ_API_KEY=gsk_...
heroku config:set GOOGLE_API_KEY=...
heroku config:set ANTHROPIC_API_KEY=sk-ant-...

# 5. Deploy
git push heroku main
```

### 2. Procfile

```
web: streamlit run csv_analysis_app_v2.py --server.port=$PORT --server.address=0.0.0.0
```

## 🔧 Deploy no VPS/Servidor

### 1. Preparar Servidor

```bash
# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# 3. Instalar Nginx
sudo apt install nginx -y

# 4. Configurar firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Deploy da Aplicação

```bash
# 1. Clonar repositório
git clone https://github.com/SEU-USUARIO/csv-analysis-ai.git
cd csv-analysis-ai

# 2. Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
export OPENAI_API_KEY=sk-...
export GROQ_API_KEY=gsk_...
export GOOGLE_API_KEY=...
export ANTHROPIC_API_KEY=sk-ant-...

# 5. Executar aplicação
streamlit run csv_analysis_app_v2.py --server.port=8501
```

### 3. Configurar Nginx

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔒 Configuração de Segurança

### 1. Variáveis de Ambiente

```bash
# Nunca commite API keys no código
echo "*.env" >> .gitignore
echo "secrets.json" >> .gitignore
```

### 2. Configuração de Produção

```python
# config.py
import os

class Config:
    # APIs
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    # App
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Upload
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 200)) * 1024 * 1024  # MB
```

## 📊 Monitoramento

### 1. Logs

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Métricas

```python
import psutil
import streamlit as st

# Mostrar métricas do sistema
@st.cache_data
def get_system_metrics():
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent
    }
```

## 🚀 Checklist de Deploy

### Antes do Deploy
- [ ] ✅ Código testado localmente
- [ ] ✅ Testes automatizados passando
- [ ] ✅ Documentação atualizada
- [ ] ✅ API keys configuradas
- [ ] ✅ Variáveis de ambiente definidas
- [ ] ✅ Arquivos sensíveis no .gitignore

### Durante o Deploy
- [ ] ✅ Build sem erros
- [ ] ✅ Dependências instaladas
- [ ] ✅ Aplicação iniciando
- [ ] ✅ Portas configuradas
- [ ] ✅ SSL/HTTPS configurado

### Após o Deploy
- [ ] ✅ Aplicação acessível
- [ ] ✅ Upload de arquivos funcionando
- [ ] ✅ APIs de IA respondendo
- [ ] ✅ Relatórios sendo gerados
- [ ] ✅ Logs sendo coletados
- [ ] ✅ Monitoramento ativo

## 🆘 Troubleshooting

### Problemas Comuns

1. **Erro de API Key**
   ```
   Solução: Verificar se as variáveis de ambiente estão configuradas
   ```

2. **Erro de Dependências**
   ```
   Solução: Verificar requirements.txt e versões do Python
   ```

3. **Erro de Porta**
   ```
   Solução: Verificar se a porta está disponível e configurada
   ```

4. **Erro de Upload**
   ```
   Solução: Verificar permissões e tamanho máximo de arquivo
   ```

### Logs Úteis

```bash
# Streamlit logs
streamlit run app.py --logger.level=debug

# Docker logs
docker logs container-name

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

---

**🎉 Deploy realizado com sucesso!**

Para mais informações, consulte a [documentação completa](README.md) ou abra uma [issue](https://github.com/SEU-USUARIO/csv-analysis-ai/issues).

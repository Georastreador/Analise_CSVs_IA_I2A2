# 🤖 CSV Analysis AI - Sistema de Análise Inteligente de Dados

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![CrewAI](https://img.shields.io/badge/CrewAI-Latest-green.svg)](https://crewai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Visão Geral

O **CSV Analysis AI** é uma aplicação web avançada que utiliza inteligência artificial para análise automática de dados CSV. O sistema combina agentes especializados CrewAI com múltiplas APIs de IA para fornecer insights profundos e interativos sobre seus dados.

## ✨ Funcionalidades Principais

### 💬 Chat Inteligente com IA
- **Conversação natural** com dados em linguagem simples
- **Múltiplas APIs** suportadas (OpenAI, Groq, Gemini, Claude)
- **Respostas específicas** para cada dataset
- **Geração automática** de gráficos e visualizações

### 🤖 Agentes CrewAI Especializados
- **Data Validator** - Validação e integridade dos dados
- **Data Profiler** - Perfilamento e estatísticas descritivas
- **Pattern Detective** - Detecção de padrões e tendências
- **Anomaly Hunter** - Identificação de anomalias e outliers
- **Relationship Analyst** - Análise de correlações e relacionamentos
- **Strategic Synthesizer** - Síntese estratégica e recomendações

### 📊 Visualizações Avançadas
- **Gráficos interativos** com Plotly
- **Análises estatísticas** automatizadas
- **Detecção de outliers** e anomalias
- **Correlações** entre variáveis

### 📄 Relatórios Automáticos
- **PDF** com análises completas
- **Markdown** com conversação incluída
- **JSON** para exportação de dados
- **Download** de conversações completas

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/csv-analysis-ai.git
cd csv-analysis-ai
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as APIs de IA
Configure pelo menos uma das seguintes APIs na interface:

- **OpenAI**: [Obter chave API](https://platform.openai.com/api-keys)
- **Groq**: [Obter chave API](https://console.groq.com/keys)
- **Google Gemini**: [Obter chave API](https://makersuite.google.com/app/apikey)
- **Anthropic Claude**: [Obter chave API](https://console.anthropic.com/)

### 4. Execute a Aplicação
```bash
streamlit run csv_analysis_app_v2.py
```

### 5. Acesse a Aplicação
Abra seu navegador em: `http://localhost:8501`

## 📖 Como Usar

### 1. Carregar Dados
- Arraste e solte seu arquivo CSV na interface
- Ou use o botão "Browse files" para selecionar

### 2. Configurar API
- Selecione seu provedor de IA na sidebar
- Insira sua chave de API
- Teste a conexão

### 3. Executar Análise CrewAI
- Clique em "🚀 Executar Análise CrewAI"
- Aguarde os agentes processarem os dados

### 4. Interagir com os Dados
- Use o **Chat IA** para fazer perguntas
- Consulte as **Conclusões** dos agentes
- Explore o **Overview** dos dados
- Visualize **Gráficos** avançados

### 5. Exportar Resultados
- Gere **relatórios PDF** ou **Markdown**
- Baixe **conversações em JSON**
- Exporte insights e análises

## 🏗️ Arquitetura

### Componentes Principais
```
csv_analysis_app_v2.py     # Aplicação principal Streamlit
├── chat_ai_enhanced.py    # Sistema de chat com IA
├── crewai_enhanced.py     # Orquestração dos agentes CrewAI
├── analysis_memory.py     # Sistema de persistência
├── data_manager.py        # Gerenciamento de dados CSV
└── Relatorios_appCSV/     # Gerador de relatórios
```

### Fluxo de Dados
1. **Upload** → Carregamento do CSV
2. **Análise** → Processamento pelos agentes CrewAI
3. **Chat** → Interação com IA para insights
4. **Visualização** → Gráficos e análises
5. **Exportação** → Relatórios e downloads

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```bash
# OpenAI
export OPENAI_API_KEY="sua-chave-aqui"

# Groq
export GROQ_API_KEY="sua-chave-aqui"

# Google Gemini
export GOOGLE_API_KEY="sua-chave-aqui"

# Anthropic Claude
export ANTHROPIC_API_KEY="sua-chave-aqui"
```

### Personalização
- Modifique `crewai_agents.py` para ajustar agentes
- Edite `chat_ai_enhanced.py` para personalizar respostas
- Configure `analysis_memory.py` para persistência

## 📊 Tipos de Dados Suportados

### Formatos
- ✅ **CSV** (Comma Separated Values)
- ✅ **Arquivos grandes** (até 200MB+)
- ✅ **Diferentes codificações** (UTF-8, Latin-1, etc.)

### Estruturas
- ✅ **Dados numéricos** (int, float)
- ✅ **Dados categóricos** (string, object)
- ✅ **Dados temporais** (datetime)
- ✅ **Dados geográficos** (lat/lng)

### Tamanhos
- ✅ **Pequenos** (até 1K registros)
- ✅ **Médios** (1K - 100K registros)
- ✅ **Grandes** (100K+ registros)

## 🧪 Testes

### Executar Testes
```bash
# Testes automatizados
python test_automated.py

# Testes de funcionalidades
python test_enhanced_features.py
```

### Testes de Compatibilidade
- ✅ Múltiplos formatos de CSV
- ✅ Diferentes tamanhos de arquivo
- ✅ Várias APIs de IA
- ✅ Interface responsiva

## 🤝 Contribuição

### Como Contribuir
1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

### Diretrizes
- Siga o padrão de código Python (PEP 8)
- Adicione testes para novas funcionalidades
- Documente mudanças no README
- Mantenha compatibilidade com versões anteriores

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

### Problemas Conhecidos
- **Arquivos muito grandes**: Use amostragem para melhor performance
- **APIs limitadas**: Configure múltiplas APIs para fallback
- **Memória**: Monitore uso de RAM com datasets grandes

### Obter Ajuda
- 📧 **Email**: ursodecasaco@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/georastreeador/csv-analysis-ai/issues)
- 📖 **Documentação**: [Wiki do Projeto](https://github.com/georastreador/csv-analysis-ai/wiki)

## 🎯 Roadmap

### Próximas Versões
- [ ] **v2.1**: Suporte a mais formatos (Excel, JSON, Parquet)
- [ ] **v2.2**: Integração com bancos de dados
- [ ] **v2.3**: API REST para integração
- [ ] **v2.4**: Dashboard em tempo real
- [ ] **v2.5**: Machine Learning automático

### Funcionalidades Planejadas
- [ ] **Análise preditiva** com ML
- [ ] **Visualizações 3D** avançadas
- [ ] **Integração com BI** (Power BI, Tableau)
- [ ] **Colaboração** em tempo real
- [ ] **Templates** de análise personalizados

## 🙏 Agradecimentos

- **CrewAI** - Framework de agentes de IA
- **Streamlit** - Framework web para Python
- **OpenAI, Groq, Google, Anthropic** - APIs de IA
- **Plotly** - Visualizações interativas
- **Pandas** - Manipulação de dados

---

**Desenvolvido com ❤️ para democratizar a análise de dados**

⭐ **Se este projeto foi útil, considere dar uma estrela!**

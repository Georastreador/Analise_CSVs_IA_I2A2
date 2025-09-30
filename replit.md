# CSV Analysis AI - Replit Project Documentation

## Project Overview
**CSV Analysis AI** is an advanced Streamlit web application that uses artificial intelligence for automatic CSV data analysis. The system combines specialized CrewAI agents with multiple AI APIs to provide deep and interactive insights about data.

### Purpose
- Intelligent CSV data analysis using AI agents
- Natural language chat interface for data exploration
- Automated visualizations and reports generation
- Support for multiple AI providers (OpenAI, Groq, Gemini, Claude, Perplexity)

### Current State
✅ **Fully functional and ready to use**
- Python 3.11 installed
- All dependencies installed via pip
- Streamlit configured for Replit environment
- Workflow running on port 5000
- Deployment configured for autoscale

## Recent Changes
**Date: 2025-09-30**
- ✅ Installed Python 3.11 and all dependencies
- ✅ Created Streamlit configuration (.streamlit/config.toml) for Replit
- ✅ Configured workflow to run Streamlit on port 5000 with 0.0.0.0 binding
- ✅ Set up deployment configuration for autoscale
- ✅ Verified application runs successfully

## Project Architecture

### Main Application
- **csv_analysis_app_v2.py** - Main Streamlit application with modern UI
- **Port**: 5000 (frontend on 0.0.0.0)
- **Framework**: Streamlit 1.50.0

### Core Components
```
csv_analysis_app_v2.py     # Main Streamlit application
├── chat_ai_enhanced.py    # Enhanced AI chat system
├── crewai_enhanced.py     # CrewAI agents orchestration
├── analysis_memory.py     # Persistence system
├── data_manager.py        # CSV data management
├── cache_system.py        # Caching system
├── chart_generator.py     # Chart generation
└── Relatorios_appCSV/     # Report generator module
```

### AI Agents (CrewAI)
1. **Data Validator** - Data validation and integrity
2. **Data Profiler** - Profiling and descriptive statistics
3. **Pattern Detective** - Pattern and trend detection
4. **Anomaly Hunter** - Anomaly and outlier identification
5. **Relationship Analyst** - Correlation analysis
6. **Strategic Synthesizer** - Strategic synthesis and recommendations

### Supported AI Providers
- OpenAI (GPT models)
- Groq (fast inference)
- Google Gemini
- Anthropic Claude
- Perplexity

## Technical Configuration

### Environment Setup
- **Python Version**: 3.11
- **Package Manager**: pip
- **Virtual Environment**: Replit managed (.pythonlibs)

### Streamlit Configuration
Location: `.streamlit/config.toml`
```toml
[server]
headless = true
port = 5000
enableCORS = false
enableXsrfProtection = false
address = "0.0.0.0"
```

### Workflow
- **Name**: CSV Analysis AI
- **Command**: `streamlit run csv_analysis_app_v2.py --server.port=5000 --server.address=0.0.0.0`
- **Port**: 5000
- **Output**: webview

### Deployment
- **Target**: autoscale (stateless web app)
- **Run Command**: streamlit with port 5000 and 0.0.0.0 binding
- **Suitable for**: Interactive data analysis web application

## Key Features

### 💬 Intelligent AI Chat
- Natural language conversation with data
- Support for multiple AI APIs
- Context-aware responses
- Automatic graph generation

### 🤖 CrewAI Specialized Agents
- Six specialized agents for comprehensive analysis
- Automated data validation and profiling
- Pattern and anomaly detection
- Relationship and correlation analysis

### 📊 Advanced Visualizations
- Interactive charts with Plotly
- Automated statistical analysis
- Outlier and anomaly detection
- Correlation matrices

### 📄 Automatic Reports
- PDF reports with complete analysis
- Markdown with included conversation
- JSON for data export
- Download complete conversations

## User Instructions

### How to Use
1. **Upload CSV**: Drag and drop or browse for CSV file (up to 200MB)
2. **Configure API**: 
   - Select AI provider in sidebar (OpenAI, Groq, Gemini, Claude, or Perplexity)
   - Enter API key
   - Test connection
3. **Run Analysis**: Click "🚀 Executar Análise CrewAI" to start agent analysis
4. **Interact**: Use AI chat to ask questions about data
5. **Export**: Generate PDF/Markdown reports or download conversations

### API Keys Required
Users need to provide their own API keys for at least one provider:
- OpenAI: https://platform.openai.com/api-keys
- Groq: https://console.groq.com/keys
- Google Gemini: https://makersuite.google.com/app/apikey
- Anthropic Claude: https://console.anthropic.com/

## Dependencies

### Main Libraries
- streamlit==1.50.0 - Web framework
- pandas==2.3.2 - Data manipulation
- plotly==6.3.0 - Interactive visualizations
- crewai==0.193.2 - AI agents framework
- langchain==0.3.27 - LLM orchestration
- openai==1.109.1 - OpenAI API
- groq==0.31.1 - Groq API

### Full Dependencies
See `requirements.txt` for complete list

## File Structure

### Application Files
- `csv_analysis_app_v2.py` - Main application
- `chat_ai_enhanced.py` - Chat system
- `crewai_enhanced.py` - CrewAI integration
- `analysis_memory.py` - Memory/persistence
- `data_manager.py` - Data management
- `cache_system.py` - Caching
- `chart_generator.py` - Visualizations
- `visualization_enhanced.py` - Enhanced visualizations

### Configuration
- `.streamlit/config.toml` - Streamlit config
- `requirements.txt` - Python dependencies
- `setup.py` - Package setup

### Documentation
- `README.md` - Project overview
- `DEPLOY.md` - Deployment guide
- `CHANGELOG.md` - Change history
- `Relatorios_appCSV/` - Report documentation

### Examples
- `examples/example_usage.py` - Usage examples

## Development Notes

### Architecture Decisions
- **Date**: 2025-09-30
- Using Streamlit for rapid web development
- CrewAI for multi-agent AI analysis
- Multiple AI provider support for flexibility
- Stateless design suitable for autoscale deployment

### Known Issues
- Minor browser console warning about password field not in form (cosmetic only)
- Large files (>200MB) may need sampling for performance

### Future Enhancements (from README)
- Support for more formats (Excel, JSON, Parquet)
- Database integration
- REST API
- Real-time dashboard
- Automatic machine learning

## User Preferences
(To be updated as user preferences are expressed)

## Troubleshooting

### Common Issues
1. **App not loading**: Check workflow is running, verify port 5000 is accessible
2. **API errors**: Verify API key is valid and has sufficient credits
3. **Large file issues**: Consider using data sampling for files >100MB
4. **Import errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`

### Logs Location
- Workflow logs: `/tmp/logs/CSV_Analysis_AI_*.log`
- Check with refresh_all_logs tool

## Links
- Original repo structure preserved from GitHub import
- License: MIT (see LICENSE file)
- Language: Portuguese (Brazilian) UI with English code

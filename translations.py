# Sistema de Traduções - ROC CSV Analysis AI

TRANSLATIONS = {
    "pt": {
        # Configuração da página
        "page_title": "ROC CSV Analysis AI",
        "page_subtitle": "Análise inteligente de dados com agentes de IA",
        
        # Sidebar
        "sidebar_config": "⚙️ Configurações",
        "sidebar_language": "🌐 Idioma",
        "sidebar_ai_provider": "🔑 Provedor de IA",
        "sidebar_api_key": "Chave da API",
        "sidebar_api_key_help": "Insira sua chave de API",
        "sidebar_test_api": "🧪 Testar API",
        "sidebar_testing": "Testando...",
        "sidebar_api_working": "✅ API funcionando!",
        "sidebar_api_error": "❌ Erro ao testar API:",
        "sidebar_api_not_configured": "⚠️ Configure uma API key primeiro",
        
        "sidebar_files": "📁 Arquivos",
        "sidebar_upload_csv": "Carregar CSV",
        "sidebar_drag_drop": "Drag and drop files here",
        "sidebar_file_limit": "Limit 200MB per file • CSV",
        "sidebar_browse_files": "Browse files",
        
        "sidebar_analysis": "📊 Análise",
        "sidebar_analysis_name": "Nome da análise:",
        "sidebar_generate_reports": "📄 Gerar Relatórios",
        "sidebar_pdf_report": "📑 Relatório PDF",
        "sidebar_markdown_report": "📝 Relatório Markdown",
        
        # Mensagens de erro
        "error_configure_api": "❌ Configure uma API key na sidebar primeiro!",
        "error_no_openai": "Biblioteca OpenAI não instalada",
        "error_no_groq": "Biblioteca Groq não instalada",
        "error_no_gemini": "Biblioteca Gemini não instalada",
        "error_no_claude": "Biblioteca Claude não instalada",
        
        # Menu principal
        "menu_chat": "💬 Chat IA",
        "menu_conclusions": "🎯 Conclusões",
        "menu_overview": "📊 Overview",
        "menu_visualizations": "📈 Visualizações",
        
        # Chat
        "chat_title": "💬 Chat com IA",
        "chat_execute_crewai": "🚀 Executar Análise CrewAI",
        "chat_executing": "Executando análise com agentes CrewAI...",
        "chat_provider": "Provedor:",
        "chat_crewai_complete": "✅ Análise CrewAI concluída!",
        "chat_crewai_info": "Agora você pode fazer perguntas sobre os insights dos agentes.",
        "chat_api_configured": "✅ {provider} configurado",
        "chat_api_not_configured": "⚠️ API não configurada",
        "chat_suggestions_title": "💡 Sugestões de Perguntas:",
        "chat_input_placeholder": "Ex: Quais são os tipos de dados das colunas?",
        "chat_response_title": "🤖 Resposta:",
        "chat_download_conversation": "📥 Download da Conversação",
        "chat_conversation_messages": "💬 Conversação com {count} mensagens",
        "chat_clear_conversation": "🗑️ Limpar Conversação",
        
        # Sugestões de perguntas
        "suggestion_1": "Quais são os tipos de dados das colunas?",
        "suggestion_2": "Quantos registros existem no dataset?",
        "suggestion_3": "Quais colunas têm valores ausentes?",
        "suggestion_4": "Mostre a distribuição da coluna [nome_da_coluna]",
        "suggestion_5": "Quais são os valores únicos em [coluna_categórica]?",
        "suggestion_6": "Calcule estatísticas descritivas das colunas numéricas",
        "suggestion_7": "Identifique possíveis outliers nos dados",
        "suggestion_8": "Mostre a correlação entre variáveis numéricas",
        "suggestion_9": "Qual é a tendência temporal dos dados?",
        "suggestion_10": "Resuma os principais insights dos dados",
        
        # Conclusões
        "conclusions_title": "🎯 Conclusões dos Agentes CrewAI",
        "conclusions_clear_history": "🗑️ Limpar Histórico",
        "conclusions_history_cleared": "✅ Histórico de análises limpo!",
        "conclusions_no_analysis": "📋 Nenhuma análise CrewAI disponível. Execute uma análise primeiro.",
        "conclusions_current_analysis": "📊 Análise Atual:",
        "conclusions_date": "Data:",
        "conclusions_dataset": "Dataset analisado:",
        "conclusions_columns_analyzed": "📋 Colunas Analisadas",
        "conclusions_agent_results": "🤖 Conclusões dos Agentes",
        "conclusions_old_format": "⚠️ Formato de resultados desatualizado. Execute uma nova análise.",
        "conclusions_no_results": "⚠️ Nenhum resultado encontrado nesta análise.",
        "conclusions_view_previous": "📚 Ver Análises Anteriores",
        "conclusions_no_previous": "Nenhuma análise anterior disponível.",
        "conclusions_select_previous": "Selecione uma análise anterior:",
        
        # Overview
        "overview_title": "📊 Visão Geral dos Dados",
        "overview_load_csv": "📁 Carregue um arquivo CSV para ver a visão geral",
        "overview_records": "📊 Registros",
        "overview_columns": "📋 Colunas",
        "overview_missing": "⚠️ Valores Faltantes",
        "overview_duplicates": "🔄 Duplicatas",
        "overview_data_types": "📈 Distribuição dos Tipos de Dados",
        "overview_profiling": "🔍 Perfilamento dos Dados",
        "overview_correlation": "📊 Matriz de Correlação",
        "overview_correlation_title": "Matriz de Correlação entre Variáveis Numéricas",
        "overview_numeric_cols": "📊 Colunas Numéricas",
        "overview_categorical_cols": "📋 Colunas Categóricas",
        "overview_no_numeric": "Nenhuma coluna numérica encontrada",
        "overview_no_categorical": "Nenhuma coluna categórica encontrada",
        "overview_data_quality": "📋 Qualidade dos Dados",
        "overview_completeness": "✅ Completude",
        "overview_uniqueness": "🔄 Unicidade",
        "overview_numeric_percent": "📊 % Numéricas",
        "overview_mean": "Média:",
        "overview_median": "Mediana:",
        "overview_std": "Desvio Padrão:",
        "overview_min_max": "Min: {min} | Max: {max}",
        "overview_unique_values": "Valores únicos:",
        "overview_most_common": "Mais comum:",
        "overview_missing_values": "Valores faltantes:",
        
        # Visualizações
        "viz_title": "📈 Visualizações Avançadas",
        
        # Tela inicial
        "welcome_title": "🎯 Bem-vindo ao ROC CSV Analysis AI",
        "welcome_description": "Esta é uma ferramenta de análise de dados com inteligência artificial que permite:",
        "welcome_feature_1": "💬 <strong>Chat com Agentes IA:</strong> Faça perguntas sobre seus dados em linguagem natural",
        "welcome_feature_2": "🎯 <strong>Conclusões dos Agentes:</strong> Consulte insights e descobertas dos agentes CrewAI",
        "welcome_feature_3": "📊 <strong>Overview Inteligente:</strong> Visualização clara e objetiva dos seus dados",
        "welcome_feature_4": "📈 <strong>Visualizações Avançadas:</strong> Gráficos e análises visuais dos dados",
        "welcome_feature_5": "📄 <strong>Relatórios Automáticos:</strong> Geração de relatórios em PDF e Markdown",
        "welcome_start": "<strong>Para começar:</strong> Carregue um arquivo CSV na barra lateral e comece a conversar com nossos agentes de IA!",
        
        # Agentes
        "agent_data_validator": "🔍 Data Validator",
        "agent_data_profiler": "📊 Data Profiler",
        "agent_pattern_detective": "🎯 Pattern Detective",
        "agent_anomaly_hunter": "⚠️ Anomaly Hunter",
        "agent_relationship_analyst": "🔗 Relationship Analyst",
        "agent_strategic_synthesizer": "💡 Strategic Synthesizer",
        "agent_complete_analysis": "📋 Complete Analysis",
    },
    
    "en": {
        # Page configuration
        "page_title": "ROC CSV Analysis AI",
        "page_subtitle": "Intelligent data analysis with AI agents",
        
        # Sidebar
        "sidebar_config": "⚙️ Settings",
        "sidebar_language": "🌐 Language",
        "sidebar_ai_provider": "🔑 AI Provider",
        "sidebar_api_key": "API Key",
        "sidebar_api_key_help": "Enter your API key",
        "sidebar_test_api": "🧪 Test API",
        "sidebar_testing": "Testing...",
        "sidebar_api_working": "✅ API working!",
        "sidebar_api_error": "❌ Error testing API:",
        "sidebar_api_not_configured": "⚠️ Configure an API key first",
        
        "sidebar_files": "📁 Files",
        "sidebar_upload_csv": "Upload CSV",
        "sidebar_drag_drop": "Drag and drop files here",
        "sidebar_file_limit": "Limit 200MB per file • CSV",
        "sidebar_browse_files": "Browse files",
        
        "sidebar_analysis": "📊 Analysis",
        "sidebar_analysis_name": "Analysis name:",
        "sidebar_generate_reports": "📄 Generate Reports",
        "sidebar_pdf_report": "📑 PDF Report",
        "sidebar_markdown_report": "📝 Markdown Report",
        
        # Error messages
        "error_configure_api": "❌ Configure an API key in the sidebar first!",
        "error_no_openai": "OpenAI library not installed",
        "error_no_groq": "Groq library not installed",
        "error_no_gemini": "Gemini library not installed",
        "error_no_claude": "Claude library not installed",
        
        # Main menu
        "menu_chat": "💬 AI Chat",
        "menu_conclusions": "🎯 Conclusions",
        "menu_overview": "📊 Overview",
        "menu_visualizations": "📈 Visualizations",
        
        # Chat
        "chat_title": "💬 AI Chat",
        "chat_execute_crewai": "🚀 Run CrewAI Analysis",
        "chat_executing": "Running analysis with CrewAI agents...",
        "chat_provider": "Provider:",
        "chat_crewai_complete": "✅ CrewAI analysis complete!",
        "chat_crewai_info": "Now you can ask questions about the agents' insights.",
        "chat_api_configured": "✅ {provider} configured",
        "chat_api_not_configured": "⚠️ API not configured",
        "chat_suggestions_title": "💡 Question Suggestions:",
        "chat_input_placeholder": "Ex: What are the data types of the columns?",
        "chat_response_title": "🤖 Response:",
        "chat_download_conversation": "📥 Download Conversation",
        "chat_conversation_messages": "💬 Conversation with {count} messages",
        "chat_clear_conversation": "🗑️ Clear Conversation",
        
        # Question suggestions
        "suggestion_1": "What are the data types of the columns?",
        "suggestion_2": "How many records are in the dataset?",
        "suggestion_3": "Which columns have missing values?",
        "suggestion_4": "Show the distribution of column [column_name]",
        "suggestion_5": "What are the unique values in [categorical_column]?",
        "suggestion_6": "Calculate descriptive statistics for numeric columns",
        "suggestion_7": "Identify possible outliers in the data",
        "suggestion_8": "Show the correlation between numeric variables",
        "suggestion_9": "What is the temporal trend of the data?",
        "suggestion_10": "Summarize the main insights from the data",
        
        # Conclusions
        "conclusions_title": "🎯 CrewAI Agent Conclusions",
        "conclusions_clear_history": "🗑️ Clear History",
        "conclusions_history_cleared": "✅ Analysis history cleared!",
        "conclusions_no_analysis": "📋 No CrewAI analysis available. Run an analysis first.",
        "conclusions_current_analysis": "📊 Current Analysis:",
        "conclusions_date": "Date:",
        "conclusions_dataset": "Dataset analyzed:",
        "conclusions_columns_analyzed": "📋 Columns Analyzed",
        "conclusions_agent_results": "🤖 Agent Conclusions",
        "conclusions_old_format": "⚠️ Outdated results format. Run a new analysis.",
        "conclusions_no_results": "⚠️ No results found in this analysis.",
        "conclusions_view_previous": "📚 View Previous Analyses",
        "conclusions_no_previous": "No previous analysis available.",
        "conclusions_select_previous": "Select a previous analysis:",
        
        # Overview
        "overview_title": "📊 Data Overview",
        "overview_load_csv": "📁 Load a CSV file to see the overview",
        "overview_records": "📊 Records",
        "overview_columns": "📋 Columns",
        "overview_missing": "⚠️ Missing Values",
        "overview_duplicates": "🔄 Duplicates",
        "overview_data_types": "📈 Data Types Distribution",
        "overview_profiling": "🔍 Data Profiling",
        "overview_correlation": "📊 Correlation Matrix",
        "overview_correlation_title": "Correlation Matrix between Numeric Variables",
        "overview_numeric_cols": "📊 Numeric Columns",
        "overview_categorical_cols": "📋 Categorical Columns",
        "overview_no_numeric": "No numeric columns found",
        "overview_no_categorical": "No categorical columns found",
        "overview_data_quality": "📋 Data Quality",
        "overview_completeness": "✅ Completeness",
        "overview_uniqueness": "🔄 Uniqueness",
        "overview_numeric_percent": "📊 % Numeric",
        "overview_mean": "Mean:",
        "overview_median": "Median:",
        "overview_std": "Std Dev:",
        "overview_min_max": "Min: {min} | Max: {max}",
        "overview_unique_values": "Unique values:",
        "overview_most_common": "Most common:",
        "overview_missing_values": "Missing values:",
        
        # Visualizations
        "viz_title": "📈 Advanced Visualizations",
        
        # Welcome screen
        "welcome_title": "🎯 Welcome to ROC CSV Analysis AI",
        "welcome_description": "This is an artificial intelligence data analysis tool that allows:",
        "welcome_feature_1": "💬 <strong>AI Agent Chat:</strong> Ask questions about your data in natural language",
        "welcome_feature_2": "🎯 <strong>Agent Conclusions:</strong> Consult insights and discoveries from CrewAI agents",
        "welcome_feature_3": "📊 <strong>Intelligent Overview:</strong> Clear and objective visualization of your data",
        "welcome_feature_4": "📈 <strong>Advanced Visualizations:</strong> Graphs and visual analysis of data",
        "welcome_feature_5": "📄 <strong>Automatic Reports:</strong> Generate reports in PDF and Markdown",
        "welcome_start": "<strong>To get started:</strong> Load a CSV file in the sidebar and start chatting with our AI agents!",
        
        # Agents
        "agent_data_validator": "🔍 Data Validator",
        "agent_data_profiler": "📊 Data Profiler",
        "agent_pattern_detective": "🎯 Pattern Detective",
        "agent_anomaly_hunter": "⚠️ Anomaly Hunter",
        "agent_relationship_analyst": "🔗 Relationship Analyst",
        "agent_strategic_synthesizer": "💡 Strategic Synthesizer",
        "agent_complete_analysis": "📋 Complete Analysis",
    }
}

def get_text(key: str, lang: str = "pt", **kwargs) -> str:
    """
    Obtém o texto traduzido para a chave especificada.
    
    Args:
        key: Chave da tradução
        lang: Idioma (pt ou en)
        **kwargs: Argumentos para formatação do texto
    
    Returns:
        Texto traduzido e formatado
    """
    text = TRANSLATIONS.get(lang, TRANSLATIONS["pt"]).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

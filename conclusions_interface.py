# Interface para Consultar Conclusões dos Agentes CrewAI
import streamlit as st
import pandas as pd
from datetime import datetime
import json
from analysis_memory import analysis_memory

def show_conclusions_interface():
    """Interface para consultar conclusões específicas dos agentes"""
    
    
    # Verificar se há análises disponíveis
    history = analysis_memory.get_analysis_history()
    
    if not history:
        st.warning("⚠️ Nenhuma análise CrewAI disponível. Execute uma análise primeiro na aba Chat IA.")
        return
    
    # Seleção de análise
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Lista de análises disponíveis
        analysis_options = {}
        for analysis_id, info in history.items():
            display_name = f"{info['analysis_name']} ({analysis_id}) - {info['timestamp'][:10]}"
            analysis_options[display_name] = analysis_id
        
        selected_display = st.selectbox(
            "📊 Selecione uma análise:",
            options=list(analysis_options.keys()),
            index=0
        )
        
        selected_analysis_id = analysis_options[selected_display]
    
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    # Obter dados da análise selecionada
    analysis_data = analysis_memory.get_analysis_results(selected_analysis_id)
    
    if not analysis_data:
        st.error("❌ Erro ao carregar dados da análise.")
        return
    
    # Mostrar informações básicas da análise
    st.markdown("#### 📋 Informações da Análise")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Registros", f"{analysis_data.get('data_summary', {}).get('rows', 0):,}")
    
    with col2:
        st.metric("📋 Colunas", analysis_data.get('data_summary', {}).get('columns', 0))
    
    with col3:
        st.metric("📅 Data", analysis_data.get('timestamp', 'N/A')[:10])
    
    # Tabs para diferentes tipos de consulta
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 Por Agente", "📊 Resumo Geral", "🔍 Buscar", "📈 Insights"])
    
    with tab1:
        show_agent_conclusions(analysis_data, selected_analysis_id)
    
    with tab2:
        show_general_summary(analysis_data)
    
    with tab3:
        show_search_interface(selected_analysis_id)
    
    with tab4:
        show_insights_interface(analysis_data)

def show_agent_conclusions(analysis_data, analysis_id):
    """Mostra conclusões organizadas por agente"""
    
    st.markdown("#### 🤖 Conclusões por Agente")
    
    # Obter conclusões dos agentes
    conclusions = analysis_memory.get_agent_conclusions(analysis_id)
    
    if not conclusions:
        st.warning("⚠️ Nenhuma conclusão de agente disponível.")
        return
    
    # Mapear agentes para ícones e descrições
    agent_info = {
        "Data Validator": {
            "icon": "🔍",
            "description": "Validação e qualidade dos dados",
            "color": "blue"
        },
        "Data Profiler": {
            "icon": "📊", 
            "description": "Perfilamento estatístico",
            "color": "green"
        },
        "Pattern Detective": {
            "icon": "🎯",
            "description": "Descoberta de padrões e tendências",
            "color": "orange"
        },
        "Anomaly Hunter": {
            "icon": "⚠️",
            "description": "Detecção de anomalias",
            "color": "red"
        },
        "Relationship Analyst": {
            "icon": "🔗",
            "description": "Análise de relacionamentos",
            "color": "purple"
        },
        "Strategic Synthesizer": {
            "icon": "🎯",
            "description": "Síntese estratégica",
            "color": "gold"
        }
    }
    
    # Mostrar cada agente
    for agent_name, agent_data in conclusions.items():
        agent_details = agent_info.get(agent_name, {"icon": "🤖", "description": "Agente de IA", "color": "gray"})
        
        with st.expander(f"{agent_details['icon']} {agent_name} - {agent_details['description']}", expanded=False):
            
            # Status do agente
            status = agent_data.get('status', 'unknown')
            status_emoji = "✅" if status == "completed" else "❌" if status == "error" else "⏳"
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"**Status:** {status_emoji} {status}")
                st.markdown(f"**Timestamp:** {agent_data.get('timestamp', 'N/A')}")
            
            with col2:
                # Resultado do agente
                result = agent_data.get('result', 'Nenhum resultado disponível')
                
                if isinstance(result, str):
                    st.markdown(f"**Resultado:**\n{result}")
                elif isinstance(result, dict):
                    st.markdown("**Resultado:**")
                    st.json(result)
                else:
                    st.markdown(f"**Resultado:** {str(result)}")
            
            # Botão para copiar resultado
            if st.button(f"📋 Copiar Resultado", key=f"copy_{agent_name}"):
                st.code(result if isinstance(result, str) else json.dumps(result, indent=2))
                st.success("✅ Resultado copiado!")

def show_general_summary(analysis_data):
    """Mostra resumo geral da análise"""
    
    st.markdown("#### 📊 Resumo Geral da Análise")
    
    # Resumo dos dados
    data_summary = analysis_data.get('data_summary', {})
    
    st.markdown("**📋 Dados Analisados:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"- **Registros:** {data_summary.get('rows', 0):,}")
        st.markdown(f"- **Colunas:** {data_summary.get('columns', 0)}")
    
    with col2:
        st.markdown(f"- **Análise:** {analysis_data.get('analysis_name', 'N/A')}")
        st.markdown(f"- **Data:** {analysis_data.get('timestamp', 'N/A')[:19]}")
    
    # Lista de colunas
    column_names = data_summary.get('column_names', [])
    if column_names:
        st.markdown("**📊 Colunas do Dataset:**")
        cols_display = st.columns(min(4, len(column_names)))
        for i, col in enumerate(column_names):
            with cols_display[i % 4]:
                st.markdown(f"• {col}")
    
    # Resumo dos agentes
    crew_results = analysis_data.get('crew_results', {})
    
    st.markdown("**🤖 Status dos Agentes:**")
    
    agent_mapping = {
        "validation": "🔍 Data Validator",
        "profiling": "📊 Data Profiler", 
        "patterns": "🎯 Pattern Detective",
        "anomalies": "⚠️ Anomaly Hunter",
        "relationships": "🔗 Relationship Analyst",
        "synthesis": "🎯 Strategic Synthesizer"
    }
    
    for agent_key, agent_name in agent_mapping.items():
        agent_result = crew_results.get(agent_key, {})
        status = agent_result.get('status', 'unknown')
        status_emoji = "✅" if status == "completed" else "❌" if status == "error" else "⏳"
        
        st.markdown(f"- {agent_name}: {status_emoji} {status}")

def show_search_interface(analysis_id):
    """Interface para buscar informações específicas"""
    
    st.markdown("#### 🔍 Buscar Informações")
    
    # Campo de busca
    search_query = st.text_input("🔍 Digite o que você está procurando:", placeholder="Ex: correlação, anomalia, padrão...")
    
    if search_query:
        # Buscar nas análises
        search_results = analysis_memory.search_analyses(search_query)
        
        if search_results:
            st.markdown(f"**📊 Resultados para '{search_query}':**")
            
            for result in search_results:
                with st.expander(f"📄 {result['analysis_name']} - {result['match_type']}", expanded=False):
                    st.markdown(f"**ID:** {result['analysis_id']}")
                    st.markdown(f"**Data:** {result['timestamp'][:19]}")
                    st.markdown(f"**Tipo de Match:** {result['match_type']}")
                    
                    if 'matched_column' in result:
                        st.markdown(f"**Coluna Encontrada:** {result['matched_column']}")
                    
                    if st.button(f"Ver Análise", key=f"view_{result['analysis_id']}"):
                        st.info(f"Análise {result['analysis_id']} selecionada!")
        else:
            st.warning(f"⚠️ Nenhum resultado encontrado para '{search_query}'")
    
    # Sugestões de busca
    st.markdown("**💡 Sugestões de Busca:**")
    suggestions = [
        "correlação", "anomalia", "padrão", "tendência", "outlier",
        "estatística", "distribuição", "média", "mediana", "desvio"
    ]
    
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(f"🔍 {suggestion}", key=f"search_{suggestion}"):
                st.session_state.search_query = suggestion
                st.rerun()

def show_insights_interface(analysis_data):
    """Interface para mostrar insights principais"""
    
    st.markdown("#### 📈 Insights Principais")
    
    # Obter conclusões dos agentes
    analysis_id = analysis_data.get('analysis_id')
    conclusions = analysis_memory.get_agent_conclusions(analysis_id)
    
    if not conclusions:
        st.warning("⚠️ Nenhum insight disponível.")
        return
    
    # Insights por categoria
    insights_categories = {
        "🔍 Qualidade dos Dados": ["Data Validator"],
        "📊 Características": ["Data Profiler"],
        "🎯 Padrões": ["Pattern Detective"],
        "⚠️ Anomalias": ["Anomaly Hunter"],
        "🔗 Relacionamentos": ["Relationship Analyst"],
        "🎯 Estratégicos": ["Strategic Synthesizer"]
    }
    
    for category, agents in insights_categories.items():
        st.markdown(f"### {category}")
        
        for agent_name in agents:
            if agent_name in conclusions:
                agent_data = conclusions[agent_name]
                result = agent_data.get('result', 'Nenhum insight disponível')
                
                if result and result != "Nenhum resultado disponível":
                    with st.container():
                        st.markdown(f"**{agent_name}:**")
                        st.info(result)
                        st.markdown("---")
    
    # Resumo executivo
    st.markdown("### 📋 Resumo Executivo")
    
    # Gerar resumo automático
    summary = analysis_memory.get_analysis_summary(analysis_id)
    st.markdown(summary)
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Exportar Insights"):
            export_data = {
                "analysis_id": analysis_id,
                "insights": conclusions,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"insights_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("🔄 Atualizar Insights"):
            st.rerun()
    
    with col3:
        if st.button("💬 Chat sobre Insights"):
            st.info("💡 Use a aba 'Chat IA' para fazer perguntas específicas sobre estes insights!")

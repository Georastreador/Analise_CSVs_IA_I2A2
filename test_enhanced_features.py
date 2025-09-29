# Teste das Funcionalidades Melhoradas - Sistema de Chat com Agentes CrewAI
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Importar módulos melhorados
from analysis_memory import analysis_memory
from chat_ai_enhanced import EnhancedChatAI
from conclusions_interface import show_conclusions_interface

def create_sample_data():
    """Cria dados de exemplo para teste"""
    np.random.seed(42)
    
    # Dados de vendas
    data = {
        'data': pd.date_range('2023-01-01', periods=100, freq='D'),
        'vendas': np.random.normal(1000, 200, 100),
        'clientes': np.random.poisson(50, 100),
        'produto': np.random.choice(['A', 'B', 'C', 'D'], 100),
        'regiao': np.random.choice(['Norte', 'Sul', 'Leste', 'Oeste'], 100),
        'desconto': np.random.uniform(0, 0.3, 100)
    }
    
    df = pd.DataFrame(data)
    df['receita'] = df['vendas'] * (1 - df['desconto'])
    
    return df

def test_analysis_memory():
    """Testa o sistema de memória"""
    st.markdown("### 🧠 Teste do Sistema de Memória")
    
    # Criar dados de exemplo
    df = create_sample_data()
    
    # Simular resultados de agentes
    mock_crew_results = {
        "validation": {
            "status": "completed",
            "result": "Dados validados com sucesso. 100% de completude.",
            "timestamp": datetime.now().isoformat()
        },
        "profiling": {
            "status": "completed", 
            "result": "Dataset com 100 registros e 6 colunas. Vendas média: R$ 1,000.",
            "timestamp": datetime.now().isoformat()
        },
        "patterns": {
            "status": "completed",
            "result": "Padrão sazonal identificado. Picos nas vendas aos finais de semana.",
            "timestamp": datetime.now().isoformat()
        },
        "anomalies": {
            "status": "completed",
            "result": "3 anomalias detectadas em vendas extremamente altas.",
            "timestamp": datetime.now().isoformat()
        },
        "relationships": {
            "status": "completed",
            "result": "Correlação forte entre vendas e número de clientes (0.85).",
            "timestamp": datetime.now().isoformat()
        },
        "synthesis": {
            "status": "completed",
            "result": "Recomendação: Focar em aumentar número de clientes para impulsionar vendas.",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # Salvar análise
    analysis_id = "test_001"
    success = analysis_memory.save_analysis_results(
        analysis_id=analysis_id,
        csv_data=df,
        crew_results=mock_crew_results,
        analysis_name="Teste de Vendas"
    )
    
    if success:
        st.success(f"✅ Análise salva com sucesso! ID: {analysis_id}")
        
        # Testar recuperação
        retrieved = analysis_memory.get_analysis_results(analysis_id)
        if retrieved:
            st.success("✅ Análise recuperada com sucesso!")
            
            # Mostrar resumo
            summary = analysis_memory.get_analysis_summary(analysis_id)
            st.markdown("**Resumo da Análise:**")
            st.markdown(summary)
            
            # Mostrar conclusões
            conclusions = analysis_memory.get_agent_conclusions(analysis_id)
            st.markdown("**Conclusões dos Agentes:**")
            for agent, data in conclusions.items():
                st.markdown(f"- **{agent}:** {data['result']}")
    else:
        st.error("❌ Erro ao salvar análise")

def test_enhanced_chat():
    """Testa o chat melhorado"""
    st.markdown("### 💬 Teste do Chat Melhorado")
    
    # Simular configuração de API (sem chave real para teste)
    api_provider = "OpenAI"
    api_key = "test_key"
    
    chat_ai = EnhancedChatAI(api_provider, api_key)
    
    # Testar sugestões de perguntas
    df = create_sample_data()
    suggestions = chat_ai.suggest_enhanced_questions(df)
    
    st.markdown("**Sugestões de Perguntas:**")
    for i, suggestion in enumerate(suggestions[:5]):
        st.markdown(f"{i+1}. {suggestion}")
    
    # Testar contexto de análise
    if analysis_memory.current_analysis:
        context = chat_ai.get_analysis_context()
        st.markdown("**Contexto de Análise:**")
        st.text_area("Contexto", context, height=200)

def main():
    """Função principal de teste"""
    st.set_page_config(
        page_title="🧪 Teste - Funcionalidades Melhoradas",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 Teste das Funcionalidades Melhoradas")
    st.markdown("---")
    
    # Tabs para diferentes testes
    tab1, tab2, tab3 = st.tabs(["🧠 Memória", "💬 Chat", "🎯 Conclusões"])
    
    with tab1:
        test_analysis_memory()
    
    with tab2:
        test_enhanced_chat()
    
    with tab3:
        st.markdown("### 🎯 Teste da Interface de Conclusões")
        show_conclusions_interface()
    
    # Informações sobre o teste
    st.markdown("---")
    st.markdown("### 📋 Informações do Teste")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Análises Salvas", len(analysis_memory.get_analysis_history()))
    
    with col2:
        st.metric("🤖 Agentes", 6)
    
    with col3:
        st.metric("💾 Memória", "Ativa" if analysis_memory.current_analysis else "Vazia")
    
    # Botões de controle
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Limpar Memória"):
            if analysis_memory.clear_analysis_memory():
                st.success("✅ Memória limpa!")
                st.rerun()
    
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()

if __name__ == "__main__":
    main()

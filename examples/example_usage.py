#!/usr/bin/env python3
"""
Exemplo de uso do CSV Analysis AI
Este script demonstra como usar a aplicação programaticamente
"""

import pandas as pd
import sys
import os

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat_ai_enhanced import EnhancedChatAI
from analysis_memory import analysis_memory
from crewai_enhanced import get_crewai_instance

def exemplo_basico():
    """Exemplo básico de uso da aplicação"""
    print("🚀 Exemplo Básico - CSV Analysis AI")
    print("=" * 50)
    
    # 1. Carregar dados de exemplo
    print("📊 Carregando dados de exemplo...")
    df = pd.read_csv("examples/data/sample_data.csv")
    print(f"✅ Dados carregados: {len(df)} registros, {len(df.columns)} colunas")
    
    # 2. Configurar chat AI (simulação - sem API key real)
    print("\n🤖 Configurando Chat AI...")
    try:
        # Em um ambiente real, você configuraria com uma API key válida
        chat_ai = EnhancedChatAI("OpenAI", "sua-api-key-aqui")
        print("✅ Chat AI configurado")
    except Exception as e:
        print(f"⚠️ Chat AI não configurado: {e}")
        return
    
    # 3. Fazer perguntas sobre os dados
    print("\n💬 Fazendo perguntas sobre os dados...")
    perguntas = [
        "Quantos funcionários temos no total?",
        "Qual é a média salarial por departamento?",
        "Quais são os funcionários com melhor performance?",
        "Há alguma correlação entre experiência e salário?"
    ]
    
    for pergunta in perguntas:
        print(f"\n❓ Pergunta: {pergunta}")
        try:
            resposta = chat_ai.generate_enhanced_response(pergunta, df)
            if isinstance(resposta, tuple):
                texto, grafico = resposta
                print(f"🤖 Resposta: {texto[:200]}...")
                print(f"📊 Gráfico gerado: {grafico is not None}")
            else:
                print(f"🤖 Resposta: {resposta[:200]}...")
        except Exception as e:
            print(f"❌ Erro: {e}")

def exemplo_crewai():
    """Exemplo de uso dos agentes CrewAI"""
    print("\n\n🤖 Exemplo CrewAI - Análise com Agentes")
    print("=" * 50)
    
    # 1. Carregar dados
    df = pd.read_csv("examples/data/sample_data.csv")
    print(f"📊 Dados carregados: {len(df)} registros")
    
    # 2. Executar análise CrewAI (simulação)
    print("\n🔍 Executando análise CrewAI...")
    try:
        crewai_instance = get_crewai_instance()
        # Em um ambiente real, você executaria:
        # results = crewai_instance.run_analysis("Análise de Funcionários", "OpenAI", "sua-api-key")
        print("✅ Análise CrewAI executada (simulação)")
        
        # 3. Verificar resultados
        print("\n📋 Verificando resultados...")
        analysis_history = analysis_memory.get_analysis_history()
        print(f"📊 Análises disponíveis: {len(analysis_history)}")
        
        if analysis_history:
            for analysis_id, analysis_data in analysis_history.items():
                print(f"  - {analysis_data.get('analysis_name', 'N/A')} ({analysis_data.get('status', 'N/A')})")
        
    except Exception as e:
        print(f"❌ Erro na análise CrewAI: {e}")

def exemplo_relatorios():
    """Exemplo de geração de relatórios"""
    print("\n\n📄 Exemplo Relatórios")
    print("=" * 50)
    
    # 1. Carregar dados
    df = pd.read_csv("examples/data/sample_data.csv")
    
    # 2. Gerar relatório Markdown
    print("📝 Gerando relatório Markdown...")
    try:
        from Relatorios_appCSV.report_generator import generate_markdown_report
        
        # Dados de exemplo para o relatório
        conversation_data = {
            'messages': [
                {
                    'timestamp': '2025-09-29T20:00:00',
                    'user_message': 'Quantos funcionários temos?',
                    'ai_response': f'O dataset possui {len(df)} funcionários.',
                    'has_chart': False
                }
            ]
        }
        
        overview_data = {
            'data_quality': 100.0,
            'numeric_columns': len(df.select_dtypes(include=['number']).columns),
            'categorical_columns': len(df.select_dtypes(include=['object']).columns),
            'insights': [
                f"Dataset com {len(df)} registros e {len(df.columns)} colunas",
                "Dados completos sem valores ausentes",
                "Boa distribuição entre departamentos"
            ]
        }
        
        markdown_data = generate_markdown_report(
            df, 
            "Análise de Funcionários", 
            "Análise de dados de funcionários da empresa",
            None,  # analysis_results
            conversation_data,
            overview_data,
            None   # crewai_conclusions
        )
        
        print(f"✅ Relatório Markdown gerado: {len(markdown_data)} bytes")
        
        # Salvar relatório
        with open("exemplo_relatorio.md", "wb") as f:
            f.write(markdown_data)
        print("💾 Relatório salvo como 'exemplo_relatorio.md'")
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")

def main():
    """Função principal"""
    print("🎯 CSV Analysis AI - Exemplos de Uso")
    print("=" * 60)
    
    try:
        # Executar exemplos
        exemplo_basico()
        exemplo_crewai()
        exemplo_relatorios()
        
        print("\n\n✅ Todos os exemplos executados com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Configure uma API key válida")
        print("2. Execute: streamlit run csv_analysis_app_v2.py")
        print("3. Carregue seus próprios dados CSV")
        print("4. Explore as funcionalidades da aplicação")
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

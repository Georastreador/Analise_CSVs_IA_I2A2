#!/bin/bash

# Script para limpeza do projeto CSV Analysis AI
# Remove arquivos duplicados, antigos e desnecessários

echo "🧹 Iniciando limpeza do projeto CSV Analysis AI..."
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "csv_analysis_app_v2.py" ]; then
    echo "❌ Erro: Execute este script no diretório do projeto"
    exit 1
fi

echo "📊 Arquivos que serão removidos:"
echo ""

# 1. Remover arquivos de documentação duplicados (mantém apenas os da raiz)
echo "🗑️ Removendo documentação duplicada..."
echo "   - ARQUITETURA_IMPLEMENTACAO.md (duplicado)"
echo "   - DEMONSTRACAO_FUNCIONALIDADES.md (duplicado)"
echo "   - INDICE_DOCUMENTACAO.md (duplicado)"
echo "   - RELATORIO_CONFERENCIA_FUNCOES.md (duplicado)"
echo "   - RELATORIO_DESENVOLVIMENTO.md (duplicado)"
echo "   - RELATORIO_IMPLEMENTACAO_VISUALIZACAO.md (duplicado)"
echo "   - RESUMO_EXECUTIVO.md (duplicado)"
echo "   - README_BACKUP.md (backup desnecessário)"

# 2. Remover arquivos Python antigos/duplicados
echo ""
echo "🐍 Removendo arquivos Python antigos/duplicados..."
echo "   - csv_analysis_app.py (versão antiga)"
echo "   - chat_ai.py (versão básica)"
echo "   - chat_simple.py (versão simplificada)"
echo "   - report_generator.py (duplicado - existe em Relatorios_appCSV/)"

# 3. Remover arquivos de cache
echo ""
echo "🗂️ Removendo arquivos de cache..."
echo "   - __pycache__/ (diretório de cache Python)"
echo "   - Relatorios_appCSV/__pycache__/ (cache do módulo)"

# 4. Remover arquivos vazios
echo ""
echo "📄 Removendo arquivos vazios..."
echo "   - gw_config.json (arquivo vazio)"

# 5. Remover arquivos de teste antigos (opcional)
echo ""
echo "🧪 Arquivos de teste (manter ou remover):"
echo "   - test_enhanced_features.py (testes antigos)"
echo "   - conclusions_interface.py (interface antiga)"

echo ""
echo "⚠️ ATENÇÃO: Esta operação irá remover arquivos permanentemente!"
echo "📋 Arquivos que serão MANTIDOS:"
echo "   ✅ csv_analysis_app_v2.py (aplicação principal)"
echo "   ✅ chat_ai_enhanced.py (chat aprimorado)"
echo "   ✅ crewai_enhanced.py (sistema CrewAI)"
echo "   ✅ analysis_memory.py (sistema de memória)"
echo "   ✅ data_manager.py (gerenciador de dados)"
echo "   ✅ Relatorios_appCSV/ (módulo de relatórios)"
echo "   ✅ README.md, CONTRIBUTING.md, etc. (documentação principal)"
echo "   ✅ .github/, .streamlit/, etc. (configuração)"

echo ""
read -p "🤔 Deseja continuar com a limpeza? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🧹 Executando limpeza..."
    
    # Remover documentação duplicada
    rm -f ARQUITETURA_IMPLEMENTACAO.md
    rm -f DEMONSTRACAO_FUNCIONALIDADES.md
    rm -f INDICE_DOCUMENTACAO.md
    rm -f RELATORIO_CONFERENCIA_FUNCOES.md
    rm -f RELATORIO_DESENVOLVIMENTO.md
    rm -f RELATORIO_IMPLEMENTACAO_VISUALIZACAO.md
    rm -f RESUMO_EXECUTIVO.md
    rm -f README_BACKUP.md
    
    # Remover arquivos Python antigos/duplicados
    rm -f csv_analysis_app.py
    rm -f chat_ai.py
    rm -f chat_simple.py
    rm -f report_generator.py
    
    # Remover arquivos de cache
    rm -rf __pycache__
    rm -rf Relatorios_appCSV/__pycache__
    
    # Remover arquivos vazios
    rm -f gw_config.json
    
    # Remover arquivos de teste antigos (opcional)
    rm -f test_enhanced_features.py
    rm -f conclusions_interface.py
    
    echo "✅ Limpeza concluída!"
    echo ""
    echo "📊 Resumo da limpeza:"
    echo "   🗑️ Documentação duplicada: 8 arquivos removidos"
    echo "   🐍 Python antigos/duplicados: 4 arquivos removidos"
    echo "   🗂️ Cache: 2 diretórios removidos"
    echo "   📄 Arquivos vazios: 1 arquivo removido"
    echo "   🧪 Testes antigos: 2 arquivos removidos"
    echo ""
    echo "📁 Total de arquivos removidos: ~17 arquivos"
    echo ""
    echo "🎯 Próximos passos:"
    echo "1. Verificar se tudo ainda funciona: git status"
    echo "2. Fazer commit das mudanças: git add . && git commit -m 'chore: remove arquivos duplicados e desnecessários'"
    echo "3. Fazer push: git push origin main"
    
else
    echo ""
    echo "❌ Limpeza cancelada. Nenhum arquivo foi removido."
    echo ""
    echo "💡 Para remover arquivos manualmente, use:"
    echo "   rm arquivo_para_remover"
    echo ""
    echo "📋 Lista de arquivos que podem ser removidos:"
    echo "   - ARQUITETURA_IMPLEMENTACAO.md"
    echo "   - DEMONSTRACAO_FUNCIONALIDADES.md"
    echo "   - INDICE_DOCUMENTACAO.md"
    echo "   - RELATORIO_CONFERENCIA_FUNCOES.md"
    echo "   - RELATORIO_DESENVOLVIMENTO.md"
    echo "   - RELATORIO_IMPLEMENTACAO_VISUALIZACAO.md"
    echo "   - RESUMO_EXECUTIVO.md"
    echo "   - README_BACKUP.md"
    echo "   - csv_analysis_app.py"
    echo "   - chat_ai.py"
    echo "   - chat_simple.py"
    echo "   - report_generator.py"
    echo "   - __pycache__/"
    echo "   - Relatorios_appCSV/__pycache__/"
    echo "   - gw_config.json"
    echo "   - test_enhanced_features.py"
    echo "   - conclusions_interface.py"
fi

echo ""
echo "🏁 Script de limpeza finalizado."

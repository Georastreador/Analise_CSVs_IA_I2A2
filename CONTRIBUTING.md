# 🤝 Guia de Contribuição

Obrigado por considerar contribuir para o CSV Analysis AI! Este documento fornece diretrizes e informações para contribuidores.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Padrões de Código](#padrões-de-código)
- [Processo de Pull Request](#processo-de-pull-request)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Funcionalidades](#sugerindo-funcionalidades)

## 📜 Código de Conduta

Este projeto segue um código de conduta para garantir um ambiente acolhedor para todos os contribuidores. Ao participar, você concorda em manter este código.

### Nossos Compromissos
- Usar linguagem acolhedora e inclusiva
- Respeitar diferentes pontos de vista e experiências
- Aceitar críticas construtivas graciosamente
- Focar no que é melhor para a comunidade
- Demonstrar empatia com outros membros da comunidade

## 🚀 Como Contribuir

### Tipos de Contribuição
- 🐛 **Bug fixes** - Correção de problemas
- ✨ **Novas funcionalidades** - Adição de recursos
- 📚 **Documentação** - Melhoria da documentação
- 🧪 **Testes** - Adição ou melhoria de testes
- 🎨 **UI/UX** - Melhorias na interface
- 🔧 **Refatoração** - Melhoria do código existente

### Processo de Contribuição
1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie** uma branch para sua feature
4. **Faça** suas alterações
5. **Teste** suas alterações
6. **Commit** com mensagens claras
7. **Push** para seu fork
8. **Abra** um Pull Request

## ⚙️ Configuração do Ambiente

### Pré-requisitos
- Python 3.8+
- Git
- Editor de código (VS Code, PyCharm, etc.)

### Configuração Local
```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/csv-analysis-ai.git
cd csv-analysis-ai

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instale dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desenvolvimento

# 4. Configure pre-commit hooks
pre-commit install

# 5. Execute testes
pytest
```

### Estrutura do Projeto
```
csv-analysis-ai/
├── csv_analysis_app_v2.py    # Aplicação principal
├── chat_ai_enhanced.py       # Sistema de chat
├── crewai_enhanced.py        # Agentes CrewAI
├── analysis_memory.py        # Sistema de memória
├── data_manager.py           # Gerenciador de dados
├── Relatorios_appCSV/        # Gerador de relatórios
├── tests/                    # Testes automatizados
├── docs/                     # Documentação
└── examples/                 # Exemplos de uso
```

## 📝 Padrões de Código

### Python Style Guide
- Siga **PEP 8** para estilo de código
- Use **type hints** quando possível
- Escreva **docstrings** para funções e classes
- Mantenha **linhas com máximo 88 caracteres**

### Formatação
```bash
# Formatar código com Black
black .

# Verificar estilo com flake8
flake8 .

# Verificar tipos com mypy
mypy .
```

### Estrutura de Commits
Use o padrão **Conventional Commits**:

```
tipo(escopo): descrição

Corpo da mensagem (opcional)

Rodapé (opcional)
```

**Tipos:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Tarefas de manutenção

**Exemplos:**
```
feat(chat): adiciona suporte a múltiplas APIs
fix(analysis): corrige erro na validação de dados
docs(readme): atualiza instruções de instalação
```

## 🔄 Processo de Pull Request

### Antes de Abrir um PR
- [ ] Testes passando localmente
- [ ] Código formatado com Black
- [ ] Sem erros de linting
- [ ] Documentação atualizada
- [ ] Commits com mensagens claras

### Template de Pull Request
```markdown
## 📝 Descrição
Breve descrição das alterações.

## 🔗 Tipo de Mudança
- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação

## 🧪 Como Testar
1. Passo 1
2. Passo 2
3. Passo 3

## 📸 Screenshots (se aplicável)
Adicione screenshots das mudanças na UI.

## ✅ Checklist
- [ ] Código testado localmente
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Sem conflitos de merge
```

### Processo de Review
1. **Automated checks** devem passar
2. **Review** por pelo menos 1 mantenedor
3. **Discussão** de mudanças se necessário
4. **Aprovação** e merge

## 🐛 Reportando Bugs

### Antes de Reportar
- Verifique se o bug já foi reportado
- Teste com a versão mais recente
- Tente reproduzir o problema

### Template de Bug Report
```markdown
## 🐛 Descrição do Bug
Descrição clara e concisa do bug.

## 🔄 Passos para Reproduzir
1. Vá para '...'
2. Clique em '...'
3. Veja o erro

## 🎯 Comportamento Esperado
O que deveria acontecer.

## 📸 Screenshots
Se aplicável, adicione screenshots.

## 💻 Ambiente
- OS: [ex: Windows 10, macOS 12, Ubuntu 20.04]
- Python: [ex: 3.9.7]
- Versão: [ex: 2.0.0]

## 📋 Informações Adicionais
Qualquer informação adicional relevante.
```

## 💡 Sugerindo Funcionalidades

### Template de Feature Request
```markdown
## 🚀 Funcionalidade Sugerida
Descrição clara da funcionalidade.

## 💭 Motivação
Por que esta funcionalidade seria útil?

## 📋 Descrição Detalhada
Como a funcionalidade deveria funcionar?

## 🎯 Casos de Uso
Exemplos de como seria usada.

## 🔄 Alternativas Consideradas
Outras soluções que você considerou.

## 📋 Informações Adicionais
Qualquer informação adicional relevante.
```

## 🏷️ Versionamento

Seguimos [Semantic Versioning](https://semver.org/):
- **MAJOR**: Mudanças incompatíveis
- **MINOR**: Novas funcionalidades compatíveis
- **PATCH**: Correções de bugs compatíveis

## 📞 Suporte

### Canais de Comunicação
- 📧 **Email**: ursodecasaco@gmail.com
- 💬 **Discord**: [Link do servidor]
- 🐛 **Issues**: GitHub Issues
- 📖 **Wiki**: Documentação do projeto

### Perguntas Frequentes
- **Como configurar APIs?** Veja a documentação
- **Problemas de instalação?** Verifique os pré-requisitos
- **Erros de execução?** Consulte os logs

## 🙏 Reconhecimento

Contribuidores são reconhecidos em:
- README.md
- CHANGELOG.md
- Releases do GitHub
- Documentação do projeto

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a [Licença MIT](LICENSE).

---

**Obrigado por contribuir para o CSV Analysis AI! 🎉**

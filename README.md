
# Portaria Sunset – Sistema de Controle de Acesso

Sistema de portaria desenvolvido em **Python** para a **Academia Sunset**, com foco em controle de acesso de alunos e gestão simples de mensalidades.

## Funcionalidades

- Cadastro de alunos com:
  - Nome
  - Matrícula (código único)
  - Código de biometria (simulado)
  - Data de vencimento da mensalidade
- Verificação de acesso na portaria:
  - Entrada autorizada se o pagamento estiver em dia
  - Aviso quando a mensalidade **vence hoje**
  - Bloqueio de entrada em caso de **atraso**
- Atualização automática do vencimento:
  - Ao registrar pagamento, o sistema avança o vencimento em **+1 mês**
- Histórico dos acessos:
  - Data e hora
  - Matrícula
  - Se foi autorizado ou negado
  - Motivo (em atraso, não encontrado, etc.)

## Tecnologias

- Python 3
- Banco de dados **SQLite** (`sunset_academia.db`)
- Execução em terminal (CMD) no Windows

## Como executar

1. Clone o repositório ou copie os arquivos para uma pasta:

```bash
git clone https://github.com/adailtoncunha32/PORTARIA-DE-ACADEMIA.git
cd PORTARIA-DE-ACADEMIA

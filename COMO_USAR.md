# Consultor de NTs CBMERJ

Sistema de consulta inteligente das Normas Técnicas do Corpo de Bombeiros do Rio de Janeiro.

## Setup (uma única vez)

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Baixar as NTs do CBMERJ
```bash
python baixar_normas.py
```

### 3. Indexar os PDFs
```bash
python indexar.py
```

---

## Usar o sistema

```bash
streamlit run app.py
```

O navegador abre automaticamente em `http://localhost:8501`

---

## Configuração da API

Na barra lateral do app, informe sua chave da Anthropic.

Ou defina como variável de ambiente para não precisar digitar toda vez:

```bash
# Windows
set ANTHROPIC_API_KEY=sua-chave-aqui

# Linux/Mac
export ANTHROPIC_API_KEY=sua-chave-aqui
```

---

## Custo estimado

| Ação | Custo |
|------|-------|
| Download e indexação | Gratuito |
| Busca nas NTs | Gratuito (BM25 local) |
| Consulta à IA (Haiku) | ~$0,0002 por pergunta |
| 100 consultas/dia | ~$0,02/dia |
| 1.000 consultas/mês | ~$0,20/mês |

---

## NTs disponíveis

O sistema tenta baixar as 37 NTs do CBMERJ. As principais para projetos de incêndio:

- **NT-02** – Saídas de emergência
- **NT-11** – Iluminação de emergência
- **NT-16** – Detecção e alarme de incêndio
- **NT-17** – Sprinklers
- **NT-20** – Hidrantes e mangotinhos
- **NT-22** – SPDA (para-raios)
- **NT-24** – Extintores
- **NT-32** – Plano de emergência

## Se alguns PDFs não baixarem

O CBMERJ atualiza os links das NTs periodicamente. Se alguma não baixar automaticamente, você pode adicionar manualmente na pasta `normas/` com o nome `NT-XX.pdf` e depois rodar `python indexar.py` novamente.

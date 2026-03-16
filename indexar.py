"""
Extrai texto dos PDFs das NTs e cria o índice de busca BM25.
Execute após baixar_normas.py.
"""

import json
import pickle
import re
from pathlib import Path

import pdfplumber
from rank_bm25 import BM25Okapi

BASE = Path(__file__).parent
PASTA_NORMAS = BASE / "normas"
ARQUIVO_INDICE = BASE / "dados" / "indice.json"
ARQUIVO_CHUNKS = BASE / "dados" / "chunks.pkl"
ARQUIVO_BM25 = BASE / "dados" / "bm25.pkl"
ARQUIVO_CHUNKS_JSONL = BASE / "dados" / "chunks.jsonl"
ARQUIVO_PROGRESSO = BASE / "dados" / "indexados.json"

TAMANHO_CHUNK = 800
SOBREPOSICAO = 80
MAX_CHARS_PAGINA = 8_000     # ignora páginas com mais que isso (lixo/binário)
MAX_CHARS_NORMA = 500_000    # corta texto de uma NT se passar disso


def eh_pdf_valido(caminho: Path) -> bool:
    """Verifica se o arquivo começa com a assinatura %PDF."""
    try:
        with open(caminho, "rb") as f:
            return f.read(4) == b"%PDF"
    except Exception:
        return False


def extrair_texto_pdf(caminho: Path) -> str:
    partes = []
    total = 0
    try:
        with pdfplumber.open(caminho) as pdf:
            for i, pagina in enumerate(pdf.pages):
                t = pagina.extract_text()
                if not t:
                    continue
                if len(t) > MAX_CHARS_PAGINA:
                    print(f"    página {i+1}: {len(t)} chars (provável lixo, pulando)")
                    continue
                partes.append(t)
                total += len(t)
                if total >= MAX_CHARS_NORMA:
                    print(f"    limite de {MAX_CHARS_NORMA} chars atingido, truncando")
                    break
    except Exception as e:
        print(f"    erro ao extrair: {e}")
    return "\n".join(partes)


def limpar_texto(texto: str) -> str:
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'(\w)-\s+(\w)', r'\1\2', texto)
    return texto.strip()


def dividir_em_chunks(texto: str, nt: str, titulo: str) -> list[dict]:
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = min(inicio + TAMANHO_CHUNK, len(texto))
        if fim < len(texto):
            ultimo_ponto = texto.rfind('.', inicio, fim)
            if ultimo_ponto > inicio + TAMANHO_CHUNK // 2:
                fim = ultimo_ponto + 1
        trecho = texto[inicio:fim].strip()
        if len(trecho) > 50:
            chunks.append({"nt": nt, "titulo": titulo, "texto": trecho})
        proximo = fim - SOBREPOSICAO
        if proximo <= inicio:   # garante avanço mínimo
            proximo = inicio + 100
        inicio = proximo
    return chunks


def tokenizar(texto: str) -> list[str]:
    return re.findall(r'\b[a-záéíóúàãõâêîôûç]+\b', texto.lower())


def carregar_progresso() -> set:
    if ARQUIVO_PROGRESSO.exists():
        return set(json.loads(ARQUIVO_PROGRESSO.read_text(encoding="utf-8")))
    return set()


def salvar_progresso(feitos: set):
    ARQUIVO_PROGRESSO.write_text(
        json.dumps(sorted(feitos), ensure_ascii=False), encoding="utf-8"
    )


def indexar():
    if not ARQUIVO_INDICE.exists():
        print("Execute primeiro: python baixar_normas.py")
        return

    catalogo = json.loads(ARQUIVO_INDICE.read_text(encoding="utf-8"))
    disponiveis = [n for n in catalogo if n["disponivel"] and n["arquivo"]]

    if not disponiveis:
        print("Nenhuma norma disponível para indexar.")
        return

    feitos = carregar_progresso()
    pendentes = [n for n in disponiveis if n["nt"] not in feitos]

    print(f"\n{'='*60}")
    print(f"  INDEXANDO NORMAS TÉCNICAS")
    print(f"  Já indexadas: {len(feitos)} | Pendentes: {len(pendentes)}")
    print(f"{'='*60}\n")

    # ── Passo 1: extrai texto → grava em JSONL incrementalmente ───────────────
    total_novos = 0
    modo = "a" if feitos else "w"   # append se retomando, novo se primeira vez

    with open(ARQUIVO_CHUNKS_JSONL, modo, encoding="utf-8") as fout:
        for norma in pendentes:
            nt = norma["nt"]
            titulo = norma["titulo"]
            caminho = Path(norma["arquivo"])

            print(f"  NT-{nt}: ", end="", flush=True)

            if not caminho.exists():
                print("arquivo não encontrado")
                feitos.add(nt)
                salvar_progresso(feitos)
                continue

            if not eh_pdf_valido(caminho):
                print("não é PDF válido (pode ser HTML de erro) — pulando")
                feitos.add(nt)
                salvar_progresso(feitos)
                continue

            tamanho_kb = caminho.stat().st_size // 1024
            print(f"{tamanho_kb} KB → extraindo...", end=" ", flush=True)

            texto = limpar_texto(extrair_texto_pdf(caminho))

            if not texto:
                print("sem texto (PDF pode ser imagem)")
                feitos.add(nt)
                salvar_progresso(feitos)
                continue

            chunks = dividir_em_chunks(texto, nt, titulo)
            for chunk in chunks:
                fout.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            fout.flush()

            total_novos += len(chunks)
            feitos.add(nt)
            salvar_progresso(feitos)
            print(f"{len(chunks)} trechos")

            del texto, chunks

    print(f"\n  {total_novos} novos trechos adicionados")

    # ── Passo 2: lê JSONL e reconstrói índice BM25 ────────────────────────────
    print(f"  Construindo índice BM25...", flush=True)

    todos_chunks = []
    corpus_tokens = []

    with open(ARQUIVO_CHUNKS_JSONL, encoding="utf-8") as fin:
        for linha in fin:
            chunk = json.loads(linha)
            todos_chunks.append(chunk)
            corpus_tokens.append(tokenizar(chunk["texto"]))

    print(f"  {len(todos_chunks)} trechos totais no índice")

    bm25 = BM25Okapi(corpus_tokens)
    del corpus_tokens

    with open(ARQUIVO_CHUNKS, "wb") as f:
        pickle.dump(todos_chunks, f)
    with open(ARQUIVO_BM25, "wb") as f:
        pickle.dump(bm25, f)

    print(f"\n{'='*60}")
    print(f"  Indexação concluída! Execute: streamlit run app.py")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    indexar()

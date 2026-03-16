"""
Baixa as Notas Técnicas do CBMERJ e indexa para consulta.
Execute uma vez antes de usar o app.
Fonte: https://www.cbmerj.rj.gov.br/notas-tecnicas/
"""

import json
import time
import requests
from pathlib import Path

BASE = Path(__file__).parent
PASTA_NORMAS = BASE / "normas"
ARQUIVO_INDICE = BASE / "dados" / "indice.json"

# Links atuais das Notas Técnicas do CBMERJ (verificados em março/2026)
NORMAS_CBMERJ = [
    # ── Grupo 1 – Generalidades ───────────────────────────────────────────────
    {"nt": "1-01-P1", "titulo": "Procedimentos Administrativos – Regularização e Fiscalização (Parte 1)",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2026/01/NT_1-01_Parte1_alterada_Portaria_1317_2025.pdf"},
    {"nt": "1-01-P2", "titulo": "Procedimentos Administrativos – Regularização e Fiscalização (Parte 2)",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT_1-01-Procedimentos-Administrativos-para-Regularizacao-e-Fiscalizacao-Parte-2-Fiscalizacao_2021_1620759470.pdf"},
    {"nt": "1-02", "titulo": "Terminologia de Segurança Contra Incêndio e Pânico",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-1-02-Terminologia-de-seguranca-contra-incendio-e-panico.pdf"},
    {"nt": "1-03", "titulo": "Símbolos Gráficos para Projetos de Segurança Contra Incêndio e Pânico",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/05/NT1-03_2Edio_2023.pdf"},
    {"nt": "1-04", "titulo": "Classificação das Edificações e Áreas de Risco quanto ao Risco de Incêndio",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-1-04-Classificacao-das-edificacoes-e-areas-de-risco-quanto-ao-risco-de-incendio.pdf"},
    {"nt": "1-05", "titulo": "Edificações Anteriores – Adequação ao COSCIP",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-1-05-Edificacoes-anteriores-Adequacao-ao-COSCIP.pdf"},
    {"nt": "1-06", "titulo": "Processo Administrativo em Tramitação por Adequação Normativa",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/05/NT1-06_2Edio_2023.pdf"},
    {"nt": "1-07", "titulo": "Atividades Econômicas de Baixo Risco",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-1-07-Atividades-economicas-de-baixo-risco-2020.pdf"},

    # ── Grupo 2 – Medidas de Segurança Contra Incêndio e Pânico ──────────────
    {"nt": "2-01", "titulo": "Sistema de Proteção por Extintores de Incêndio",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-2-01-Sistema-de-protecao-por-extintores-de-incendio-versao-02-Aprovada-pela-Portaria-CBMERJ-1120_2020_1601400175.pdf"},
    {"nt": "2-02", "titulo": "Sistemas de Hidrantes e Mangotinhos para Combate a Incêndio",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2026/01/NT_2-02_alterada-pela-Portaria-1317_2025.pdf"},
    {"nt": "2-03-P1", "titulo": "Sistemas de Chuveiros Automáticos Sprinklers – Parte 1 – Requisitos Gerais",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-2-03-Sistemas-de-chuveiros-automticos-sprinklers-Parte-1-Requisitos-gerais-2019-atualizada_1647374313.pdf"},
    {"nt": "2-03-P2", "titulo": "Sistemas de Chuveiros Automáticos Sprinklers – Parte 2 – Áreas de Armazenagem",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-2-03-sprinklers-Parte-2-Minuta-das-alteracoes_1604941555.pdf"},
    {"nt": "2-04", "titulo": "Conjunto de Pressurização para Sistemas de Combate a Incêndio",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/05/NT2-04_2Edio_2023.pdf"},
    {"nt": "2-05", "titulo": "Sinalização de Segurança Contra Incêndio e Pânico",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/05/NT2-05_3Edio_2023.pdf"},
    {"nt": "2-06", "titulo": "Iluminação de Emergência",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-2-06-Iluminacao-de-emergencia-Minuta-das-alteracoes_1605536471.pdf"},
    {"nt": "2-07", "titulo": "Sistema de Detecção e Alarme de Incêndio",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-2-07-Sistema-de-deteccao-e-alarme-de-incendio.pdf"},
    {"nt": "2-08", "titulo": "Saídas de Emergência em Edificações",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2026/01/NT_2-08_1Ed_2019_alterada_Portaria_1317_2025.pdf"},
    {"nt": "2-09", "titulo": "Pressurização de Escada de Emergência, Elevador de Emergência, Antecâmaras e Áreas de Refúgio",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/12/NT_2_09_2Ed_2025.pdf"},
    {"nt": "2-10", "titulo": "Plano de Emergência Contra Incêndio e Pânico (PECIP)",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-2-10-Plano-de-emergencia-contra-incendio-e-panico-PECIP.pdf"},
    {"nt": "2-11", "titulo": "Brigadas de Incêndio",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-2-11-Brigadas-de-incendio.pdf"},
    {"nt": "2-12", "titulo": "Sistema de Proteção Contra Descargas Atmosféricas (SPDA)",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/05/NT-2-12-SPDA-2019-Atualizada-Portaria_1179_2022.pdf"},
    {"nt": "2-13", "titulo": "Sistemas Fixos de Gases para Combate a Incêndio",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/05/NT2-13_2Edio_2023.pdf"},
    {"nt": "2-14", "titulo": "Controle de Fumaça",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-2-14-Controle-de-fumaca.pdf"},
    {"nt": "2-15", "titulo": "Hidrante Urbano",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/12/NT_2_15_2Ed_2025.pdf"},
    {"nt": "2-16", "titulo": "Acesso de Viaturas em Edificações",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-2-16-Acesso-de-viaturas-em-edificacoes-2020-versao-02.pdf"},
    {"nt": "2-17", "titulo": "Separação entre Edificações",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-2-17-Separacao-entre-edificacoes.pdf"},
    {"nt": "2-18", "titulo": "Compartimentação Horizontal e Vertical",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/05/NT-2-18-Compartimentao-horizontal-e-vertical-2022_1649879739.pdf"},
    {"nt": "2-19", "titulo": "Segurança Estrutural Contra Incêndio – Resistência ao Fogo",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2025/12/NT2_19_2Ed_2025_alterada_Portaria_1317_2025.pdf"},
    {"nt": "2-20", "titulo": "Controle de Materiais de Acabamento e de Revestimento",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-2-20-Controle-de-materiais-de-acabamento-e-de-revestimento.pdf"},

    # ── Grupo 3 – Riscos Específicos ──────────────────────────────────────────
    {"nt": "3-01", "titulo": "Cozinha Profissional",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-3-01-Cozinha-profissional.pdf"},
    {"nt": "3-02", "titulo": "Gás Combustível (GLP/GN) – Uso Predial",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2025/02/NT3-02_2Ed_2023_alterada_2025.pdf"},
    {"nt": "3-03", "titulo": "Grupos Geradores de Emergência em Edificações",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2026/01/NT_3-03_1Ed_2019_alterada_Portaria_1317_2025.pdf"},
    {"nt": "3-04", "titulo": "Subestações Elétricas",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-3-04-Subestacoes-eletricas.pdf"},
    {"nt": "3-05", "titulo": "Caldeiras e Vasos de Pressão",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-3-05-Caldeiras-e-vasos-de-pressao.pdf"},
    {"nt": "3-06", "titulo": "Armazenagem de Líquidos Inflamáveis e Combustíveis",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-3-06-Armazenagem-de-liquidos-inflamaveis-e-combustiveis.pdf"},
    {"nt": "3-07", "titulo": "Heliponto e Heliporto",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/05/NT3-07_2Edio_2023.pdf"},

    # ── Grupo 4 – Edificações Especiais ──────────────────────────────────────
    {"nt": "4-01", "titulo": "Quiosques e Áreas de Serviço",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/05/NT4-01_2Edio_2023.pdf"},
    {"nt": "4-02", "titulo": "Edificações Destinadas à Restrição de Liberdade",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-4-02-Edificacoes-destinadas-a-restricao-de-liberdade.pdf"},
    {"nt": "4-03", "titulo": "Edificações Tombadas",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-4-03-Edificacoes-tombadas.pdf"},
    {"nt": "4-04", "titulo": "Munições, Explosivos e Artefatos Pirotécnicos",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-4-04-Municoes-explosivos-e-artefatos-pirotecnicos-Fabricacao-armazenagem-e-comercio.pdf"},
    {"nt": "4-05", "titulo": "Gás GLP/GN – Manipulação, Armazenamento e Comercialização",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/05/NT-4-05-Gas-GLPGN-Manipulacao-armazenamento-e-comercializacao-2022.pdf"},
    {"nt": "4-06", "titulo": "Postos de Serviços e Abastecimento de Veículos",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-4-06-Postos-de-servicos-e-abastecimento-de-veiculos.pdf"},
    {"nt": "4-07", "titulo": "Edificações e Estruturas para Garagens",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-4-07-Edificacoes-e-estruturas-para-garagens.pdf"},
    {"nt": "4-08", "titulo": "Pátios para Armazenagens Diversas",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-4-08-Patios-para-armazenagens-diversas.pdf"},
    {"nt": "4-09", "titulo": "Túneis",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-4-09-Tuneis.pdf"},
    {"nt": "4-10", "titulo": "Canteiro de Obras",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-4-10-Canteiro-de-obras.pdf"},
    {"nt": "4-11", "titulo": "Estruturas Temporárias para Atendimento Médico",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/05/NT4-11_2Edio_2023.pdf"},

    # ── Grupo 5 – Reunião de Público e Eventos ────────────────────────────────
    {"nt": "5-01", "titulo": "Centros Esportivos, de Eventos e de Exibição",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-5-01-Centros-esportivos-de-eventos-e-de-exibicao.pdf"},
    {"nt": "5-02", "titulo": "Eventos Pirotécnicos",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2025/12/NT_5-02_3Ed_2025.pdf"},
    {"nt": "5-03", "titulo": "Carros Alegóricos, Trios Elétricos e Carros de Som",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2025/12/NT_5-03_2Ed_2025.pdf"},
    {"nt": "5-04", "titulo": "Eventos Temporários de Reunião de Público",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT_5-04_alterada_pela_Portaria_1167_2022_1644255940_2022-02-07-1.pdf"},
    {"nt": "5-05", "titulo": "Atendimento Médico para Eventos de Reunião de Público",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2022/04/NT-5-05-Atendimento-medico-para-eventos-de-reuniao-de-publico.pdf"},

    # ── COSCIP ────────────────────────────────────────────────────────────────
    {"nt": "COSCIP", "titulo": "Código de Segurança Contra Incêndio e Pânico – COSCIP (Decreto 42/2018 compilado)",
     "url": "https://www.cbmerj.rj.gov.br/wp-content/uploads/2024/05/COSCIP_DEC_42-2018_COMPILADO.pdf"},
]


def baixar_pdf(url: str, destino: Path) -> bool:
    """Tenta baixar um PDF. Retorna True se sucesso."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200 and len(r.content) > 1000:
            destino.write_bytes(r.content)
            return True
        print(f"    HTTP {r.status_code}, tamanho={len(r.content)}")
        return False
    except Exception as e:
        print(f"    Erro: {e}")
        return False


def baixar_todas_normas():
    """Baixa todas as NTs disponíveis."""
    PASTA_NORMAS.mkdir(exist_ok=True)
    (BASE / "dados").mkdir(exist_ok=True)

    resultados = []
    print(f"\n{'='*60}")
    print("  DOWNLOAD DAS NOTAS TÉCNICAS DO CBMERJ")
    print(f"{'='*60}\n")

    for norma in NORMAS_CBMERJ:
        nt = norma["nt"]
        titulo = norma["titulo"]
        url = norma["url"]
        destino = PASTA_NORMAS / f"NT-{nt}.pdf"

        if destino.exists():
            print(f"  ✓ NT-{nt} já existe — pulando")
            resultados.append({**norma, "arquivo": str(destino), "disponivel": True})
            continue

        print(f"  ↓ NT-{nt}: {titulo[:50]}...")
        ok = baixar_pdf(url, destino)

        if ok:
            tamanho = destino.stat().st_size // 1024
            print(f"  ✓ NT-{nt} baixada ({tamanho} KB)")
            resultados.append({**norma, "arquivo": str(destino), "disponivel": True})
        else:
            print(f"  ✗ NT-{nt} não disponível")
            resultados.append({**norma, "arquivo": None, "disponivel": False})

        time.sleep(0.3)

    ARQUIVO_INDICE.write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    baixadas = sum(1 for r in resultados if r["disponivel"])
    print(f"\n{'='*60}")
    print(f"  {baixadas}/{len(NORMAS_CBMERJ)} normas baixadas")
    print(f"  Catálogo salvo em: {ARQUIVO_INDICE}")
    print(f"{'='*60}\n")

    return resultados


if __name__ == "__main__":
    baixar_todas_normas()
    print("Próximo passo: python indexar.py")

"""Relatório gerencial do Auxiliar PJ.

Código originalmente desenvolvido no repositório relatorio-altomatizado-de-contas-.
Aceita CSV exportado pela API /api/pj/exportar.csv ou planilha .xlsx equivalente.
Execução: python relatorios/gerar_relatorio.py relatorios/exemplo-pj.csv --saida relatorio-pj.html
Este relatório não calcula impostos e não substitui documentos fiscais.
"""

import math
import pandas as pd
import argparse
from html import escape
import matplotlib
matplotlib.use("Agg")  # não precisa de interface gráfica
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import base64
from io import BytesIO

# ============================================================
# CONFIGURAÇÕES — ajuste aqui para a sua planilha
# ============================================================
ARQUIVO_ENTRADA = "lancamentos-pj.csv"   # CSV exportado pela API ou arquivo .xlsx
ABA = 0                                   # nome ou índice da aba (0 = primeira)

COLUNA_DATA = "Data"                      # coluna com datas (ou None se não tiver)
COLUNA_CATEGORIA = "Categoria"              # coluna categórica principal (ex: produto, região)
COLUNA_VALOR = "Valor"                    # coluna numérica a somar/analisar

ARQUIVO_SAIDA = "relatorio-pj.html"
# ============================================================


def carregar_dados(caminho: str, aba) -> pd.DataFrame:
    """Lê CSV da API ou planilha e faz limpeza básica."""
    if Path(caminho).suffix.lower() == ".csv":
        df = pd.read_csv(caminho, sep=";", encoding="utf-8-sig", decimal=".")
    else:
        df = pd.read_excel(caminho, sheet_name=aba)

    required = [column for column in (COLUNA_CATEGORIA, COLUNA_VALOR) if column]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing)}")

    # remove linhas totalmente vazias
    df = df.dropna(how="all")
    df[COLUNA_VALOR] = pd.to_numeric(df[COLUNA_VALOR], errors="coerce")
    df = df.dropna(subset=[COLUNA_CATEGORIA, COLUNA_VALOR])
    # Exclude +/- infinity: these values survive dropna and corrupt totals/charts.
    df = df[df[COLUNA_VALOR].map(math.isfinite)]
    if df.empty:
        raise ValueError("A planilha não possui registros válidos após a limpeza.")

    # converte a coluna de data, se existir
    if COLUNA_DATA and COLUNA_DATA in df.columns:
        df[COLUNA_DATA] = pd.to_datetime(df[COLUNA_DATA], errors="coerce")

    return df


def fig_para_base64(fig) -> str:
    """Converte uma figura matplotlib em string base64 para embutir no HTML."""
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def grafico_por_categoria(df: pd.DataFrame) -> str:
    """Gráfico de barras: soma do valor por categoria."""
    resumo = df.groupby(COLUNA_CATEGORIA)[COLUNA_VALOR].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    resumo.plot(kind="bar", ax=ax, color="#4C72B0")
    ax.set_title(f"{COLUNA_VALOR} total por {COLUNA_CATEGORIA}")
    ax.set_ylabel(COLUNA_VALOR)
    ax.set_xlabel(COLUNA_CATEGORIA)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig_para_base64(fig)


def grafico_temporal(df: pd.DataFrame) -> str | None:
    """Gráfico de linha: evolução do valor ao longo do tempo (se houver coluna de data)."""
    if not COLUNA_DATA or COLUNA_DATA not in df.columns:
        return None

    if df[COLUNA_DATA].notna().sum() == 0:
        return None
    serie = df.groupby(pd.Grouper(key=COLUNA_DATA, freq="MS"))[COLUNA_VALOR].sum()

    fig, ax = plt.subplots(figsize=(8, 4.5))
    serie.plot(kind="line", marker="o", ax=ax, color="#DD8452")
    ax.set_title(f"Evolução mensal de {COLUNA_VALOR}")
    ax.set_ylabel(COLUNA_VALOR)
    ax.set_xlabel("Período")
    plt.tight_layout()
    return fig_para_base64(fig)


def grafico_pizza(df: pd.DataFrame) -> str:
    """Gráfico de pizza: participação percentual por categoria."""
    resumo = df.groupby(COLUNA_CATEGORIA)[COLUNA_VALOR].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(6, 6))
    if (resumo < 0).any() or resumo.sum() <= 0:
        ax.text(0.5, 0.5, "Participação indisponível: totais negativos ou soma zero.",
                ha="center", va="center", wrap=True, transform=ax.transAxes)
        ax.axis("off")
    else:
        ax.pie(resumo, labels=resumo.index, autopct="%1.1f%%", startangle=90)
    ax.set_title(f"Participação de {COLUNA_VALOR} por {COLUNA_CATEGORIA}")
    plt.tight_layout()
    return fig_para_base64(fig)


def parse_aba(value: str):
    """Converte o seletor da aba para índice inteiro ou nome literal."""
    try:
        return int(value)
    except ValueError:
        return value


def montar_html(df: pd.DataFrame, imgs: dict, origem: str = ARQUIVO_ENTRADA) -> str:
    """Monta o relatório HTML final."""
    total = df[COLUNA_VALOR].sum()
    media = df[COLUNA_VALOR].mean()
    qtd_registros = len(df)
    top_categoria = df.groupby(COLUNA_CATEGORIA)[COLUNA_VALOR].sum().idxmax()

    resumo_pj = ""
    if "Tipo" in df.columns:
        tipos = df["Tipo"].astype(str).str.strip().str.upper()
        receitas = df.loc[tipos.eq("RECEITA"), COLUNA_VALOR].sum()
        despesas = df.loc[tipos.eq("DESPESA"), COLUNA_VALOR].sum()
        saldo = receitas - despesas
        resumo_pj = f"""
        <div class="cards">
            <div class="card"><div class="valor">R$ {receitas:,.2f}</div><div class="label">Receitas previstas</div></div>
            <div class="card"><div class="valor">R$ {despesas:,.2f}</div><div class="label">Despesas previstas</div></div>
            <div class="card"><div class="valor">R$ {saldo:,.2f}</div><div class="label">Saldo previsto</div></div>
        </div>
        """

    tabela_resumo = (
        df.groupby(COLUNA_CATEGORIA)[COLUNA_VALOR]
        .agg(["sum", "mean", "count"])
        .rename(columns={"sum": "Total", "mean": "Média", "count": "Registros"})
        .sort_values("Total", ascending=False)
        .round(2)
        .to_html(classes="tabela")
    )

    blocos_grafico = ""
    for titulo, img_b64 in imgs.items():
        if img_b64:
            blocos_grafico += f"""
            <div class="grafico">
                <h2>{titulo}</h2>
                <img src="data:image/png;base64,{img_b64}" alt="{titulo}">
            </div>
            """

    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Auxiliar PJ | Relatório gerencial</title>
<style>
    body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; background: #f7f7f9; }}
    h1 {{ color: #2c3e50; }}
    h2 {{ color: #34495e; margin-top: 30px; }}
    .cards {{ display: flex; gap: 20px; margin: 20px 0 40px 0; flex-wrap: wrap; }}
    .card {{ background: white; border-radius: 10px; padding: 20px 25px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); min-width: 160px; }}
    .card .valor {{ font-size: 24px; font-weight: bold; color: #4C72B0; }}
    .card .label {{ font-size: 13px; color: #777; margin-top: 4px; }}
    .grafico {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 25px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
    .grafico img {{ max-width: 100%; }}
    table.tabela {{ border-collapse: collapse; width: 100%; background: white; }}
    table.tabela th, table.tabela td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: right; }}
    table.tabela th {{ background: #4C72B0; color: white; }}
    table.tabela td:first-child, table.tabela th:first-child {{ text-align: left; }}
    footer {{ margin-top: 40px; font-size: 12px; color: #999; }}
</style>
</head>
<body>
    <h1>Auxiliar PJ — Relatório financeiro</h1>
    <p>Gerado a partir de <b>{escape(str(origem))}</b> em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>

    {resumo_pj}

    <div class="cards">
        <div class="card"><div class="valor">{total:,.2f}</div><div class="label">Volume total ({COLUNA_VALOR})</div></div>
        <div class="card"><div class="valor">{media:,.2f}</div><div class="label">Média ({COLUNA_VALOR})</div></div>
        <div class="card"><div class="valor">{qtd_registros}</div><div class="label">Registros</div></div>
        <div class="card"><div class="valor">{escape(str(top_categoria))}</div><div class="label">Top {escape(COLUNA_CATEGORIA)}</div></div>
    </div>

    {blocos_grafico}

    <h2>Tabela resumo por {COLUNA_CATEGORIA}</h2>
    {tabela_resumo}

    <footer>Relatório gerencial automatizado. Não substitui contabilidade, apuração tributária ou documentos fiscais.</footer>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Gera relatório HTML a partir de CSV exportado ou planilha Excel.")
    parser.add_argument("arquivo", nargs="?", default=ARQUIVO_ENTRADA, help="Caminho do arquivo .csv ou .xlsx")
    parser.add_argument("--aba", type=parse_aba, default=ABA, help="Índice (0-based) ou nome da aba")
    parser.add_argument("--saida", default=ARQUIVO_SAIDA, help="Caminho do HTML gerado")
    args = parser.parse_args()

    caminho = Path(args.arquivo)
    if not caminho.exists():
        parser.error(f"Arquivo não encontrado: {caminho}")

    print(f"Lendo {caminho} ...")
    try:
        df = carregar_dados(str(caminho), args.aba)
    except ValueError as error:
        parser.error(str(error))
    print(f"{len(df)} linhas carregadas.")

    print("Gerando gráficos...")
    imgs = {
        f"Total por {COLUNA_CATEGORIA}": grafico_por_categoria(df),
        "Evolução no tempo": grafico_temporal(df),
        f"Participação por {COLUNA_CATEGORIA}": grafico_pizza(df),
    }

    print("Montando relatório...")
    html = montar_html(df, imgs, origem=str(caminho))

    Path(args.saida).write_text(html, encoding="utf-8")
    print(f"Relatório salvo em: {args.saida}")


if __name__ == "__main__":
    main()

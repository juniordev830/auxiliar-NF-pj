"""Relatório gerencial do Auxiliar PJ.

Código originalmente desenvolvido no repositório relatorio-altomatizado-de-contas-.
Aceita CSV exportado pela API /api/pj/exportar.csv ou planilha .xlsx equivalente.
Execução: python relatorios/gerar_relatorio.py relatorios/exemplo-pj.csv --saida relatorio-pj.html
Este relatório não calcula impostos e não substitui documentos fiscais.
"""

import warnings
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
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


CENTAVOS = "_valor_centavos"

def centavos(value):
    """Parse decimal text exactly; reject invalid values or fractional cents."""
    try:
        amount = Decimal(str(value).strip())
        if not amount.is_finite() or abs(amount) > Decimal("100000000"):
            return None
        with localcontext() as ctx:
            ctx.prec = 40
            scaled = amount * 100
            return int(scaled) if scaled == scaled.to_integral_value() else None
    except (InvalidOperation, ValueError, TypeError):
        return None

def moeda(value):
    """Format integer or Decimal cents in Brazilian notation."""
    with localcontext() as ctx:
        ctx.prec = 40
        amount = (Decimal(value) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return "R$ " + f"{amount:,.2f}".translate(str.maketrans(",.", ".,"))

def valores_exatos(df):
    if CENTAVOS in df:
        return [int(v) for v in df[CENTAVOS]]
    values = [centavos(v) for v in df[COLUNA_VALOR]]
    if any(v is None for v in values):
        raise ValueError("Valor inválido ou com mais de duas casas decimais.")
    return values

def carregar_dados(caminho: str, aba) -> pd.DataFrame:
    """Lê CSV da API ou planilha e faz limpeza básica."""
    if Path(caminho).suffix.lower() == ".csv":
        df = pd.read_csv(caminho, sep=";", encoding="utf-8-sig", dtype={COLUNA_VALOR: str})
    else:
        df = pd.read_excel(caminho, sheet_name=aba)

    required = [column for column in (COLUNA_CATEGORIA, COLUNA_VALOR) if column]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing)}")

    df = df.dropna(how="all").copy()
    rejected = []
    valid = []
    values = []
    for position, (_, row) in enumerate(df.iterrows(), start=1):
        value = centavos(row[COLUNA_VALOR])
        category = row[COLUNA_CATEGORIA]
        reason = None
        if pd.isna(category) or not str(category).strip():
            reason = "categoria ausente"
        elif value is None:
            reason = "valor inválido, fora do limite ou fracionário"
        elif "Tipo" in df.columns:
            if str(row["Tipo"]).strip().upper() not in ("RECEITA", "DESPESA"):
                reason = "tipo inválido"
            elif value <= 0:
                reason = "valor PJ deve ser positivo"
        if reason:
            rejected.append(f"Registro {position}: {reason}")
        else:
            valid.append(position - 1)
            values.append(value)
    df = df.iloc[valid].copy()
    if df.empty:
        raise ValueError("A planilha não possui registros válidos após a limpeza. " + "; ".join(rejected[:20]))
    df[CENTAVOS] = pd.Series(values, index=df.index, dtype=object)
    # Only charts use the floating-point projection; monetary totals use cents.
    df[COLUNA_VALOR] = [v / 100 for v in values]
    invalid_dates = 0
    if COLUNA_DATA and COLUNA_DATA in df.columns:
        df[COLUNA_DATA] = pd.to_datetime(df[COLUNA_DATA], format="mixed", errors="coerce")
        invalid_dates = int(df[COLUNA_DATA].isna().sum())
    df.attrs["rejected"] = rejected
    df.attrs["invalid_dates"] = invalid_dates
    if rejected or invalid_dates:
        warnings.warn(f"{len(rejected)} registro(s) rejeitado(s); {invalid_dates} data(s) ausente(s)/inválida(s). Consulte o relatório.", UserWarning)
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
    cents = valores_exatos(df)
    total = sum(cents)
    qtd_registros = len(df)
    media = Decimal(total) / qtd_registros
    groups = {}
    for category, amount in zip(df[COLUNA_CATEGORIA], cents):
        groups.setdefault(str(category), []).append(amount)
    top_categoria = max(groups, key=lambda key: sum(groups[key]))
    rejected = df.attrs.get("rejected", [])
    invalid_dates = df.attrs.get("invalid_dates", 0)
    quality = ""
    if rejected or invalid_dates:
        details = "".join(f"<li>{escape(reason)}</li>" for reason in rejected)
        quality = f"<section><h2>Atenção: qualidade dos dados</h2><p>{len(rejected)} registro(s) rejeitado(s); {invalid_dates} data(s) inválida(s)/ausente(s), não incluída(s) no gráfico temporal.</p><ul>{details}</ul></section>"

    resumo_pj = ""
    if "Tipo" in df.columns:
        tipos = df["Tipo"].astype(str).str.strip().str.upper()
        receitas = sum(v for t, v in zip(tipos, cents) if t == "RECEITA")
        despesas = sum(v for t, v in zip(tipos, cents) if t == "DESPESA")
        saldo = receitas - despesas
        resumo_pj = f"""
        <div class="cards">
            <div class="card"><div class="valor">{moeda(receitas)}</div><div class="label">Receitas previstas</div></div>
            <div class="card"><div class="valor">{moeda(despesas)}</div><div class="label">Despesas previstas</div></div>
            <div class="card"><div class="valor">{moeda(saldo)}</div><div class="label">Saldo previsto</div></div>
        </div>
        """

    tabela_resumo = pd.DataFrame([
        {"Categoria": key, "Total": moeda(sum(items)),
         "Média": moeda(Decimal(sum(items)) / len(items)), "Registros": len(items)}
        for key, items in sorted(groups.items(), key=lambda pair: sum(pair[1]), reverse=True)
    ]).to_html(classes="tabela", index=False, escape=True)

    blocos_grafico = ""
    for titulo, img_b64 in imgs.items():
        if img_b64:
            titulo_seguro = escape(str(titulo), quote=True)
            imagem_segura = escape(str(img_b64), quote=True)
            blocos_grafico += f"""
            <div class="grafico">
                <h2>{titulo_seguro}</h2>
                <img src="data:image/png;base64,{imagem_segura}" alt="{titulo_seguro}">
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

    {quality}
    {resumo_pj}

    <div class="cards">
        <div class="card"><div class="valor">{moeda(total)}</div><div class="label">Volume total ({escape(COLUNA_VALOR)})</div></div>
        <div class="card"><div class="valor">{moeda(media)}</div><div class="label">Média ({escape(COLUNA_VALOR)})</div></div>
        <div class="card"><div class="valor">{qtd_registros}</div><div class="label">Registros</div></div>
        <div class="card"><div class="valor">{escape(str(top_categoria))}</div><div class="label">Top {escape(COLUNA_CATEGORIA)}</div></div>
    </div>

    {blocos_grafico}

    <h2>Tabela resumo por {escape(COLUNA_CATEGORIA)}</h2>
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
    saida = Path(args.saida)
    if not caminho.exists():
        parser.error(f"Arquivo não encontrado: {caminho}")

    try:
        if saida.exists() and saida.samefile(caminho):
            parser.error("O arquivo de saída deve ser diferente do arquivo de entrada.")
    except OSError as error:
        parser.error(str(error))

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

    try:
        saida.write_text(html, encoding="utf-8")
    except OSError as error:
        parser.error(str(error))
    print(f"Relatório salvo em: {args.saida}")


if __name__ == "__main__":
    main()

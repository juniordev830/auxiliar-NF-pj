using System.Globalization;
using System.Text;
using Microsoft.EntityFrameworkCore;

namespace ControladorGastos.PJ;

public static class AuxiliarPjEndpoints
{
    public static void MapAuxiliarPjEndpoints(this WebApplication app)
    {
        var pj = app.MapGroup("/api/pj");

        pj.MapGet("/lancamentos", async Task<IResult> (
            int? ano, int? mes, string? tipo, string? status, int? page, int? limit,
            AuxiliarPjContext db) =>
        {
            var erro = ValidarPeriodo(ano, mes);
            if (erro is not null) return Results.BadRequest(new { error = erro });
            if (!TipoValido(tipo) || !StatusValido(status))
                return Results.BadRequest(new { error = "Filtros tipo ou status inválidos." });

            var pagina = page ?? 1;
            var tamanho = limit ?? 50;
            if (pagina is < 1 or > 100_000 || tamanho is < 1 or > 100)
                return Results.BadRequest(new { error = "Use page de 1 a 100000 e limit de 1 a 100." });

            var rows = await Filtrar(db, ano, mes, tipo).ToListAsync();
            var statusNormalizado = status?.Trim().ToUpperInvariant();
            if (!string.IsNullOrEmpty(statusNormalizado))
                rows = rows.Where(x => Situacao(x) == statusNormalizado).ToList();

            var total = rows.Count;
            var items = rows.OrderByDescending(x => x.Competencia).ThenByDescending(x => x.Id)
                .Skip((pagina - 1) * tamanho).Take(tamanho).Select(Apresentar).ToList();
            return Results.Ok(new { items, total, page = pagina, limit = tamanho });
        });

        pj.MapPost("/lancamentos", async Task<IResult> (LancamentoPjInput input, AuxiliarPjContext db) =>
        {
            var erro = ValidarLancamento(input);
            if (erro is not null) return Results.BadRequest(new { error = erro });

            var row = new LancamentoPj
            {
                Descricao = input.Descricao!.Trim(),
                Tipo = input.Tipo!.Trim().ToUpperInvariant(),
                Categoria = input.Categoria!.Trim(),
                Contraparte = string.IsNullOrWhiteSpace(input.Contraparte) ? null : input.Contraparte.Trim(),
                Valor = input.Valor,
                Competencia = input.Competencia.Date,
                Vencimento = input.Vencimento?.Date,
                DataPagamento = input.DataPagamento?.Date
            };
            db.Lancamentos.Add(row);
            await db.SaveChangesAsync();
            return Results.Created($"/api/pj/lancamentos/{row.Id}", Apresentar(row));
        });

        pj.MapPut("/lancamentos/{id:int}/pagamento", async Task<IResult> (
            int id, PagamentoPjInput input, AuxiliarPjContext db) =>
        {
            if (input.DataPagamento.HasValue && !DataValida(input.DataPagamento.Value))
                return Results.BadRequest(new { error = "Data do pagamento inválida." });
            var row = await db.Lancamentos.FindAsync(id);
            if (row is null) return Results.NotFound(new { error = "Lançamento não encontrado." });
            row.DataPagamento = input.DataPagamento?.Date;
            await db.SaveChangesAsync();
            return Results.Ok(Apresentar(row));
        });

        pj.MapDelete("/lancamentos/{id:int}", async Task<IResult> (int id, AuxiliarPjContext db) =>
        {
            var row = await db.Lancamentos.FindAsync(id);
            if (row is null) return Results.NotFound(new { error = "Lançamento não encontrado." });
            db.Lancamentos.Remove(row);
            await db.SaveChangesAsync();
            return Results.NoContent();
        });

        pj.MapGet("/resumo", async Task<IResult> (int? ano, int? mes, AuxiliarPjContext db) =>
        {
            var erro = ValidarPeriodo(ano, mes);
            if (erro is not null) return Results.BadRequest(new { error = erro });
            var hoje = DateTime.UtcNow.Date;
            var efetivoAno = ano ?? hoje.Year;
            var efetivoMes = mes ?? hoje.Month;
            var rows = await Filtrar(db, efetivoAno, efetivoMes, null).ToListAsync();

            var receitas = rows.Where(x => x.Tipo == "RECEITA").Sum(x => x.Valor);
            var despesas = rows.Where(x => x.Tipo == "DESPESA").Sum(x => x.Valor);
            var receitasRecebidas = rows.Where(x => x.Tipo == "RECEITA" && x.DataPagamento.HasValue)
                .Sum(x => x.Valor);
            var despesasPagas = rows.Where(x => x.Tipo == "DESPESA" && x.DataPagamento.HasValue)
                .Sum(x => x.Valor);
            var atrasados = rows.Where(x => Situacao(x) == "ATRASADO").ToList();
            var categorias = rows.GroupBy(x => new { x.Tipo, x.Categoria })
                .Select(g => new { g.Key.Tipo, g.Key.Categoria, Valor = g.Sum(x => x.Valor), Quantidade = g.Count() })
                .OrderBy(x => x.Tipo).ThenByDescending(x => x.Valor).ToList();

            return Results.Ok(new
            {
                ano = efetivoAno,
                mes = efetivoMes,
                receitasPrevistas = receitas,
                despesasPrevistas = despesas,
                saldoPrevisto = receitas - despesas,
                receitasRecebidas,
                despesasPagas,
                saldoRealizado = receitasRecebidas - despesasPagas,
                aReceber = receitas - receitasRecebidas,
                aPagar = despesas - despesasPagas,
                quantidadeAtrasada = atrasados.Count,
                valorAtrasado = atrasados.Sum(x => x.Valor),
                quantidade = rows.Count,
                categorias
            });
        });

        // Arquivo compatível com o gerador Python migrado do repositório nº 2.
        pj.MapGet("/exportar.csv", async Task<IResult> (int? ano, int? mes, AuxiliarPjContext db) =>
        {
            var erro = ValidarPeriodo(ano, mes);
            if (erro is not null) return Results.BadRequest(new { error = erro });
            var rows = await Filtrar(db, ano, mes, null)
                .OrderBy(x => x.Competencia).ThenBy(x => x.Id).ToListAsync();

            var csv = new StringBuilder("Data;Categoria;Valor;Tipo;Descricao;Status;Contraparte;Vencimento;Pagamento\r\n");
            foreach (var row in rows)
            {
                var fields = new[]
                {
                    row.Competencia.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture),
                    $"{row.Tipo} / {row.Categoria}",
                    row.Valor.ToString("0.00", CultureInfo.InvariantCulture),
                    row.Tipo,
                    row.Descricao,
                    Situacao(row),
                    row.Contraparte ?? "",
                    row.Vencimento?.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture) ?? "",
                    row.DataPagamento?.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture) ?? ""
                };
                csv.AppendLine(string.Join(";", fields.Select(EscaparCsv)));
            }
            var bytes = Encoding.UTF8.GetPreamble().Concat(Encoding.UTF8.GetBytes(csv.ToString())).ToArray();
            return Results.File(bytes, "text/csv; charset=utf-8", "lancamentos-pj.csv");
        });
    }

    private static IQueryable<LancamentoPj> Filtrar(
        AuxiliarPjContext db, int? ano, int? mes, string? tipo)
    {
        var query = db.Lancamentos.AsNoTracking().AsQueryable();
        if (ano.HasValue)
        {
            var inicio = new DateTime(ano.Value, mes ?? 1, 1);
            var fim = mes.HasValue ? inicio.AddMonths(1) : inicio.AddYears(1);
            query = query.Where(x => x.Competencia >= inicio && x.Competencia < fim);
        }
        if (!string.IsNullOrWhiteSpace(tipo))
        {
            var t = tipo.Trim().ToUpperInvariant();
            query = query.Where(x => x.Tipo == t);
        }
        return query;
    }

    private static string? ValidarPeriodo(int? ano, int? mes)
    {
        if (ano.HasValue && ano is < 2000 or > 2200) return "Ano deve estar entre 2000 e 2200.";
        if (mes.HasValue && mes is < 1 or > 12) return "Mês deve estar entre 1 e 12.";
        if (mes.HasValue && !ano.HasValue) return "Informe ano ao filtrar por mês.";
        return null;
    }

    private static bool TipoValido(string? tipo) =>
        string.IsNullOrWhiteSpace(tipo) || tipo.Trim().ToUpperInvariant() is "RECEITA" or "DESPESA";

    private static bool StatusValido(string? status) =>
        string.IsNullOrWhiteSpace(status) || status.Trim().ToUpperInvariant() is "PAGO" or "PENDENTE" or "ATRASADO";

    private static string? ValidarLancamento(LancamentoPjInput input)
    {
        if (string.IsNullOrWhiteSpace(input.Descricao) || input.Descricao.Trim().Length > 200)
            return "Descrição deve ter entre 1 e 200 caracteres.";
        if (!TipoValido(input.Tipo) || string.IsNullOrWhiteSpace(input.Tipo))
            return "Tipo deve ser RECEITA ou DESPESA.";
        if (string.IsNullOrWhiteSpace(input.Categoria) || input.Categoria.Trim().Length > 80)
            return "Categoria deve ter entre 1 e 80 caracteres.";
        if (input.Contraparte?.Length > 120) return "Contraparte pode ter até 120 caracteres.";
        if (input.Valor <= 0 || input.Valor > 100_000_000m ||
            input.Valor != decimal.Round(input.Valor, 2))
            return "Valor deve ser positivo, até 100 milhões, com no máximo 2 casas decimais.";
        if (!DataValida(input.Competencia)) return "Data de competência inválida.";
        if (input.Vencimento.HasValue && !DataValida(input.Vencimento.Value))
            return "Data de vencimento inválida.";
        if (input.DataPagamento.HasValue && !DataValida(input.DataPagamento.Value))
            return "Data de pagamento inválida.";
        return null;
    }

    private static bool DataValida(DateTime date) => date.Year is >= 2000 and <= 2200;

    private static string Situacao(LancamentoPj row) =>
        row.DataPagamento.HasValue ? "PAGO"
        : row.Vencimento.HasValue && row.Vencimento.Value.Date < DateTime.UtcNow.Date ? "ATRASADO"
        : "PENDENTE";

    private static object Apresentar(LancamentoPj row) => new
    {
        row.Id, row.Descricao, row.Tipo, row.Categoria, row.Contraparte,
        row.Valor, row.Competencia, row.Vencimento, row.DataPagamento,
        Status = Situacao(row), row.CriadoEm
    };

    // Evita CSV injection ao abrir textos em aplicativos de planilha.
    private static string EscaparCsv(string value)
    {
        var candidate = value.TrimStart();
        if (candidate.Length > 0 && "=+-@\t\r".Contains(candidate[0]))
            value = "'" + value;
        return "\"" + value.Replace("\"", "\"\"") + "\"";
    }
}

public sealed record LancamentoPjInput(
    string? Descricao, string? Tipo, string? Categoria, decimal Valor,
    DateTime Competencia, DateTime? Vencimento, DateTime? DataPagamento, string? Contraparte);
public sealed record PagamentoPjInput(DateTime? DataPagamento);

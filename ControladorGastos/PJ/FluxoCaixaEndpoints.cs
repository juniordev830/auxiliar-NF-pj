using Microsoft.EntityFrameworkCore;

namespace ControladorGastos.PJ;

public static class FluxoCaixaEndpoints
{
    // Fluxo por data efetiva de pagamento, independentemente da competência.
    public static void MapFluxoCaixaEndpoints(this WebApplication app)
    {
        app.MapGet("/api/pj/fluxo-caixa", async Task<IResult> (
            int ano, int mes, AuxiliarPjContext db, CancellationToken cancellationToken) =>
        {
            if (ano is < 2000 or > 2200 || mes is < 1 or > 12)
                return Results.BadRequest(new { error = "Informe ano entre 2000 e 2200 e mês entre 1 e 12." });

            var inicio = new DateTime(ano, mes, 1);
            var fim = inicio.AddMonths(1);
            // SQLite armazena decimal como texto. Somar em C# mantém a precisão monetária.
            var dias = new SortedDictionary<int, TotaisDia>();
            await foreach (var row in db.Lancamentos.AsNoTracking()
                .Where(x => x.DataPagamento >= inicio && x.DataPagamento < fim)
                .Select(x => new { x.DataPagamento, x.Tipo, x.Valor })
                .AsAsyncEnumerable().WithCancellation(cancellationToken))
            {
                var dia = row.DataPagamento!.Value.Day;
                var totais = dias.GetValueOrDefault(dia) ?? new TotaisDia();
                if (row.Tipo == "RECEITA") totais.Receitas += row.Valor;
                else if (row.Tipo == "DESPESA") totais.Despesas += row.Valor;
                totais.Quantidade++;
                dias[dia] = totais;
            }
            var receitas = dias.Values.Sum(x => x.Receitas);
            var despesas = dias.Values.Sum(x => x.Despesas);
            return Results.Ok(new
            {
                ano, mes, receitas, despesas, saldo = receitas - despesas,
                quantidade = dias.Values.Sum(x => x.Quantidade),
                dias = dias.Select(x => new
                {
                    data = new DateTime(ano, mes, x.Key).ToString("yyyy-MM-dd", System.Globalization.CultureInfo.InvariantCulture),
                    x.Value.Receitas, x.Value.Despesas,
                    saldo = x.Value.Receitas - x.Value.Despesas, x.Value.Quantidade
                }).ToArray()
            });
        });
    }

    private sealed class TotaisDia
    {
        public decimal Receitas { get; set; }
        public decimal Despesas { get; set; }
        public int Quantidade { get; set; }
    }
}

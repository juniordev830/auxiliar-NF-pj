using Microsoft.EntityFrameworkCore;

namespace ControladorGastos.PJ;

public static class ContasAVencerEndpoints
{
    public static void MapContasAVencerEndpoints(this WebApplication app)
    {
        app.MapGet("/api/pj/contas-a-vencer", async Task<IResult> (
            DateOnly referencia, AuxiliarPjContext db, CancellationToken cancellationToken) =>
        {
            if (referencia.Year is < 2000 or > 2200)
                return Results.BadRequest(new { error = "Data de referência fora do intervalo permitido." });

            var buckets = new[] { new Faixa("ATRASADO"), new Faixa("HOJE"),
                new Faixa("ATE_7_DIAS"), new Faixa("ATE_30_DIAS"),
                new Faixa("MAIS_DE_30_DIAS"), new Faixa("SEM_VENCIMENTO") };

            await foreach (var item in db.Lancamentos.AsNoTracking()
                .Where(x => x.DataPagamento == null)
                .Select(x => new { x.Vencimento, x.Tipo, x.Valor })
                .AsAsyncEnumerable().WithCancellation(cancellationToken))
            {
                var dias = item.Vencimento.HasValue
                    ? DateOnly.FromDateTime(item.Vencimento.Value).DayNumber - referencia.DayNumber
                    : (int?)null;
                var faixa = buckets[dias switch
                {
                    null => 5, < 0 => 0, 0 => 1, <= 7 => 2, <= 30 => 3, _ => 4
                }];
                if (item.Tipo == "RECEITA") faixa.Receitas += item.Valor;
                else if (item.Tipo == "DESPESA") faixa.Despesas += item.Valor;
                faixa.Quantidade++;
            }

            return Results.Ok(new
            {
                referencia,
                aReceber = buckets.Sum(x => x.Receitas),
                aPagar = buckets.Sum(x => x.Despesas),
                quantidade = buckets.Sum(x => x.Quantidade),
                faixas = buckets.Select(x => new
                {
                    x.Nome, aReceber = x.Receitas, aPagar = x.Despesas,
                    saldoPrevisto = x.Receitas - x.Despesas, x.Quantidade
                }).ToArray()
            });
        });
    }

    private sealed class Faixa(string nome)
    {
        public string Nome { get; } = nome;
        public decimal Receitas { get; set; }
        public decimal Despesas { get; set; }
        public int Quantidade { get; set; }
    }
}

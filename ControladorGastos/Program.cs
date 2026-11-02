using ControladorGastos.Data;
using ControladorGastos.Models;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? "Data Source=controlador-gastos.db";
builder.Services.AddDbContext<ControladorGastosContext>(options => options.UseSqlite(connectionString));

var app = builder.Build();

// Bootstrap simples para o protótipo local. Para produção, substitua por migrations versionadas.
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<ControladorGastosContext>();
    db.Database.EnsureCreated();
}

app.MapGet("/api/health", () => Results.Ok(new { status = "ok" }));

app.MapGet("/api/pessoas", async (ControladorGastosContext db) =>
    Results.Ok(await db.Pessoas.AsNoTracking()
        .OrderBy(x => x.Nome)
        .Select(x => new { x.Id, x.Nome, x.Idade, x.DataCriacao })
        .ToListAsync()));

app.MapPost("/api/pessoas", async Task<IResult> (PessoaInput input, ControladorGastosContext db) =>
{
    var nome = input.Nome?.Trim();
    if (string.IsNullOrWhiteSpace(nome) || nome.Length > 100)
        return Results.BadRequest(new { error = "O nome deve ter entre 1 e 100 caracteres." });
    if (input.Idade is null or < 0 or > 120)
        return Results.BadRequest(new { error = "A idade deve estar entre 0 e 120." });

    var pessoa = new Pessoa { Nome = nome, Idade = input.Idade.Value };
    db.Pessoas.Add(pessoa);
    await db.SaveChangesAsync();
    return Results.Created($"/api/pessoas/{pessoa.Id}",
        new { pessoa.Id, pessoa.Nome, pessoa.Idade, pessoa.DataCriacao });
});

app.MapDelete("/api/pessoas/{id:int}", async Task<IResult> (int id, ControladorGastosContext db) =>
{
    var pessoa = await db.Pessoas.FindAsync(id);
    if (pessoa is null) return Results.NotFound(new { error = "Pessoa não encontrada." });
    db.Pessoas.Remove(pessoa);
    await db.SaveChangesAsync();
    return Results.NoContent();
});

app.MapGet("/api/transacoes", async (ControladorGastosContext db) =>
    Results.Ok(await db.Transacoes.AsNoTracking()
        .OrderByDescending(x => x.DataCriacao)
        .Select(x => new { x.Id, x.Descricao, x.Valor, x.Tipo, x.PessoaId, PessoaNome = x.Pessoa.Nome, x.DataCriacao })
        .ToListAsync()));

app.MapPost("/api/transacoes", async Task<IResult> (TransacaoInput input, ControladorGastosContext db) =>
{
    var descricao = input.Descricao?.Trim();
    if (string.IsNullOrWhiteSpace(descricao) || descricao.Length > 200)
        return Results.BadRequest(new { error = "A descrição deve ter entre 1 e 200 caracteres." });
    if (input.Valor <= 0 || input.Valor > 100_000_000m)
        return Results.BadRequest(new { error = "O valor deve ser positivo e não pode exceder 100.000.000." });
    if (input.Valor != decimal.Round(input.Valor, 2, MidpointRounding.ToEven))
        return Results.BadRequest(new { error = "O valor deve ter no máximo duas casas decimais." });

    var tipo = input.Tipo?.Trim().ToUpperInvariant();
    if (tipo is not ("RECEITA" or "DESPESA"))
        return Results.BadRequest(new { error = "O tipo deve ser RECEITA ou DESPESA." });

    var pessoa = await db.Pessoas.FindAsync(input.PessoaId);
    if (pessoa is null) return Results.BadRequest(new { error = "Pessoa não encontrada." });
    if (pessoa.Idade < 18 && tipo == "RECEITA")
        return Results.BadRequest(new { error = "Menores de idade não podem registrar receitas." });

    var transacao = new Transacao { Descricao = descricao, Valor = decimal.Round(input.Valor, 2), Tipo = tipo, PessoaId = pessoa.Id };
    db.Transacoes.Add(transacao);
    await db.SaveChangesAsync();
    return Results.Created($"/api/transacoes/{transacao.Id}",
        new { transacao.Id, transacao.Descricao, transacao.Valor, transacao.Tipo, transacao.PessoaId, PessoaNome = pessoa.Nome, transacao.DataCriacao });
});

app.MapGet("/api/transacoes/totais/resumo", async (ControladorGastosContext db) =>
{
    var transacoes = await db.Transacoes.AsNoTracking()
        .Select(x => new { x.Valor, x.Tipo, x.PessoaId, PessoaNome = x.Pessoa.Nome })
        .ToListAsync();
    var receitas = transacoes.Where(x => x.Tipo == "RECEITA").Sum(x => x.Valor);
    var despesas = transacoes.Where(x => x.Tipo == "DESPESA").Sum(x => x.Valor);
    var porPessoa = transacoes.GroupBy(x => new { x.PessoaId, x.PessoaNome })
        .Select(g => new {
            g.Key.PessoaId,
            g.Key.PessoaNome,
            Receitas = g.Where(x => x.Tipo == "RECEITA").Sum(x => x.Valor),
            Despesas = g.Where(x => x.Tipo == "DESPESA").Sum(x => x.Valor),
            Saldo = g.Where(x => x.Tipo == "RECEITA").Sum(x => x.Valor)
                - g.Where(x => x.Tipo == "DESPESA").Sum(x => x.Valor)
        }).OrderBy(x => x.PessoaNome).ToList();
    return Results.Ok(new { totalReceitas = receitas, totalDespesas = despesas, saldoGeral = receitas - despesas, porPessoa });
});

// A API ainda não tem autenticação; mantenha-a restrita ao loopback por padrão.
app.Urls.Clear();
app.Urls.Add("http://127.0.0.1:5000");

app.Run();

public sealed record PessoaInput(string? Nome, int? Idade);
public sealed record TransacaoInput(string? Descricao, decimal Valor, string? Tipo, int PessoaId);

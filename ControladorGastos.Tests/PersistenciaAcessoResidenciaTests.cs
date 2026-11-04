using ControladorGastos.Security;
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;
using Xunit;

namespace ControladorGastos.Tests;

public sealed class PersistenciaAcessoResidenciaTests
{
    private static async Task<(SqliteConnection Connection, AcessoResidencialContext Db)> AbrirBancoAsync()
    {
        var connection = new SqliteConnection("Data Source=:memory:");
        await connection.OpenAsync();
        var options = new DbContextOptionsBuilder<AcessoResidencialContext>()
            .UseSqlite(connection).Options;
        var db = new AcessoResidencialContext(options);
        await db.Database.EnsureCreatedAsync(); // SQLite isolado de teste, não o banco financeiro.
        return (connection, db);
    }

    [Fact]
    public async Task PermissoesPersistidasNegamAcessoEntreResidencias()
    {
        var (connection, db) = await AbrirBancoAsync();
        await using var _ = connection;
        await using var context = db;
        var alice = new ContaAcesso { Emissor = "https://identidade.example", SujeitoExterno = "alice" };
        var bob = new ContaAcesso { Emissor = "https://identidade.example", SujeitoExterno = "bob" };
        var casaA = new ResidenciaAcesso { Nome = "Residencia A" };
        var casaB = new ResidenciaAcesso { Nome = "Residencia B" };
        db.AddRange(alice, bob, casaA, casaB);
        await db.SaveChangesAsync();

        db.Vinculos.AddRange(
            new VinculoAcesso { UsuarioId = alice.Id, ResidenciaId = casaA.Id, Papel = PapelResidencia.Administrador },
            new VinculoAcesso { UsuarioId = bob.Id, ResidenciaId = casaB.Id, Papel = PapelResidencia.Leitor });
        await db.SaveChangesAsync();

        Assert.True(await ConsultaAcessoResidencia.PermiteAsync(db, alice.Id, casaA.Id, AcaoResidencia.Excluir));
        Assert.False(await ConsultaAcessoResidencia.PermiteAsync(db, alice.Id, casaB.Id, AcaoResidencia.Consultar));
        Assert.False(await ConsultaAcessoResidencia.PermiteAsync(db, bob.Id, casaA.Id, AcaoResidencia.Consultar));
        Assert.True(await ConsultaAcessoResidencia.PermiteAsync(db, bob.Id, casaB.Id, AcaoResidencia.Consultar));
        Assert.False(await ConsultaAcessoResidencia.PermiteAsync(db, bob.Id, casaB.Id, AcaoResidencia.Registrar));
        Assert.False(await ConsultaAcessoResidencia.PermiteAsync(db, bob.Id, casaB.Id, AcaoResidencia.Excluir));
        Assert.False(await ConsultaAcessoResidencia.PermiteAsync(db, null, casaA.Id, AcaoResidencia.Consultar));
    }

    [Fact]
    public async Task MesmoSubjectEmEmissoresDiferentesPodeSerContaDistinta()
    {
        var (connection, db) = await AbrirBancoAsync();
        await using var _ = connection;
        await using var context = db;
        db.Contas.AddRange(
            new ContaAcesso { Emissor = "https://idp-a.example", SujeitoExterno = "shared-id" },
            new ContaAcesso { Emissor = "https://idp-b.example", SujeitoExterno = "shared-id" });
        await db.SaveChangesAsync();
        Assert.Equal(2, await db.Contas.CountAsync());
    }

    [Fact]
    public async Task MesmoEmissorESubjectNaoGeramContasDuplicadas()
    {
        var (connection, db) = await AbrirBancoAsync();
        await using var _ = connection;
        await using var context = db;
        db.Contas.Add(new ContaAcesso { Emissor = "https://idp.example", SujeitoExterno = "same-user" });
        await db.SaveChangesAsync();
        db.Contas.Add(new ContaAcesso { Emissor = "https://idp.example", SujeitoExterno = "same-user" });
        await Assert.ThrowsAsync<DbUpdateException>(() => db.SaveChangesAsync());
    }

    [Fact]
    public async Task TabelasDeAutorizacaoNaoAlteramSchemaFinanceiroLegado()
    {
        var (connection, db) = await AbrirBancoAsync();
        await using var _ = connection;
        await using var context = db;
        using var command = connection.CreateCommand();
        command.CommandText = "SELECT name FROM sqlite_master WHERE type = 'table'";
        using var reader = await command.ExecuteReaderAsync();
        var names = new HashSet<string>();
        while (await reader.ReadAsync()) names.Add(reader.GetString(0));
        Assert.Contains("acesso_contas", names);
        Assert.Contains("acesso_residencias", names);
        Assert.Contains("acesso_vinculos", names);
        Assert.DoesNotContain("Pessoas", names);
        Assert.DoesNotContain("Transacoes", names);
    }
}

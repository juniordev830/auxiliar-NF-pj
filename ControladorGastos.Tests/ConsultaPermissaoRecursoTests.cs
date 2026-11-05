using ControladorGastos.Security;
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;
using Xunit;

namespace ControladorGastos.Tests;

public sealed class ConsultaPermissaoRecursoTests
{
    [Fact]
    public async Task ResidenciaDeRecursoPersistidoDefineQuemPodeConsultarOuExcluir()
    {
        await using var connection = new SqliteConnection("Data Source=:memory:");
        await connection.OpenAsync();
        var options = new DbContextOptionsBuilder<AcessoResidencialContext>()
            .UseSqlite(connection).Options;
        await using var db = new AcessoResidencialContext(options);
        await db.Database.EnsureCreatedAsync();

        var adminA = new ContaAcesso {
            Emissor = "https://identity.example", SujeitoExterno = "admin-a"
        };
        var leitorB = new ContaAcesso {
            Emissor = "https://identity.example", SujeitoExterno = "leitor-b"
        };
        var casaA = new ResidenciaAcesso { Nome = "Casa A" };
        var casaB = new ResidenciaAcesso { Nome = "Casa B" };
        db.AddRange(adminA, leitorB, casaA, casaB);
        await db.SaveChangesAsync();

        db.Vinculos.AddRange(
            new VinculoAcesso {
                UsuarioId = adminA.Id, ResidenciaId = casaA.Id,
                Papel = PapelResidencia.Administrador
            },
            new VinculoAcesso {
                UsuarioId = leitorB.Id, ResidenciaId = casaB.Id,
                Papel = PapelResidencia.Leitor
            });
        db.Recursos.AddRange(
            new VinculoRecursoResidencia {
                TipoRecurso = TipoRecursoFinanceiro.Pessoa, RecursoId = 10,
                ResidenciaId = casaA.Id
            },
            new VinculoRecursoResidencia {
                TipoRecurso = TipoRecursoFinanceiro.Pessoa, RecursoId = 20,
                ResidenciaId = casaB.Id
            },
            new VinculoRecursoResidencia {
                TipoRecurso = TipoRecursoFinanceiro.Transacao, RecursoId = 100,
                ResidenciaId = casaA.Id
            },
            new VinculoRecursoResidencia {
                TipoRecurso = TipoRecursoFinanceiro.Transacao, RecursoId = 200,
                ResidenciaId = casaB.Id
            });
        await db.SaveChangesAsync();

        Assert.Equal(casaA.Id, await ConsultaPermissaoRecurso.ResolverResidenciaAsync(
            db, TipoRecursoFinanceiro.Pessoa, 10));
        Assert.Equal(casaB.Id, await ConsultaPermissaoRecurso.ResolverResidenciaAsync(
            db, TipoRecursoFinanceiro.Transacao, 200));

        Assert.True(await ConsultaPermissaoRecurso.PermiteAsync(
            db, "https://identity.example", "admin-a",
            TipoRecursoFinanceiro.Pessoa, 10, AcaoResidencia.Excluir));
        Assert.True(await ConsultaPermissaoRecurso.PermiteAsync(
            db, "https://identity.example", "admin-a",
            TipoRecursoFinanceiro.Transacao, 100, AcaoResidencia.Consultar));
        Assert.False(await ConsultaPermissaoRecurso.PermiteAsync(
            db, "https://identity.example", "admin-a",
            TipoRecursoFinanceiro.Pessoa, 20, AcaoResidencia.Consultar));
        Assert.True(await ConsultaPermissaoRecurso.PermiteAsync(
            db, "https://identity.example", "leitor-b",
            TipoRecursoFinanceiro.Transacao, 200, AcaoResidencia.Consultar));
        Assert.False(await ConsultaPermissaoRecurso.PermiteAsync(
            db, "https://identity.example", "leitor-b",
            TipoRecursoFinanceiro.Transacao, 200, AcaoResidencia.Excluir));
        Assert.False(await ConsultaPermissaoRecurso.PermiteAsync(
            db, "https://identity.example", "leitor-b",
            TipoRecursoFinanceiro.Transacao, 100, AcaoResidencia.Consultar));

        // A mapped Pessoa #10 must not authorize an unmapped Transacao #10.
        Assert.False(await ConsultaPermissaoRecurso.PermiteAsync(
            db, "https://identity.example", "admin-a",
            TipoRecursoFinanceiro.Transacao, 10, AcaoResidencia.Consultar));
        Assert.False(await ConsultaPermissaoRecurso.PermiteAsync(
            db, "https://identity.example", "admin-a",
            TipoRecursoFinanceiro.Pessoa, 999, AcaoResidencia.Consultar));
        Assert.False(await ConsultaPermissaoRecurso.PermiteAsync(
            db, "https://identity.example", "unknown-subject",
            TipoRecursoFinanceiro.Pessoa, 10, AcaoResidencia.Consultar));
        Assert.Equal(4, await db.Recursos.CountAsync());
    }

    [Fact]
    public async Task RecursoNaoPodeTerDuasResidenciasMesmoComUsuarioAdministrador()
    {
        await using var connection = new SqliteConnection("Data Source=:memory:");
        await connection.OpenAsync();
        var options = new DbContextOptionsBuilder<AcessoResidencialContext>()
            .UseSqlite(connection).Options;
        await using var db = new AcessoResidencialContext(options);
        await db.Database.EnsureCreatedAsync();

        var casaA = new ResidenciaAcesso { Nome = "A" };
        var casaB = new ResidenciaAcesso { Nome = "B" };
        db.Residencias.AddRange(casaA, casaB);
        await db.SaveChangesAsync();

        db.Recursos.Add(new VinculoRecursoResidencia {
            TipoRecurso = TipoRecursoFinanceiro.Pessoa, RecursoId = 10,
            ResidenciaId = casaA.Id
        });
        await db.SaveChangesAsync();

        // Composite primary key is (type, id); no silent reassignment.
        db.Recursos.Add(new VinculoRecursoResidencia {
            TipoRecurso = TipoRecursoFinanceiro.Pessoa, RecursoId = 10,
            ResidenciaId = casaB.Id
        });
        await Assert.ThrowsAsync<InvalidOperationException>(
            () => db.SaveChangesAsync());
    }

    [Fact]
    public async Task IdInvalidoOuTipoDesconhecidoNaoIdentificaResidencia()
    {
        await using var connection = new SqliteConnection("Data Source=:memory:");
        await connection.OpenAsync();
        var options = new DbContextOptionsBuilder<AcessoResidencialContext>()
            .UseSqlite(connection).Options;
        await using var db = new AcessoResidencialContext(options);
        await db.Database.EnsureCreatedAsync();

        Assert.Null(await ConsultaPermissaoRecurso.ResolverResidenciaAsync(
            db, TipoRecursoFinanceiro.Pessoa, 0));
        Assert.Null(await ConsultaPermissaoRecurso.ResolverResidenciaAsync(
            db, TipoRecursoFinanceiro.Transacao, -1));
        Assert.Null(await ConsultaPermissaoRecurso.ResolverResidenciaAsync(
            db, (TipoRecursoFinanceiro)99, 1));

        Assert.False(await ConsultaPermissaoRecurso.PermiteAsync(
            db, "https://identity.example", "admin-a",
            (TipoRecursoFinanceiro)99, 1, AcaoResidencia.Consultar));
        Assert.False(await ConsultaPermissaoRecurso.PermiteAsync(
            db, "https://identity.example", "admin-a",
            TipoRecursoFinanceiro.Pessoa, 0, AcaoResidencia.Consultar));
    }
}

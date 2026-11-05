using ControladorGastos.Security;
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;
using Xunit;

namespace ControladorGastos.Tests;

public sealed class ConsultaIdentidadeValidadaTests
{
    [Fact]
    public async Task MesmoSubjectEmProvedoresDistintosNaoConcedeAcessoCruzado()
    {
        await using var connection = new SqliteConnection("Data Source=:memory:");
        await connection.OpenAsync();
        var options = new DbContextOptionsBuilder<AcessoResidencialContext>()
            .UseSqlite(connection).Options;
        await using var db = new AcessoResidencialContext(options);
        await db.Database.EnsureCreatedAsync();

        var usuarioA = new ContaAcesso {
            Emissor = "https://login-a.example", SujeitoExterno = "shared-subject"
        };
        var usuarioB = new ContaAcesso {
            Emissor = "https://login-b.example", SujeitoExterno = "shared-subject"
        };
        var casaA = new ResidenciaAcesso { Nome = "Casa A" };
        var casaB = new ResidenciaAcesso { Nome = "Casa B" };
        db.AddRange(usuarioA, usuarioB, casaA, casaB);
        await db.SaveChangesAsync();
        db.Vinculos.AddRange(
            new VinculoAcesso {
                UsuarioId = usuarioA.Id, ResidenciaId = casaA.Id,
                Papel = PapelResidencia.Administrador
            },
            new VinculoAcesso {
                UsuarioId = usuarioB.Id, ResidenciaId = casaB.Id,
                Papel = PapelResidencia.Leitor
            });
        await db.SaveChangesAsync();

        Assert.Equal(usuarioA.Id, await ConsultaIdentidadeValidada.ResolverContaAsync(
            db, "https://login-a.example", "shared-subject"));
        Assert.Equal(usuarioB.Id, await ConsultaIdentidadeValidada.ResolverContaAsync(
            db, "https://login-b.example", "shared-subject"));

        Assert.True(await ConsultaIdentidadeValidada.PermiteAsync(
            db, "https://login-a.example", "shared-subject",
            casaA.Id, AcaoResidencia.Excluir));
        Assert.False(await ConsultaIdentidadeValidada.PermiteAsync(
            db, "https://login-a.example", "shared-subject",
            casaB.Id, AcaoResidencia.Consultar));
        Assert.True(await ConsultaIdentidadeValidada.PermiteAsync(
            db, "https://login-b.example", "shared-subject",
            casaB.Id, AcaoResidencia.Consultar));
        Assert.False(await ConsultaIdentidadeValidada.PermiteAsync(
            db, "https://login-b.example", "shared-subject",
            casaB.Id, AcaoResidencia.Registrar));
        Assert.False(await ConsultaIdentidadeValidada.PermiteAsync(
            db, "https://login-b.example", "shared-subject",
            casaA.Id, AcaoResidencia.Excluir));
    }

    [Fact]
    public async Task IdentidadeDesconhecidaOuAlegacoesInvalidasNaoAutorizam()
    {
        await using var connection = new SqliteConnection("Data Source=:memory:");
        await connection.OpenAsync();
        var options = new DbContextOptionsBuilder<AcessoResidencialContext>()
            .UseSqlite(connection).Options;
        await using var db = new AcessoResidencialContext(options);
        await db.Database.EnsureCreatedAsync();

        var usuario = new ContaAcesso {
            Emissor = "https://login.example", SujeitoExterno = "known-user"
        };
        var casa = new ResidenciaAcesso { Nome = "Casa" };
        db.AddRange(usuario, casa);
        await db.SaveChangesAsync();
        db.Vinculos.Add(new VinculoAcesso {
            UsuarioId = usuario.Id, ResidenciaId = casa.Id,
            Papel = PapelResidencia.Administrador
        });
        await db.SaveChangesAsync();

        foreach (var (emissor, sujeito) in new (string?, string?)[] {
            (null, "known-user"),
            ("https://login.example", null),
            ("", "known-user"),
            (" ", "known-user"),
            ("https://login.example", ""),
            ("https://login.example", "   "),
            (new string('x', 201), "known-user"),
            ("https://login.example", new string('x', 201)),
            ("https://another-issuer.example", "known-user"),
            ("https://login.example", "unknown-user"),
            ("https://login.example", "KNOWN-USER")
        }) {
            Assert.Null(await ConsultaIdentidadeValidada.ResolverContaAsync(db, emissor, sujeito));
            Assert.False(await ConsultaIdentidadeValidada.PermiteAsync(
                db, emissor, sujeito, casa.Id, AcaoResidencia.Consultar));
        }

        Assert.False(await ConsultaIdentidadeValidada.PermiteAsync(
            db, "https://login.example", "known-user",
            Guid.Empty, AcaoResidencia.Consultar));
        Assert.Equal(1, await db.Contas.CountAsync());
    }
}

using ControladorGastos.Security;
using Xunit;

namespace ControladorGastos.Tests;

public sealed class PoliticaAcessoResidenciaTests
{
    private static readonly Guid UsuarioA = Guid.Parse("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa");
    private static readonly Guid UsuarioB = Guid.Parse("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb");
    private static readonly Guid ResidenciaA = Guid.Parse("11111111-1111-1111-1111-111111111111");
    private static readonly Guid ResidenciaB = Guid.Parse("22222222-2222-2222-2222-222222222222");

    private static readonly VinculoResidencia[] Vinculos =
    [
        new(UsuarioA, ResidenciaA, PapelResidencia.Administrador),
        new(UsuarioB, ResidenciaB, PapelResidencia.Leitor)
    ];

    [Theory]
    [InlineData(AcaoResidencia.Consultar)]
    [InlineData(AcaoResidencia.Registrar)]
    [InlineData(AcaoResidencia.Excluir)]
    public void AdministradorNaoAcessaOutraResidencia(AcaoResidencia acao)
    {
        Assert.False(PoliticaAcessoResidencia.Permite(UsuarioA, ResidenciaB, acao, Vinculos));
        Assert.False(PoliticaAcessoResidencia.Permite(UsuarioB, ResidenciaA, acao, Vinculos));
    }

    [Theory]
    [InlineData(AcaoResidencia.Consultar)]
    [InlineData(AcaoResidencia.Registrar)]
    [InlineData(AcaoResidencia.Excluir)]
    public void NegaSemIdentidadeValidada(AcaoResidencia acao)
    {
        Assert.False(PoliticaAcessoResidencia.Permite(null, ResidenciaA, acao, Vinculos));
        Assert.False(PoliticaAcessoResidencia.Permite(Guid.Empty, ResidenciaA, acao, Vinculos));
        Assert.False(PoliticaAcessoResidencia.Permite(UsuarioA, Guid.Empty, acao, Vinculos));
    }

    [Fact]
    public void AdministradorOperaNaSuaResidencia()
    {
        foreach (AcaoResidencia acao in Enum.GetValues<AcaoResidencia>())
            Assert.True(PoliticaAcessoResidencia.Permite(UsuarioA, ResidenciaA, acao, Vinculos));
    }

    [Fact]
    public void LeitorNaoRegistraNemExclui()
    {
        Assert.True(PoliticaAcessoResidencia.Permite(UsuarioB, ResidenciaB, AcaoResidencia.Consultar, Vinculos));
        Assert.False(PoliticaAcessoResidencia.Permite(UsuarioB, ResidenciaB, AcaoResidencia.Registrar, Vinculos));
        Assert.False(PoliticaAcessoResidencia.Permite(UsuarioB, ResidenciaB, AcaoResidencia.Excluir, Vinculos));
    }

    [Fact]
    public void EditorPodeRegistrarMasNaoExcluir()
    {
        var vinculos = new[] { new VinculoResidencia(UsuarioB, ResidenciaA, PapelResidencia.Editor) };
        Assert.True(PoliticaAcessoResidencia.Permite(UsuarioB, ResidenciaA, AcaoResidencia.Registrar, vinculos));
        Assert.False(PoliticaAcessoResidencia.Permite(UsuarioB, ResidenciaA, AcaoResidencia.Excluir, vinculos));
    }

    [Fact]
    public void PapelInvalidoNaoAutorizaNemLeitura()
    {
        var vinculos = new[]
        {
            new VinculoResidencia(UsuarioA, ResidenciaA, (PapelResidencia)999)
        };
        Assert.False(PoliticaAcessoResidencia.Permite(
            UsuarioA, ResidenciaA, AcaoResidencia.Consultar, vinculos));
    }

    [Fact]
    public void AcaoDesconhecidaNaoEAutorizada()
    {
        Assert.False(PoliticaAcessoResidencia.Permite(
            UsuarioA, ResidenciaA, (AcaoResidencia)999, Vinculos));
    }

    [Fact]
    public void IdentidadeSemVinculoNaoTemPermissao()
    {
        Assert.False(PoliticaAcessoResidencia.Permite(UsuarioA, ResidenciaA, AcaoResidencia.Consultar, []));
    }
}

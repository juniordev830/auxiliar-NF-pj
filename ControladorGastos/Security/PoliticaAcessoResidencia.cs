namespace ControladorGastos.Security;

// Conta autenticada e pessoa cadastrada na residência são conceitos diferentes.
// Esta política só deve receber um UsuarioId de autenticação VALIDADA e vínculos lidos do banco.
public enum PapelResidencia
{
    Leitor,
    Editor,
    Administrador
}

public enum AcaoResidencia
{
    Consultar,
    Registrar,
    Excluir
}

public sealed record VinculoResidencia(Guid UsuarioId, Guid ResidenciaId, PapelResidencia Papel);

public static class PoliticaAcessoResidencia
{
    public static bool Permite(
        Guid? usuarioAutenticadoId,
        Guid residenciaDoRecursoId,
        AcaoResidencia acao,
        IEnumerable<VinculoResidencia> vinculos)
    {
        ArgumentNullException.ThrowIfNull(vinculos);

        if (usuarioAutenticadoId is null || usuarioAutenticadoId == Guid.Empty ||
            residenciaDoRecursoId == Guid.Empty)
        {
            return false;
        }

        // Não permitir "administrador global": o papel só vale dentro da residência vinculada.
        return vinculos.Any(vinculo =>
            vinculo.UsuarioId == usuarioAutenticadoId.Value &&
            vinculo.ResidenciaId == residenciaDoRecursoId &&
            (acao switch
            {
                AcaoResidencia.Consultar => true,
                AcaoResidencia.Registrar => vinculo.Papel is PapelResidencia.Editor or PapelResidencia.Administrador,
                AcaoResidencia.Excluir => vinculo.Papel == PapelResidencia.Administrador,
                _ => false
            }));
    }
}

using Microsoft.EntityFrameworkCore;

namespace ControladorGastos.Security;

// Checks membership loaded from storage, never from caller-provided role claims.
public static class ConsultaAcessoResidencia
{
    public static async Task<bool> PermiteAsync(
        AcessoResidencialContext db,
        Guid? usuarioAutenticadoId,
        Guid residenciaDoRecursoId,
        AcaoResidencia acao,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(db);
        if (usuarioAutenticadoId is null || usuarioAutenticadoId == Guid.Empty ||
            residenciaDoRecursoId == Guid.Empty)
            return false;

        var vinculos = await db.Vinculos.AsNoTracking()
            .Where(x => x.UsuarioId == usuarioAutenticadoId.Value &&
                        x.ResidenciaId == residenciaDoRecursoId)
            .Select(x => new VinculoResidencia(x.UsuarioId, x.ResidenciaId, x.Papel))
            .ToListAsync(cancellationToken);

        return PoliticaAcessoResidencia.Permite(
            usuarioAutenticadoId, residenciaDoRecursoId, acao, vinculos);
    }
}

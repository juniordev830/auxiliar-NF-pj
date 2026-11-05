using Microsoft.EntityFrameworkCore;

namespace ControladorGastos.Security;

/// <summary>
/// Resolves the residence of a persisted resource rather than trusting an
/// owner/residence identifier supplied by the caller.
/// This preparatory component is not wired into the legacy financial routes.
/// </summary>
public static class ConsultaPermissaoRecurso
{
    public static async Task<Guid?> ResolverResidenciaAsync(
        AcessoResidencialContext db,
        TipoRecursoFinanceiro tipo,
        int recursoId,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(db);
        if (recursoId <= 0 || !Enum.IsDefined(typeof(TipoRecursoFinanceiro), tipo))
            return null;

        return await db.Recursos.AsNoTracking()
            .Where(x => x.TipoRecurso == tipo && x.RecursoId == recursoId)
            .Select(x => (Guid?)x.ResidenciaId)
            .SingleOrDefaultAsync(cancellationToken);
    }

    public static async Task<bool> PermiteAsync(
        AcessoResidencialContext db,
        string? emissorValidado,
        string? sujeitoValidado,
        TipoRecursoFinanceiro tipo,
        int recursoId,
        AcaoResidencia acao,
        CancellationToken cancellationToken = default)
    {
        var residenciaId = await ResolverResidenciaAsync(
            db, tipo, recursoId, cancellationToken);
        if (residenciaId is null || residenciaId == Guid.Empty)
            return false;

        return await ConsultaIdentidadeValidada.PermiteAsync(
            db, emissorValidado, sujeitoValidado, residenciaId.Value,
            acao, cancellationToken);
    }
}

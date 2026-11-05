using Microsoft.EntityFrameworkCore;

namespace ControladorGastos.Security;

/// <summary>
/// Resolves an existing account from an issuer and subject extracted from a
/// cryptographically validated identity token. Never accept these two values
/// directly from request JSON, query parameters or unverified JWT payloads.
/// This helper deliberately does not create accounts or register authentication.
/// </summary>
public static class ConsultaIdentidadeValidada
{
    public static async Task<Guid?> ResolverContaAsync(
        AcessoResidencialContext db,
        string? emissorValidado,
        string? sujeitoValidado,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(db);

        // Fail closed for missing or malformed claims before the database query.
        if (string.IsNullOrWhiteSpace(emissorValidado) ||
            string.IsNullOrWhiteSpace(sujeitoValidado) ||
            emissorValidado.Length > 200 ||
            sujeitoValidado.Length > 200)
            return null;

        // Both fields must match exactly: the same subject from a different
        // identity provider is NOT the same account.
        return await db.Contas.AsNoTracking()
            .Where(x => x.Emissor == emissorValidado &&
                        x.SujeitoExterno == sujeitoValidado)
            .Select(x => (Guid?)x.Id)
            .SingleOrDefaultAsync(cancellationToken);
    }

    public static async Task<bool> PermiteAsync(
        AcessoResidencialContext db,
        string? emissorValidado,
        string? sujeitoValidado,
        Guid residenciaDoRecursoId,
        AcaoResidencia acao,
        CancellationToken cancellationToken = default)
    {
        var contaId = await ResolverContaAsync(
            db, emissorValidado, sujeitoValidado, cancellationToken);

        // The persisted account and its membership decide permissions.
        // Unknown identities cannot choose their own role/residence.
        return await ConsultaAcessoResidencia.PermiteAsync(
            db, contaId, residenciaDoRecursoId, acao, cancellationToken);
    }
}

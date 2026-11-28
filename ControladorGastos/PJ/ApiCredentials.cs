using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using Microsoft.EntityFrameworkCore;

namespace ControladorGastos.PJ;

internal sealed record ApiCredential(string UserId, byte[] Hash, bool CanWrite, DateTime ExpiresAt);

internal sealed class ApiCredentials
{
    private const string LogoutPath = "/api/session/logout";
    internal const string ActorItem = "Gastos.Actor";
    private readonly Dictionary<string, ApiCredential> credentials = new(StringComparer.Ordinal);

    public ApiCredentials(IConfiguration config)
    {
        foreach (var entry in config.GetSection("GASTOS_CREDENCIAIS").GetChildren())
        {
            var id = entry.Key;
            var role = entry["Role"];
            var hashHex = entry["TokenHash"];
            if (id.Length is < 1 or > 64 || !id.All(c => char.IsAsciiLetterOrDigit(c) || c is '-' or '_') ||
                role is not ("admin" or "read") ||
                hashHex?.Length != 64 || !hashHex.All(Uri.IsHexDigit) ||
                !DateTimeOffset.TryParseExact(entry["ExpiresAt"], "yyyy-MM-dd'T'HH:mm:ss'Z'",
                    CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal, out var expiresAt))
            {
                throw new InvalidOperationException("Configuração inválida em GASTOS_CREDENCIAIS.");
            }
            credentials.Add(id, new ApiCredential(id, Convert.FromHexString(hashHex), role == "admin", expiresAt.UtcDateTime));
        }
    }

    public bool IsConfigured => credentials.Count > 0;

    public async Task<ApiCredential?> Authenticate(string? token, AuxiliarPjContext db, CancellationToken cancellation)
    {
        if (token is null || token.Length > 1024) return null;
        var separator = token.IndexOf('.');
        if (separator < 1 || token.Length - separator - 1 < 32 ||
            !credentials.TryGetValue(token[..separator], out var credential) ||
            credential.ExpiresAt <= DateTime.UtcNow ||
            !CryptographicOperations.FixedTimeEquals(SHA256.HashData(Encoding.UTF8.GetBytes(token)), credential.Hash))
            return null;

        var hash = Convert.ToHexString(credential.Hash);
        return await db.RevokedCredentials.AnyAsync(x => x.Digest == hash, cancellation) ? null : credential;
    }

    public static bool IsLogout(HttpRequest request) =>
        HttpMethods.IsPost(request.Method) && request.Path.Equals(LogoutPath, StringComparison.OrdinalIgnoreCase);

    public static Task<int> Revoke(ApiCredential credential, AuxiliarPjContext db, CancellationToken cancellation)
    {
        var hash = Convert.ToHexString(credential.Hash);
        return db.Database.ExecuteSqlInterpolatedAsync(
            $"INSERT OR IGNORE INTO RevokedCredentials (Digest) VALUES ({hash})", cancellation);
    }
}

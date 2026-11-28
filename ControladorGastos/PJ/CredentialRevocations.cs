using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;

namespace ControladorGastos.PJ;

internal sealed class CredentialRevocations(string path)
{
    private readonly string connectionString = new SqliteConnectionStringBuilder
    {
        DataSource = path,
        Mode = SqliteOpenMode.ReadWriteCreate,
        DefaultTimeout = 3
    }.ToString();

    public async Task Initialize(AuxiliarPjContext db)
    {
        var financialPath = new SqliteConnectionStringBuilder(db.Database.GetConnectionString()).DataSource;
        var compare = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
        if (string.Equals(Path.GetFullPath(path), Path.GetFullPath(financialPath), compare))
            throw new InvalidOperationException("Use um arquivo de revogações separado do banco financeiro.");
        await using var connection = new SqliteConnection(connectionString);
        await connection.OpenAsync();
        await using var setup = connection.CreateCommand();
        setup.CommandText = "CREATE TABLE IF NOT EXISTS RevokedCredentials (Digest TEXT PRIMARY KEY NOT NULL)";
        await setup.ExecuteNonQueryAsync();

        // Import prior revocations once per startup without dropping newer history.
        using var transaction = connection.BeginTransaction();
        await using var insert = connection.CreateCommand();
        insert.Transaction = transaction;
        insert.CommandText = "INSERT OR IGNORE INTO RevokedCredentials (Digest) VALUES ($digest)";
        var digest = insert.Parameters.Add("$digest", SqliteType.Text);
        await foreach (var record in db.RevokedCredentials.AsNoTracking().AsAsyncEnumerable())
        {
            digest.Value = record.Digest;
            await insert.ExecuteNonQueryAsync();
        }
        transaction.Commit();
    }

    public async Task<bool> Contains(string digest, CancellationToken cancellation) =>
        (long)(await Execute(
            "SELECT EXISTS(SELECT 1 FROM RevokedCredentials WHERE Digest = $digest)",
            digest, cancellation, scalar: true) ?? 0L) == 1L;

    public async Task Add(string digest, CancellationToken cancellation) =>
        await Execute("INSERT OR IGNORE INTO RevokedCredentials (Digest) VALUES ($digest)",
            digest, cancellation, scalar: false);

    private async Task<object?> Execute(string sql, string digest, CancellationToken cancellation, bool scalar)
    {
        // Requiring an existing database during requests prevents a missing file from
        // resetting revocations silently while the process is running.
        var noCreate = new SqliteConnectionStringBuilder(connectionString) { Mode = SqliteOpenMode.ReadWrite };
        await using var connection = new SqliteConnection(noCreate.ToString());
        await connection.OpenAsync(cancellation);
        await using var command = connection.CreateCommand();
        command.CommandText = sql;
        command.Parameters.AddWithValue("$digest", digest);
        if (scalar) return await command.ExecuteScalarAsync(cancellation);
        await command.ExecuteNonQueryAsync(cancellation);
        return null;
    }
}

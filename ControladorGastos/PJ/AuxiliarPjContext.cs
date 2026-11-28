using Microsoft.EntityFrameworkCore;

namespace ControladorGastos.PJ;

// Contexto isolado para preservar o banco residencial já existente.
public sealed class AuxiliarPjContext(DbContextOptions<AuxiliarPjContext> options) : DbContext(options)
{
    public DbSet<LancamentoPj> Lancamentos => Set<LancamentoPj>();

    public DbSet<LancamentoHistorico> Historico => Set<LancamentoHistorico>();

    public DbSet<RevokedCredential> RevokedCredentials => Set<RevokedCredential>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var entity = modelBuilder.Entity<LancamentoPj>();
        entity.Property(x => x.Descricao).HasMaxLength(200).IsRequired();
        entity.Property(x => x.Categoria).HasMaxLength(80).IsRequired();
        entity.Property(x => x.Tipo).HasMaxLength(10).IsRequired();
        entity.Property(x => x.Contraparte).HasMaxLength(120);
        entity.Property(x => x.Valor).HasPrecision(14, 2);
        entity.HasIndex(x => x.Competencia);
        entity.HasQueryFilter(x => x.ExcluidoEm == null);
        entity.Property(x => x.Versao).IsConcurrencyToken();
        var audit = modelBuilder.Entity<LancamentoHistorico>();
        audit.HasIndex(x => x.LancamentoId);
        audit.Property(x => x.Acao).HasMaxLength(20).IsRequired();
        audit.Property(x => x.Responsavel).HasMaxLength(64);
        var revoked = modelBuilder.Entity<RevokedCredential>();
        revoked.HasKey(x => x.Digest);
        revoked.Property(x => x.Digest).HasMaxLength(64);
    }
}

public sealed class LancamentoPj
{
    public int Id { get; set; }
    public string Descricao { get; set; } = string.Empty;
    public string Tipo { get; set; } = string.Empty;
    public string Categoria { get; set; } = string.Empty;
    public string? Contraparte { get; set; }
    public decimal Valor { get; set; }
    public DateTime Competencia { get; set; }
    public DateTime? Vencimento { get; set; }
    public DateTime? DataPagamento { get; set; }
    public DateTime? ExcluidoEm { get; set; }
    public int Versao { get; set; }
    public DateTime CriadoEm { get; set; } = DateTime.UtcNow;
}

public sealed class LancamentoHistorico
{
    public int Id { get; set; }
    public int LancamentoId { get; set; }
    public string Acao { get; set; } = string.Empty;
    public string? Responsavel { get; set; }
    public string? Antes { get; set; }
    public string? Depois { get; set; }
    public DateTime OcorridoEm { get; set; } = DateTime.UtcNow;
}


public sealed class RevokedCredential
{
    public string Digest { get; set; } = string.Empty;
}

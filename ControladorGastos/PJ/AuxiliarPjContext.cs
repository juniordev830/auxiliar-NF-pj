using Microsoft.EntityFrameworkCore;

namespace ControladorGastos.PJ;

// Contexto isolado para preservar o banco residencial já existente.
// Trocar EnsureCreated por migrations antes de operar em produção.
public sealed class AuxiliarPjContext(DbContextOptions<AuxiliarPjContext> options) : DbContext(options)
{
    public DbSet<LancamentoPj> Lancamentos => Set<LancamentoPj>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var entity = modelBuilder.Entity<LancamentoPj>();
        entity.Property(x => x.Descricao).HasMaxLength(200).IsRequired();
        entity.Property(x => x.Categoria).HasMaxLength(80).IsRequired();
        entity.Property(x => x.Tipo).HasMaxLength(10).IsRequired();
        entity.Property(x => x.Contraparte).HasMaxLength(120);
        entity.Property(x => x.Valor).HasPrecision(14, 2);
        entity.HasIndex(x => x.Competencia);
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
    public DateTime CriadoEm { get; set; } = DateTime.UtcNow;
}

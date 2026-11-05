using Microsoft.EntityFrameworkCore;

namespace ControladorGastos.Security;

// Separate persistence model; not registered in the existing local API yet.
public sealed class AcessoResidencialContext(DbContextOptions<AcessoResidencialContext> options)
    : DbContext(options)
{
    public DbSet<ContaAcesso> Contas => Set<ContaAcesso>();
    public DbSet<ResidenciaAcesso> Residencias => Set<ResidenciaAcesso>();
    public DbSet<VinculoAcesso> Vinculos => Set<VinculoAcesso>();
    public DbSet<VinculoRecursoResidencia> Recursos => Set<VinculoRecursoResidencia>();

    protected override void OnModelCreating(ModelBuilder builder)
    {
        builder.Entity<ContaAcesso>(entity =>
        {
            entity.ToTable("acesso_contas");
            entity.HasKey(x => x.Id);
            entity.Property(x => x.Emissor).HasMaxLength(200).IsRequired();
            entity.Property(x => x.SujeitoExterno).HasMaxLength(200).IsRequired();
            entity.HasIndex(x => new { x.Emissor, x.SujeitoExterno }).IsUnique();
        });

        builder.Entity<ResidenciaAcesso>(entity =>
        {
            entity.ToTable("acesso_residencias");
            entity.HasKey(x => x.Id);
            entity.Property(x => x.Nome).HasMaxLength(120).IsRequired();
        });

        builder.Entity<VinculoAcesso>(entity =>
        {
            entity.ToTable("acesso_vinculos");
            entity.HasKey(x => new { x.UsuarioId, x.ResidenciaId });
            entity.Property(x => x.Papel).HasConversion<string>().HasMaxLength(24).IsRequired();
            entity.HasOne(x => x.Usuario).WithMany(x => x.Vinculos)
                .HasForeignKey(x => x.UsuarioId).OnDelete(DeleteBehavior.Restrict);
            entity.HasOne(x => x.Residencia).WithMany(x => x.Vinculos)
                .HasForeignKey(x => x.ResidenciaId).OnDelete(DeleteBehavior.Restrict);
            entity.HasIndex(x => x.ResidenciaId);
        });
        builder.Entity<VinculoRecursoResidencia>(entity =>
        {
            entity.ToTable("acesso_recursos");
            entity.HasKey(x => new { x.TipoRecurso, x.RecursoId });
            entity.Property(x => x.TipoRecurso).HasConversion<string>()
                .HasMaxLength(20).IsRequired();
            entity.Property(x => x.RecursoId).IsRequired();
            entity.HasOne(x => x.Residencia)
                .WithMany()
                .HasForeignKey(x => x.ResidenciaId)
                .OnDelete(DeleteBehavior.Restrict);
            entity.HasIndex(x => x.ResidenciaId);
            entity.ToTable(table => table.HasCheckConstraint(
                "CK_acesso_recursos_id_positivo", "RecursoId > 0"));
        });
    }
}

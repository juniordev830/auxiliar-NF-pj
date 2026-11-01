using ControladorGastos.Models;
using Microsoft.EntityFrameworkCore;

namespace ControladorGastos.Data;

public sealed class ControladorGastosContext(DbContextOptions<ControladorGastosContext> options)
    : DbContext(options)
{
    public DbSet<Pessoa> Pessoas => Set<Pessoa>();
    public DbSet<Transacao> Transacoes => Set<Transacao>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Pessoa>().Property(x => x.Nome).HasMaxLength(100).IsRequired();
        modelBuilder.Entity<Transacao>().Property(x => x.Descricao).HasMaxLength(200).IsRequired();
        modelBuilder.Entity<Transacao>().Property(x => x.Tipo).HasMaxLength(10).IsRequired();
        modelBuilder.Entity<Transacao>().Property(x => x.Valor).HasPrecision(12, 2);
        modelBuilder.Entity<Pessoa>()
            .HasMany(x => x.Transacoes)
            .WithOne(x => x.Pessoa)
            .HasForeignKey(x => x.PessoaId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}

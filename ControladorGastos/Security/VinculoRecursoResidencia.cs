namespace ControladorGastos.Security;

/// <summary>
/// Describes an explicit resource/residence link in the separate access model.
/// These IDs refer to legacy demo records. They are NOT foreign keys to the
/// existing financial database and must never be inferred from client input.
/// </summary>
public enum TipoRecursoFinanceiro
{
    Pessoa = 1,
    Transacao = 2
}

public sealed class VinculoRecursoResidencia
{
    public TipoRecursoFinanceiro TipoRecurso { get; set; }
    public int RecursoId { get; set; }
    public Guid ResidenciaId { get; set; }
    public ResidenciaAcesso Residencia { get; set; } = null!;
}

namespace ControladorGastos.Security;

/// <summary>
/// Identidade de login vinculada a um provedor confiável.
/// Não representa uma Pessoa cadastrada para fins financeiros.
/// </summary>
public sealed class ContaAcesso
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Emissor { get; set; } = string.Empty;
    public string SujeitoExterno { get; set; } = string.Empty;
    public DateTime CriadaEm { get; set; } = DateTime.UtcNow;
    public ICollection<VinculoAcesso> Vinculos { get; set; } = new List<VinculoAcesso>();
}

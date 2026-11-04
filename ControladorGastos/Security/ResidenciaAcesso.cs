namespace ControladorGastos.Security;

/// <summary>Escopo de autorização, separado de Pessoa e de Transacao do protótipo local.</summary>
public sealed class ResidenciaAcesso
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Nome { get; set; } = string.Empty;
    public ICollection<VinculoAcesso> Vinculos { get; set; } = new List<VinculoAcesso>();
}

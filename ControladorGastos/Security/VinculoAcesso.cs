namespace ControladorGastos.Security;

/// <summary>O papel pertence a uma residência específica, não é privilégio global.</summary>
public sealed class VinculoAcesso
{
    public Guid UsuarioId { get; set; }
    public ContaAcesso Usuario { get; set; } = null!;
    public Guid ResidenciaId { get; set; }
    public ResidenciaAcesso Residencia { get; set; } = null!;
    public PapelResidencia Papel { get; set; }
}

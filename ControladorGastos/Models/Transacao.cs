namespace ControladorGastos.Models;

public sealed class Transacao
{
    public int Id { get; set; }
    public string Descricao { get; set; } = string.Empty;
    public decimal Valor { get; set; }
    public string Tipo { get; set; } = string.Empty;
    public int PessoaId { get; set; }
    public Pessoa Pessoa { get; set; } = null!;
    public DateTime DataCriacao { get; set; } = DateTime.UtcNow;
}

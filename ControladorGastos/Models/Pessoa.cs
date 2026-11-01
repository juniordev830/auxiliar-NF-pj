namespace ControladorGastos.Models;

public sealed class Pessoa
{
    public int Id { get; set; }
    public string Nome { get; set; } = string.Empty;
    public int Idade { get; set; }
    public DateTime DataCriacao { get; set; } = DateTime.UtcNow;
    public ICollection<Transacao> Transacoes { get; set; } = new List<Transacao>();
}

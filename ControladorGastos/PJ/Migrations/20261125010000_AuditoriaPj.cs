using ControladorGastos.PJ;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Migrations;

namespace ControladorGastos.PJ.Migrations;

[DbContext(typeof(AuxiliarPjContext))]
[Migration("20261125010000_AuditoriaPj")]
public sealed class AuditoriaPj : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.AddColumn<DateTime>(name: "ExcluidoEm", table: "Lancamentos", type: "TEXT", nullable: true);
        migrationBuilder.AddColumn<int>(name: "Versao", table: "Lancamentos", type: "INTEGER", nullable: false, defaultValue: 0);
        migrationBuilder.CreateTable(
            name: "Historico",
            columns: table => new
            {
                Id = table.Column<int>(type: "INTEGER", nullable: false).Annotation("Sqlite:Autoincrement", true),
                LancamentoId = table.Column<int>(type: "INTEGER", nullable: false),
                Acao = table.Column<string>(type: "TEXT", maxLength: 20, nullable: false),
                Antes = table.Column<string>(type: "TEXT", nullable: true),
                Depois = table.Column<string>(type: "TEXT", nullable: true),
                OcorridoEm = table.Column<DateTime>(type: "TEXT", nullable: false)
            },
            constraints: table => table.PrimaryKey("PK_Historico", x => x.Id));
        migrationBuilder.CreateIndex(name: "IX_Historico_LancamentoId", table: "Historico", column: "LancamentoId");
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropTable("Historico");
        migrationBuilder.DropColumn("ExcluidoEm", "Lancamentos");
        migrationBuilder.DropColumn("Versao", "Lancamentos");
    }
}

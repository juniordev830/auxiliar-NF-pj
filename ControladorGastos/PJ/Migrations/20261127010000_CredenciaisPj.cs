using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Migrations;

namespace ControladorGastos.PJ.Migrations;

[DbContext(typeof(AuxiliarPjContext))]
[Migration("20261127010000_CredenciaisPj")]
public sealed class CredenciaisPj : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.AddColumn<string>(name: "Responsavel", table: "Historico", type: "TEXT",
            maxLength: 64, nullable: true);
        migrationBuilder.CreateTable(
            name: "RevokedCredentials",
            columns: table => new { Digest = table.Column<string>(type: "TEXT", maxLength: 64, nullable: false) },
            constraints: table => table.PrimaryKey("PK_RevokedCredentials", x => x.Digest));
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropTable("RevokedCredentials");
        migrationBuilder.DropColumn("Responsavel", "Historico");
    }
}

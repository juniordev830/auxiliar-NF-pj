using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ControladorGastos.PJ.Migrations
{
    /// <inheritdoc />
    public partial class BaselineAuxiliarPj : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // A versão anterior criava este mesmo esquema com EnsureCreated.
            // Registrar a baseline preserva as tabelas e os dados já existentes.
            migrationBuilder.Sql("""
                CREATE TABLE IF NOT EXISTS "Lancamentos" (
                    "Id" INTEGER NOT NULL CONSTRAINT "PK_Lancamentos" PRIMARY KEY AUTOINCREMENT,
                    "Descricao" TEXT NOT NULL,
                    "Tipo" TEXT NOT NULL,
                    "Categoria" TEXT NOT NULL,
                    "Contraparte" TEXT NULL,
                    "Valor" TEXT NOT NULL,
                    "Competencia" TEXT NOT NULL,
                    "Vencimento" TEXT NULL,
                    "DataPagamento" TEXT NULL,
                    "CriadoEm" TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS "IX_Lancamentos_Competencia" ON "Lancamentos" ("Competencia");
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Lancamentos");
        }
    }
}

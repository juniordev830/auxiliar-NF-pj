using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ControladorGastos.Data.Migrations
{
    /// <inheritdoc />
    public partial class BaselineResidencial : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // A versão anterior criava este mesmo esquema com EnsureCreated.
            // Registrar a baseline preserva as tabelas e os dados já existentes.
            migrationBuilder.Sql("""
                CREATE TABLE IF NOT EXISTS "Pessoas" (
                    "Id" INTEGER NOT NULL CONSTRAINT "PK_Pessoas" PRIMARY KEY AUTOINCREMENT,
                    "Nome" TEXT NOT NULL,
                    "Idade" INTEGER NOT NULL,
                    "DataCriacao" TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS "Transacoes" (
                    "Id" INTEGER NOT NULL CONSTRAINT "PK_Transacoes" PRIMARY KEY AUTOINCREMENT,
                    "Descricao" TEXT NOT NULL,
                    "Valor" TEXT NOT NULL,
                    "Tipo" TEXT NOT NULL,
                    "PessoaId" INTEGER NOT NULL,
                    "DataCriacao" TEXT NOT NULL,
                    CONSTRAINT "FK_Transacoes_Pessoas_PessoaId" FOREIGN KEY ("PessoaId") REFERENCES "Pessoas" ("Id") ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS "IX_Transacoes_PessoaId" ON "Transacoes" ("PessoaId");
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Transacoes");

            migrationBuilder.DropTable(
                name: "Pessoas");
        }
    }
}

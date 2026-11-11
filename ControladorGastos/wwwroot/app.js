"use strict";

const el = (id) => document.getElementById(id);
const currency = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
let people = [];

async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(path, {
      ...options,
      headers: { "Accept": "application/json", ...(options.body ? { "Content-Type": "application/json" } : {}) }
    });
  } catch {
    throw new Error("Não foi possível alcançar a API local. Execute 'dotnet run --project ControladorGastos/ControladorGastos.csproj' e abra http://127.0.0.1:5000/.");
  }

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      throw new Error("A API está protegida por tokens. Este painel local não solicita nem armazena segredos no navegador; consulte o README para usar a API protegida.");
    }
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `A API retornou o erro HTTP ${response.status}.`);
  }
  if (response.status === 204) return null;
  return response.json();
}

function message(value, success = false) {
  const element = el("message");
  element.hidden = !value;
  element.textContent = value || "";
  element.classList.toggle("success", success);
}

function renderPeople() {
  const list = el("people");
  list.replaceChildren();
  const select = el("person");
  const current = select.value;
  select.replaceChildren();
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Selecione um morador";
  select.append(placeholder);

  if (people.length === 0) {
    const item = document.createElement("li");
    item.textContent = "Nenhum morador cadastrado.";
    list.append(item);
  }
  for (const person of people) {
    const item = document.createElement("li");
    item.textContent = `${person.nome} · ${person.idade} anos`;
    list.append(item);

    const option = document.createElement("option");
    option.value = String(person.id);
    option.textContent = person.nome;
    select.append(option);
  }
  if ([...select.options].some((option) => option.value === current)) select.value = current;
}

function renderTransactions(rows) {
  const tbody = el("transactions");
  tbody.replaceChildren();
  if (rows.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.textContent = "Nenhuma transação cadastrada.";
    row.append(cell);
    tbody.append(row);
    return;
  }
  for (const transaction of rows) {
    const row = document.createElement("tr");
    const fields = [
      transaction.descricao,
      transaction.pessoaNome,
      transaction.tipo === "RECEITA" ? "Receita" : "Despesa",
      currency.format(transaction.valor)
    ];
    for (const field of fields) {
      const cell = document.createElement("td");
      cell.textContent = String(field ?? "");
      row.append(cell);
    }
    tbody.append(row);
  }
}

async function refresh() {
  message("");
  el("refresh").disabled = true;
  try {
    const health = await api("/api/health");
    if (health.status !== "ok") throw new Error("A API não respondeu corretamente à verificação de saúde.");
    el("connection").textContent = "API local conectada";
    el("connection").classList.add("online");

    const [peopleResponse, totals, transactions] = await Promise.all([
      api("/api/pessoas"),
      api("/api/transacoes/totais/resumo"),
      api("/api/transacoes?page=1&limit=20")
    ]);
    people = peopleResponse;
    renderPeople();
    renderTransactions(transactions);
    el("income").textContent = currency.format(totals.totalReceitas);
    el("expenses").textContent = currency.format(totals.totalDespesas);
    el("balance").textContent = currency.format(totals.saldoGeral);
  } catch (error) {
    if (el("connection").textContent !== "API local conectada") {
      el("connection").textContent = "Sem conexão com a API";
      el("connection").classList.remove("online");
    }
    message(error.message);
  } finally {
    el("refresh").disabled = false;
  }
}

el("refresh").addEventListener("click", refresh);

el("person-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const data = new FormData(form);
  try {
    await api("/api/pessoas", {
      method: "POST",
      body: JSON.stringify({ nome: data.get("nome"), idade: Number(data.get("idade")) })
    });
    form.reset();
    await refresh();
    if (el("message").hidden) message("Morador cadastrado com sucesso.", true);
  } catch (error) {
    message(error.message);
  }
});

el("transaction-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const data = new FormData(form);
  try {
    await api("/api/transacoes", {
      method: "POST",
      body: JSON.stringify({
        descricao: data.get("descricao"),
        valor: Number(data.get("valor")),
        tipo: data.get("tipo"),
        pessoaId: Number(data.get("pessoaId"))
      })
    });
    form.reset();
    await refresh();
    if (el("message").hidden) message("Transação cadastrada com sucesso.", true);
  } catch (error) {
    message(error.message);
  }
});

refresh();

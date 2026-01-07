// src/services/loadData.js
export async function carregarDadosApi() {
  const url = "http://localhost:5000/api/data";
  const res = await fetch(url);
  if (!res.ok) throw new Error("Falha ao buscar dados: " + res.status);
  const data = await res.json();

  // Seleciona o arquivo correto
  const arquivo = data.find(x =>
    x.filename === "Relatório painel orçamentário - Histórico.json"
  ) || data[0];

  const registrosBrutos = arquivo.records;

  // Se o JSON vier como objeto único, transforma em lista com 1 item
  const lista = Array.isArray(registrosBrutos)
    ? registrosBrutos
    : [registrosBrutos];

  // Mapeia cada item para formato padronizado
  const registros = lista.map(raw => ({
    valor_13: raw["13"],
    valor_23: raw["23"],
    ano: raw["Ano Lançamento"],
    mes: raw["Mês Lançamento"],
    resultado: raw["Resultado Lei"],
    resultado_descricao: raw["Resultado Lei: 3"],
    acao: raw["Ação Governo"],
    acao_descricao: raw["Ação Governo: 5"],
    item: raw["Item Informação"],
    item_descricao: raw["Item Informação: 7"]
  }));

  return registros;
}

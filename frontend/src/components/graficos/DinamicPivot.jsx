"use client";

import { useMemo } from "react";

export default function DynamicPivotTable({ filteredData }) {
  if (!filteredData || filteredData.length === 0) {
    return (
      <div className="w-full h-64 flex items-center justify-center text-gray-400">
        Nenhum dado disponível
      </div>
    );
  }

  // CAMPO PARA AGRUPAMENTO (você pode trocar para qualquer um do JSON)
  const groupField = "Ação Governo: 5";

  const pivot = useMemo(() => {
    const map = {};

    filteredData.forEach((item) => {
      const key = item[groupField] || "Não informado";

      if (!map[key]) {
        map[key] = {
          categoria: key,
          dotacao: 0,
          execucao: 0,
        };
      }

      map[key].dotacao += Number(item["13"]) || 0;
      map[key].execucao += Number(item["23"]) || 0;
    });

    // Transformar em array e calcular %
    let rows = Object.values(map).map((r) => ({
      ...r,
      percentual:
        r.dotacao > 0 ? (r.execucao / r.dotacao) * 100 : 0,
    }));

    // Ordenar pelo maior valor executado
    rows.sort((a, b) => b.execucao - a.execucao);

    // Adicionar ranking
    rows = rows.map((row, index) => ({
      ...row,
      ranking: index + 1,
    }));

    return rows;
  }, [filteredData]);

  return (
    <div className="bg-white shadow rounded-lg p-4 w-full">
      <h2 className="text-lg font-semibold mb-3">
        Tabela Dinâmica Avançada — Ranking por Execução
      </h2>

      <div className="overflow-auto max-h-[400px]">
        <table className="min-w-full border-collapse">
          <thead className="bg-gray-100 sticky top-0">
            <tr>
              <th className="border p-2 text-left">Ranking</th>
              <th className="border p-2 text-left">{groupField}</th>
              <th className="border p-2 text-right">Dotação (R$)</th>
              <th className="border p-2 text-right">Execução (R$)</th>
              <th className="border p-2 text-right">% Execução</th>
            </tr>
          </thead>

          <tbody>
            {pivot.map((row) => (
              <tr key={row.categoria} className="hover:bg-gray-50">
                <td className="border p-2">{row.ranking}</td>

                <td className="border p-2">{row.categoria}</td>

                <td className="border p-2 text-right">
                  {row.dotacao.toLocaleString("pt-BR", {
                    style: "currency",
                    currency: "BRL",
                  })}
                </td>

                <td className="border p-2 text-right">
                  {row.execucao.toLocaleString("pt-BR", {
                    style: "currency",
                    currency: "BRL",
                  })}
                </td>

                <td className="border p-2 text-right">
                  {row.percentual.toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

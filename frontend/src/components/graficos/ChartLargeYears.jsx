// components/charts/ChartLargeAnual.jsx
"use client";

import { useEffect } from "react";
import * as echarts from "echarts";

export default function ChartLargeAnual({ filtrados }) {

  useEffect(() => {
    if (!filtrados || filtrados.length === 0) return;

    const chartDom = document.getElementById("chart-large-anual");
    if (!chartDom) return;

    const chart = echarts.init(chartDom);

    // ---------------------------------------
    // 1. PEGAR ANOS DO JSON
    // ---------------------------------------
    const anosSet = new Set();

    filtrados.forEach(item => {
      const ano = item["Filtro do relatório:"];
      if (ano) anosSet.add(ano);
    });

    const anos = Array.from(anosSet).sort();

    // ---------------------------------------
    // 2. SOMAR VALORES POR ANO
    // ---------------------------------------
    const valores = anos.map(ano => {
      return filtrados
        .filter(i => i["Filtro do relatório:"] === ano)
        .reduce((acc, cur) => acc + (Number(cur["Filtro do relatório:: 26"]) || 0), 0);
    });

    // ---------------------------------------
    // 3. OPÇÃO DO ECHARTS
    // ---------------------------------------
    const option = {
      tooltip: {
        trigger: "axis",
        formatter: (params) => {
          const item = params[0];
          return `${item.name}: ${item.value.toLocaleString("pt-BR")}`;
        }
      },

      color: [ "#5470C6", "#91CC75", "#EE6666", "#73C0DE", "#FAC858" ], // cores automáticas

      xAxis: {
        type: "category",
        data: anos,
        axisLabel: { rotate: 0 }
      },

      yAxis: { type: "value" },

      series: [
        {
          type: "bar",
          data: valores,
          label: {
            show: true,
            position: "top",
            formatter: (v) =>
              v.value.toLocaleString("pt-BR")
          }
        }
      ]
    };

    chart.setOption(option);

    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, [filtrados]);

  return (
    <div className="card-dashboard larger">
      <div className="card-header">Dotação Orçamentária (Por Ano) </div>
      <div className="card-body">
        <div id="chart-large-anual" className="chart-container"></div>
      </div>
    </div>
  );
}

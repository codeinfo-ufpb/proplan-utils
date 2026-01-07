"use client";

import { useEffect } from "react";
import * as echarts from "echarts";

export default function ChartControl({ filtrados }) {

  useEffect(() => {
    if (!filtrados || filtrados.length === 0) return;

    const chartDom = document.getElementById("chart-control");
    const chart = echarts.init(chartDom);

    // ================================
    // 1. PEGAR MESES E EXECUÇÃO (23)
    // ================================
    const ordemMeses = [
      "JAN/2025", "FEV/2025", "MAR/2025", "ABR/2025",
      "MAI/2025", "JUN/2025", "JUL/2025", "AGO/2025",
      "SET/2025", "OUT/2025", "NOV/2025", "DEZ/2025"
    ];

    const meses = [...new Set(filtrados.map(i => i["Filtro do relatório:: 20"]))].sort(
      (a, b) => ordemMeses.indexOf(a) - ordemMeses.indexOf(b)
    );

    const valores = meses.map(mes =>
      filtrados
        .filter(i => i["Filtro do relatório:: 20"] === mes)
        .reduce((acc, cur) => acc + (Number(cur["Filtro do relatório:: 30"]) || 0), 0)
    );

    // ================================
    // 2. CÁLCULO DA MÉDIA E DESVIO
    // ================================
    const media =
      valores.reduce((acc, v) => acc + v, 0) / valores.length;

    const desvioPadrao = Math.sqrt(
      valores
        .map(v => Math.pow(v - media, 2))
        .reduce((acc, v) => acc + v, 0) / valores.length
    );

    const UCL = media + 3 * desvioPadrao;
    const LCL = Math.max(0, media - 3 * desvioPadrao); // não deixa negativo

    // Colocar linhas horizontais
    const linhaMedia = Array(valores.length).fill(media);
    const linhaUCL = Array(valores.length).fill(UCL);
    const linhaLCL = Array(valores.length).fill(LCL);

    // ================================
    // 3. MONTAR O GRÁFICO
    // ================================
    const option = {
      title: { text: "Carta de Controle (X-bar)" },
      tooltip: { trigger: "axis" },

      xAxis: {
        type: "category",
        data: meses
      },

      yAxis: { type: "value" },

      series: [
        // Série principal — Execução
        {
          name: "Execução (Filtro do relatório:: 30)",
          type: "line",
          smooth: true,
          data: valores,
          symbol: "circle",
          symbolSize: 10,
        },

        // Média
        {
          name: "Média",
          type: "line",
          data: linhaMedia,
          lineStyle: { type: "dashed" },
        },

        // UCL
        {
          name: "UCL (Limite Superior)",
          type: "line",
          data: linhaUCL,
          lineStyle: { color: "red", type: "dotted" },
        },

        // LCL
        {
          name: "LCL (Limite Inferior)",
          type: "line",
          data: linhaLCL,
          lineStyle: { color: "green", type: "dotted" },
        }
      ]
    };

    chart.setOption(option);
    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, [filtrados]);

  return (
    <div className="card-dashboard">
      <div className="card-header">Carta de Controle (X-bar)</div>
      <div className="card-body">
        <div id="chart-control" className="chart-container"></div>
      </div>
    </div>
  );
}

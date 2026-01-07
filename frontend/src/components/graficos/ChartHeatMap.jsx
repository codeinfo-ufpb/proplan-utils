"use client";

import { useEffect } from "react";
import * as echarts from "echarts";

export default function ChartHeatmap({ filtrados }) {

  useEffect(() => {
    if (!filtrados || filtrados.length === 0) return;

    const chartDom = document.getElementById("chart-heatmap");
    const chart = echarts.init(chartDom);

    // ========================
    // 1. EIXOS
    // ========================
    const ordemMeses = [
      "JAN/2025", "FEV/2025", "MAR/2025", "ABR/2025",
      "MAI/2025", "JUN/2025", "JUL/2025", "AGO/2025",
      "SET/2025", "OUT/2025", "NOV/2025", "DEZ/2025"
    ];

    const meses = [...new Set(filtrados.map(i => i["Filtro do relatório:: 20"]))]
      .filter(Boolean)
      .sort((a, b) => ordemMeses.indexOf(a) - ordemMeses.indexOf(b));

    const anos = [...new Set(filtrados.map(i => i["Filtro do relatório:: 21"]))]
      .filter(Boolean)
      .sort();

    // ========================
    // 2. AGRUPAR EXECUÇÃO (23)
    // ========================
    const matriz = anos.map(ano =>
      meses.map(mes => {
        const soma = filtrados
          .filter(i => i["Filtro do relatório:: 21"] === ano && i["Filtro do relatório:: 20"] === mes)
          .reduce((acc, cur) => acc + (Number(cur["Filtro do relatório:: 26"]) || 0), 0);

        return soma;
      })
    );

    // Formatar para o formato exigido pelo Heatmap
    const dadosHeatmap = [];
    anos.forEach((ano, yIndex) => {
      meses.forEach((mes, xIndex) => {
        dadosHeatmap.push([xIndex, yIndex, matriz[yIndex][xIndex] || 0]);
      });
    });

    // ========================
    // 3. CONFIG DO ECHARTS
    // ========================
    const option = {
      title: { text: "Heatmap Ano x Mês — Execução (23)" },

      tooltip: {
        formatter: (params) => {
          const valor = params.value[2] || 0;
          return `
            Ano: <b>${anos[params.value[1]]}</b><br>
            Mês: <b>${meses[params.value[0]]}</b><br>
            Execução: <b>R$ ${valor.toLocaleString("pt-BR")}</b>
          `;
        }
      },

      grid: { top: 50, bottom: 40 },

      xAxis: {
        type: "category",
        data: meses,
        axisLabel: { rotate: 35 }
      },

      yAxis: {
        type: "category",
        data: anos
      },

      visualMap: {
        min: 0,
        max: Math.max(...dadosHeatmap.map(d => d[2])),
        calculable: true,
        orient: "vertical",
        right: 10,
        top: "center"
      },

      series: [
        {
          name: "Execução",
          type: "heatmap",
          data: dadosHeatmap,
          label: { show: true, formatter: p => p.value[2] ? "" : "" },
          emphasis: { itemStyle: { shadowBlur: 10 } }
        }
      ]
    };

    chart.setOption(option);
    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, [filtrados]);

  return (
    <div className="card-dashboard-small">
      <div className="card-header">Mapa de Calor — Execução</div>
      <div className="card-body">
        <div id="chart-heatmap" className="chart-container"></div>
      </div>
    </div>
  );
}

"use client";

import { useEffect } from "react";
import * as echarts from "echarts";

export default function BoxplotExecucaoPorItem({ filteredData }) {
  useEffect(() => {
    if (!filteredData || filteredData.length === 0) return;

    const chartDom = document.getElementById("boxplot-execucao-item");
    const chart = echarts.init(chartDom);

    // -----------------------------
    // 1. AGRUPAR EXECUÇÃO POR ITEM
    // -----------------------------
    const grupos = {};

    filteredData.forEach((item) => {
      const categoria = item["Item Informação: 7"] || "Não informado";
      const valor = Number(item["13"]) || 0;

      if (!grupos[categoria]) grupos[categoria] = [];
      grupos[categoria].push(valor);
    });

    // -----------------------------
    // 2. CALCULAR ESTATÍSTICAS
    // -----------------------------
    function calcularBoxplot(valores) {
      valores.sort((a, b) => a - b);

      const min = valores[0];
      const max = valores[valores.length - 1];

      const Q1 = quantil(valores, 0.25);
      const mediana = quantil(valores, 0.5);
      const Q3 = quantil(valores, 0.75);

      return [min, Q1, mediana, Q3, max];
    }

    function quantil(valores, q) {
      const pos = (valores.length - 1) * q;
      const base = Math.floor(pos);
      const resto = pos - base;

      if (valores[base + 1] !== undefined) {
        return valores[base] + resto * (valores[base + 1] - valores[base]);
      } else {
        return valores[base];
      }
    }

    const categorias = Object.keys(grupos);
    const estatisticas = categorias.map((cat) =>
      calcularBoxplot(grupos[cat])
    );

    // Ordenar categorias pela mediana
    const ordenado = categorias
      .map((cat, i) => ({ cat, mediana: estatisticas[i][2], stats: estatisticas[i] }))
      .sort((a, b) => b.mediana - a.mediana);

    const categoriasOrdenadas = ordenado.map((x) => x.cat);
    const estatisticasOrdenadas = ordenado.map((x) => x.stats);

    // -----------------------------
    // 3. CONFIG ECHARTS
    // -----------------------------
    const option = {
      tooltip: {
        trigger: "item",
        formatter: (param) => {
          const [min, q1, mediana, q3, max] = param.data;
          return `
            <b>${param.name}</b><br/>
            Min: ${min.toLocaleString("pt-BR")}<br/>
            Q1: ${q1.toLocaleString("pt-BR")}<br/>
            Mediana: ${mediana.toLocaleString("pt-BR")}<br/>
            Q3: ${q3.toLocaleString("pt-BR")}<br/>
            Max: ${max.toLocaleString("pt-BR")}
          `;
        },
      },
      xAxis: {
        type: "category",
        data: categoriasOrdenadas,
        axisLabel: { rotate: 30 },
      },
      yAxis: {
        type: "value",
        name: "Execução (R$)",
      },
      series: [
        {
          name: "Execução",
          type: "boxplot",
          data: estatisticasOrdenadas,
          itemStyle: {
            borderColor: "#444",
          },
        },
      ],
    };

    chart.setOption(option);

    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.dispose();
    };
  }, [filteredData]);

  return (
    <div className="card-dashboard">
        <div className="card-header">
          Boxplot — Execução por Item Informação
        </div>
        <div className="card-body">
          <div id="boxplot-execucao-item" className="chart-container"></div>
        </div>
    </div>
  );
}
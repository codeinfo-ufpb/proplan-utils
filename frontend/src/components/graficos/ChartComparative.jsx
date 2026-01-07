"use client";

import { useEffect } from "react";
import * as echarts from "echarts";

export default function ChartComparativoDotacaoExecucao({ filtrados }) {

  useEffect(() => {
    if (!filtrados || filtrados.length === 0) return;

    const chartDom = document.getElementById("chart-comparativo-dotacao-execucao");
    const chart = echarts.init(chartDom);

    // ---------------------------------------
    // 1. CAPTURAR ANO + MÊS
    // ---------------------------------------
    let categorias = [];

    filtrados.forEach(item => {
      const mes = item["Filtro do relatório:: 20"];
      const ano = item["Filtro do relatório:: 21"];
      if (!mes || !ano) return;

      const chave = `${mes}-${ano}`;
      if (!categorias.includes(chave)) categorias.push(chave);
    });

    // Ordenação correta JAN..DEZ por ano
    const ordemMeses = [
      "JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
      "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"
    ];

    categorias.sort((a, b) => {
      const [mesA, anoA] = a.split("-");
      const [mesB, anoB] = b.split("-");

      if (anoA !== anoB) return Number(anoA) - Number(anoB);
      return ordemMeses.indexOf(mesA.split("/")[0]) - ordemMeses.indexOf(mesB.split("/")[0]);
    });

    // ---------------------------------------
    // 2. MONTAR VALORES PARA DOTACAO E EXECUCAO
    // ---------------------------------------
    const valoresDotacao = [];
    const valoresExecucao = [];

    categorias.forEach(chave => {
      const [mes, ano] = chave.split("-");

      const filtradosMesAno = filtrados.filter(
        i => i["Filtro do relatório:: 20"] === mes && i["Filtro do relatório:: 21"] == ano
      );

      const soma13 = filtradosMesAno.reduce((acc, cur) => acc + (Number(cur["Filtro do relatório:: 26"]) || 0), 0);
      const soma23 = filtradosMesAno.reduce((acc, cur) => acc + (Number(cur["Filtro do relatório:: 30"]) || 0), 0);

      valoresDotacao.push(soma13);
      valoresExecucao.push(soma23);
    });

    // ---------------------------------------
    // 3. OPÇÃO DO GRÁFICO
    // ---------------------------------------
    const option = {
      title: { text: "Dotação x Execução (Comparação Mensal por Ano)" },
      tooltip: { trigger: "axis" },
      legend: {
        type: "scroll",          // permite rolagem se ultrapassar o limite
        orient: "horizontal",
        bottom: 0,
        left: "center",
        width: "80%",            // legenda não fica tão larga
        itemWidth: 14,
        itemHeight: 10,
        data: ["Dotação (Filtro do relatório:: 26)", "Execução (Filtro do relatório:: 30)"],
      },
      xAxis: {
        type: "category",
        data: categorias,
        axisLabel: { rotate: 45 }
      },
      yAxis: { type: "value" },
      series: [
        {
          name: "Dotação (Filtro do relatório:: 26)",
          type: "line",
          smooth: true,
          data: valoresDotacao
        },
        {
          name: "Execução (Filtro do relatório:: 30)",
          type: "line",
          smooth: true,
          data: valoresExecucao
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
      <div className="card-header">Dotação x Execução</div>
      <div className="card-body">
        <div id="chart-comparativo-dotacao-execucao" className="chart-container"></div>
      </div>
    </div>
  );
}

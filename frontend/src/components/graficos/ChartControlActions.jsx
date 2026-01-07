// components/charts/ChartControleAcoes.jsx
"use client";

import { useEffect, useState } from "react";
import * as echarts from "echarts";
import * as XLSX from "xlsx";


export default function ChartControleAcoes({ filtrados }) {
  

  const [isFullscreen, setIsFullscreen] = useState(false);
  const [chartInstance, setChartInstance] = useState(null);



  useEffect(() => {
    if (!filtrados || filtrados.length === 0) return;

    const chartDom = document.getElementById("chart-controle-acoes");
    if (!chartDom) return;

    const chart = echarts.init(chartDom);
    setChartInstance(chart);

    // ------------------------------
    // AGRUPAMENTO
    // ------------------------------
    const mapa = new Map();

    filtrados.forEach(item => {
      const acao = item["Filtro do relatório:: 6"];
      const valor = Number(item["Filtro do relatório:: 26"]) || 0;

      if (!acao) return;

      if (!mapa.has(acao)) mapa.set(acao, 0);
      mapa.set(acao, mapa.get(acao) + valor);
    });

    const categorias = Array.from(mapa.keys());
    const valores = Array.from(mapa.values());

    const media = valores.reduce((a, b) => a + b, 0) / valores.length;
    const limiteSuperior = media * 1.20;
    const limiteInferior = media * 0.80;

    const linhaMedia = categorias.map(() => media);
    const linhaLS = categorias.map(() => limiteSuperior);
    const linhaLI = categorias.map(() => limiteInferior);

    const option = {
      title: { text: "Carta de Controle - Unidades Responsáveis", left: "center" },

      grid: {
        top: 80,
        left: 60,
        right: 40,
        bottom: 140,   
        containLabel: true
      },

      tooltip: {
        trigger: "axis"
      },

      xAxis: {
        type: "category",
        data: categorias,
        axisLabel: { rotate: 35 }
      },

      yAxis: {
        type: "value",
        name: "Execução"
      },

      series: [
        {
          name: "Valor Total",
          type: "line",
          data: valores,
          smooth: true
        },
        {
          name: "Média",
          type: "line",
          data: linhaMedia,
          lineStyle: { type: "dashed" }
        },
        {
          name: "Limite Superior",
          type: "line",
          data: linhaLS,
          lineStyle: { type: "dotted" }
        },
        {
          name: "Limite Inferior",
          type: "line",
          data: linhaLI,
          lineStyle: { type: "dotted" }
        }
      ]
    };

    chart.setOption(option);

    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.dispose();
    };

  }, [filtrados, isFullscreen]);

    // ---------------------------
    // DOWNLOAD: JPEG
    // ---------------------------
    const downloadJPEG = () => {
      if (!chartInstance) return;
      const imageURI = chartInstance.getDataURL({
        pixelRatio: 2,
        backgroundColor: "#ffffff",
        type: "jpeg",
      });
  
      const a = document.createElement("a");
      a.href = imageURI;
      a.download = `${title}.jpeg`;
      a.click();
    };
  
    // ---------------------------
    // DOWNLOAD: Excel
    // ---------------------------
    const downloadExcel = () => {
      if (!filtrados) return;
  
      const grupos = {};
      filtrados.forEach(i => {
        const cat = i["Filtro do relatório:: 4"];
        const v = Number(i["Filtro do relatório:: 26"]) || 0;
        grupos[cat] = (grupos[cat] || 0) + v;
      });
  
      const rows = Object.keys(grupos).map(k => ({
        Categoria: k,
        Valor: grupos[k],
      }));
  
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(rows);
  
      XLSX.utils.book_append_sheet(wb, ws, "Dados");
      XLSX.writeFile(wb, `${title}.xlsx`);
    };
  
    // ---------------------------
    // DOWNLOAD: PDF
    // ---------------------------
    const downloadPDF = async () => {
      if (!chartInstance) return;
  
      const img = chartInstance.getDataURL({
        pixelRatio: 2,
        backgroundColor: "#ffffff",
        type: "jpeg",
      });
  
      const { jsPDF } = await import("jspdf");
      const pdf = new jsPDF("landscape", "pt", "a4");
  
      pdf.addImage(img, "JPEG", 20, 20, 750, 550);
      pdf.save(`${title}.pdf`);
    };


  return (
    <div className={`card-dashboard larger ${isFullscreen ? "fullscreen-chart" : ""}`}>
      
      
      <div className="card-header">
        Carta de Controle — Ações do Governo
      </div>
              <div className="chart-actions">
          <button onClick={downloadJPEG}>
            <img src="../svg/card-image.svg" alt="Imagem representando o download em formato JPEG" />
          </button>
          <button onClick={downloadExcel}>
            <img src="../svg/file-earmark-excel.svg" alt="Imagem representando o download em formato xlsx" />
          </button>
          <button onClick={downloadPDF}>
            <img src="../svg/filetype-pdf.svg" alt="Imagem representando o download em formato PDF" />
          </button>
        {/* Botão Fullscreen */}
        <button
          onClick={() => setIsFullscreen(!isFullscreen)}
          className="fullscreen-btn"
        >
          {isFullscreen ? <img src="../svg/fullscreen-exit.svg" alt="Imagem representando tela cheia fullscreen" /> : <img src="../svg/arrows-fullscreen.svg" alt="Imagem representando tela cheia fullscreen" />}
        </button>
        </div>
      

      {/* ÁREA DO GRÁFICO 100% AJUSTADA */}
      <div className="card-body">
        <div id="chart-controle-acoes" className="chart-container"></div>
      </div>

    </div>
  );
}

// --------------------------------------------
// EXPORTAÇÕES FUTURAS (placeholder)
// --------------------------------------------
function exportar(tipo) {
  alert("Exportar em " + tipo + " ainda será implementado.");
}

// components/charts/ChartPie.jsx
"use client";

import { useEffect, useState } from "react";
import * as echarts from "echarts";
import * as XLSX from "xlsx";

export default function ChartPie({ title, filtrados = [], anoSelecionado}) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [chartInstance, setChartInstance] = useState(null);

  useEffect(() => {
    if (!filtrados || filtrados.length === 0) return;

    const elementId = title.replaceAll(" ", "-").toLowerCase();
    const chartDom = document.getElementById(elementId);
    if (!chartDom) return;

    // Inicializando
    const chart = echarts.init(chartDom);
    setChartInstance(chart);

    // ---------------------------
    // 1. AGRUPAR DADOS
    // ---------------------------
    const grupos = {};
    filtrados.forEach(item => {
      const categoria = item["Filtro do relatório:: 4"];
      const valor = Number(item["Filtro do relatório:: 26"]) || 0;
      if (categoria) grupos[categoria] = (grupos[categoria] || 0) + valor;
    });

    const categorias = Object.keys(grupos);
    const valores = categorias.map(c => ({
      name: c,
      value: grupos[c],
    }));

    // ---------------------------
    // Fonte responsiva
    // ---------------------------
    const responsiveFont = Math.max(10, chartDom.clientWidth * 0.015);

    const option = {
      tooltip: {
        trigger: "item",
        formatter: "{b}<br/>{c} ({d}%)",
      },
        legend: {
          type: "scroll",          // permite rolagem se ultrapassar o limite
          orient: "horizontal",
          bottom: 0,
          left: "center",
          width: "80%",            // legenda não fica tão larga
          itemWidth: 14,
          itemHeight: 10,
          textStyle: {
            fontSize: responsiveFont * 0.9,
          },
        },
      series: [
        {
          type: "pie",
          radius: "70%",
          center: ["40%", "50%"],
          selectedMode: "single",
          data: valores,
          label: {
            show: false,
            formatter: "{b}\n{d}%",
            fontSize: responsiveFont,
            overflow: "truncate",
          },
          labelLayout: { hideOverlap: true },
        },
      ],
    };

    chart.setOption(option);
    const resize = () => chart.resize();
    window.addEventListener("resize", resize);

    return () => {
      window.removeEventListener("resize", resize);
      chart.dispose();
    };
  }, [title, filtrados, anoSelecionado, isFullscreen]);

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

  const elementId = title.replaceAll(" ", "-").toLowerCase();
  const periodoTexto = anoSelecionado ? `Ano: ${anoSelecionado}` : "Todos os anos";

  return (
    <div className={`card-dashboard-small ${isFullscreen ? "fullscreen-chart" : ""}`}>
      <div className="card-header">
        {title}
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
      <span className="subinfo">{periodoTexto}</span>
      <div className="card-body">
        <div id={elementId} className="chart-container"></div>
      </div>
    </div>
  );
}

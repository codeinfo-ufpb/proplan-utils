"use client";

import { useEffect, useState } from "react";
import * as echarts from "echarts";
import * as XLSX from "xlsx";

export default function ChartSmall({ title, categorias = [], valores = [], cores = [] }) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [chartInstance, setChartInstance] = useState(null);

  useEffect(() => {
    const elementId = title.replaceAll(" ", "-").toLowerCase();
    const chartDom = document.getElementById(elementId);
    if (!chartDom) return;

    const chart = echarts.init(chartDom);
    setChartInstance(chart);

    // Fonte responsiva
    const responsiveFont = Math.max(10, chartDom.clientWidth * 0.02);

    const option = {
      tooltip: { trigger: "axis" },
      color: cores,
      grid: { left: 40, right: 20, top: 40, bottom: 50 },

      xAxis: {
        type: "category",
        data: categorias,
        axisLabel: {
          rotate: 35,
          fontSize: responsiveFont * 0.7,
        },
      },

      yAxis: {
        type: "value",
        axisLabel: { fontSize: responsiveFont * 0.8 },
      },

      series: [
        {
          type: "bar",
          data: valores,
          label: {
            show: true,
            position: "top",
            fontSize: responsiveFont * 0.9,
            formatter: v =>
              v.value.toLocaleString("pt-BR", {
                minimumFractionDigits: 0,
              }),
          },
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
  }, [title, categorias, valores, cores, isFullscreen]);

  // --------------------------------------------
  // EXPORTAR JPEG
  // --------------------------------------------
  const downloadJPEG = () => {
    if (!chartInstance) return;
    const img = chartInstance.getDataURL({
      pixelRatio: 2,
      backgroundColor: "#fff",
      type: "jpeg",
    });

    const a = document.createElement("a");
    a.href = img;
    a.download = `${title}.jpeg`;
    a.click();
  };

  // --------------------------------------------
  // EXPORTAR EXCEL
  // --------------------------------------------
  const downloadExcel = () => {
    const rows = categorias.map((cat, i) => ({
      Categoria: cat,
      Valor: valores[i] || 0,
    }));

    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.json_to_sheet(rows);

    XLSX.utils.book_append_sheet(wb, ws, "Dados");
    XLSX.writeFile(wb, `${title}.xlsx`);
  };

  // --------------------------------------------
  // EXPORTAR PDF
  // --------------------------------------------
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

  // --------------------------------------------
  // HTML
  // --------------------------------------------
  const elementId = title.replaceAll(" ", "-").toLowerCase();

  return (
    <div className={`card-dashboard-small ${isFullscreen ? "fullscreen-chart" : ""}`}>
      <div className="card-header">
        {title}

        <div className="export-buttons">
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
      </div>

      <span className="subinfo">Período: Todos os anos</span>

      <div className="card-body">
        <div id={elementId} className="chart-container"></div>
      </div>
    </div>
  );
}

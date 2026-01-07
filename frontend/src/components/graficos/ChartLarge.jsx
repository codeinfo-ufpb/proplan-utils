"use client";

import { useEffect, useState, useRef } from "react";
import * as echarts from "echarts";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

export default function ChartLarge({ filtrados = [], onSelect }) {
  const [quantidadeMeses, setQuantidadeMeses] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [view, setView] = useState("bar"); 
  const chartRef = useRef(null);

  let variavel = "Filtro do relatório:: 20";


  // ----------------------------------------------------
  // EXPORTADOR PARA JPEG
  // ----------------------------------------------------
  const downloadJPEG = () => {
    if (!chartRef.current || view === "table") return;

    const img = chartRef.current.getDataURL({
      pixelRatio: 3,
      backgroundColor: "#fff",
      type: "jpeg",
    });

    const a = document.createElement("a");
    a.href = img;
    a.download = "execucao_mensal.jpeg";
    a.click();
  };

  // ----------------------------------------------------
  // EXPORTADOR PARA EXCEL
  // ----------------------------------------------------
  const downloadExcel = (meses, valores) => {
    const rows = meses.map((mes, i) => ({
      Mes: mes,
      Execucao: valores[i] ?? 0,
    }));

    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.json_to_sheet(rows);
    XLSX.utils.book_append_sheet(wb, ws, "Dados");
    XLSX.writeFile(wb, "execucao_mensal.xlsx");
  };

  // ----------------------------------------------------
  // EXPORTADOR PARA PDF
  // ----------------------------------------------------
  const downloadPDF = (meses, valores) => {
    const pdf = new jsPDF("landscape");

    pdf.setFontSize(18);
    pdf.text("Execução Mensal", 30, 30);

    if (chartRef.current && view !== "table") {
      const img = chartRef.current.getDataURL({
        pixelRatio: 3,
        type: "jpeg",
      });

      pdf.addImage(img, "JPEG", 20, 40, 760, 400);
    }

    autoTable(pdf, {
      startY: 460,
      head: [["Mês", "Execução"]],
      body: meses.map((m, i) => [m, valores[i]]),
    });

    pdf.save("execucao_mensal.pdf");
  };

  // ----------------------------------------------------
  // MONTAGEM DO GRÁFICO
  // ----------------------------------------------------
  useEffect(() => {
    if (!filtrados || filtrados.length === 0 || view === "table") return;

    const chartDom = document.getElementById("chart-large");
    if (!chartDom) return;

    const chart = echarts.init(chartDom);
    chartRef.current = chart;

    // ----- CALCULA OS MESES -----
    const meses = Array.from(
      new Set(filtrados.map((i) => i[variavel]).filter(Boolean))
    );

    const ordemMeses = [
      "JAN/2025","FEV/2025","MAR/2025","ABR/2025",
      "MAI/2025","JUN/2025","JUL/2025","AGO/2025",
      "SET/2025","OUT/2025","NOV/2025","DEZ/2025"
    ];

    meses.sort((a, b) => ordemMeses.indexOf(a) - ordemMeses.indexOf(b));

    const mesesFiltrados =
      quantidadeMeses === null ? meses : meses.slice(-quantidadeMeses);

    // ----- SOMA VALORES -----
    const valores = mesesFiltrados.map((mes) =>
      filtrados
        .filter((i) => i["Filtro do relatório:: 20"] === mes)
        .reduce((acc, cur) => acc + (Number(cur["Filtro do relatório:: 26"]) || 0), 0)
    );

    // ----------------------------------------------------------
    // Configuração dos tipos dos gráficos disponíveis (Barras, Linhas, Empilhados...)
    // ----------------------------------------------------------
    const baseSeries = {
      data: valores,
      label: {
        show: true,
        position: "top",
        formatter: (v) => v.value.toLocaleString("pt-BR"),
      },
      animationDuration: 800,
      animationEasing: "quadraticOut",
    };

    const chartOptions = {
      animation: true,
      tooltip: { trigger: "axis" },
      grid: { left: 50, right: 30, top: 60, bottom: 80 },
      xAxis: { type: "category", data: mesesFiltrados },
      yAxis: { type: "value" },
      series: [
        {
          ...baseSeries,
          type:
            view === "bar" ? "bar" :
            view === "line" ? "line" :
            "bar", // stacked usa bar

          stack: view === "stacked" ? "total" : undefined,

          itemStyle: {
            color: view === "line" ? "#5eff00" : "#4287f5",
          },
          areaStyle: view === "line" ? { opacity: 0.15 } : undefined,
        },
      ],
    };

    chart.setOption(chartOptions);

    chart.on("click", (params) => {
      if (onSelect) onSelect(params.name);
    });

    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.dispose();
    };
  }, [filtrados, quantidadeMeses, isFullscreen, view]);

  // ----------------------------------------------------------
  // VIEW: TABELA
  // ----------------------------------------------------------
  const renderTable = () => {
    const meses = Array.from(
      new Set(filtrados.map((i) => i["Filtro do relatório:: 20"]).filter(Boolean))
    );

    const ordem = [
      "JAN/2025","FEV/2025","MAR/2025","ABR/2025",
      "MAI/2025","JUN/2025","JUL/2025","AGO/2025",
      "SET/2025","OUT/2025","NOV/2025","DEZ/2025"
    ];

    meses.sort((a, b) => ordem.indexOf(a) - ordem.indexOf(b));

    const mesesFiltrados =
      quantidadeMeses === null ? meses : meses.slice(-quantidadeMeses);

    const valores = mesesFiltrados.map((mes) =>
      filtrados
        .filter((i) => i["Filtro do relatório:: 20"] === mes)
        .reduce((acc, cur) => acc + (Number(cur["Filtro do relatório:: 26"]) || 0), 0)
    );

    return (
      <table className="table-view">
        <thead>
          <tr>
            <th>Mês</th>
            <th>Execução</th>
          </tr>
        </thead>
        <tbody>
          {mesesFiltrados.map((mes, i) => (
            <tr key={mes}>
              <td>{mes}</td>
              <td>{valores[i].toLocaleString("pt-BR")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  // ----------------------------------------------------------
  // RENDER
  // ----------------------------------------------------------
  return (
    <div className={`card-dashboard larger ${isFullscreen ? "fullscreen-chart" : ""}`}>
      <div className="card-header">
        Despesas Empenhadas (Mensalmente)
        
        <select
          value={view}
          onChange={(e) => setView(e.target.value)}
          style={{ marginRight: "15px", marginLeft: "10px", padding: "4px 8px", borderRadius: "6px" }}
        >
          <option value="bar">Barras</option>
          <option value="line">Linha</option>
          <option value="stacked">Barras Empilhadas</option>
          <option value="table">Tabela</option>
        </select>
        {/* BOTÕES DE EXPORTAÇÃO */}
        <div className="export-buttons">
          <button onClick={downloadJPEG}>
            <img src="../svg/card-image.svg" />
          </button>

          <button
            onClick={() => {
              const opt = chartRef.current?.getOption();
              downloadExcel(
                view === "table" ? [] : opt.xAxis[0].data,
                view === "table" ? [] : opt.series[0].data
              );
            }}
          >
            <img src="../svg/file-earmark-excel.svg" />
          </button>

          <button
            onClick={() => {
              const opt = chartRef.current?.getOption();
              downloadPDF(
                view === "table" ? [] : opt.xAxis[0].data,
                view === "table" ? [] : opt.series[0].data
              );
            }}
          >
            <img src="../svg/filetype-pdf.svg" />
          </button>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="fullscreen-btn"
          >
            {isFullscreen ? (
              <img src="../svg/fullscreen-exit.svg" />
            ) : (
              <img src="../svg/arrows-fullscreen.svg" />
            )}
          </button>
        </div>
        
        {/* SELECTOR DE VISUALIZAÇÃO */}

      </div>

      <span className="subinfo">Período: Últimos Meses</span>

      {/* BOTÕES DE MESES */}
      <div className="month-buttons">
        <button className={quantidadeMeses === null ? "active" : ""} onClick={() => setQuantidadeMeses(null)}>Todos</button>
        <button className={quantidadeMeses === 12 ? "active" : ""} onClick={() => setQuantidadeMeses(12)}>12m</button>
        <button className={quantidadeMeses === 6 ? "active" : ""} onClick={() => setQuantidadeMeses(6)}>6m</button>
        <button className={quantidadeMeses === 3 ? "active" : ""} onClick={() => setQuantidadeMeses(3)}>3m</button>
      </div>

      <div className="card-body">
        {view === "table" ? (
          renderTable()
        ) : (
          <div id="chart-large" className="chart-container"></div>
        )}
      </div>
    </div>
  );
}

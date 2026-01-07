
export default function Exportadores(){

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



}
import { useMemo } from "react";

export function useCards(filteredData = []) {

  const safeArray = Array.isArray(filteredData) ? filteredData : [];

  // ======================== LIMPAR CABEÇALHO ========================
  const dadosValidos = useMemo(() => {
    return safeArray.filter(item => {
      const valor13 = item["Filtro do relatório:: 26"];
      return typeof valor13 === "number" && !isNaN(valor13);
    });
  }, [safeArray]);

  // ======================== TOTAL EM REAIS ==========================
  const totalReais = useMemo(() => {
    return dadosValidos.reduce((acc, item) => acc + (item["Filtro do relatório:: 26"] || 0), 0);
  }, [dadosValidos]);

  // ======================== TOTAL EXECUÇÃO ==========================
  const totalExecucao = useMemo(() => {
    return dadosValidos.reduce((acc, item) => acc + (item["Filtro do relatório:: 30"] || 0), 0);
  }, [dadosValidos]);

  // ======================== PERCENTUAL TOTAL ========================
  const totalPercentual = useMemo(() => {
    if (totalReais === 0) return 0;
    return (totalExecucao / totalReais) * 100;
  }, [totalExecucao, totalReais]);

  // ======================== GRUPOS ================================
  const grupos = useMemo(() => {
    const mapa = {};

    dadosValidos.forEach(item => {
      const titulo = item["Filtro do relatório:: 6"] || "Sem título";

      if (!mapa[titulo]) {
        mapa[titulo] = { titulo, total: 0, execucao: 0 };
      }

      mapa[titulo].total += item["Filtro do relatório:: 26"] || 0;
      mapa[titulo].execucao += item["Filtro do relatório:: 30"] || 0;
    });

    return Object.values(mapa).map(g => ({
      titulo: g.titulo,
      total: g.total,
      execucao: g.execucao,   
      percentual: g.total === 0 ? 0 : (g.execucao / g.total) * 100
    }));
  }, [dadosValidos]);

  // ======================== RETORNO FINAL ==========================
  return {
    totalReais,
    totalExecucao,  
    totalPercentual,
    grupos,
  };
}

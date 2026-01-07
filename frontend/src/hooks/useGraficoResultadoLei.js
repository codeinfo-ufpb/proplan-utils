import { useMemo } from "react";
import * as echarts from "echarts";

export function useGraficoResultadoLei(data = []) {

  // Apenas linhas válidas com número na coluna Filtro do relatório:: 26
  const dadosValidos = useMemo(() => {
    return Array.isArray(data)
      ? data.filter(item => typeof item["Filtro do relatório:: 26"] === "number")
      : [];
  }, [data]);

  // Agrupar por "Filtro do relatório:: 8"
  const grupos = useMemo(() => {
    const mapa = {};

    dadosValidos.forEach(item => {
      const categoria = item["Filtro do relatório:: 8"] || "Não informado";
      const valor = item["Filtro do relatório:: 26"] || 0;

      if (!mapa[categoria]) {
        mapa[categoria] = 0;
      }

      mapa[categoria] += valor;
    });

    return {
      categorias: Object.keys(mapa),
      valores: Object.values(mapa)
    };

  }, [dadosValidos]);

  // Gerar cores automáticas (base do ECharts)
  const cores = useMemo(() => {
    return echarts?.color?.presets?.default
      ? echarts.color.presets.default
      : ["#5470C6", "#91CC75", "#EE6666", "#FAC858", "#73C0DE"];
  }, []);

  return { ...grupos, cores };
}

import ChartLarge from "./graficos/ChartLarge";
import ChartSmall from "./graficos/ChartSmall";
import { useFiltros } from "../hooks/useFiltros";
import { useGraficoResultadoLei } from "../hooks/useGraficoResultadoLei";

import "../css/DashboardGrid.css";
import ChartPie from "./graficos/ChartPie";
import ChartLargeAnual from "./graficos/ChartLargeYears";
import ChartControleAcoes from "./graficos/ChartControlActions";
import ChartComparativoDotacaoExecucao from "./graficos/ChartComparative";
import ChartControl from "./graficos/ChartControl";
import ChartHeatmap from "./graficos/ChartHeatMap";
import ScatterPlotExecucaoDotacao from "./graficos/ScatterPlot";
import DynamicPivotTable from "./graficos/DinamicPivot";
import BoxplotExecucaoPorItem from "./graficos/Boxplot";


export default function DashboardGrid({ filtrados = [] }) {
  

  const { filtros } = useFiltros();
  const anoSelecionado = filtros.ano;

  const { categorias, valores, cores } = useGraficoResultadoLei(filtrados);
  console.log("ANO SELECIONADO:", filtros.ano);

  return (
    <div>
      <div className="row">
        <div className="col-12">
          <ChartLarge  filtrados={filtrados}
          title="Execução Mensal (Por cada ano)"
          valores={valores}
          cores={cores}
          />
        </div>
      </div>
      <div className="row">
        <div className="col-4">
          <ChartSmall
            title="Execução por Resultado da Lei"
            categorias={categorias}
            valores={valores}
            cores={cores}
          />
        </div>
        <div className="col-4">
          <ChartPie 
            title="Dotação - Ano x Grupo de Despesa"
            filtrados={filtrados}
            anoSelecionado={anoSelecionado}
            
            />
        </div>
        <div className="col-4">
          <ChartHeatmap  
          filtrados={filtrados} 
          />
        </div>
      </div>
       <div className="row">
        <div className="col-12">
          <ChartControleAcoes  filtrados={filtrados} />
        </div>
      </div>
      
      <div className="row">
        <div className="col-6">
          <ChartComparativoDotacaoExecucao  filtrados={filtrados} />
        </div>
        <div className="col-6">
          <ChartControl  filtrados={filtrados} />
        </div>
      </div>
      {/*
      <div className="row">
          <div className="col-12">
            <ChartLargeAnual  filtrados={filtrados} />
          </div>
      </div>
      <div className="row">
        <div className="col-8">
          <BoxplotExecucaoPorItem filtrados={filtrados}/>

        </div>
      </div> */}

                        {/* <div className="col-8">
        <ScatterPlotExecucaoDotacao  filtrados={filtrados} />
      </div> */}
      <div className="col-8">
        <DynamicPivotTable  filtrados={filtrados} />
      </div>
      <div>
      </div>
    </div>
    
  );
}

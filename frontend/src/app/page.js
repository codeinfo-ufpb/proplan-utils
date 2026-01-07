"use client";

import MenuFiltros from "../components/MenuFiltros";
import Card from "../components/Cards";
import DashboardGrid from "../components/DashboardGrid";
import { useFiltros } from "../hooks/useFiltros";
import { useCards } from "../hooks/useCards";
import { useGraficoResultadoLei } from "../hooks/useGraficoResultadoLei";

export default function DashboardPage() {

  // filtros + dados filtrados
  const {
    filtrados,
    filtros,
    opcoes,
    atualizarFiltro,
    resetFiltros,
    loading
  } = useFiltros();

  const { categorias, valores, cores } = useGraficoResultadoLei(filtrados);


  
  const {
    totalReais,
    totalExecucao,
    tituloValorPrincipal,        
    totalPercentual,
    grupos
  } = useCards(filtrados);


  if (loading) return <div>Carregando...</div>;

  return (
    <>
    {/* FILTROS */}
    <MenuFiltros
      filtros={filtros}
      opcoes={opcoes}
      atualizarFiltro={atualizarFiltro}
      resetFiltros={resetFiltros}
    />
    <div className="container padding-3" id="conteudo">


      <div className="row cards-no-wrap-container mt-4">

      <Card
        title="Dotação Orçamentária"
        tipo="dotacao"
        valorPrincipal={totalReais}
        valorPercentual={totalPercentual}   // totalPercentual = execucao / dotacao * 100
        grupos={grupos}
      />

      <Card
        title="Execução Orçamentária"
        tipo="execucao"
        valorPrincipal={totalExecucao}
        valorPercentual={(totalExecucao / totalReais) * 100}   // mesmo cálculo
        grupos={grupos}
      />
      </div>
      <DashboardGrid filtrados={filtrados}/>
    </div>
  </>
      
  );
  
}


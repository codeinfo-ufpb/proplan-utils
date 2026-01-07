"use client";

import { useState, useEffect } from "react";

export function useFiltros() {


  const [registros, setRegistros] = useState([]);
  const [filtrados, setFiltrados] = useState([]);

  const [opcoes, setOpcoes] = useState({
    UnidOrcamentaria: [],
    acao: [],
    resultado: [],
    ano: [],
    mes: []
  });

  const [filtros, setFiltros] = useState({
    UnidOrcamentaria: "",
    acao: "",
    resultado: "",
    ano: "",
    mes: ""
  });

  const [loading, setLoading] = useState(true);

  // ---------------------------------------------------------
  // UTILITÁRIO → sempre converter para string
  // ---------------------------------------------------------
  const toStr = v => (v === null || v === undefined ? "" : String(v).trim());

  // ---------------------------------------------------------
  // extrair opções únicas higienizadas
  // ---------------------------------------------------------
  function extrair(base, campo) {
    return [...new Set(base.map(r => toStr(r[campo])).filter(Boolean))];
  }

  // ---------------------------------------------------------
  // 1. Carregar dados da API uma vez
  // ---------------------------------------------------------
  useEffect(() => {
    async function carregar() {
      try {
        const resp = await fetch("http://localhost:5000/api/data");
        const json = await resp.json();

        const records = json.flatMap(item => item.records);

        // higienizar todos os campos NA HORA DA CARGA

        const normalizados = records.map(r => ({
          ...r,
          "Filtro do relatório:: 2": toStr(r["Filtro do relatório:: 2"]),
          "Filtro do relatório:: 4": toStr(r["Filtro do relatório:: 4"]),
          "Filtro do relatório:: 6": toStr(r["Filtro do relatório:: 6"]),
          "Filtro do relatório:: 21": toStr(r["Filtro do relatório:: 21"]),
          "Filtro do relatório:: 20": toStr(r["Filtro do relatório:: 20"])
        }));

        setRegistros(normalizados);
        setFiltrados(normalizados);

      setOpcoes({
        UnidOrcamentaria: extrair(registros, "Filtro do relatório:: 2"),
        acao: extrair(registros, "Filtro do relatório:: 4"),
        resultado: extrair(registros, "Filtro do relatório:: 6"),
        ano: extrair(registros, "Filtro do relatório:: 21"),
        mes: extrair(registros, "Filtro do relatório:: 20"),
      });

      } catch (e) {
        console.error("Erro ao carregar dados:", e);
      } finally {
        setLoading(false);
      }
    }

    carregar();
  }, []);

  // ---------------------------------------------------------
  // 2. Encadeamento correto dos filtros
  // ---------------------------------------------------------
  useEffect(() => {
    if (registros.length === 0) return;

    let base = [...registros];

    // A ordem importa!
    if (filtros.ano) {
      base = base.filter(r => r["Filtro do relatório:: 21"] === toStr(filtros.ano));
    }

    if (filtros.mes) {
      base = base.filter(r => r["Filtro do relatório:: 20"] === toStr(filtros.mes));
    }

    if (filtros.acao) {
      base = base.filter(r => r["Filtro do relatório:: 4"] === toStr(filtros.acao));
    }

    if (filtros.resultado) {
      base = base.filter(r => r["Filtro do relatório:: 6"] === toStr(filtros.resultado));
    }

    if (filtros.UnidOrcamentaria){
      base = base.filter(r => r["Filtro do relatório:: 2"] === toStr(filtros.UnidOrcamentaria));
    }

    setFiltrados(base);

    // ---------------------------------------------------------
    // Atualização das opções disponíveis (reestritas ao filtrado)
    // sem disparar loop infinito
    // ---------------------------------------------------------
    setOpcoes({
      UnidOrcamentaria: extrair(base, "Filtro do relatório:: 2"),
      acao: extrair(base, "Filtro do relatório:: 4"),
      resultado: extrair(base, "Filtro do relatório:: 6"),
      ano: extrair(base, "Filtro do relatório:: 21"),
      mes: extrair(base, "Filtro do relatório:: 20"),
    });

  }, [filtros, registros]);

  // ---------------------------------------------------------
  // Atualizar 1 filtro
  // ---------------------------------------------------------
  function atualizarFiltro(campo, valor) {
    setFiltros(prev => ({ ...prev, [campo]: valor }));
  }

  // ---------------------------------------------------------
  // Resetar tudo
  // ---------------------------------------------------------
  function resetFiltros() {
    setFiltros({
      UnidOrcamentaria: "",
      acao: "",
      resultado: "",
      ano: "",
      mes: ""
    });

    setFiltrados(registros);

    setOpcoes({
      UnidOrcamentaria: extrair(registros, "Filtro do relatório:: 2"),
      acao: extrair(registros, "Filtro do relatório:: 4"),
      resultado: extrair(registros, "Filtro do relatório:: 6"),
      ano: extrair(registros, "Filtro do relatório:: 21"),
      mes: extrair(registros, "Filtro do relatório:: 20"),
    });
  }

  return {
    opcoes,
    filtros,
    atualizarFiltro,
    resetFiltros,
    loading,
    filtrados
  };
}

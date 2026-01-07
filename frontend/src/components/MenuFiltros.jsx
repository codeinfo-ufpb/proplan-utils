"use client";

import { useEffect, useRef, useState } from "react";
import css from "... @/css/MenuFiltros.module.css";

export default function MenuFiltros({
  opcoes,
  filtros,
  atualizarFiltro,
  resetFiltros,
  loading
}) {
  const refWrapper = useRef(null);
  const refSentinel = useRef(null); 

  const [sticky, setSticky] = useState(false);
  const [open, setOpen] = useState(true);

  function onChange(e) {
    const id = e.target.id.replace("filtro-", "");
    atualizarFiltro(id, e.target.value);
  }

  // Observador para controlar e detectar quando o menu sai da tela
  useEffect(() => {
    const sentinel = refSentinel.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setSticky(!entry.isIntersecting);
      },
      {
        threshold: 1,
        rootMargin: "0px 0px 0px 0px",
      }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, []);

  if (loading) return <div>Carregando filtros...</div>;

  return (
    <>
      {/* Elemento invisível que controla o sticky */}
      <div ref={refSentinel} style={{ height: 1 }}></div>

      <div
        ref={refWrapper}
        className={`${css.wrapper} ${sticky ? css.sticky : ""}`}
      >
        {/* TOGGLE MOBILE */}
        <button className={css.toggleBtn} onClick={() => setOpen((v) => !v)}>
          {open ? "Ocultar Filtros ▲" : "Mostrar Filtros ▼"}
        </button>

        {/* FILTROS */}
        <div className={`${css.filtrosContainer} ${open ? css.show : css.hide}`}>

          <div className={css.filtroItem}>
            <label>Unidade Orçamentária</label>
            <select id="filtro-UnidOrcamentaria" value={filtros.UnidOrcamentaria} onChange={onChange}>
              <option value="">Todas</option>
              {opcoes.UnidOrcamentaria.map((v, i) => (
                <option key={i} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </div>
          
          {/* AÇÃO */}
          <div className={css.filtroItem}>
            <label>Unidade Gestora</label>
            <select id="filtro-acao" value={filtros.acao} onChange={onChange}>
              <option value="">Todas</option>
              {opcoes.acao.map((v, i) => (
                <option key={i} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </div>

          {/* RESULTADO */}
          <div className={css.filtroItem}>
            <label>Unidade Responsável</label>
            <select id="filtro-resultado" value={filtros.resultado} onChange={onChange}>
              <option value="">Todos</option>
              {opcoes.resultado.map((v, i) => (
                <option key={i} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </div>

          {/* ANO */}
          <div className={css.filtroItem}>
            <label>Ano de Lançamento</label>
            <select id="filtro-ano" value={filtros.ano} onChange={onChange}>
              <option value="">Todos</option>
              {opcoes.ano.map((v, i) => (
                <option key={i} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </div>

          {/* MÊS */}
          <div className={css.filtroItem}>
            <label>Mês de Lançamento</label>
            <select id="filtro-mes" value={filtros.mes} onChange={onChange}>
              <option value="">Todos</option>
              {opcoes.mes.map((v, i) => (
                <option key={i} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </div>

          {/* RESET */}
          <div className={css.filtroItem}>
            <label>&nbsp;</label>
            <button className={css.btnReset} onClick={resetFiltros}>
              Limpar Filtros
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

"use client";
import css from "../css/Card.module.css";

export default function Card({
  title,
  tipo = "dotacao",   // "dotacao" ou "execucao"
  valorPrincipal,
  valorPercentual,
  grupos = []
}) {

  const safeNumber = (v) => {
    if (v === null || v === undefined || v === "" || isNaN(Number(v))) return 0;
    return Number(v);
  };

  const reais = safeNumber(valorPrincipal).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });

  const percentual = safeNumber(valorPercentual).toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const tituloValorPrincipal =
    tipo === "dotacao" ? "Total Dotação" : "Total Execução";

  const tituloPercentual =
    tipo === "dotacao" ? "% Execução / Dotação" : "% Execução / Dotação";

  return (
    <div className="col-6 col-sm-12 col-md-6 col-lg-4 mb-3">
      <div className={css.card}>

        <div className={css.cardHeader}>
          <h2>{title}</h2>
        </div>

        <div className={css.cardBody}>

          {/* VALORES SUPERIORES */}
          <div className="text-center row mb-3">
            <div className="col-6">
              <div className={`fade alert ${css.alertDark} show`}>
                <p><strong>{tituloValorPrincipal}</strong></p>
                <h3>{reais}</h3>
                <p>Subtítulo</p>
              </div>
            </div>

            <div className="col-6">
              <div className={`fade alert ${css.alertDark} show`}>
                <p><strong>{tituloPercentual}</strong></p>
                <h3>{percentual}%</h3>
                <p>Subtítulo</p>
              </div>
            </div>
          </div>

          {/* TABELA */}
          <div className="row" id={css.tabela}>

            {/* DESCRIÇÃO */}
            <div className="col-6">
              <div className={`${css.borderBottom} ${css.border3} ${css.tabelaIndiceHeader}`}>
                Descrição
              </div>

              {grupos.length === 0
                ? <div className={css.tabelaIndiceItem}>Nenhum dado</div>
                : grupos.map((g, idx) => (
                    <div key={"t" + idx} className={css.tabelaIndiceItem}>
                      {g.titulo}
                    </div>
                  ))}
            </div>

            {/* VALOR EM R$ */}
            <div className="col-4">
              <div className={`${css.borderBottom} ${css.border3} ${css.tabelaIndiceHeader}`}>
                {tipo === "dotacao" ? "R$ Dotação" : "R$ Execução"}
              </div>

              {grupos.length === 0
                ? <div>0</div>
                : grupos.map((g, idx) => {

                    const valor = tipo === "dotacao"
                      ? safeNumber(g.total)
                      : safeNumber(g.execucao);

                    {valor.toLocaleString("pt-BR")}

                    return (
                          <div key={"v" + idx} className={`${css.tabelaIndiceItem} ${css.valor}`}>
                            {(tipo === "dotacao"
                                ? safeNumber(g.total)
                                : safeNumber(g.execucao)
                            ).toLocaleString("pt-BR")}
                          </div>
                    );
                  })}
            </div>

            {/* PERCENTUAL */}
            <div className="col">
              <div className={`${css.borderBottom} ${css.border3} ${css.tabelaIndiceHeader}`}>
                Perc. (%)
              </div>

              {grupos.length === 0
                ? <div>0%</div>
                : grupos.map((g, idx) => (
                    <div
                      key={"p" + idx}
                      className={`${css.tabelaIndiceItem} ${css.percentual}`}
                    >
                      {safeNumber(g.percentual).toLocaleString("pt-BR", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}%
                    </div>
                ))}
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}

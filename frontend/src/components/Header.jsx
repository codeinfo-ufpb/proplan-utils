"use client"; // permite usar eventos e lógica interativa no Next

import css from '... @/css/Header.module.css';

export default function Header() {

  const handleLogoClick = (side) => {
    alert(`Logo ${side} clicada!`);
  };

  return (

    <header className={`${css.bgHeader}`}>
      <div className={css.relative}>
        <div className={``}>
          <div className="flex absolute items-center space-x4 justify-between inset-0 px-4 md:px-6">
            <div className={`flex items-center cursor-pointer space-x-4`}>
              <div className="hidden sm:block">
                <h1 className="text-lg md:text-2xl text-white font-bold">Relatório de Execução Orçamentária</h1>
                <p className="text-white/60 text-xs md:text-sm">Relatório de Execução Orçamentária - PRA/PROPLAN</p>
                <p className="text-white/90 text-xs md:text-sm">Universidade Federal da Paraíba (UFPB)</p>
              </div>
              <div className="sm:hidden">
                <h1 className="text-lg md:text-2xl text-white font-bold">Relatório de Execução Orçamentária</h1>
                <p className="text-white/60 text-xs md:text-sm">Relatório de Execução Orçamentária - PRA/PROPLAN</p>
                <p className="text-white/90 text-xs md:text-sm">Dotação e Execução</p>
            </div>
            </div>
            <div className="flex items-center space-x-2 md:space-x-6 text-white/90">Sobre</div>
          </div>
        </div>
      </div>
      <nav className='bg-white/10 backdrop-blur-sm border-t border-white/20'>
        <div className='container mx-auto px-4 md:px-6'>
          <div className='flex items-center space-x-1 overflow-x-auto'>
            <span className='hidden md:inline'>Visão Geral</span>
            <span>Painel II</span>
          </div>
        </div>
      </nav>
    </header>
  );
}

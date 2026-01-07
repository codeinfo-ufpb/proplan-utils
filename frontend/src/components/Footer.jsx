"use client"; // permite usar eventos e lógica interativa no Next

import css from '... @/css/Footer.module.css';

export default function Footer() {

  const handleLogoClick = (side) => {
    alert(`Logo ${side} clicada!`);
  };

  return (
    <footer className={css.borderT}>
          {/* <div className="container">
            <div className={css.gridCols1.gap8.grid}>
              <div className={css.spaceY4}>
                Teste
              </div>
            </div>
          </div> */}
    </footer>
  );
}

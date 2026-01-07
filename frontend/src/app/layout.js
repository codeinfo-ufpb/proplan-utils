import '... @/app/globals.css';
import Header from '../components/Header';
// import MenuFiltros from '../components/MenuFiltros';
// import Card from '../components/Cards';
import Footer from '../components/Footer';
// import DashboardGrid from '../components/DashboardGrid';


export const metadata = {
  title: "Histórico Orçamentário - UFPB",
  description: "Sistema de Indicadores e Histórico Orçamentário da UFPB",
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body>
        <Header />

        {children}

        <Footer />
      </body>
    </html>
  );
}

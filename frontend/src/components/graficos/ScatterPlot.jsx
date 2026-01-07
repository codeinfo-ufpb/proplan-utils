// "use client";

// import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// export default function ScatterPlotExecucaoDotacao({ filteredData }) {
//   if (!filteredData || filteredData.length === 0) {
//     return (
//       <div className="w-full h-64 flex items-center justify-center text-gray-400">
//         Nenhum dado disponível
//       </div>
//     );
//   }

//   // Preparação do dataset
//   const scatterData = filteredData.map((item, index) => ({
//     id: index,
//     dotacao: Number(item["13"]) || 0,
//     execucao: Number(item["23"]) || 0,
//   }));

//   return (
//     <div className="bg-white shadow rounded-lg p-4 w-full h-[350px]">
//       <h2 className="text-lg font-semibold mb-2">Execução vs Dotação</h2>

//       <ResponsiveContainer width="100%" height="100%">
//         <ScatterChart>
//           <CartesianGrid strokeDasharray="3 3" />

//           <XAxis
//             type="number"
//             dataKey="dotacao"
//             name="Dotação"
//             tickFormatter={(v) => v.toLocaleString("pt-BR")}
//             stroke="#555"
//           />

//           <YAxis
//             type="number"
//             dataKey="execucao"
//             name="Execução"
//             tickFormatter={(v) => v.toLocaleString("pt-BR")}
//             stroke="#555"
//           />

//           <Tooltip
//             formatter={(value) => value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
//             labelFormatter={() => ""}
//           />

//           <Scatter
//             name="Valores"
//             data={scatterData}
//             fill="var(--chart-color, #8884d8)" // cor automática, respeita tema/dash
//           />
//         </ScatterChart>
//       </ResponsiveContainer>
//     </div>
//   );
// }

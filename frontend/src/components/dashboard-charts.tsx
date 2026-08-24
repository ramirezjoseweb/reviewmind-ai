/**
 * Marca este archivo como un Client Component de Next.js. Es necesaria porque
 * los gráficos de Recharts se renderizan en el navegador y pueden requerir
 * interactividad o APIs del cliente.
 */
"use client"; 

import {
    Bar, 
    BarChart,
    CartesianGrid, 
    ResponsiveContainer, 
    Tooltip, 
    XAxis, 
    YAxis,
} from "recharts"; 

import type { AnalysisSummary, AspectCount } from "@/app/lib/api";

type DashboardChartsProps = {
    summary: AnalysisSummary
}; 

const toolTipStyle = {
    backgroundColor: "#020617", 
    border: "1px solid #1e293b", 
    borderRadius: "12px", 
    color: "#e2e8f0", 
};

const labelStyle = {
    color: "#e2e8f0", 
}; 

export function DashboardCharts ({ summary }: DashboardChartsProps) {
    const sentimentData = [
        {
            name: "Positivas", 
            value: summary.positive_reviews, 
        }, 
        {
            name: "Neutras", 
            value: summary.neutral_reviews, 
        }, 
        {
            name: "Negativas", 
            value: summary.negative_reviews,
        }, 
    ]; 

    return (
        <div className="grid gap-4 xl:grid-cols-3">
            <ChartCard
                title="Distribución de sentimiento"
                description="Número de reseñas por tipo de sentimiento."
            >
                <ResponsiveContainer width="100%" height={240}>
                    <BarChart data={sentimentData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis
                         dataKey="name"
                         stroke="#94a3b8"
                         tickLine={false}
                         axisLine={false}
                        />
                        <YAxis
                        allowDecimals={false}
                        stroke="#94a3b8"
                        tickLine={false}
                        axisLine={false}
                        />
                        <Tooltip contentStyle={toolTipStyle} labelStyle={labelStyle} />
                        <Bar dataKey="value" name="Reseñas" fill="#22d3ee" radius={[8, 8, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </ChartCard>

            <AspectChart
                title="Aspectos Positivos"
                description="Aspectos favorables más repetidos."
                data={summary.top_positive_aspects}
                barFill="#4ade80"
            />

            <AspectChart
                title="Aspectos Negativos"
                description="Problemas más repetidos en las reseñas."
                data={summary.top_negative_aspects}
                barFill="#fb7185"
            />
        </div>
    ); 
}

function AspectChart({
  title,
  description,
  data,
  barFill,
}: {
  title: string;
  description: string;
  data: AspectCount[];
  barFill: string;
}) {
  return (
    <ChartCard title={title} description={description}>
      {data.length > 0 ? (
        <ResponsiveContainer width="100%" height={240}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{
              top: 8,
              right: 16,
              bottom: 8,
              left: 16,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              type="number"
              allowDecimals={false}
              stroke="#94a3b8"
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              type="category"
              dataKey="name"
              width={90}
              stroke="#94a3b8"
              tickLine={false}
              axisLine={false}
            />
            <Tooltip contentStyle={toolTipStyle} labelStyle={labelStyle} />
            <Bar dataKey="count" name="Menciones" fill={barFill} radius={[0, 8, 8, 0]} />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="flex h-[240px] items-center justify-center rounded-xl border border-dashed border-slate-800 bg-slate-950 text-sm text-slate-500">
          Sin datos suficientes todavía.
        </div>
      )}
    </ChartCard>
  );
}

function ChartCard({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <div>
        <h3 className="font-semibold text-slate-100">{title}</h3>
        <p className="mt-1 text-sm text-slate-400">{description}</p>
      </div>

      <div className="mt-4">{children}</div>
    </div>
  );
}
"use client"; 

import { FormEvent, useEffect, useState } from "react";
import { DashboardCharts } from "@/components/dashboard-charts";

import {
  AnalysisSummary,
  Business, 
  Review, 
  ReviewImportResult,
  ExecutiveReport,
  createBusiness, 
  createReview,
  getAnalysisSummary,
  getBusinesses, 
  getReviews, 
  runAnalysis,
  deleteReview, 
  deleteBusiness, 
  importReviewCsv, 
  generateExecutiveReport,
  getLatestExecutiveReport,
} from "@/app/lib/api"; 

export default function Home() {
  // Estado para almacenar la lista de negocios obtenidos o creados
  const [businesses, setBusinesses] = useState<Business[]>([]); 
  // Gestiona el negocio actualmente seleccionado
  const [selectedBusiness, setSelectedBusiness] = useState<Business | null>(
    null
  ); 

  const [businessName, setBusinessName] = useState(""); 
  const [businessCategory, setBusinessCategory] = useState("Hotel"); 
  const [businessLocation, setBusinessLocation] = useState(""); 

  const [reviewText, setReviewText] = useState(""); 
  const [reviewRating, setReviewRating] = useState(5); 
  const [reviewAuthor, setReviewAutor] = useState(""); 
  const [reviews, setReviews] = useState<Review[]>([]); 

  const [summary, setSummary] = useState<AnalysisSummary | null>(null); 
  const [error, setError] = useState(""); 
  const [loading, setLoading] = useState(false); 

  const [showAllReviews, setShowAllReviews] = useState(false); 

  const [csvFile, setCsvFile] = useState<File | null>(null); 
  const [importResult, setImportResult] = useState<ReviewImportResult | null>(
    null
  )

  const [executiveReport, setExecutiveReport] = useState<ExecutiveReport | null> (
    null
  ); 

  const visibleReviews = showAllReviews ? reviews : reviews.slice(0, 3); 
  const hasMoreReviews = reviews.length > 3;

  async function loadBusinesses() {
    try{
      setError("");
      const data = await getBusinesses(); 
      setBusinesses(data); 

      // Si aún no hay un negocio seleccionado y la lista obtenida tiene al menos
      // un elemento, selecciona automáticamente el primer negocio de la lista.
      // Esto evita que selectedBusiness quede null cuando hay negocios disponibles.
      if (!selectedBusiness && data.length > 0) {
        setSelectedBusiness(data[0]); 
      } 
    } catch (error) {
      setError(error instanceof Error ? error.message : "Error inesperado") 
    }
  }

  async function loadSummary(businessId: number) {
    try {
      setError(""); 
      const data = await getAnalysisSummary(businessId);
      setSummary(data);  
    } catch {
      // Si ocurre un error al obtener el resumen de análisis,
      // se resetea el estado summary a null para indicar que no hay datos.
      setSummary(null); 
    }
  }

  async function loadReviews(businessId: number) {
    try {
      setError(""); 
      const data = await getReviews(businessId); 
      setReviews(data); 
    } catch (error) {
      setReviews([]); 
      setError(error instanceof Error ? error.message : "Error al obtener reseñas");
    }
  }

  async function loadLatestReport(businessId: number) {
    try {
      setError(""); 
      const data = await getLatestExecutiveReport(businessId); 
      setExecutiveReport(data); 
    } catch (error) {
      setExecutiveReport(null) 
    }
  }

  // Cargamos los negocios al montar el componente.
  // El array de dependencia vacío [] asegura que la llamada
  // se ejecute solo una vez y no en cada renderizado.
  useEffect(() => {
    loadBusinesses(); 
  }, []); 

  // useEffect se ejecuta cada vez que cambia selectedBusiness.
  // Si hay un negocio seleccionado, llama a loadSummary con su id.
  // Esto permite cargar el resumen de análisis correspondiente
  // al negocio que el usuario haya seleccionado.
  useEffect(() => {
    setShowAllReviews(false); 
    setExecutiveReport(null); 

    if (selectedBusiness) {
      loadSummary(selectedBusiness.id);
      loadReviews(selectedBusiness.id);
      loadLatestReport(selectedBusiness.id); 
    }
    else {
      setReviews([]); 
      setSummary(null); 
    }
  }, [selectedBusiness]); 

  // FormEvent<HTMLFormElement> es un tipo genérico que representa el evento de un formulario HTML.
  // El tipo genérico <HTMLFormElement> especifica que el evento proviene de un elemento <form>.
  // event.preventDefault() detiene el comportamiento predeterminado del formulario,
  // evitando que la página se recargue cuando se envía (submit) el formulario.
  async function handleCreateBusiness(event: FormEvent<HTMLFormElement>) {
    try {
      setLoading(true); 
      setError(""); 

      const business = await createBusiness({
        name: businessName, 
        category: businessCategory,
        location: businessLocation || undefined, 
      }); 

      setBusinessName(""); 
      setBusinessCategory("hotel"); 
      setBusinessLocation(""); 
      setSelectedBusiness(business); 

      await loadBusinesses(); 
    } catch (error) {
      setError(error instanceof Error ? error.message : "Error creando negocio"); 
    } finally {
      setLoading(false); 
    }
  }

  async function handleCreateReview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); 

    if(!selectedBusiness) return; 

    try{
      setLoading(true); 
      setError(""); 

      await createReview(selectedBusiness.id, {
        text: reviewText, 
        rating: reviewRating, 
        author: reviewAuthor || undefined,
        source: "manual", 
        language: "es", 
      }); 

      setExecutiveReport(null);
      setReviewText(""); 
      setReviewRating(5); 
      setReviewAutor(""); 

      await loadReviews(selectedBusiness.id);
    } catch(error) {
      setError(error instanceof Error ? error.message : "Error creando la reseña"); 
    } finally {
      setLoading(false); 
    }
  }

  async function handleRunAnalysis() {
    if(!selectedBusiness) return; 

    try{
      setLoading(true); 
      setError("");

      await runAnalysis(selectedBusiness.id); 
      await loadSummary(selectedBusiness.id); 
    } catch (error) {
      setError(error instanceof Error ? error.message : "Error ejecutando el análisis"); 
    } finally {
      setLoading(false); 
    }
  }

  async function handleDeleteBusiness() {
    if(!selectedBusiness) return 
    
    const confirmed = window.confirm(
      "¿Seguro que quieres borrar el negocio?"
    ); 

    if(!confirmed) return; 

    try {
      setLoading(true); 
      setError(""); 

      await deleteBusiness(selectedBusiness.id); 

      const remainingBusiness = await getBusinesses(); 

      setBusinesses(remainingBusiness); 
      setSelectedBusiness(remainingBusiness[0] ?? null);
      setReviews([]); 
      setSummary(null);  
    } catch (error) {
      setError(
        error instanceof Error ? error.message: "Error borrando negocio"
      ); 
    } finally {
      setLoading(false); 
      
    }
  }

  async function handleDeleteReview(reviewId: number) {
    if(!selectedBusiness) return; 

    const confirmed = window.confirm(
      "¿Seguro que quieres borrar la reseña?"
    ); 

    if(!confirmed) return; 

    try {
      setLoading(true); 
      setError(""); 

      await deleteReview(selectedBusiness.id, reviewId); 
      setExecutiveReport(null);
      await loadReviews(selectedBusiness.id);  
      await loadSummary(selectedBusiness.id); 
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Error borrando la reseña"
      );
    } finally {
      setLoading(false); 
    }
  }

  async function handleImportCsv(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); 

    if(!selectedBusiness || !csvFile) return; 
    
    try{
      setLoading(true); 
      setError(""); 
      setImportResult(null); 

      const result = await importReviewCsv(selectedBusiness.id, csvFile); 

      setImportResult(result); 
      setCsvFile(null); 
      setExecutiveReport(null);
    
      await runAnalysis(selectedBusiness.id); 
      await loadReviews(selectedBusiness.id); 
      await loadSummary(selectedBusiness.id); 
    } catch (error) {
      setError (error instanceof Error ? error.message : "Error importando CSV"); 
    } finally {
      setLoading(false); 
    }
  }

  async function handleGenerateReport() {
    if(!selectedBusiness) return;

    try{
      setLoading(true); 
      setError(""); 

      await runAnalysis(selectedBusiness.id); 

      const report = await generateExecutiveReport(selectedBusiness.id);

      setExecutiveReport(report); 

      await loadSummary(selectedBusiness.id); 
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Error generando informe"
      ); 
    } finally {
      setLoading(false); 
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-6xl space-y-8">
        <header>
          <p className="text-xl font-medium uppercase tracking-[0.8em] text-cyan-400 text-center border border-red py-8 bg-slate-900">
            ReviewMind AI
          </p>
          <h1 className="mt-3 text-xl font-bold tracking-tight opacity-90 text-cyan-400">
            Análisis inteligente de reseñas
          </h1>
          <p className="mt-1 max-w-1xl text-slate-400 opacity-80">
            Crea negocios, añade reseñas y genera un resumen básico de
            sentimiento, aspectos positivos y aspectos negativos.
          </p>
        </header>

        {error && (
          <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-sm text-red-200">
            {error}
          </div>
        )}

        <section className="grid gap-6 lg:grid-cols-[1fr_1.4fr]">
  {/* Fila 1 - Crear negocio */}
  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
    <h2 className="text-xl font-semibold">Crear negocio</h2>

    <form onSubmit={handleCreateBusiness} className="mt-5 space-y-4">
      <div>
        <label className="text-sm text-slate-300">Nombre</label>
        <input
          value={businessName}
          onChange={(event) => setBusinessName(event.target.value)}
          className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 outline-none focus:border-cyan-400"
          placeholder="Hotel Granada Centro"
          required
        />
      </div>

      <div>
        <label className="text-sm text-slate-300">Categoría</label>
        <select
          value={businessCategory}
          onChange={(event) => setBusinessCategory(event.target.value)}
          className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 outline-none focus:border-cyan-400"
        >
          <option value="hotel">Hotel</option>
          <option value="restaurant">Restaurante</option>
          <option value="product">Producto</option>
        </select>
      </div>

      <div>
        <label className="text-sm text-slate-300">Ubicación</label>
        <input
          value={businessLocation}
          onChange={(event) => setBusinessLocation(event.target.value)}
          className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 outline-none focus:border-cyan-400"
          placeholder="Granada"
        />
      </div>

      <button
        disabled={loading}
        className="w-full rounded-lg bg-cyan-400 px-4 py-2 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? "Procesando..." : "Crear negocio"}
      </button>
    </form>
  </div>

  {/* Fila 1 - Negocio seleccionado */}
  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
    <div className="flex items-start justify-between gap-4">
      <h2 className="text-xl font-semibold">
        {selectedBusiness ? selectedBusiness.name : "Selecciona un negocio"}
      </h2>

      {selectedBusiness && (
        <button
          type="button"
          onClick={handleDeleteBusiness}
          disabled={loading}
          className="rounded-lg border border-red-500/50 px-3 py-1.5 text-sm font-semibold text-red-300 transition hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Eliminar negocio
        </button>
      )}
  </div>

    {selectedBusiness ? (
  <div className="mt-5">
    <form onSubmit={handleCreateReview} className="space-y-4">
      <div>
        <label className="text-sm text-slate-300">Reseña</label>
        <textarea
          value={reviewText}
          onChange={(event) => setReviewText(event.target.value)}
          className="mt-1 min-h-32 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 outline-none focus:border-cyan-400"
          placeholder="El hotel estaba muy limpio y el personal fue muy amable, aunque había ruido por la noche."
          required
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="text-sm text-slate-300">Puntuación</label>
          <input
            type="number"
            min={1}
            max={5}
            value={reviewRating}
            onChange={(event) => setReviewRating(Number(event.target.value))}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 outline-none focus:border-cyan-400"
          />
        </div>

        <div>
          <label className="text-sm text-slate-300">Autor</label>
          <input
            value={reviewAuthor}
            onChange={(event) => setReviewAutor(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 outline-none focus:border-cyan-400"
            placeholder="Cliente demo"
          />
        </div>
      </div>

      <div className="flex flex-col gap-3 md:flex-row">
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-white px-4 py-2 font-semibold text-slate-950 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Añadir reseña
        </button>

        <button
          type="button"
          onClick={handleRunAnalysis}
          disabled={loading}
          className="rounded-lg border border-cyan-400 px-4 py-2 font-semibold text-cyan-300 transition hover:bg-cyan-400/10 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Ejecutar análisis
        </button>
      </div>
    </form>

    <div className="mt-6 border-t border-slate-800 pt-6">
      <h3 className="font-semibold">Importar reseñas desde CSV</h3>

      <p className="mt-2 text-sm text-slate-400">
        El CSV debe incluir una columna obligatoria{" "}
        <code className="rounded bg-slate-950 px-1.5 py-0.5 text-cyan-300">
          text
        </code>
        . Opcionales:{" "}
        <code className="rounded bg-slate-950 px-1.5 py-0.5 text-cyan-300">
          rating
        </code>
        ,{" "}
        <code className="rounded bg-slate-950 px-1.5 py-0.5 text-cyan-300">
          author
        </code>
        ,{" "}
        <code className="rounded bg-slate-950 px-1.5 py-0.5 text-cyan-300">
          source
        </code>
        ,{" "}
        <code className="rounded bg-slate-950 px-1.5 py-0.5 text-cyan-300">
          language
        </code>
        .
      </p>

      <form onSubmit={handleImportCsv} className="mt-4 space-y-4">
        <input
          type="file"
          accept=".csv,text/csv"
          onChange={(event) => {
            const file = event.target.files?.[0] ?? null;
            setCsvFile(file);
          }}
          className="block w-full cursor-pointer rounded-lg border border-slate-700 bg-slate-950 text-sm text-slate-300 file:mr-4 file:border-0 file:bg-cyan-400 file:px-4 file:py-2 file:font-semibold file:text-slate-950 hover:file:bg-cyan-300"
        />

        <button
          type="submit"
          disabled={loading || !csvFile}
          className="rounded-lg border border-cyan-400 px-4 py-2 font-semibold text-cyan-300 transition hover:bg-cyan-400/10 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Importar CSV
        </button>
      </form>

      {importResult && (
        <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950 p-4 text-sm">
          <p className="text-slate-300">
            Importadas:{" "}
            <span className="font-semibold text-cyan-300">
              {importResult.imported_reviews}
            </span>
          </p>

          <p className="mt-1 text-slate-300">
            Filas omitidas:{" "}
            <span className="font-semibold text-amber-300">
              {importResult.skipped_rows}
            </span>
          </p>

          {importResult.errors.length > 0 && (
            <ul className="mt-3 space-y-1 text-xs text-red-300">
              {importResult.errors.slice(0, 5).map((error) => (
                <li key={error}>{error}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  </div>
) : (
  <p className="mt-4 text-sm text-slate-400">
    Crea o selecciona un negocio para añadir reseñas.
  </p>
)}
  </div>

  {/* Fila 2 - Negocios */}
  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
    <h2 className="text-xl font-semibold">Negocios</h2>

    <div className="mt-5 space-y-3">
      {businesses.length === 0 && (
        <p className="text-sm text-slate-400">
          Todavía no hay negocios creados.
        </p>
      )}

      {businesses.map((business) => (
        <button
          key={business.id}
          onClick={() => setSelectedBusiness(business)}
          className={`w-full rounded-xl border p-4 text-left transition ${
            selectedBusiness?.id === business.id
              ? "border-cyan-400 bg-cyan-400/10"
              : "border-slate-800 bg-slate-950 hover:border-slate-600"
          }`}
        >
          <p className="font-semibold">{business.name}</p>
          <p className="text-sm text-slate-400">
            {business.category}
            {business.location ? ` · ${business.location}` : ""}
          </p>
        </button>
      ))}
    </div>
  </div>

  {/* Fila 2 - Resumen */}
  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
      <h2 className="text-xl font-semibold">Resumen del análisis</h2>

      {selectedBusiness && summary && (
      <button
        type="button"
        onClick={handleGenerateReport}
        disabled={loading}
        className="rounded-lg border border-cyan-400 px-4 py-2 text-sm font-semibold text-cyan-300 transition hover:bg-cyan-400/10 disabled:cursor-not-allowed disabled:opacity-60"
      >
      {loading ? "Generando..." : "Generar informe"}
      </button>
  )}
</div>

{executiveReport && (
  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
    <div className="flex flex-col gap-1">
      <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-400">
        Informe ejecutivo
      </p>
      <h2 className="text-2xl font-bold">{executiveReport.business_name}</h2>
      <p className="text-sm text-slate-500">
        Último informe guardado ·{" "}
        {new Date(executiveReport.generated_at).toLocaleString("es-ES")}
      </p>
    </div>

    <div className="mt-6 space-y-5">
      <ReportSection
        title="Resumen ejecutivo"
        content={executiveReport.executive_summary}
      />

      <ReportSection
        title="Visión general del sentimiento"
        content={executiveReport.sentiment_overview}
      />

      <ReportList
        title="Fortalezas principales"
        items={executiveReport.strengths}
      />

      <ReportList
        title="Debilidades principales"
        items={executiveReport.weaknesses}
      />

      <ReportList
        title="Recomendaciones"
        items={executiveReport.recommendations}
      />

      <ReportList
        title="Acciones prioritarias"
        items={executiveReport.priority_actions}
      />
    </div>
  </div>
)}

    {summary ? (
      <div className="mt-5 space-y-6">
        <div className="grid gap-4 md:grid-cols-4">
          <SummaryCard label="Reseñas" value={summary.total_reviews} />
          <SummaryCard label="Positivas" value={summary.positive_reviews} />
          <SummaryCard label="Neutras" value={summary.neutral_reviews} />
          <SummaryCard label="Negativas" value={summary.negative_reviews} />
        </div>

        <DashboardCharts summary = {summary} /> 

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-sm text-slate-400">Sentimiento medio</p>
          <p className="mt-1 text-3xl font-bold">
            {summary.average_sentiment_score}
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <AspectList
            title="Aspectos positivos"
            aspects={summary.top_positive_aspects}
          />
          <AspectList
            title="Aspectos negativos"
            aspects={summary.top_negative_aspects}
          />
        </div>
      </div>
    ) : (
      <p className="mt-4 text-sm text-slate-400">
        Todavía no hay análisis para este negocio. Añade reseñas y pulsa
        “Ejecutar análisis”.
      </p>
    )}
  </div>

  {/* Fila 3 - Reseñas guardadas a ancho completo */}
  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 lg:col-span-2">
    <div className="flex items-center justify-between gap-4">
      <h2 className="text-xl font-semibold">Reseñas guardadas</h2>
      <span className="rounded-full bg-slate-950 px-3 py-1 text-sm text-slate-400">
        {reviews.length} reseñas
      </span>
    </div>

    {selectedBusiness ? (
      reviews.length > 0 ? (
        <div className="mt-5 space-y-4">
          {visibleReviews.map((review) => (
            <article
              key={review.id}
              className="rounded-xl border border-slate-800 bg-slate-950 p-4"
            >
              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
                  <span className="rounded-full bg-slate-900 px-2 py-1">
                    Rating: {review.rating ?? "Sin rating"}
                  </span>

                  <span className="rounded-full bg-slate-900 px-2 py-1">
                    Autor: {review.author || "Anónimo"}
                  </span>

                  <span className="rounded-full bg-slate-900 px-2 py-1">
                    Fuente: {review.source || "manual"}
                  </span>

                  <span className="rounded-full bg-slate-900 px-2 py-1">
                    Idioma: {review.language || "N/D"}
                  </span>
                </div>

                <button
    type="button"
    onClick={() => handleDeleteReview(review.id)}
    disabled={loading}
    className="self-start rounded-lg border border-red-500/50 px-3 py-1.5 text-xs font-semibold text-red-300 transition hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-60"
  >
    Eliminar
  </button>
</div>

              <p className="mt-3 text-sm leading-6 text-slate-300">
                {review.text}
              </p>

              <p className="mt-3 text-xs text-slate-500">
                Creada el {new Date(review.created_at).toLocaleString("es-ES")}
              </p>
            </article>
          ))}

          {hasMoreReviews && (
            <button
              type="button"
              onClick={() => setShowAllReviews((currentValue) => !currentValue)}
              className="mt-2 w-full rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-cyan-400 hover:text-cyan-300"
            >
              {showAllReviews
                ? "Ver menos"
                : `Ver más reseñas (${reviews.length - 3} más)`}
            </button>
          )}
        </div>
      ) : (
        <p className="mt-4 text-sm text-slate-400">
          Este negocio todavía no tiene reseñas guardadas.
        </p>
      )
    ) : (
      <p className="mt-4 text-sm text-slate-400">
        Selecciona un negocio para ver sus reseñas.
      </p>
    )}
  </div>
</section>
          
      </div>
    </main>
  );
}

function SummaryCard({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-1 text-3xl font-bold">{value}</p>
    </div>
  );
}

function AspectList({
  title,
  aspects,
}: {
  title: string;
  aspects: { name: string; count: number }[];
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <p className="font-semibold">{title}</p>

      {aspects.length > 0 ? (
        <ul className="mt-3 space-y-2 text-sm text-slate-300">
          {aspects.map((aspect) => (
            <li 
              key={aspect.name}
              className="flex items-center justify-between gap-3 rounded-lg bg-slate-900 px-3 py-4"
              >
                <span>{aspect.name}</span>

                <span className="rounded-full bg-slate-950 px-6 py-1.5 text-xs text-cyan-300">
                  {aspect.count}
                </span>
              </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-slate-500">
          Sin aspectos detectados todavía.
        </p>
      )}
    </div>
  );
}

function ReportSection({
  title, 
  content, 
}: {
  title: string; 
  content: string; 
}) {
  return (
    <section className="rounded-x1 border border-slate-800 bg-slate-950 p-4">
      <h3 className="font-semibold text-slate-100">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-300">{content}</p>
    </section>
  ); 
}

function ReportList({
  title,
  items, 
}: {
  title: string; 
  items: string[]; 
}) {
  return (
    <section className="rounded-x1 border border-slate-800 bg-slate-950 p-4">
      <h3 className="font-semibold text-slate-100">{title}</h3>"

      <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-300">
        {items.map((item) => (
          <li key={item} className="rounded-lg bg-slate-900 px-3 py-2">
            {item}
          </li>   
        ))}
      </ul>
    </section>
  )
}
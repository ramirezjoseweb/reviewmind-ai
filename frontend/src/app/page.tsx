"use client"; 

import { FormEvent, useEffect, useState } from "react";

import {
  AnalysisSummary,
  Business, 
  Review, 
  createBusiness, 
  createReview,
  getAnalysisSummary,
  getBusinesses, 
  getReviews, 
  runAnalysis,
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
  const [review, setReviews] = useState<Review[]>([]); 

  const [summary, setSummary] = useState<AnalysisSummary | null>(null); 
  const [error, setError] = useState(""); 
  const [loading, setLoading] = useState(false); 

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
    if (selectedBusiness) {
      loadSummary(selectedBusiness.id);
      loadReviews(selectedBusiness.id);
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

      setReviewText(""); 
      setReviewRating(5); 
      setReviewAutor(""); 
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
          <div className="space-y-6">
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
                    onChange={(event) =>
                      setBusinessCategory(event.target.value)
                    }
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
                    onChange={(event) =>
                      setBusinessLocation(event.target.value)
                    }
                    className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 outline-none focus:border-cyan-400"
                    placeholder="Granada"
                  />
                </div>

                <button
                  disabled={loading}
                  className="w-full rounded-lg bg-cyan-400 hover:opacity-60 px-4 py-2 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? "Procesando..." : "Crear negocio"}
                </button>
              </form>
            </div>

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
          </div>

          <div className="space-y-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">
                {selectedBusiness
                  ? selectedBusiness.name
                  : "Selecciona un negocio"}
              </h2>

              {selectedBusiness ? (
                <form onSubmit={handleCreateReview} className="mt-5 space-y-4">
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
                      <label className="text-sm text-slate-300">
                        Puntuación
                      </label>
                      <input
                        type="number"
                        min={1}
                        max={5}
                        value={reviewRating}
                        onChange={(event) =>
                          setReviewRating(Number(event.target.value))
                        }
                        className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 outline-none focus:border-cyan-400"
                      />
                    </div>

                    <div>
                      <label className="text-sm text-slate-300">Autor</label>
                      <input
                        value={reviewAuthor}
                        onChange={(event) =>
                          setReviewAutor(event.target.value)
                        }
                        className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 outline-none focus:border-cyan-400"
                        placeholder="Nombre"
                      />
                    </div>
                  </div>

                  <div className="flex flex-col gap-3 md:flex-row">
                    <button
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
              ) : (
                <p className="mt-4 text-sm text-slate-400">
                  Crea o selecciona un negocio para añadir reseñas.
                </p>
              )}
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">Resumen del análisis</h2>

              {summary ? (
                <div className="mt-5 space-y-6">
                  <div className="grid gap-4 md:grid-cols-4">
                    <SummaryCard
                      label="Reseñas"
                      value={summary.total_reviews}
                    />
                    <SummaryCard
                      label="Positivas"
                      value={summary.positive_reviews}
                    />
                    <SummaryCard
                      label="Neutras"
                      value={summary.neutral_reviews}
                    />
                    <SummaryCard
                      label="Negativas"
                      value={summary.negative_reviews}
                    />
                  </div>

                  <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                    <p className="text-sm text-slate-400">
                      Sentimiento medio
                    </p>
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
                  Todavía no hay análisis para este negocio. Añade reseñas y
                  pulsa “Ejecutar análisis”.
                </p>
              )}
            </div>
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
  aspects: string[];
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <p className="font-semibold">{title}</p>

      {aspects.length > 0 ? (
        <ul className="mt-3 space-y-2 text-sm text-slate-300">
          {aspects.map((aspect) => (
            <li key={aspect} className="rounded-lg bg-slate-900 px-3 py-2">
              {aspect}
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
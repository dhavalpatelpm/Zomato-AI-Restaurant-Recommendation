import React, { useState, useEffect } from 'react'
import FilterForm from './components/FilterForm'
import RecommendationList from './components/RecommendationList'
import Loader from './components/Loader'
import { getLocalities, getCuisines } from './services/api'

export default function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [localityCount, setLocalityCount] = useState(null)
  const [cuisineCount, setCuisineCount] = useState(null)
  const [countsLoading, setCountsLoading] = useState(true)
  const [cuisineToAdd, setCuisineToAdd] = useState(null)

  useEffect(() => {
    const loadCounts = async () => {
      setCountsLoading(true)
      const [localitiesResult, cuisinesResult] = await Promise.allSettled([
        getLocalities(),
        getCuisines(),
      ])
      if (localitiesResult.status === 'fulfilled') {
        const { localities = [] } = localitiesResult.value
        setLocalityCount(Array.isArray(localities) ? localities.length : 0)
      }
      if (cuisinesResult.status === 'fulfilled' && Array.isArray(cuisinesResult.value)) {
        setCuisineCount(cuisinesResult.value.length)
      }
      setCountsLoading(false)
    }
    loadCounts()
  }, [])

  const handleResults = (data) => {
    setResults(data)
  }

  const handleError = () => {
    setResults(null)
  }

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const isProdDeploy = typeof window !== 'undefined' && !window.location.hostname.includes('localhost')
  const apiFailing = !countsLoading && (localityCount === 0 || localityCount == null) && (cuisineCount === 0 || cuisineCount == null)

  return (
    <>
      <div className="vertical-zomato-text" aria-hidden="true">
        {'ZOMATO'.split('').map((char, i) => (
          <span key={i} className="vertical-zomato-char">{char}</span>
        ))}
      </div>
      {isProdDeploy && apiFailing && (
        <div className="api-config-banner" role="alert">
          <strong>API not configured.</strong> Set <code>VITE_API_URL</code> in Vercel → Settings → Environment Variables to your backend URL (e.g. <code>https://your-api.onrender.com</code>), then redeploy. <a href="https://github.com/dhavalpatelpm/Zomato-AI-Restaurant-Recommendation/blob/main/docs/VERCEL_DEPLOY.md" target="_blank" rel="noopener noreferrer">View guide</a>
        </div>
      )}
      <div className="app">
      <header className="hero">
        <h1 className="hero-title">
          <span className="accent-red">Zomato</span> AI Recommender
        </h1>
        <p className="hero-subtitle">Helping you find the best places to eat in <span className="accent-red">Bangalore</span> city</p>
        <div className="hero-stats">
          <span className="stat">
            📍 <span className="stat-number">{countsLoading ? '...' : (localityCount ?? '—')}</span> Localities
          </span>
          <span className="stat-divider">|</span>
          <span className="stat">
            🍴 <span className="stat-number">{countsLoading ? '...' : (cuisineCount ?? '—')}</span> Cuisines
          </span>
        </div>
        <div className="top-cuisines">
          <span className="top-cuisines-label">Top cuisines in <span className="top-cuisines-label-city">Bangalore</span></span>
          <div className="top-cuisines-boxes">
            {['North Indian', 'Chinese', 'South Indian', 'Fast Food', 'Biryani'].map((cuisine) => (
              <button
                key={cuisine}
                type="button"
                className="top-cuisine-box"
                onClick={() => setCuisineToAdd(cuisine)}
                aria-label={`Select ${cuisine} cuisine`}
              >
                {cuisine}
              </button>
            ))}
          </div>
        </div>
      </header>
      <FilterForm
        onResults={handleResults}
        onError={handleError}
        onLoading={setLoading}
        cuisineToAdd={cuisineToAdd}
        onCuisineAdded={() => setCuisineToAdd(null)}
      />
      {loading && <Loader />}
      {results && <RecommendationList data={results} />}
      <button
        className="scroll-to-top"
        onClick={scrollToTop}
        aria-label="Scroll to top"
      >
        ▲
      </button>
      <footer className="app-footer">
        <div className="footer-badge">
          <div className="footer-text-block">
            <span className="footer-line1">POWERED BY GROQ AI</span>
            <span className="footer-line2">Made by <strong className="footer-name">Dhaval Patel</strong> with</span>
          </div>
          <span className="footer-heart" aria-hidden="true">❤️</span>
        </div>
      </footer>
    </div>
    </>
  )
}

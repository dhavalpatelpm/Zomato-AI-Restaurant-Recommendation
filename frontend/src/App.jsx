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

  useEffect(() => {
    // Load counts immediately on mount - no delay
    const loadCounts = async () => {
      try {
        setCountsLoading(true)
        // Fetch both in parallel for fastest loading
        const [localitiesData, cuisinesData] = await Promise.all([
          getLocalities(),
          getCuisines(),
        ])
        // Update counts as soon as data arrives
        setLocalityCount(Array.isArray(localitiesData) ? localitiesData.length : 0)
        setCuisineCount(Array.isArray(cuisinesData) ? cuisinesData.length : 0)
      } catch (err) {
        console.error('Failed to load counts:', err)
        // Don't set to 0 on error, keep showing ... until retry succeeds
      } finally {
        setCountsLoading(false)
      }
    }
    // Start loading immediately, no delay
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

  return (
    <>
      <div className="vertical-zomato-text" aria-hidden="true">
        {'ZOMATO'.split('').map((char, i) => (
          <span key={i} className="vertical-zomato-char">{char}</span>
        ))}
      </div>
      <div className="app">
      <header className="hero">
        <h1 className="hero-title">
          <span className="accent-red">Zomato</span> AI Recommender
        </h1>
        <p className="hero-subtitle">Helping you find the best places to eat in <span className="accent-red">Bangalore</span> city</p>
        <div className="hero-stats">
          <span className="stat">
            📍 <span className="stat-number">{countsLoading ? '...' : localityCount}</span> Localities
          </span>
          <span className="stat-divider">|</span>
          <span className="stat">
            🍴 <span className="stat-number">{countsLoading ? '...' : cuisineCount}</span> Cuisines
          </span>
        </div>
      </header>
      <FilterForm
        onResults={handleResults}
        onError={handleError}
        onLoading={setLoading}
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

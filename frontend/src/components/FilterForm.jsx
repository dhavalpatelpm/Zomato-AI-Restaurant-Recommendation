import React, { useState, useEffect, useRef, useCallback } from 'react'
import { getRecommendations, getLocalities, getCuisines } from '../services/api'

function toTitleCase(str) {
  return str
    .trim()
    .split(/\s+/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ')
}

const PRICE_RANGES = [
  { value: 500, label: 'Budget (₹ < 500)' },
  { value: 1500, label: 'Mid-range (₹500 - ₹1500)' },
  { value: 5000, label: 'Premium (₹ > 1500)' },
]

const MAX_RETRIES = 6
const RETRY_DELAY_MS = 2000

export default function FilterForm({ onResults, onError, onLoading, cuisineToAdd, onCuisineAdded }) {
  const [localities, setLocalities] = useState([])
  const [cuisinesList, setCuisinesList] = useState([])
  const [locality, setLocality] = useState('')
  const [priceRange, setPriceRange] = useState('')
  const [cuisines, setCuisines] = useState([])
  const [cuisineSearch, setCuisineSearch] = useState('')
  const [cuisineDropdownOpen, setCuisineDropdownOpen] = useState(false)
  const cuisineInputRef = useRef(null)
  const cuisineDropdownRef = useRef(null)
  const [minRating, setMinRating] = useState(4.5)
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(true)
  const [validationError, setValidationError] = useState('')

  const loadData = useCallback(async (isRetry = false) => {
    let timeoutId = null
    try {
      if (!isRetry) setLoadingData(true)
      timeoutId = setTimeout(() => setLoadingData(false), 15000)

      const [localitiesData, cuisinesData] = await Promise.all([
        getLocalities().catch(err => {
          if (!isRetry) console.error('Error loading localities:', err)
          return { localities: [] }
        }),
        getCuisines().catch(err => {
          if (!isRetry) console.error('Error loading cuisines:', err)
          return []
        }),
      ])

      clearTimeout(timeoutId)
      const validLocalities = Array.isArray(localitiesData?.localities) ? localitiesData.localities : (Array.isArray(localitiesData) ? localitiesData : [])
      const validCuisines = Array.isArray(cuisinesData) ? cuisinesData : []

      setLocalities(validLocalities)
      setCuisinesList(validCuisines)
      setLoadingData(false)

      return validLocalities.length > 0 && validCuisines.length > 0
    } catch (err) {
      console.error('Failed to load data:', err)
      clearTimeout(timeoutId)
      setLocalities([])
      setCuisinesList([])
      setLoadingData(false)
      return false
    }
  }, [])

  useEffect(() => {
    let retryCount = 0
    let retryTimeoutId = null

    const tryLoad = async () => {
      const success = await loadData(retryCount > 0)
      if (success || retryCount >= MAX_RETRIES) return
      retryCount += 1
      retryTimeoutId = setTimeout(tryLoad, RETRY_DELAY_MS)
    }

    tryLoad()
    return () => {
      if (retryTimeoutId) clearTimeout(retryTimeoutId)
    }
  }, [loadData])

  const handleCuisineToggle = (cuisine) => {
    setCuisines((prev) =>
      prev.includes(cuisine)
        ? prev.filter((c) => c !== cuisine)
        : [...prev, cuisine]
    )
    setValidationError('')
  }

  const removeCuisine = (cuisine) => {
    setCuisines((prev) => prev.filter((c) => c !== cuisine))
    setValidationError('')
  }

  const addCuisine = useCallback((cuisine) => {
    const c = typeof cuisine === 'string' ? cuisine.trim() : ''
    if (!c) return
    const title = toTitleCase(c)
    setCuisines((prev) => (prev.includes(title) ? prev : [...prev, title]))
    setCuisineSearch('')
    setValidationError('')
  }, [])

  useEffect(() => {
    if (cuisineToAdd && typeof cuisineToAdd === 'string') {
      addCuisine(cuisineToAdd)
      onCuisineAdded?.()
    }
  }, [cuisineToAdd, addCuisine, onCuisineAdded])

  const filteredCuisines = cuisinesList.filter((c) =>
    c.toLowerCase().includes(cuisineSearch.trim().toLowerCase())
  )

  const handleCuisineKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      const q = cuisineSearch.trim()
      if (q) {
        const match = cuisinesList.find((c) => c.toLowerCase() === q.toLowerCase())
        addCuisine(match || q)
      } else if (filteredCuisines.length > 0) {
        addCuisine(filteredCuisines[0])
      }
      setCuisineDropdownOpen(false)
    }
  }

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (cuisineDropdownRef.current && !cuisineDropdownRef.current.contains(e.target)) {
        setCuisineDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const incrementRating = () => {
    setMinRating((r) => Math.min(5, Math.round((r + 0.5) * 10) / 10))
    setValidationError('')
  }

  const decrementRating = () => {
    setMinRating((r) => Math.max(0, Math.round((r - 0.5) * 10) / 10))
    setValidationError('')
  }

  const handleRatingChange = (e) => {
    const value = Number(e.target.value) || 0
    const clamped = Math.max(0, Math.min(5, value))
    setMinRating(clamped)
    setValidationError('')
  }

  const validateForm = () => {
    if (!locality || !locality.trim()) {
      setValidationError('Locality is required! Please select a locality to continue.')
      return false
    }
    if (!priceRange || priceRange === '') {
      setValidationError('Price range is required!')
      return false
    }
    if (!cuisines || cuisines.length === 0) {
      setValidationError('Please select at least one cuisine.')
      return false
    }
    if (minRating === null || minRating === undefined || isNaN(minRating) || minRating < 0) {
      setValidationError('Minimum rating is required.')
      return false
    }
    return true
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setValidationError('')

    if (!validateForm()) {
      return
    }

    const loc = locality.trim().toLowerCase()
    const price = Number(priceRange)
    const rating = Number(minRating)

    if (isNaN(price) || price <= 0) {
      setValidationError('Invalid price range selected.')
      return
    }

    if (isNaN(rating) || rating < 0 || rating > 5) {
      setValidationError('Rating must be between 0 and 5.')
      return
    }

    setLoading(true)
    onLoading?.(true)
    try {
      const data = await getRecommendations({
        locality: loc,
        price_range: price,
        min_rating: rating,
        cuisines: cuisines || [],
      })
      
      // Handle empty results gracefully
      if (data && data.recommendations && data.recommendations.length === 0) {
        onResults?.(data) // Still show empty state
        setValidationError('')
      } else {
        onResults?.(data)
        setValidationError('')
      }
    } catch (err) {
      const message = err.response?.data?.detail
        ? (typeof err.response.data.detail === 'string'
            ? err.response.data.detail
            : JSON.stringify(err.response.data.detail))
        : err.message || 'Failed to fetch recommendations.'
      setValidationError(message)
      onError?.(err)
    } finally {
      setLoading(false)
      onLoading?.(false)
    }
  }

  return (
    <section className="filter-section">
      <form onSubmit={handleSubmit} className="filter-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="locality">
              📍 Select Locality *
            </label>
            <select
              id="locality"
              value={locality}
              onChange={(e) => {
                setLocality(e.target.value)
                setValidationError('')
              }}
              required
              disabled={loading || loadingData}
              className={!locality && validationError.includes('Locality') ? 'error' : ''}
              style={{ minHeight: '44px' }}
              aria-label="Select Locality"
            >
              <option value="">Select Locality...</option>
              {loadingData ? (
                <option value="" disabled>Loading localities...</option>
              ) : localities.length > 0 ? (
                localities.map((loc) => {
                  const formatted = loc
                    .split(' ')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                    .join(' ')
                  return (
                    <option key={loc} value={loc}>
                      {formatted}
                    </option>
                  )
                })
              ) : (
                <option value="" disabled>No localities available — check backend</option>
              )}
            </select>
            {!loadingData && localities.length === 0 && (
              <div className="retry-data-block">
                <p className="retry-data-msg">
                  Can&apos;t connect to API. If this is the deployed app, set <code>VITE_API_URL</code> in Vercel to your backend URL.
                </p>
                <button
                  type="button"
                  className="retry-data-btn"
                  onClick={loadData}
                >
                  Retry loading localities
                </button>
              </div>
            )}
          </div>
          <div className="form-group">
            <label htmlFor="price_range">
              💰 Price Range *
            </label>
            <select
              id="price_range"
              value={priceRange}
              onChange={(e) => {
                setPriceRange(e.target.value)
                setValidationError('')
              }}
              required
              disabled={loading || loadingData}
              className={!priceRange && validationError.includes('Price') ? 'error' : ''}
            >
              <option value="">Select price range...</option>
              {PRICE_RANGES.map(({ value, label }) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="cuisine-input">
              🍴 Cuisines (Multi-select) *
            </label>
            <div
              className={`cuisine-selector-wrap ${cuisines.length === 0 && validationError.includes('cuisine') ? 'error' : ''}`}
              ref={cuisineDropdownRef}
            >
              <div
                className="cuisine-input-area"
                onClick={() => !(loading || loadingData) && cuisineInputRef.current?.focus()}
              >
                <div className="cuisine-chips-input">
                  {cuisines.map((c) => (
                    <span key={c} className="cuisine-chip">
                      {c}
                      <button
                        type="button"
                        className="chip-remove"
                        onClick={(e) => {
                          e.stopPropagation()
                          removeCuisine(c)
                        }}
                        aria-label={`Remove ${c}`}
                        disabled={loading || loadingData}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                  <input
                    ref={cuisineInputRef}
                    id="cuisine-input"
                    type="text"
                    placeholder={cuisines.length === 0 ? 'Type or select cuisines...' : ''}
                    value={cuisineSearch}
                    onChange={(e) => {
                      setCuisineSearch(e.target.value)
                      setCuisineDropdownOpen(true)
                    }}
                    onFocus={() => setCuisineDropdownOpen(true)}
                    onKeyDown={handleCuisineKeyDown}
                    disabled={loading || loadingData}
                    className="cuisine-text-input"
                    autoComplete="off"
                  />
                </div>
                <div className="cuisine-input-actions">
                  {cuisines.length > 0 && (
                    <button
                      type="button"
                      className="cuisine-clear-btn"
                      onClick={(e) => {
                        e.stopPropagation()
                        setCuisines([])
                      }}
                      aria-label="Clear all"
                      disabled={loading || loadingData}
                    >
                      ×
                    </button>
                  )}
                  <button
                    type="button"
                    className={`cuisine-chevron ${cuisineDropdownOpen ? 'open' : ''}`}
                    onClick={(e) => {
                      e.stopPropagation()
                      setCuisineDropdownOpen((o) => !o)
                      cuisineInputRef.current?.focus()
                    }}
                    aria-label="Toggle dropdown"
                    disabled={loading || loadingData}
                  >
                    ▾
                  </button>
                </div>
              </div>
              {cuisineDropdownOpen && (
                <ul className="cuisine-dropdown">
                  {loadingData ? (
                    <li className="cuisine-dropdown-item disabled">Loading cuisines...</li>
                  ) : filteredCuisines.length === 0 ? (
                    <li className="cuisine-dropdown-item disabled">
                      {cuisineSearch.trim()
                        ? `No match. Press Enter to add "${toTitleCase(cuisineSearch.trim())}"`
                        : 'No cuisines available'}
                    </li>
                  ) : (
                    filteredCuisines
                      .filter((c) => !cuisines.includes(c))
                      .map((c) => (
                        <li
                          key={c}
                          className="cuisine-dropdown-item"
                          onClick={() => addCuisine(c)}
                        >
                          {c}
                        </li>
                      ))
                  )}
                  {cuisineSearch.trim() &&
                    !cuisinesList.some(
                      (c) => c.toLowerCase() === cuisineSearch.trim().toLowerCase()
                    ) &&
                    !cuisines.includes(toTitleCase(cuisineSearch.trim())) && (
                      <li
                        className="cuisine-dropdown-item add-custom"
                        onClick={() => addCuisine(cuisineSearch.trim())}
                      >
                        + Add "{toTitleCase(cuisineSearch.trim())}"
                      </li>
                    )}
                </ul>
              )}
            </div>
            {!loadingData && cuisinesList.length > 0 && (
              <small className="cuisine-hint">
                Type to search or add custom cuisines. Select from dropdown or press Enter.
              </small>
            )}
          </div>
          <div className="form-group">
            <label htmlFor="min_rating">
              ⭐ Ratings *
            </label>
            <div className="rating-input-wrap">
              <button
                type="button"
                className="rating-btn"
                onClick={decrementRating}
                disabled={loading || loadingData || minRating <= 0}
                aria-label="Decrease rating"
              >
                −
              </button>
              <input
                id="min_rating"
                type="number"
                min="0"
                max="5"
                step="0.5"
                value={minRating}
                onChange={handleRatingChange}
                disabled={loading || loadingData}
                className={`rating-input ${(minRating === null || minRating === undefined || isNaN(minRating)) && validationError.includes('rating') ? 'error' : ''}`}
              />
              <button
                type="button"
                className="rating-btn"
                onClick={incrementRating}
                disabled={loading || loadingData || minRating >= 5}
                aria-label="Increase rating"
              >
                +
              </button>
            </div>
          </div>
        </div>
        <div className="submit-row">
          <button
            type="submit"
            className="submit-btn"
            disabled={loading || loadingData}
          >
            {loading ? (
              <span className="btn-loading">
                <span className="btn-spinner" />
                Loading...
              </span>
            ) : (
              <>Get Recommendations ✨</>
            )}
          </button>
        </div>
        {validationError && (
          <div className="validation-error">
            {validationError}
          </div>
        )}
      </form>
    </section>
  )
}

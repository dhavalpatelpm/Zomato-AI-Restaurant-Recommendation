import React, { useState, useMemo } from 'react'
import RecommendationCard from './RecommendationCard'

const SORT_OPTIONS = [
  { value: 'price-high-low', label: 'Price (High-Low)' },
  { value: 'price-low-high', label: 'Price (Low-High)' },
  { value: 'ratings-high-low', label: 'Ratings (High-Low)' },
  { value: 'ratings-low-high', label: 'Ratings (Low-High)' },
]

export default function RecommendationList({ data }) {
  const [sortBy, setSortBy] = useState('ratings-high-low')

  if (!data) return null

  const recommendations = data.recommendations || data.restaurants || []
  const totalResults = data.total_results ?? recommendations.length
  const relaxedMessage = data.relaxed_message

  const sortedRecommendations = useMemo(() => {
    const sorted = [...recommendations]
    const getRating = (r) => (r.rating != null ? Number(r.rating) : 0)
    const getPrice = (r) => (r.price_range != null ? Number(r.price_range) : 0)

    switch (sortBy) {
      case 'price-high-low':
        return sorted.sort((a, b) => getPrice(b) - getPrice(a))
      case 'price-low-high':
        return sorted.sort((a, b) => getPrice(a) - getPrice(b))
      case 'ratings-high-low':
        return sorted.sort((a, b) => getRating(b) - getRating(a))
      case 'ratings-low-high':
        return sorted.sort((a, b) => getRating(a) - getRating(b))
      default:
        return sorted
    }
  }, [recommendations, sortBy])

  if (recommendations.length === 0) {
    return (
      <div className="results-section">
        <div className="no-results">
          <p className="no-results-title">No recommendations found</p>
          <p className="no-results-message">
            Try adjusting your filters (lower rating, different cuisines, or higher price range) to see more results.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="results-section">
      {relaxedMessage && (
        <div className="relaxed-message">
          ℹ️ {relaxedMessage}
        </div>
      )}
      <div className="results-header">
        <span className="results-count">{totalResults} result{totalResults !== 1 ? 's' : ''} found</span>
        <div className="results-sort-filter">
          <span className="results-sort-label">Sort by</span>
          <div className="results-sort-buttons" role="group" aria-label="Sort results">
            {SORT_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                className={`sort-option-btn ${sortBy === opt.value ? 'active' : ''}`}
                onClick={() => setSortBy(opt.value)}
                aria-pressed={sortBy === opt.value}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className="recommendation-list">
        {sortedRecommendations.map((rec, index) => (
          <RecommendationCard key={`${rec.restaurant_name}-${index}`} recommendation={rec} />
        ))}
      </div>
    </div>
  )
}

import React from 'react'
import RecommendationCard from './RecommendationCard'

export default function RecommendationList({ data }) {
  if (!data) return null

  const recommendations = data.recommendations || data.restaurants || []
  const totalResults = data.total_results ?? recommendations.length
  const generatedAt = data.generated_at
  const relaxedMessage = data.relaxed_message

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
        {generatedAt && (
          <span className="results-generated">Generated {new Date(generatedAt).toLocaleString()}</span>
        )}
      </div>
      <div className="recommendation-list">
        {recommendations.map((rec, index) => (
          <RecommendationCard key={`${rec.restaurant_name}-${index}`} recommendation={rec} />
        ))}
      </div>
    </div>
  )
}

import React from 'react'

function formatAddress(str) {
  if (!str || typeof str !== 'string') return ''
  return str
    .split(',')
    .map((part) => part.trim())
    .map((part) =>
      part
        .split(/\s+/)
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
        .join(' ')
    )
    .join(', ')
    .trim()
}

export default function RecommendationCard({ recommendation }) {
  const name = recommendation.restaurant_name || 'Unknown'
  const rating = recommendation.rating != null ? Number(recommendation.rating) : null
  const priceRange = recommendation.price_range != null ? Number(recommendation.price_range) : null
  const reason = recommendation.reason || recommendation.explanation || ''
  const cuisines = recommendation.cuisines || ''
  const address = recommendation.address || recommendation.locality || ''
  const displayAddress = address ? formatAddress(address) : ''

  return (
    <article className="recommendation-card">
      <div className="card-header">
        <h3 className="card-title">{name}</h3>
        {typeof rating === 'number' && (
          <span className="card-rating-badge">
            {rating.toFixed(1)} ★
          </span>
        )}
      </div>
      {cuisines && (
        <p className="card-line">
          <span className="card-icon">🍴</span>
          {' '}{cuisines}
        </p>
      )}
      {typeof priceRange === 'number' && (
        <p className="card-line">
          <span className="card-icon">💰</span>
          {' '}Avg. ₹{priceRange} for two
        </p>
      )}
      {displayAddress && (
        <p className="card-line">
          <span className="card-icon">📍</span>
          {' '}{displayAddress}
        </p>
      )}
      {reason && (
        <div className="card-why">
          <p className="card-why-text">
            <strong>Why you'll like it:</strong> {reason}
          </p>
        </div>
      )}
    </article>
  )
}

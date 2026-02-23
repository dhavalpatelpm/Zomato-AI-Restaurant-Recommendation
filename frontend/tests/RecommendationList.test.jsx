import { render, screen } from '@testing-library/react'
import RecommendationList from '../src/components/RecommendationList'

describe('RecommendationList', () => {
  it('renders recommendation cards', () => {
    const data = {
      restaurants: [
        {
          restaurant_name: 'Cafe A',
          locality: 'koramangala',
          cuisines: 'North Indian',
          price_range: 400,
          rating: 4.5,
        },
      ],
      total_results: 1,
    }
    render(<RecommendationList data={data} />)
    expect(screen.getByText('Cafe A')).toBeInTheDocument()
    expect(screen.getByText(/1 result/)).toBeInTheDocument()
  })

  it('displays total results', () => {
    const data = {
      restaurants: [
        { restaurant_name: 'X', locality: '', cuisines: '', price_range: 100, rating: 4 },
      ],
      total_results: 1,
    }
    render(<RecommendationList data={data} />)
    expect(screen.getByText(/1 result/)).toBeInTheDocument()
  })
})

import { render, screen } from '@testing-library/react'
import App from '../src/App'

describe('App', () => {
  it('renders main title', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: /ai restaurant recommender/i })).toBeInTheDocument()
  })

  it('displays filter form and recommendation section', () => {
    render(<App />)
    expect(screen.getByRole('button', { name: /get recommendations/i })).toBeInTheDocument()
  })
})

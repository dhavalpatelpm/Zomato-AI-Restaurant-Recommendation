import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import FilterForm from '../src/components/FilterForm'

vi.mock('../src/services/api', () => ({
  getRecommendations: vi.fn(),
}))

import { getRecommendations } from '../src/services/api'

describe('FilterForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders all input fields', () => {
    render(<FilterForm />)
    expect(screen.getByLabelText(/select locality/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/price range/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/cuisines/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/min rating/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /get recommendations/i })).toBeInTheDocument()
  })

  it('button disabled during loading', async () => {
    getRecommendations.mockImplementation(() => new Promise(() => {}))
    render(<FilterForm />)
    fireEvent.change(screen.getByLabelText(/select locality/i), { target: { value: 'koramangala' } })
    fireEvent.change(screen.getByLabelText(/price range/i), { target: { value: '500' } })
    const btn = screen.getByRole('button', { name: /get recommendations/i })
    expect(btn).not.toBeDisabled()
    fireEvent.click(btn)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /loading/i })).toBeDisabled()
    })
  })

  it('prevents submission when required fields empty', async () => {
    const onResults = vi.fn()
    render(<FilterForm onResults={onResults} />)
    const btn = screen.getByRole('button', { name: /get recommendations/i })
    fireEvent.click(btn)
    await waitFor(() => {
      expect(getRecommendations).not.toHaveBeenCalled()
    })
  })
})

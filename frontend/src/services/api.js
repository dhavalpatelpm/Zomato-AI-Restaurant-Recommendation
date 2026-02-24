import axios from 'axios'

// In dev, use same origin so Vite proxy forwards /api to backend
const baseURL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? '' : 'http://localhost:8000')
const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

export async function getRecommendations({ locality, price_range, min_rating, cuisines }) {
  const response = await api.post('/api/recommend', {
    locality,
    price_range,
    min_rating,
    cuisines: Array.isArray(cuisines) ? cuisines : [],
  })
  return response.data
}

export async function getLocalities() {
  try {
    const response = await api.get('/api/localities')
    const localities = response.data.localities || []
    const restaurantCount = response.data.restaurant_count
    return { localities, restaurantCount }
  } catch (error) {
    console.error('Error fetching localities:', error)
    return { localities: [], restaurantCount: 0 }
  }
}

export async function getCuisines() {
  try {
    const response = await api.get('/api/cuisines')
    const cuisines = response.data.cuisines || []
    return cuisines
  } catch (error) {
    console.error('Error fetching cuisines:', error)
    return []
  }
}

export async function getRestaurantCount() {
  try {
    const response = await api.get('/api/restaurants')
    const count = response.data.count ?? 0
    return count
  } catch (error) {
    console.error('Error fetching restaurant count:', error)
    return 0
  }
}

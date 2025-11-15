import axios from 'axios'

// Get ML Service base URL from environment variables
const getMlBaseUrl = () => {
  const envBaseUrl = import.meta.env.VITE_ML_BASE_URL
  return envBaseUrl || 'http://localhost:8000'
}

// Create axios instance for ML Service with dynamic configuration
const mlApi = axios.create({
  baseURL: getMlBaseUrl(),
  timeout: 30000, // ML operations might take longer
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Request interceptor to add auth token for ML endpoints
mlApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle ML service errors
mlApi.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle ML service specific errors
    if (error.response?.status === 429) {
      console.warn('ML Service rate limit exceeded')
    }
    return Promise.reject(error)
  }
)

// ML Service specific API methods
export const mlService = {
  // Health check
  health: () => mlApi.get('/health'),

  // Sentiment analysis
  analyzeSentiment: (text) => mlApi.post('/sentiment', { text }),

  // Batch sentiment analysis
  analyzeSentimentBatch: (texts) => mlApi.post('/sentiment/batch', { texts }),

  // Get user recommendations
  getUserRecommendations: (userId, limit = 10) =>
    mlApi.get(`/recommendations/user/${userId}`, { params: { limit } }),

  // Image classification
  classifyImage: (imageUrl) => mlApi.post('/image-classification', { image_url: imageUrl }),

  // Text generation
  generateText: (prompt, options = {}) => mlApi.post('/text-generation', {
    prompt,
    ...options
  }),

  // Generic ML endpoint
  post: (endpoint, data) => mlApi.post(endpoint, data),
  get: (endpoint, params) => mlApi.get(endpoint, { params }),
  put: (endpoint, data) => mlApi.put(endpoint, data),
  delete: (endpoint) => mlApi.delete(endpoint)
}

export default mlApi
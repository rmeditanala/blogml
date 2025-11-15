// Main API export for backend Laravel API
export { default as api } from './api.js'

// ML Service API export for Python FastAPI ML service
export { mlService, default as mlApi } from './ml-api.js'

// Configuration exports
export const API_CONFIG = {
  get BASE_URL() {
    return import.meta.env.VITE_API_BASE_URL || '/api'
  },
  get ML_BASE_URL() {
    return import.meta.env.VITE_ML_BASE_URL || '/ml'
  },
  get APP_NAME() {
    return import.meta.env.VITE_APP_NAME || 'BlogML'
  },
  get IS_DEVELOPMENT() {
    return import.meta.env.VITE_NODE_ENV === 'development'
  }
}
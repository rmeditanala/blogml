import { defineStore } from 'pinia'
import { authService } from '../services/authService'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('auth_token') || null,
    isLoading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    userName: (state) => state.user?.name || null,
    userEmail: (state) => state.user?.email || null
  },

  actions: {
    async login(credentials) {
      this.isLoading = true
      this.error = null

      try {
        const response = await authService.login(credentials)

        this.token = response.token
        this.user = response.user

        // Save to localStorage
        localStorage.setItem('auth_token', response.token)
        localStorage.setItem('user', JSON.stringify(response.user))

        return { success: true, data: response }
      } catch (error) {
        this.error = error.response?.data?.message || 'Login failed'
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    async register(userData) {
      this.isLoading = true
      this.error = null

      try {
        const response = await authService.register(userData)

        this.token = response.token
        this.user = response.user

        // Save to localStorage
        localStorage.setItem('auth_token', response.token)
        localStorage.setItem('user', JSON.stringify(response.user))

        return { success: true, data: response }
      } catch (error) {
        this.error = error.response?.data?.message || 'Registration failed'
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      this.isLoading = true

      try {
        await authService.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.user = null
        this.token = null
        this.error = null

        // Clear localStorage
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user')

        this.isLoading = false
      }
    },

    async fetchUser() {
      if (!this.token) return

      this.isLoading = true

      try {
        const response = await authService.getUser()
        this.user = response.user

        // Update localStorage
        localStorage.setItem('user', JSON.stringify(response.user))

        return { success: true, data: response }
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch user'

        // Token might be invalid, clear auth
        this.user = null
        this.token = null
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user')

        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    async updateProfile(userData) {
      this.isLoading = true
      this.error = null

      try {
        const response = await authService.updateProfile(userData)
        this.user = response.user

        // Update localStorage
        localStorage.setItem('user', JSON.stringify(response.user))

        return { success: true, data: response }
      } catch (error) {
        this.error = error.response?.data?.message || 'Profile update failed'
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    // Initialize auth state from localStorage
    initAuth() {
      const token = localStorage.getItem('auth_token')
      const user = localStorage.getItem('user')

      if (token && user) {
        this.token = token
        this.user = JSON.parse(user)
      }
    },

    clearError() {
      this.error = null
    }
  }
})
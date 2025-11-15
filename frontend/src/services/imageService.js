import api from './api'

export const imageService = {
  // Upload image to Laravel backend
  async uploadImage(file) {
    const formData = new FormData()
    formData.append('image', file)

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 30000 // 30 seconds
    })

    return response.data
  },

  // Validate image file
  validateImage(file) {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    const maxSize = 5 * 1024 * 1024 // 5MB

    if (!allowedTypes.includes(file.type)) {
      throw new Error('Invalid file type. Please upload JPEG, PNG, GIF, or WebP images.')
    }

    if (file.size > maxSize) {
      throw new Error('File size too large. Maximum size is 5MB.')
    }

    return true
  },

  // Create preview URL
  createPreviewUrl(file) {
    return URL.createObjectURL(file)
  },

  // Revoke preview URL
  revokePreviewUrl(url) {
    URL.revokeObjectURL(url)
  }
}
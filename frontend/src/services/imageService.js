import api from './api'
import { mlService } from './mlService'

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
  },

  // Upload image with ML analysis (classification + alt text generation)
  async uploadImageWithAnalysis(file, options = {}) {
    try {
      // Validate the image first
      this.validateImage(file)

      // Perform ML analysis on the image
      console.log('Analyzing image with ML service...')
      const analysis = await mlService.analyzeImageComplete(file)

      if (!analysis.success) {
        throw new Error(`ML analysis failed: ${analysis.error}`)
      }

      console.log('ML Analysis Results:', {
        tags: analysis.tags,
        altText: analysis.alt_text,
        classification: analysis.classification
      })

      // Upload the image to Laravel backend
      console.log('Uploading image to backend...')
      const uploadData = await this.uploadImage(file)

      // Combine upload results with ML analysis
      return {
        ...uploadData,
        ml_analysis: {
          tags: analysis.tags,
          classification: analysis.classification,
          alt_text: analysis.alt_text,
          alt_text_prompt: analysis.alt_text_prompt,
          generated_at: new Date().toISOString()
        },
        success: true
      }

    } catch (error) {
      console.error('Error in upload with ML analysis:', error)

      // If ML analysis fails but upload is still needed, fallback to basic upload
      if (options.fallbackToUpload) {
        console.log('Falling back to basic upload without ML analysis...')
        try {
          const uploadData = await this.uploadImage(file)
          return {
            ...uploadData,
            ml_analysis: null,
            warning: 'ML analysis failed, image uploaded without AI-generated alt text',
            success: true
          }
        } catch (uploadError) {
          throw new Error(`Both ML analysis and upload failed: ${error.message}, Upload error: ${uploadError.message}`)
        }
      }

      throw error
    }
  },

  // Analyze image without uploading (useful for previews)
  async analyzeImageOnly(file) {
    try {
      this.validateImage(file)

      const analysis = await mlService.analyzeImageComplete(file)

      if (!analysis.success) {
        throw new Error(`ML analysis failed: ${analysis.error}`)
      }

      return analysis

    } catch (error) {
      console.error('Error in image analysis:', error)
      throw error
    }
  },

  // Generate alt text from existing image tags
  async generateAltTextFromTags(tags) {
    try {
      const altText = await mlService.generateAltText(null, tags)

      return {
        alt_text: typeof altText === 'string' ? altText : altText?.generated_text || '',
        prompt_used: altText?.prompt_used || '',
        success: true
      }

    } catch (error) {
      console.error('Error generating alt text from tags:', error)
      throw error
    }
  }
}
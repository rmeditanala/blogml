import axios from 'axios'

// Direct ML service calls
const ML_BASE_URL = 'http://localhost:8000'

export const mlService = {
  // Analyze image using ML service
  async analyzeImage(file) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post(`${ML_BASE_URL}/image-classification/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 30000 // 30 seconds
    })

    return response.data
  },

  // Generate alt text using ML service (using general text generation)
  // Note: This doesn't actually use the image file, just generates generic alt text
  async generateAltText(file) {
    try {
      const response = await axios.post(`${ML_BASE_URL}/text-generation/text`, {
        prompt: `Generate a descriptive alt text for a blog post image. The alt text should be concise but descriptive for accessibility purposes. Keep it under 100 characters.`,
        max_length: 100,
        temperature: 0.7
      }, {
        timeout: 30000 // 30 seconds
      })

      return response.data
    } catch (error) {
      // Fallback to simple alt text generation
      console.warn('ML text generation failed, using fallback:', error.message)
      return {
        generated_text: this.generateSimpleAltText(file.name),
        prompt_used: "Fallback alt text generation",
        generation_params: { fallback: true },
        cached: false
      }
    }
  },

  // Simple fallback alt text generator
  generateSimpleAltText(filename) {
    const name = filename.split('.').slice(0, -1).join('.').toLowerCase()

    // Simple descriptive alt texts based on common filename patterns
    const patterns = {
      'img': 'Photograph or image file',
      'image': 'Photograph or image file',
      'photo': 'Photograph or image file',
      'pic': 'Photograph or image file',
      'screenshot': 'Screenshot of computer screen',
      'capture': 'Screen capture or snapshot',
      'download': 'Downloaded file or image',
      'upload': 'Uploaded file or image',
      'document': 'Document or text file',
      'pdf': 'PDF document file',
      'icon': 'Icon or symbol',
      'logo': 'Company or brand logo',
      'banner': 'Banner or header image',
      'thumbnail': 'Thumbnail or preview image'
    }

    for (const [pattern, description] of Object.entries(patterns)) {
      if (name.includes(pattern)) {
        return description
      }
    }

    // Generic fallback
    return 'Digital image or graphic element'
  },

  // Combined image analysis (classification + alt text)
  async analyzeImageComplete(file) {
    try {
      const [classification, altText] = await Promise.all([
        this.analyzeImage(file),
        this.generateAltText(file)
      ])

      return {
        classification: classification.tags || classification, // Handle both formats
        alt_text: typeof altText === 'string' ? altText : altText?.generated_text || '',
        success: true
      }
    } catch (error) {
      console.error('ML Service Error:', error)
      return {
        error: error.message,
        success: false
      }
    }
  }
}
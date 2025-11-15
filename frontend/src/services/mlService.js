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

  // Generate text using ML service
  async generateText(prompt, max_length = 100, temperature = 0.7) {
    try {
      const response = await axios.post(`${ML_BASE_URL}/text-generation/text`, {
        prompt: prompt,
        max_length: max_length,
        temperature: temperature
      }, {
        timeout: 60000 // 1 minute timeout
      })

      return response.data
    } catch (error) {
      console.error('ML Service text generation failed:', error)
      // Return fallback response
      return {
        generated_text: "Generated text unavailable",
        prompt_used: prompt,
        generation_params: { fallback: true },
        cached: false
      }
    }
  },

  // Generate complete blog post using ML service
  async generateBlogPost(options) {
    try {
      const response = await axios.post(`${ML_BASE_URL}/text-generation/post`, {
        topic: options.topic,
        tone: options.tone || 'informative',
        target_length: options.target_length || 1000,
        target_audience: options.target_audience || 'general',
        outline: options.outline || null
      }, {
        timeout: 120000 // 2 minutes timeout for longer content
      })

      return response.data
    } catch (error) {
      console.error('ML Service blog post generation failed:', error)
      // Return fallback response
      return {
        post_content: `Generated content about ${options.topic}`,
        title: `Blog Post about ${options.topic}`,
        sections: ['Introduction', 'Main Content', 'Conclusion'],
        metadata: {
          topic: options.topic,
          tone: options.tone,
          target_length: options.target_length,
          actual_length: 0,
          generated_with: 'fallback'
        }
      }
    }
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
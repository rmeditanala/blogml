<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div class="bg-white shadow-lg rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <h1 class="text-2xl font-bold text-gray-900">Create New Post</h1>
        </div>

        <div v-if="error" class="mx-6 mt-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
          {{ error }}
        </div>

        <form @submit.prevent="handleSubmit" class="px-6 py-6">
          <div class="space-y-6">
            <!-- Title -->
            <div>
              <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
                Post Title *
              </label>
              <input
                id="title"
                v-model="form.title"
                type="text"
                class="input-field"
                placeholder="Enter an engaging title for your post"
                required
              >
            </div>

            <!-- Featured Image -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Featured Image
              </label>

              <!-- Image Upload Area -->
              <div class="border-2 border-dashed border-gray-300 rounded-lg p-4">
                <div v-if="!imagePreview" class="text-center">
                  <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                  <div class="mt-2">
                    <label for="image-upload" class="cursor-pointer">
                      <span class="mt-2 block text-sm font-medium text-gray-900">
                        Click to upload or drag and drop
                      </span>
                      <span class="text-xs text-gray-500">
                        PNG, JPG, GIF up to 5MB
                      </span>
                    </label>
                    <input id="image-upload"
                           ref="imageInput"
                           @change="handleImageSelect"
                           type="file"
                           class="sr-only"
                           accept="image/*">
                  </div>
                </div>

                <!-- Image Preview -->
                <div v-else class="relative">
                  <img :src="imagePreview" alt="Preview" class="w-full h-48 object-cover rounded-lg">
                  <button type="button" @click="removeImage" class="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600">
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>

                  <!-- ML Analysis Results -->
                  <div v-if="imageAnalysis" class="mt-4 p-3 bg-blue-50 rounded-lg">
                    <h4 class="text-sm font-medium text-blue-900 mb-2">🤖 AI Analysis Results:</h4>
                    <div v-if="imageAnalysis.classification && imageAnalysis.classification.length > 0" class="text-xs text-blue-800">
                      <strong>Classification:</strong>
                      <div class="mt-1">
                        <span v-for="item in imageAnalysis.classification" :key="item.tag"
                              class="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs mr-1 mb-1">
                          {{ item.tag }} ({{ (item.confidence * 100).toFixed(1) }}%)
                        </span>
                      </div>
                    </div>
                    <div v-if="imageAnalysis.alt_text && imageAnalysis.alt_text !== 'Text generation unavailable'" class="text-xs text-blue-800 mt-2">
                      <strong>{{ imageAnalysis.generation_params?.fallback ? 'Generated Alt Text:' : 'AI Generated Alt Text:' }}</strong> {{ imageAnalysis.alt_text }}
                    </div>
                    <div v-if="imageAnalysis.error" class="text-xs text-red-800 mt-2">
                      <strong>Analysis Error:</strong> {{ imageAnalysis.error }}
                    </div>
                  </div>

                  <!-- Loading State -->
                  <div v-if="imageAnalyzing" class="mt-4 p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center text-sm text-gray-600">
                      <svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Analyzing image with AI...
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Excerpt -->
            <div>
              <label for="excerpt" class="block text-sm font-medium text-gray-700 mb-2">
                Excerpt
              </label>
              <textarea
                id="excerpt"
                v-model="form.excerpt"
                rows="3"
                class="input-field"
                placeholder="A brief summary of your post (optional)"
              ></textarea>
              <p class="mt-1 text-sm text-gray-500">
                Brief description that appears in post listings and search results.
              </p>
            </div>

            <!-- Content -->
            <div>
              <label for="content" class="block text-sm font-medium text-gray-700 mb-2">
                Content *
              </label>
              <textarea
                id="content"
                v-model="form.content"
                rows="12"
                class="input-field"
                placeholder="Write your blog post content here..."
                required
              ></textarea>
              <div class="mt-2 flex justify-between">
                <p class="text-sm text-gray-500">
                  {{ form.content.length }} characters
                </p>
                <p class="text-sm text-gray-500">
                  {{ wordCount }} words
                </p>
              </div>
            </div>

            <!-- Status -->
            <div>
              <label for="status" class="block text-sm font-medium text-gray-700 mb-2">
                Post Status
              </label>
              <select id="status" v-model="form.status" class="input-field">
                <option value="draft">📝 Draft</option>
                <option value="published">🚀 Publish Now</option>
              </select>
              <p class="mt-1 text-sm text-gray-500">
                Choose whether to save as draft or publish immediately.
              </p>
            </div>

            <!-- AI Blog Post Generation -->
            <div class="border-t border-gray-200 pt-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">🤖 AI Blog Post Generator</h3>

              <!-- AI Prompt Input -->
              <div class="mb-4">
                <label for="ai-prompt" class="block text-sm font-medium text-gray-700 mb-2">
                  Describe the blog post you want to create
                </label>
                <textarea
                  id="ai-prompt"
                  v-model="aiPrompt"
                  rows="3"
                  class="input-field mb-3"
                  placeholder="E.g., 'Write a blog post about the benefits of remote work for tech companies' or 'Create a tutorial on getting started with Vue.js for beginners'"
                ></textarea>

                <!-- AI Generation Options -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <label for="ai-tone" class="block text-sm font-medium text-gray-700 mb-1">Tone</label>
                    <select id="ai-tone" v-model="aiOptions.tone" class="input-field">
                      <option value="informative">Informative</option>
                      <option value="casual">Casual</option>
                      <option value="formal">Formal</option>
                      <option value="creative">Creative</option>
                    </select>
                  </div>
                  <div>
                    <label for="ai-length" class="block text-sm font-medium text-gray-700 mb-1">Length</label>
                    <select id="ai-length" v-model="aiOptions.length" class="input-field">
                      <option value="short">Short (~300 words)</option>
                      <option value="medium">Medium (~600 words)</option>
                      <option value="long">Long (~1000 words)</option>
                    </select>
                  </div>
                  <div>
                    <label for="ai-audience" class="block text-sm font-medium text-gray-700 mb-1">Target Audience</label>
                    <select id="ai-audience" v-model="aiOptions.audience" class="input-field">
                      <option value="general">General</option>
                      <option value="beginners">Beginners</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="experts">Experts</option>
                    </select>
                  </div>
                </div>

                <button
                  type="button"
                  @click="generateBlogPost"
                  :disabled="aiLoading || !aiPrompt.trim()"
                  class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed w-full flex items-center justify-center"
                >
                  <svg v-if="aiLoading" class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ aiLoading ? 'Generating Blog Post...' : '✨ Generate Complete Blog Post' }}
                </button>

                <p class="mt-2 text-sm text-gray-500">
                  AI will generate a title, content, and excerpt based on your prompt and preferences.
                </p>
              </div>

              <!-- AI Generation Progress -->
              <div v-if="aiLoading && aiGenerationStatus" class="mt-4 p-4 bg-blue-50 rounded-lg">
                <h4 class="text-sm font-medium text-blue-900 mb-2">🔄 AI Generation Progress:</h4>
                <div class="text-xs text-blue-800 space-y-1">
                  <div v-for="(status, index) in aiGenerationStatus" :key="index" class="flex items-center">
                    <span v-if="status.completed" class="text-green-600 mr-2">✅</span>
                    <span v-else-if="status.current" class="text-blue-600 mr-2 animate-pulse">🔄</span>
                    <span v-else class="text-gray-500 mr-2">⏳</span>
                    {{ status.message }}
                  </div>
                </div>
              </div>
            </div>

                      </div>

          <!-- Form Actions -->
          <div class="border-t border-gray-200 pt-6">
            <div class="flex justify-between">
              <router-link
                to="/posts"
                class="btn btn-secondary"
              >
                Cancel
              </router-link>
              <button
                type="submit"
                :disabled="isLoading || !form.title || !form.content"
                class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="isLoading" class="mr-2">
                  <svg class="animate-spin h-4 w-4 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </span>
                {{ isLoading ? (form.status === 'published' ? 'Publishing...' : 'Saving...') : (form.status === 'published' ? '🚀 Publish Post' : '📝 Save Draft') }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { postService } from '../services/postService'
import { imageService } from '../services/imageService'
import { mlService } from '../services/mlService'

const router = useRouter()

// Image upload state
const imageInput = ref(null)
const selectedImage = ref(null)
const imagePreview = ref(null)
const imageAnalysis = ref(null)
const imageAnalyzing = ref(false)
const uploadedImageUrl = ref(null)

const form = ref({
  title: '',
  excerpt: '',
  content: '',
  status: 'draft'
})

const isLoading = ref(false)
const aiLoading = ref(false)
const error = ref(null)

// AI Blog Post Generation state
const aiPrompt = ref('')
const aiOptions = ref({
  tone: 'informative',
  length: 'medium',
  audience: 'general'
})
const aiGenerationStatus = ref([])

const wordCount = computed(() => {
  if (!form.value.content) return 0
  return form.value.content.trim().split(/\s+/).filter(word => word.length > 0).length
})

// Generate excerpt from content using AI
const generateExcerptFromContent = async (content, topic) => {
  if (!content) return ''

  try {
    // Use ML service to create a summary
    const summaryPrompt = `Create a compelling excerpt/summary for a blog post about "${topic}".

Here is the blog post content:
${content}

Requirements for the excerpt:
- Write 2-3 sentences that summarize the main points
- Make it engaging and informative to encourage readers to click
- Keep it under 300 characters for SEO purposes
- Focus on the value readers will get from this post
- Write in a clear, accessible tone
- Do NOT copy exact sentences from the content - create a new summary
- End with a hint of what readers will learn

Generate only the excerpt text, no additional commentary.`

    const response = await mlService.generateText(summaryPrompt, 150, 0.7)
    let generatedExcerpt = response.generated_text || response

    // Clean up the generated excerpt
    if (generatedExcerpt) {
      generatedExcerpt = generatedExcerpt
        .replace(/^["']|["']$/g, '') // Remove surrounding quotes
        .replace(/^(Excerpt|Summary:?\s*)/i, '') // Remove prefixes
        .trim()

      // Ensure it's not too long for SEO
      if (generatedExcerpt.length > 280) {
        const lastSentence = generatedExcerpt.lastIndexOf('.')
        if (lastSentence > 100 && lastSentence < 270) {
          generatedExcerpt = generatedExcerpt.substring(0, lastSentence + 1)
        } else {
          generatedExcerpt = generatedExcerpt.substring(0, 270) + '...'
        }
      }

      return generatedExcerpt
    }
  } catch (error) {
    console.warn('AI excerpt generation failed, using fallback:', error.message)
  }

  // Fallback to simple extraction if AI fails
  const cleanContent = content
    .replace(/#{1,6}\s+/g, '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/`(.*?)`/g, '$1')
    .replace(/\[(.*?)\]\(.*?\)/g, '$1')
    .replace(/^\s*[-*+]\s+/gm, '')
    .replace(/^\s*\d+\.\s+/gm, '')
    .replace(/\n+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

  const sentences = cleanContent.split('.').filter(s => s.trim().length > 10)
  let excerpt = sentences.slice(0, 2).join('.').trim()

  if (excerpt.length > 280) {
    excerpt = excerpt.substring(0, 270) + '...'
  }

  return excerpt || `Learn about ${topic} in this comprehensive guide covering key concepts, practical applications, and expert insights.`
}

const handleSubmit = async () => {
  isLoading.value = true
  error.value = null

  try {
    // Upload image first if selected
    if (selectedImage.value) {
      try {
        const uploadResponse = await imageService.uploadImage(selectedImage.value)
        uploadedImageUrl.value = uploadResponse.url
      } catch (uploadErr) {
        error.value = 'Failed to upload image: ' + uploadErr.message
        return
      }
    }

    const postData = {
      ...form.value,
      featured_image: uploadedImageUrl.value,
      image_analysis: imageAnalysis.value,
      published_at: form.value.status === 'published' ? new Date().toISOString() : null
    }

    const response = await postService.createPost(postData)

    router.push(`/posts/${response.data.slug}`)
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to create post'
    console.error('Create post error:', err)
  } finally {
    isLoading.value = false
  }
}

const handleImageSelect = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    // Validate image
    imageService.validateImage(file)

    selectedImage.value = file
    imagePreview.value = imageService.createPreviewUrl(file)
    imageAnalysis.value = null
    imageAnalyzing.value = true

    // Analyze image with ML service
    const analysis = await mlService.analyzeImageComplete(file)
    imageAnalysis.value = analysis

  } catch (err) {
    error.value = err.message || 'Failed to process image'
    removeImage()
  } finally {
    imageAnalyzing.value = false
  }
}

const removeImage = () => {
  if (imagePreview.value) {
    imageService.revokePreviewUrl(imagePreview.value)
  }

  selectedImage.value = null
  imagePreview.value = null
  imageAnalysis.value = null
  uploadedImageUrl.value = null

  // Clear file input
  if (imageInput.value) {
    imageInput.value.value = ''
  }
}


const generateBlogPost = async () => {
  if (!aiPrompt.value.trim()) return

  aiLoading.value = true
  error.value = null

  // Initialize generation status
  aiGenerationStatus.value = [
    { message: 'Analyzing your prompt...', completed: false, current: true },
    { message: 'Generating blog post title...', completed: false, current: false },
    { message: 'Creating blog post content...', completed: false, current: false },
    { message: 'Generating excerpt...', completed: false, current: false }
  ]

  try {
    // Map options to API parameters
    const lengthMap = {
      'short': 500,
      'medium': 1000,
      'long': 1500
    }

    const targetLength = lengthMap[aiOptions.value.length] || 1000

    // Generate title first using ML service
    const titlePrompt = `Create a catchy, engaging blog post title about: ${aiPrompt.value}

Requirements:
- Tone: ${aiOptions.value.tone}
- Target audience: ${aiOptions.value.audience}
- Should be compelling and make people want to click
- Avoid clickbait but be interesting
- Keep it under 70 characters for SEO
- Use strong, active language

Generate only the title, no additional text.`

    const titleResponse = await mlService.generateText(titlePrompt, 50, 0.8)
    const generatedTitle = titleResponse.generated_text || titleResponse

    // Update status
    aiGenerationStatus.value[1].completed = true
    aiGenerationStatus.value[1].current = false
    aiGenerationStatus.value[2].current = true

    // Generate blog post content using ML service
    const blogPostPrompt = `Write a complete, well-structured blog post about: ${aiPrompt.value}

Title: "${generatedTitle}"

Style requirements:
- Tone: ${aiOptions.value.tone}
- Target audience: ${aiOptions.value.audience}
- Length: approximately ${targetLength} words
- Format: Use proper markdown formatting with headers, paragraphs, and bullet points where appropriate
- Start with a compelling introduction that hooks the reader
- Include practical examples and actionable insights
- End with a strong conclusion and call-to-action

Please create engaging, informative content that provides value to the reader and follows best practices for blog writing.`

    // Generate blog post using ML service
    const response = await mlService.generateBlogPost({
      topic: aiPrompt.value,
      prompt: blogPostPrompt,
      tone: aiOptions.value.tone,
      target_length: targetLength,
      target_audience: aiOptions.value.audience
    })

    // Fill form with generated content
    form.value.title = generatedTitle.trim()

    if (response.post_content) {
      form.value.content = response.post_content

      // Auto-generate excerpt from content if not provided by ML service
      if (!response.excerpt) {
        form.value.excerpt = await generateExcerptFromContent(response.post_content, aiPrompt.value)
      }
    }

    if (response.excerpt) {
      form.value.excerpt = response.excerpt
    }

    // Complete all status items
    aiGenerationStatus.value[2].completed = true
    aiGenerationStatus.value[2].current = false
    aiGenerationStatus.value[3].completed = true
    aiGenerationStatus.value[3].current = true

    // Clear the AI prompt after successful generation
    setTimeout(() => {
      aiGenerationStatus.value = []
    }, 2000)

  } catch (err) {
    console.error('AI blog post generation error:', err)

    // Fallback to mock generation if ML service fails
    try {
      aiGenerationStatus.value[1].completed = true
      aiGenerationStatus.value[1].current = false
      aiGenerationStatus.value[2].current = true

      // Generate fallback content with creative titles
      const titleTemplates = [
        `The Ultimate Guide to ${aiPrompt.value}`,
        `${aiPrompt.value}: Everything You Need to Know`,
        `Mastering ${aiPrompt.value}: A Comprehensive Guide`,
        `The Complete ${aiPrompt.value} Handbook`,
        `${aiPrompt.value} Explained: From Beginner to Pro`,
        `Unlocking the Power of ${aiPrompt.value}`,
        `The Art and Science of ${aiPrompt.value}`,
        `${aiPrompt.value}: A Practical Approach`
      ]

      const mockTitle = titleTemplates[Math.floor(Math.random() * titleTemplates.length)]
      const mockContent = `# ${mockTitle}

## Introduction

Welcome to this comprehensive guide on ${aiPrompt.value.toLowerCase()}. In today's fast-paced world, understanding this topic is more important than ever. Whether you're a beginner or looking to deepen your knowledge, this article will provide valuable insights and practical information.

## Why This Matters

${aiPrompt.value} plays a crucial role in modern ${aiOptions.value.audience === 'beginners' ? 'learning' : aiOptions.value.audience === 'experts' ? 'practice' : 'discussion'}. Let's explore the key aspects that make it so significant.

### Key Benefits

- **First Major Benefit**: This advantage helps users achieve better results through improved understanding and application
- **Second Major Benefit**: Another important aspect that contributes to overall success and efficiency
- **Third Major Benefit**: A crucial element that often gets overlooked but provides substantial value

## Practical Implementation

Now that we understand the importance, let's dive into how you can practically implement these concepts in your daily routine.

### Getting Started

The first step is to establish a solid foundation. Start by:

1. Understanding the basic principles and concepts
2. Setting clear goals and objectives
3. Creating a structured approach to learning and application
4. Practicing regularly to build confidence and expertise

### Advanced Techniques

Once you're comfortable with the basics, you can explore more advanced strategies:

- **Technique A**: This method allows for greater efficiency and better results
- **Technique B**: An alternative approach that works well in specific scenarios
- **Technique C**: A comprehensive strategy that combines multiple elements

## Common Challenges and Solutions

Every journey comes with its own set of challenges. Here are some common obstacles you might encounter and how to overcome them:

### Challenge 1: Lack of Time
**Solution**: Break down the learning process into manageable chunks and dedicate consistent, focused time slots.

### Challenge 2: Information Overload
**Solution**: Prioritize the most relevant information and build your knowledge incrementally.

### Challenge 3: Maintaining Motivation
**Solution**: Set realistic milestones and celebrate small wins along the way.

## Best Practices

To ensure long-term success, consider these best practices:

- **Consistency**: Regular practice and application are essential for mastery
- **Continuous Learning**: Stay updated with the latest developments and trends
- **Community Engagement**: Connect with others who share similar interests and goals
- **Documentation**: Keep track of your progress and lessons learned

## Conclusion

${aiPrompt.value} offers tremendous potential for growth and development. By following the strategies and techniques outlined in this guide, you'll be well-equipped to navigate the challenges and opportunities that lie ahead.

Remember that mastery takes time and dedication. Be patient with yourself, stay curious, and never stop learning. The journey of discovery is just as important as the destination.

### Next Steps

Now that you have a solid understanding, consider these next steps:

- Start implementing the basic concepts in your own projects
- Explore additional resources and learning materials
- Connect with communities and experts in the field
- Set specific, measurable goals for your continued growth

Thank you for taking the time to explore this important topic. We hope this guide has provided valuable insights and practical guidance for your journey.`

      form.value.title = mockTitle
      form.value.content = mockContent

      // Auto-generate excerpt from fallback content
      form.value.excerpt = await generateExcerptFromContent(mockContent, aiPrompt.value)

      aiGenerationStatus.value[2].completed = true
      aiGenerationStatus.value[2].current = false
      aiGenerationStatus.value[3].completed = true
      aiGenerationStatus.value[3].current = true

      setTimeout(() => {
        aiGenerationStatus.value = []
      }, 2000)

    } catch (fallbackErr) {
      error.value = 'Failed to generate blog post. Please try again.'
      console.error('Fallback generation also failed:', fallbackErr)
    }
  } finally {
    aiLoading.value = false
  }
}

</script>
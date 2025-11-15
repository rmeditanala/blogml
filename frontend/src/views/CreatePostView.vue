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
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <div class="flex space-x-6">
                <label class="flex items-center">
                  <input
                    v-model="form.status"
                    type="radio"
                    value="published"
                    class="mr-2"
                  >
                  <span>Publish Now</span>
                </label>
                <label class="flex items-center">
                  <input
                    v-model="form.status"
                    type="radio"
                    value="draft"
                    class="mr-2"
                  >
                  <span>Save as Draft</span>
                </label>
              </div>
            </div>

            <!-- AI Generation Tools -->
            <div class="border-t border-gray-200 pt-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">AI Writing Assistant</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  type="button"
                  @click="generateOutline"
                  :disabled="aiLoading || !form.title"
                  class="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  <svg v-if="aiLoading" class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ aiLoading ? 'Generating...' : 'Generate Outline' }}
                </button>
                <button
                  type="button"
                  @click="expandContent"
                  :disabled="aiLoading || !form.content"
                  class="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  <svg v-if="aiLoading" class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ aiLoading ? 'Expanding...' : 'Expand Content' }}
                </button>
              </div>
              <p class="mt-2 text-sm text-gray-500">
                Use AI to help with content generation and improvement.
              </p>
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
              <div class="flex space-x-3">
                <button
                  type="button"
                  @click="saveDraft"
                  :disabled="isLoading"
                  class="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ isLoading ? 'Saving...' : 'Save Draft' }}
                </button>
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
                  {{ isLoading ? 'Publishing...' : 'Publish Post' }}
                </button>
              </div>
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
import { useAuthStore } from '../stores/auth'
import { postService } from '../services/postService'
import { imageService } from '../services/imageService'
import { mlService } from '../services/mlService'

const router = useRouter()
const authStore = useAuthStore()

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

const wordCount = computed(() => {
  if (!form.value.content) return 0
  return form.value.content.trim().split(/\s+/).filter(word => word.length > 0).length
})

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

const saveDraft = async () => {
  isLoading.value = true
  error.value = null

  try {
    const postData = {
      ...form.value,
      status: 'draft'
    }

    const response = await postService.createPost(postData)

    router.push(`/posts/${response.data.slug}`)
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to save draft'
    console.error('Save draft error:', err)
  } finally {
    isLoading.value = false
  }
}

const generateOutline = async () => {
  if (!form.value.title) return

  aiLoading.value = true
  error.value = null

  try {
    // Mock AI outline generation (would call AI service in real implementation)
    const mockOutline = `## Introduction
- Hook the reader with an interesting opening
- Briefly introduce the topic and its importance
- Set expectations for what the reader will learn

## Main Points
- First key concept or argument
- Second key concept or argument
- Third key concept or argument

## Conclusion
- Summarize the main points
- Provide a call to action or final thoughts
- Encourage engagement through comments`

    form.value.content = mockOutline
  } catch (err) {
    error.value = 'Failed to generate outline'
    console.error('AI outline error:', err)
  } finally {
    aiLoading.value = false
  }
}

const expandContent = async () => {
  if (!form.value.content) return

  aiLoading.value = true
  error.value = null

  try {
    // Mock content expansion (would call AI service in real implementation)
    const expandedContent = form.value.content + '\n\n## Additional Details\n\nLet me elaborate further on the key points mentioned above. This section provides more depth and context to help readers better understand the concepts and their practical applications.\n\n## Examples and Case Studies\n\nHere are some real-world examples that demonstrate these principles in action. These case studies show how theory translates into practice in various scenarios.'

    form.value.content = expandedContent
  } catch (err) {
    error.value = 'Failed to expand content'
    console.error('AI expand error:', err)
  } finally {
    aiLoading.value = false
  }
}
</script>
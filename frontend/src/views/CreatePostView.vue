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

const router = useRouter()
const authStore = useAuthStore()

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
    const postData = {
      ...form.value,
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
<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Latest Blog Posts</h1>
            <p class="mt-1 text-sm text-gray-500">
              {{ posts.length }} post{{ posts.length !== 1 ? 's' : '' }} published
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-2">Search Posts</label>
            <input
              v-model="searchQuery"
              type="text"
              class="input-field"
              placeholder="Search by title or content..."
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Category</label>
            <select v-model="categoryFilter" class="input-field">
              <option value="">All Categories</option>
              <option value="technology">Technology</option>
              <option value="business">Business</option>
              <option value="lifestyle">Lifestyle</option>
              <option value="tutorial">Tutorial</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="text-center">
        <svg class="animate-spin h-12 w-12 text-blue-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-4 text-gray-600">Loading posts...</p>
      </div>
    </div>

    <!-- Posts Grid -->
    <div v-else class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
      <div v-if="filteredPosts.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No posts found</h3>
        <p class="mt-1 text-sm text-gray-500">
          {{ searchQuery ? 'Try adjusting your search terms' : 'No blog posts available yet' }}
        </p>
      </div>

      <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="post in paginatedPosts"
          :key="post.id"
          class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
        >
          <!-- Featured Image -->
          <div v-if="post.featured_image" class="h-48 bg-gray-200">
            <img
              :src="post.featured_image"
              :alt="post.title"
              class="w-full h-full object-cover"
              @error="handleImageError"
            >
          </div>

          <div class="p-6">
            <div class="flex items-center justify-between mb-2">
              <span
                :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  post.status === 'published' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                ]"
              >
                {{ post.status === 'published' ? 'Published' : 'Draft' }}
              </span>
              <span
                v-if="post.is_ai_generated"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
              >
                AI Generated
              </span>
            </div>

            <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
              <router-link :to="`/posts/${post.slug}`" class="hover:text-blue-600">
                {{ post.title }}
              </router-link>
            </h3>

            <p class="text-gray-600 text-sm mb-4 line-clamp-3">
              {{ post.excerpt || post.content.substring(0, 150) + '...' }}
            </p>

            <div class="flex items-center text-sm text-gray-500 mb-4">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
              </svg>
              {{ post.view_count || 0 }}

              <svg class="w-4 h-4 ml-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
              </svg>
              {{ post.comment_count || 0 }}

              <span class="ml-auto text-xs">
                {{ formatDate(post.published_at || post.created_at) }}
              </span>
            </div>

            <div class="flex justify-between">
              <router-link
                :to="`/posts/${post.slug}`"
                class="text-blue-600 hover:text-blue-800 font-medium text-sm"
              >
                Read More
              </router-link>

              <div v-if="post.author" class="flex items-center text-sm text-gray-500">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14s-4 4-4 4 4 4 0 4 4-4-4z"></path>
                </svg>
                {{ post.author.name }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="mt-8 flex justify-center">
        <nav class="flex items-center space-x-2">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          <div class="flex space-x-1">
            <button
              v-for="page in totalPages"
              :key="page"
              @click="currentPage = page"
              :class="[
                'px-3 py-2 text-sm font-medium rounded-md',
                currentPage === page
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50'
              ]"
            >
              {{ page }}
            </button>
          </div>

          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </nav>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { postService } from '../services/postService'

const authStore = useAuthStore()

const posts = ref([])
const loading = ref(false)
const searchQuery = ref('')
const categoryFilter = ref('')
const currentPage = ref(1)
const postsPerPage = 9


const filteredPosts = computed(() => {
  let filtered = posts.value

  // Only show published posts on homepage
  filtered = filtered.filter(post => post.status === 'published')

  // Filter by category
  if (categoryFilter.value) {
    filtered = filtered.filter(post =>
      post.category === categoryFilter.value
    )
  }

  // Search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(post =>
      post.title.toLowerCase().includes(query) ||
      post.content.toLowerCase().includes(query) ||
      post.excerpt?.toLowerCase().includes(query)
    )
  }

  // Sort by published date (newest first)
  filtered.sort((a, b) => new Date(b.published_at || b.created_at) - new Date(a.published_at || a.created_at))

  return filtered
})

const totalPages = computed(() => Math.ceil(filteredPosts.value.length / postsPerPage))

const paginatedPosts = computed(() => {
  const start = (currentPage.value - 1) * postsPerPage
  const end = start + postsPerPage
  return filteredPosts.value.slice(start, end)
})

const fetchPosts = async () => {
  loading.value = true
  try {
    const response = await postService.getPosts()
    posts.value = response.data || response.posts || []
  } catch (error) {
    console.error('Failed to fetch posts:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'No date'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const handleImageError = (event) => {
  event.target.src = 'data:image/svg+xml;base64,PHN2ZyB4b2xpZGVnaW5nPSJodHRwOi8vd3d3LnczL21ldGEvc3ZnIiB3aW5kZWR0PSIwIDAgMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMSAyMSIgZmlsbD0iI0UzODA4MCcgZmlsbC9vYzJkYW5kLTEiLz48L3N2Zz4K'
}

// Watch for filter changes to reset pagination
watch([searchQuery, categoryFilter], () => {
  currentPage.value = 1
})

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  display: -moz-box;
  display: box;
  -webkit-line-clamp: 2;
  -moz-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  -moz-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  display: -moz-box;
  display: box;
  -webkit-line-clamp: 3;
  -moz-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  -moz-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
}
</style>
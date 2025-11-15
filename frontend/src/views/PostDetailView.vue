<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Loading State -->
    <div v-if="loading" class="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div class="text-center">
        <svg class="animate-spin h-12 w-12 text-blue-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-4 text-gray-600">Loading post...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div class="text-center">
        <svg class="mx-auto h-12 w-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <h3 class="mt-2 text-lg font-medium text-gray-900">Post not found</h3>
        <p class="mt-1 text-gray-500">
          {{ error }}
        </p>
        <div class="mt-6">
          <router-link to="/posts" class="btn btn-primary">
            Back to Posts
          </router-link>
        </div>
      </div>
    </div>

    <!-- Post Content -->
    <div v-else-if="post" class="max-w-4xl mx-auto">
      <!-- Header Image (if available) -->
      <div v-if="post.featured_image" class="h-64 bg-gray-200 flex items-center justify-center">
        <img :src="post.featured_image" :alt="post.title" class="w-full h-full object-cover">
      </div>

      <!-- Post Header -->
      <div class="bg-white shadow">
        <div class="max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
          <div class="mb-6">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center space-x-2">
                <span
                  v-if="post.is_ai_generated"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                >
                  AI Generated
                </span>
                <span class="text-sm text-gray-500">
                  Published on {{ formatDate(post.published_at) }}
                </span>
              </div>

              <div v-if="isAuthenticated && post.user_id === currentUserId" class="flex space-x-2">
                <router-link
                  :to="`/posts/${post.slug}/edit`"
                  class="text-gray-600 hover:text-gray-800 p-2 rounded-md hover:bg-gray-100"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                </router-link>
              </div>
            </div>

            <h1 class="text-3xl font-bold text-gray-900 mb-4">
              {{ post.title }}
            </h1>

            <div class="flex items-center space-x-6 text-sm text-gray-500">
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                {{ post.user?.name || 'Anonymous' }}
              </div>

              <div class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                </svg>
                {{ post.view_count || 0 }} views
              </div>

              <div class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
                {{ post.comment_count || 0 }} comments
              </div>
            </div>

            <!-- Like Button -->
            <div class="mt-6" v-if="isAuthenticated">
              <button
                @click="toggleLike"
                :disabled="likeLoading"
                class="flex items-center space-x-2 px-4 py-2 rounded-md border transition-colors"
                :class="isLiked ? 'bg-red-50 border-red-300 text-red-600' : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'"
              >
                <svg class="w-5 h-5" :class="isLiked ? 'fill-current' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                </svg>
                <span>{{ post.like_count || 0 }} Likes</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Post Body -->
      <div class="bg-white shadow-sm mt-2">
        <div class="max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
          <div class="prose prose-lg max-w-none">
            <!-- Excerpt if available -->
            <div v-if="post.excerpt" class="text-lg text-gray-600 mb-8 italic">
              {{ post.excerpt }}
            </div>

            <!-- Main content -->
            <div class="whitespace-pre-wrap">{{ post.content }}</div>
          </div>
        </div>
      </div>

      <!-- Comments Section -->
      <div class="bg-white shadow-sm mt-2">
        <div class="max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">
            Comments ({{ comments.length }})
          </h2>

          <!-- Comment Form -->
          <div v-if="isAuthenticated" class="mb-8">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Leave a Comment</h3>
            <form @submit.prevent="submitComment">
              <div class="mb-4">
                <textarea
                  v-model="newComment"
                  rows="4"
                  class="input-field"
                  placeholder="Share your thoughts..."
                  required
                  maxlength="2000"
                ></textarea>
                <div class="mt-2 flex justify-between text-sm text-gray-500">
                  <span>Minimum 3 characters</span>
                  <span>{{ newComment.length }}/2000 characters</span>
                </div>
              </div>
              <button
                type="submit"
                :disabled="commentLoading || !newComment.trim() || newComment.trim().length < 3"
                class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ commentLoading ? 'Posting...' : 'Post Comment' }}
              </button>
            </form>
          </div>

          <div v-else class="mb-8 p-4 bg-gray-50 rounded-lg">
            <router-link to="/login" class="text-blue-600 hover:text-blue-800 font-medium">
              Sign in
            </router-link>
            to leave a comment.
          </div>

          <!-- Comments List -->
          <div v-if="comments.length === 0" class="text-center py-8 text-gray-500">
            No comments yet. Be the first to share your thoughts!
          </div>

          <div v-else class="space-y-6">
            <div
              v-for="comment in comments"
              :key="comment.id"
              class="border-b border-gray-200 pb-6 last:border-b-0"
            >
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0">
                  <div class="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-gray-600">
                      {{ comment.user?.name?.charAt(0)?.toUpperCase() || '?' }}
                    </span>
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-2">
                    <p class="text-sm font-medium text-gray-900">
                      {{ comment.user?.name || 'Anonymous' }}
                    </p>
                    <span
                      v-if="comment.sentiment_label"
                      :class="[
                        'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
                        comment.sentiment_label === 'POSITIVE' ? 'bg-green-100 text-green-800' :
                        comment.sentiment_label === 'NEGATIVE' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      ]"
                    >
                      {{ comment.sentiment_label }}
                    </span>
                    <p class="text-sm text-gray-500">
                      {{ formatDate(comment.created_at) }}
                    </p>
                  </div>
                  <div class="mt-2 text-sm text-gray-700 whitespace-pre-wrap">
                    {{ comment.content }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { postService } from '../services/postService'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const post = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref(null)
const likeLoading = ref(false)
const commentLoading = ref(false)
const newComment = ref('')
const isLiked = ref(false)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentUserId = computed(() => authStore.user?.id)

const fetchPost = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await postService.getPost(route.params.slug)
    post.value = response.data || response.post

    // Track view
    if (isAuthenticated.value) {
      await postService.viewPost(post.value.slug)
    }

    // Fetch comments
    await fetchComments()
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load post'
    console.error('Fetch post error:', err)
  } finally {
    loading.value = false
  }
}

const fetchComments = async () => {
  try {
    const response = await postService.getPostComments(post.value.slug)
    comments.value = response.data || response.comments || []
  } catch (err) {
    console.error('Fetch comments error:', err)
    // Don't set error state, just log it
  }
}

const toggleLike = async () => {
  if (!isAuthenticated.value) {
    router.push('/login')
    return
  }

  likeLoading.value = true

  try {
    if (isLiked.value) {
      await postService.unlikePost(post.value.slug)
      post.value.like_count = Math.max(0, (post.value.like_count || 0) - 1)
    } else {
      await postService.likePost(post.value.slug)
      post.value.like_count = (post.value.like_count || 0) + 1
    }
    isLiked.value = !isLiked.value
  } catch (err) {
    console.error('Like error:', err)
  } finally {
    likeLoading.value = false
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return

  commentLoading.value = true

  try {
    const response = await postService.createComment(post.value.slug, {
      content: newComment.value.trim()
    })

    // Add the new comment to the comments list
    const newCommentData = response.data || response.comment
    if (newCommentData) {
      comments.value.unshift({
        ...newCommentData,
        user: {
          name: authStore.user?.name || 'Anonymous'
        }
      })

      // Update comment count
      post.value.comment_count = (post.value.comment_count || 0) + 1
    }

    // Clear the comment form
    newComment.value = ''
  } catch (err) {
    console.error('Submit comment error:', err)

    // Show user-friendly error message
    const errorMessage = err.response?.data?.message ||
                      err.response?.data?.errors?.content?.[0] ||
                      'Failed to post comment. Please try again.'

    // You could add a toast notification here
    alert(errorMessage)
  } finally {
    commentLoading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchPost()
})
</script>
<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-3xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Profile Settings</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">
            Update your personal information and account settings.
          </p>
        </div>

        <div v-if="error" class="mx-6 mt-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
          {{ error }}
        </div>

        <div v-if="success" class="mx-6 mt-4 bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-md">
          Profile updated successfully!
        </div>

        <div class="border-t border-gray-200">
          <form @submit.prevent="handleUpdateProfile" class="px-4 py-5 sm:p-6">
            <div class="grid grid-cols-6 gap-6">
              <div class="col-span-6 sm:col-span-3">
                <label for="name" class="block text-sm font-medium text-gray-700">Full Name</label>
                <input
                  type="text"
                  id="name"
                  v-model="form.name"
                  class="input-field mt-1"
                  required
                >
              </div>

              <div class="col-span-6 sm:col-span-3">
                <label for="email" class="block text-sm font-medium text-gray-700">Email Address</label>
                <input
                  type="email"
                  id="email"
                  v-model="form.email"
                  class="input-field mt-1"
                  required
                >
              </div>

              <div class="col-span-6 sm:col-span-3">
                <label for="new_password" class="block text-sm font-medium text-gray-700">New Password (optional)</label>
                <input
                  type="password"
                  id="new_password"
                  v-model="form.password"
                  class="input-field mt-1"
                  placeholder="Leave blank to keep current password"
                >
              </div>

              <div class="col-span-6 sm:col-span-3">
                <label for="password_confirmation" class="block text-sm font-medium text-gray-700">Confirm New Password</label>
                <input
                  type="password"
                  id="password_confirmation"
                  v-model="form.password_confirmation"
                  class="input-field mt-1"
                  placeholder="Confirm new password"
                >
              </div>
            </div>

            <div class="mt-6">
              <button
                type="submit"
                :disabled="isLoading || (form.password && passwordMismatch)"
                class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="isLoading" class="mr-2">
                  <svg class="animate-spin h-4 w-4 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </span>
                {{ isLoading ? 'Updating...' : 'Update Profile' }}
              </button>
            </div>
          </form>
        </div>

        <div class="border-t border-gray-200 px-4 py-5 sm:p-6">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-lg leading-6 font-medium text-gray-900">Danger Zone</h3>
              <p class="mt-1 max-w-2xl text-sm text-gray-500">
                Permanently delete your account and all associated data.
              </p>
            </div>
            <button
              @click="handleLogout"
              class="btn btn-secondary"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      <div class="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Account Statistics</h3>
        </div>
        <div class="border-t border-gray-200">
          <dl>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Total Posts</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ stats.posts }}</dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Total Comments</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ stats.comments }}</dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Account Created</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ formattedDate }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  name: '',
  email: '',
  password: '',
  password_confirmation: ''
})

const success = ref(false)
const stats = ref({
  posts: 0,
  comments: 0
})

const isLoading = computed(() => authStore.isLoading)
const error = computed(() => authStore.error)

const passwordMismatch = computed(() => {
  return form.value.password && form.value.password_confirmation &&
         form.value.password !== form.value.password_confirmation
})

const formattedDate = computed(() => {
  if (authStore.user?.created_at) {
    return new Date(authStore.user.created_at).toLocaleDateString()
  }
  return 'Unknown'
})

const handleUpdateProfile = async () => {
  if (passwordMismatch.value) return

  const updateData = {
    name: form.value.name,
    email: form.value.email
  }

  if (form.value.password) {
    updateData.password = form.value.password
    updateData.password_confirmation = form.value.password_confirmation
  }

  const result = await authStore.updateProfile(updateData)

  if (result.success) {
    success.value = true
    // Reset password fields
    form.value.password = ''
    form.value.password_confirmation = ''

    setTimeout(() => {
      success.value = false
    }, 3000)
  }
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  // Initialize form with current user data
  if (authStore.user) {
    form.value.name = authStore.user.name || ''
    form.value.email = authStore.user.email || ''
  }

  // Fetch user stats (mock data for now)
  stats.value = {
    posts: Math.floor(Math.random() * 20) + 5,
    comments: Math.floor(Math.random() * 50) + 10
  }
})
</script>
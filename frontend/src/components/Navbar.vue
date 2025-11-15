<template>
  <nav class="bg-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Logo and main navigation -->
        <div class="flex items-center">
          <router-link to="/" class="flex-shrink-0 flex items-center">
            <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
              <span class="text-white font-bold text-sm">ML</span>
            </div>
            <span class="text-xl font-bold text-gray-900">BlogML</span>
          </router-link>

          <div class="hidden md:ml-10 md:flex md:space-x-8">
            <router-link
              to="/"
              class="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
            >
              Home
            </router-link>
            <router-link
              to="/posts"
              class="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
            >
              Posts
            </router-link>
          </div>
        </div>

        <!-- Right side buttons -->
        <div class="flex items-center">
          <div v-if="isAuthenticated" class="flex items-center space-x-4">
            <!-- Create Post Button -->
            <router-link
              to="/posts/create"
              class="btn btn-primary"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
              New Post
            </router-link>

            <!-- User Menu -->
            <div class="relative" ref="userMenuRef">
              <button
                @click="toggleUserMenu"
                class="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span class="text-sm font-medium text-gray-600">
                    {{ userName?.charAt(0)?.toUpperCase() || 'U' }}
                  </span>
                </div>
              </button>

              <!-- Dropdown Menu -->
              <div
                v-if="showUserMenu"
                class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
              >
                <div class="py-1">
                  <div class="px-4 py-2 text-sm text-gray-700 border-b">
                    <div class="font-medium">{{ userName }}</div>
                    <div class="text-gray-500 truncate">{{ userEmail }}</div>
                  </div>
                  <router-link
                    to="/profile"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    @click="closeUserMenu"
                  >
                    Profile
                  </router-link>
                  <router-link
                    v-if="isAdmin"
                    to="/admin"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    @click="closeUserMenu"
                  >
                    Admin Panel
                  </router-link>
                  <button
                    @click="handleLogout"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Login/Register buttons for guests -->
          <div v-else class="flex items-center space-x-4">
            <router-link
              to="/login"
              class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
            >
              Login
            </router-link>
            <router-link
              to="/register"
              class="btn btn-primary"
            >
              Sign Up
            </router-link>
          </div>

          <!-- Mobile menu button -->
          <div class="md:hidden">
            <button
              @click="toggleMobileMenu"
              class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path v-if="!showMobileMenu" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile menu -->
      <div v-if="showMobileMenu" class="md:hidden">
        <div class="pt-2 pb-3 space-y-1">
          <router-link
            to="/"
            class="block pl-3 pr-4 py-2 text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50"
            @click="closeMobileMenu"
          >
            Home
          </router-link>
          <router-link
            to="/posts"
            class="block pl-3 pr-4 py-2 text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50"
            @click="closeMobileMenu"
          >
            Posts
          </router-link>

          <div v-if="isAuthenticated" class="border-t border-gray-200 pt-4">
            <div class="px-4 py-2 text-sm text-gray-700">
              <div class="font-medium">{{ userName }}</div>
              <div class="text-gray-500 truncate">{{ userEmail }}</div>
            </div>
            <router-link
              to="/profile"
              class="block pl-3 pr-4 py-2 text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50"
              @click="closeMobileMenu"
            >
              Profile
            </router-link>
            <router-link
              v-if="isAdmin"
              to="/admin"
              class="block pl-3 pr-4 py-2 text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50"
              @click="closeMobileMenu"
            >
              Admin Panel
            </router-link>
            <button
              @click="handleLogout"
              class="block w-full text-left pl-3 pr-4 py-2 text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50"
            >
              Logout
            </button>
          </div>

          <div v-else class="border-t border-gray-200 pt-4">
            <router-link
              to="/login"
              class="block pl-3 pr-4 py-2 text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50"
              @click="closeMobileMenu"
            >
              Login
            </router-link>
            <router-link
              to="/register"
              class="block pl-3 pr-4 py-2 text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50"
              @click="closeMobileMenu"
            >
              Sign Up
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const userMenuRef = ref(null)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const userName = computed(() => authStore.userName)
const userEmail = computed(() => authStore.userEmail)
const isAdmin = computed(() => authStore.user?.email === 'admin@techblog.com') // Simple admin check

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const closeUserMenu = () => {
  showUserMenu.value = false
}

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const closeMobileMenu = () => {
  showMobileMenu.value = false
}

const handleLogout = async () => {
  await authStore.logout()
  closeUserMenu()
  closeMobileMenu()
  router.push('/')
}

// Close user menu when clicking outside
const handleClickOutside = (event) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
    closeUserMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
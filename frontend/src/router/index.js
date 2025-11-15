import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Components
import PostsView from '../views/PostsView.vue'
import PostDetailView from '../views/PostDetailView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileView from '../views/ProfileView.vue'
import CreatePostView from '../views/CreatePostView.vue'

const routes = [
  {
    path: '/',
    name: 'Posts',
    component: PostsView,
    meta: { title: 'BlogML - Home' }
  },
  {
    path: '/posts',
    name: 'PostsList',
    component: PostsView,
    meta: { title: 'BlogML - Posts' }
  },
  {
    path: '/posts/:slug',
    name: 'PostDetail',
    component: PostDetailView,
    meta: { title: 'BlogML - Post' }
  },
  {
    path: '/posts/create',
    name: 'CreatePost',
    component: CreatePostView,
    meta: { requiresAuth: true, title: 'BlogML - Create Post' }
  },
  {
    path: '/posts/:slug/edit',
    name: 'EditPost',
    component: CreatePostView, // Reuse create component for editing
    meta: { requiresAuth: true, title: 'BlogML - Edit Post' }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { guest: true, title: 'BlogML - Login' }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { guest: true, title: 'BlogML - Register' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true, title: 'BlogML - Profile' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue'),
    meta: { title: 'BlogML - Not Found' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Update page title
  if (to.meta.title) {
    document.title = to.meta.title
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // Check if route is for guests only
  if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'Posts' })
    return
  }

  next()
})

export default router
import api from './api'

export const postService = {
  async getPosts(params = {}) {
    const response = await api.get('/posts', { params })
    return response.data
  },

  async getPost(slug) {
    const response = await api.get(`/posts/${slug}`)
    return response.data
  },

  async createPost(postData) {
    const response = await api.post('/posts', postData)
    return response.data
  },

  async updatePost(slug, postData) {
    const response = await api.put(`/posts/${slug}`, postData)
    return response.data
  },

  async deletePost(slug) {
    const response = await api.delete(`/posts/${slug}`)
    return response.data
  },

  async likePost(slug) {
    const response = await api.post(`/posts/${slug}/like`)
    return response.data
  },

  async unlikePost(slug) {
    const response = await api.delete(`/posts/${slug}/like`)
    return response.data
  },

  async viewPost(slug) {
    const response = await api.post(`/posts/${slug}/view`)
    return response.data
  },

  async getUserPosts() {
    const response = await api.get('/user/posts')
    return response.data
  },

  async getPostComments(slug) {
    const response = await api.get(`/posts/${slug}/comments`)
    return response.data
  },

  async createComment(slug, commentData) {
    const response = await api.post(`/posts/${slug}/comments`, commentData)
    return response.data
  }
}
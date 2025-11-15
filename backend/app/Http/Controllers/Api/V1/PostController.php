<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Models\Post;
use App\Models\UserInteraction;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;

class PostController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request): JsonResponse
    {
        $query = Post::with(['user:id,name,email', 'tags:id,name', 'approvedComments' => function ($query) {
            $query->select('id', 'post_id', 'user_id', 'content', 'created_at')
                  ->with('user:id,name')
                  ->latest()
                  ->take(3);
        }]);

        // Filter by status
        if ($request->filled('status')) {
            $query->where('status', $request->status);
        } else {
            // By default, only show published posts
            $query->published();
        }

        // Filter by author
        if ($request->filled('author_id')) {
            $query->where('user_id', $request->author_id);
        }

        // Filter by tags
        if ($request->filled('tags')) {
            $tagIds = explode(',', $request->tags);
            $query->whereHas('tags', function ($q) use ($tagIds) {
                $q->whereIn('tags.id', $tagIds);
            });
        }

        // Search
        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('title', 'like', "%{$search}%")
                  ->orWhere('content', 'like', "%{$search}%")
                  ->orWhere('excerpt', 'like', "%{$search}%");
            });
        }

        // Filter by AI generated
        if ($request->filled('is_ai_generated')) {
            $query->where('is_ai_generated', $request->boolean('is_ai_generated'));
        }

        // Sort
        $sortBy = $request->get('sort_by', 'published_at');
        $sortOrder = $request->get('sort_order', 'desc');

        if (in_array($sortBy, ['view_count', 'like_count', 'comment_count'])) {
            $query->orderBy($sortBy, $sortOrder);
        } else {
            $query->orderBy($sortBy === 'trending_score' ? 'published_at' : $sortBy, $sortOrder);
        }

        // Paginate
        $perPage = min($request->get('per_page', 15), 50);
        $posts = $query->paginate($perPage);

        return response()->json([
            'posts' => $posts->items(),
            'pagination' => [
                'total' => $posts->total(),
                'per_page' => $posts->perPage(),
                'current_page' => $posts->currentPage(),
                'last_page' => $posts->lastPage(),
                'has_more_pages' => $posts->hasMorePages(),
            ],
        ]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'title' => 'required|string|max:255',
            'content' => 'required|string',
            'excerpt' => 'nullable|string|max:500',
            'status' => ['nullable', Rule::in(['draft', 'published', 'archived'])],
            'featured_image' => 'nullable|url',
            'meta_title' => 'nullable|string|max:255',
            'meta_description' => 'nullable|string|max:500',
            'tags' => 'nullable|array',
            'tags.*' => 'exists:tags,id',
            'is_ai_generated' => 'nullable|boolean',
        ]);

        if ($validator->fails()) {
            return response()->json([
                'message' => 'Validation failed',
                'errors' => $validator->errors()
            ], 422);
        }

        $data = $validator->validated();
        $data['user_id'] = Auth::id();

        // Auto-generate excerpt if not provided
        if (empty($data['excerpt'])) {
            $data['excerpt'] = Str::limit(strip_tags($data['content']), 200);
        }

        // Set status and published_at
        if ($data['status'] === 'published' && !isset($data['published_at'])) {
            $data['published_at'] = now();
        }

        DB::beginTransaction();
        try {
            $post = Post::create($data);

            // Attach tags
            if (!empty($data['tags'])) {
                $post->tags()->attach($data['tags']);
            }

            // Auto-generate meta data if not provided
            if (empty($data['meta_title'])) {
                $post->meta_title = $post->title;
                $post->save();
            }

            if (empty($data['meta_description'])) {
                $post->meta_description = $post->excerpt;
                $post->save();
            }

            DB::commit();

            return response()->json([
                'message' => 'Post created successfully',
                'post' => $post->load(['user:id,name', 'tags:id,name'])
            ], 201);

        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json([
                'message' => 'Failed to create post',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display the specified resource.
     */
    public function show(string $slug): JsonResponse
    {
        $post = Post::with([
            'user:id,name,email,created_at',
            'tags:id,name',
            'approvedComments' => function ($query) {
                $query->with('user:id,name')
                      ->latest();
            }
        ])->where('slug', $slug)->first();

        if (!$post) {
            return response()->json([
                'message' => 'Post not found'
            ], 404);
        }

        // Only show published posts to non-authors and non-admins
        if ($post->status !== 'published') {
            if (!Auth::check() || (Auth::id() !== $post->user_id && !Auth::user()->is_admin)) {
                return response()->json([
                    'message' => 'Post not found'
                ], 404);
            }
        }

        return response()->json([
            'post' => $post,
            'sentiment_distribution' => $post->sentiment_distribution,
            'average_sentiment' => $post->average_sentiment
        ]);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $slug): JsonResponse
    {
        $post = Post::where('slug', $slug)->first();

        if (!$post) {
            return response()->json([
                'message' => 'Post not found'
            ], 404);
        }

        // Check authorization
        if (Auth::id() !== $post->user_id && !Auth::user()->is_admin) {
            return response()->json([
                'message' => 'Unauthorized'
            ], 403);
        }

        $validator = Validator::make($request->all(), [
            'title' => 'sometimes|required|string|max:255',
            'content' => 'sometimes|required|string',
            'excerpt' => 'nullable|string|max:500',
            'status' => ['nullable', Rule::in(['draft', 'published', 'archived'])],
            'featured_image' => 'nullable|url',
            'meta_title' => 'nullable|string|max:255',
            'meta_description' => 'nullable|string|max:500',
            'tags' => 'nullable|array',
            'tags.*' => 'exists:tags,id',
            'is_ai_generated' => 'nullable|boolean',
        ]);

        if ($validator->fails()) {
            return response()->json([
                'message' => 'Validation failed',
                'errors' => $validator->errors()
            ], 422);
        }

        $data = $validator->validated();

        DB::beginTransaction();
        try {
            // Handle status changes
            if (isset($data['status'])) {
                if ($data['status'] === 'published' && $post->status !== 'published') {
                    $data['published_at'] = now();
                }
            }

            $post->update($data);

            // Update tags if provided
            if (array_key_exists('tags', $data)) {
                if ($data['tags']) {
                    $post->tags()->sync($data['tags']);
                } else {
                    $post->tags()->detach();
                }
            }

            DB::commit();

            return response()->json([
                'message' => 'Post updated successfully',
                'post' => $post->load(['user:id,name', 'tags:id,name'])
            ]);

        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json([
                'message' => 'Failed to update post',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $slug): JsonResponse
    {
        $post = Post::where('slug', $slug)->first();

        if (!$post) {
            return response()->json([
                'message' => 'Post not found'
            ], 404);
        }

        // Check authorization
        if (Auth::id() !== $post->user_id && !Auth::user()->is_admin) {
            return response()->json([
                'message' => 'Unauthorized'
            ], 403);
        }

        try {
            $post->delete();

            return response()->json([
                'message' => 'Post deleted successfully'
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Failed to delete post',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Like a post.
     */
    public function like(string $slug): JsonResponse
    {
        $post = Post::where('slug', $slug)->first();

        if (!$post) {
            return response()->json([
                'message' => 'Post not found'
            ], 404);
        }

        $user = Auth::user();

        // Check if already liked
        $existingLike = UserInteraction::where('user_id', $user->id)
            ->where('post_id', $post->id)
            ->where('interaction_type', UserInteraction::TYPE_LIKE)
            ->first();

        if ($existingLike) {
            return response()->json([
                'message' => 'Post already liked'
            ], 400);
        }

        // Create like interaction
        UserInteraction::create([
            'user_id' => $user->id,
            'post_id' => $post->id,
            'interaction_type' => UserInteraction::TYPE_LIKE,
        ]);

        return response()->json([
            'message' => 'Post liked successfully',
            'like_count' => $post->like_count
        ]);
    }

    /**
     * Unlike a post.
     */
    public function unlike(string $slug): JsonResponse
    {
        $post = Post::where('slug', $slug)->first();

        if (!$post) {
            return response()->json([
                'message' => 'Post not found'
            ], 404);
        }

        $user = Auth::user();

        // Find and remove like
        $like = UserInteraction::where('user_id', $user->id)
            ->where('post_id', $post->id)
            ->where('interaction_type', UserInteraction::TYPE_LIKE)
            ->first();

        if (!$like) {
            return response()->json([
                'message' => 'Post not liked'
            ], 400);
        }

        $like->delete();

        return response()->json([
            'message' => 'Post unliked successfully',
            'like_count' => $post->like_count
        ]);
    }

    /**
     * View a post (record view interaction).
     */
    public function view(string $slug): JsonResponse
    {
        $post = Post::where('slug', $slug)->first();

        if (!$post) {
            return response()->json([
                'message' => 'Post not found'
            ], 404);
        }

        $user = Auth::user();

        // Only record view if it's a published post
        if ($post->status === 'published') {
            // Check if user has viewed this post in the last hour
            $recentView = UserInteraction::where('user_id', $user->id)
                ->where('post_id', $post->id)
                ->where('interaction_type', UserInteraction::TYPE_VIEW)
                ->where('created_at', '>', now()->subHour())
                ->first();

            if (!$recentView) {
                UserInteraction::create([
                    'user_id' => $user->id,
                    'post_id' => $post->id,
                    'interaction_type' => UserInteraction::TYPE_VIEW,
                ]);
            }
        }

        return response()->json([
            'message' => 'View recorded successfully',
            'view_count' => $post->view_count
        ]);
    }

    /**
     * Bookmark a post.
     */
    public function bookmark(string $slug): JsonResponse
    {
        $post = Post::where('slug', $slug)->first();

        if (!$post) {
            return response()->json([
                'message' => 'Post not found'
            ], 404);
        }

        $user = Auth::user();

        // Check if already bookmarked
        $existingBookmark = UserInteraction::where('user_id', $user->id)
            ->where('post_id', $post->id)
            ->where('interaction_type', UserInteraction::TYPE_BOOKMARK)
            ->first();

        if ($existingBookmark) {
            return response()->json([
                'message' => 'Post already bookmarked'
            ], 400);
        }

        // Create bookmark interaction
        UserInteraction::create([
            'user_id' => $user->id,
            'post_id' => $post->id,
            'interaction_type' => UserInteraction::TYPE_BOOKMARK,
        ]);

        return response()->json([
            'message' => 'Post bookmarked successfully'
        ]);
    }

    /**
     * Get authenticated user's posts.
     */
    public function userPosts(Request $request): JsonResponse
    {
        $user = Auth::user();

        $query = Post::where('user_id', $user->id)
            ->with(['tags:id,name']);

        // Filter by status
        if ($request->filled('status')) {
            $query->where('status', $request->status);
        }

        // Sort
        $sortBy = $request->get('sort_by', 'created_at');
        $sortOrder = $request->get('sort_order', 'desc');
        $query->orderBy($sortBy, $sortOrder);

        // Paginate
        $perPage = min($request->get('per_page', 15), 50);
        $posts = $query->paginate($perPage);

        return response()->json([
            'posts' => $posts->items(),
            'pagination' => [
                'total' => $posts->total(),
                'per_page' => $posts->perPage(),
                'current_page' => $posts->currentPage(),
                'last_page' => $posts->lastPage(),
            ],
        ]);
    }

    /**
     * Get authenticated user's interactions.
     */
    public function userInteractions(Request $request): JsonResponse
    {
        $user = Auth::user();

        $query = UserInteraction::where('user_id', $user->id)
            ->with(['post:id,title,slug,excerpt,featured_image,user_id'])
            ->with('post.user:id,name');

        // Filter by interaction type
        if ($request->filled('type')) {
            $query->where('interaction_type', $request->type);
        }

        // Sort
        $query->latest();

        // Paginate
        $perPage = min($request->get('per_page', 20), 50);
        $interactions = $query->paginate($perPage);

        return response()->json([
            'interactions' => $interactions->items(),
            'pagination' => [
                'total' => $interactions->total(),
                'per_page' => $interactions->perPage(),
                'current_page' => $interactions->currentPage(),
                'last_page' => $interactions->lastPage(),
            ],
        ]);
    }

    /**
     * Admin: Get all posts with admin filters.
     */
    public function adminIndex(Request $request): JsonResponse
    {
        $this->authorize('admin', Post::class);

        $query = Post::with(['user:id,name,email', 'tags:id,name']);

        // Admin can filter by any status
        if ($request->filled('status')) {
            $query->where('status', $request->status);
        }

        // Filter by author
        if ($request->filled('author_id')) {
            $query->where('user_id', $request->author_id);
        }

        // Filter by AI generated
        if ($request->filled('is_ai_generated')) {
            $query->where('is_ai_generated', $request->boolean('is_ai_generated'));
        }

        // Search
        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('title', 'like', "%{$search}%")
                  ->orWhere('content', 'like', "%{$search}%")
                  ->orWhere('excerpt', 'like', "%{$search}%");
            });
        }

        // Sort
        $sortBy = $request->get('sort_by', 'created_at');
        $sortOrder = $request->get('sort_order', 'desc');
        $query->orderBy($sortBy, $sortOrder);

        // Paginate
        $perPage = min($request->get('per_page', 20), 100);
        $posts = $query->paginate($perPage);

        return response()->json([
            'posts' => $posts->items(),
            'pagination' => [
                'total' => $posts->total(),
                'per_page' => $posts->perPage(),
                'current_page' => $posts->currentPage(),
                'last_page' => $posts->lastPage(),
            ],
        ]);
    }

    /**
     * Admin: Update post status.
     */
    public function updateStatus(Request $request, string $slug): JsonResponse
    {
        $this->authorize('admin', Post::class);

        $post = Post::where('slug', $slug)->first();

        if (!$post) {
            return response()->json([
                'message' => 'Post not found'
            ], 404);
        }

        $validator = Validator::make($request->all(), [
            'status' => ['required', Rule::in(['draft', 'published', 'archived'])],
        ]);

        if ($validator->fails()) {
            return response()->json([
                'message' => 'Validation failed',
                'errors' => $validator->errors()
            ], 422);
        }

        $data = $validator->validated();

        // Handle publishing
        if ($data['status'] === 'published' && $post->status !== 'published') {
            $data['published_at'] = now();
        }

        $post->update($data);

        return response()->json([
            'message' => 'Post status updated successfully',
            'post' => $post->load(['user:id,name', 'tags:id,name'])
        ]);
    }

    /**
     * Generate AI-powered outline for a post.
     */
    public function generateOutline(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'topic' => 'required|string|max:255',
            'keywords' => 'nullable|array',
            'keywords.*' => 'string|max:100',
            'tone' => 'nullable|string|in:professional,casual,academic,friendly',
            'length' => 'nullable|string|in:short,medium,long',
        ]);

        if ($validator->fails()) {
            return response()->json([
                'message' => 'Validation failed',
                'errors' => $validator->errors()
            ], 422);
        }

        $data = $validator->validated();

        try {
            // This would integrate with your ML service
            // For now, we'll return a mock response
            $outline = [
                'title' => $data['topic'],
                'introduction' => 'Introduction to ' . $data['topic'],
                'sections' => [
                    [
                        'heading' => 'Understanding ' . $data['topic'],
                        'points' => ['Definition', 'Importance', 'Key concepts']
                    ],
                    [
                        'heading' => 'Benefits and Applications',
                        'points' => ['Primary benefits', 'Real-world applications', 'Case studies']
                    ],
                    [
                        'heading' => 'Conclusion',
                        'points' => ['Summary', 'Future outlook', 'Call to action']
                    ]
                ],
                'estimated_reading_time' => 5,
                'suggested_tags' => ['technology', 'innovation', 'trends']
            ];

            return response()->json([
                'message' => 'Outline generated successfully',
                'outline' => $outline
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Failed to generate outline',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Generate AI-powered post content.
     */
    public function generatePost(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'outline' => 'required|array',
            'tone' => 'nullable|string|in:professional,casual,academic,friendly',
            'word_count' => 'nullable|integer|min:300|max:3000',
        ]);

        if ($validator->fails()) {
            return response()->json([
                'message' => 'Validation failed',
                'errors' => $validator->errors()
            ], 422);
        }

        $data = $validator->validated();

        try {
            // This would integrate with your ML service
            // For now, we'll return a mock response
            $content = "This is an AI-generated blog post based on the provided outline.
                        In a real implementation, this would call your ML service to generate
                        comprehensive content based on the outline sections and specified tone.";

            $excerpt = Str::limit(strip_tags($content), 200);

            return response()->json([
                'message' => 'Post generated successfully',
                'content' => $content,
                'excerpt' => $excerpt,
                'estimated_reading_time' => ceil(str_word_count($content) / 200)
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Failed to generate post',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}

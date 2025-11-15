<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Models\Comment;
use App\Models\Post;
use App\Models\UserInteraction;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;

class CommentController extends Controller
{
    /**
     * Display comments for a specific post.
     */
    public function index(Request $request, string $postSlug): JsonResponse
    {
        $post = Post::where('slug', $postSlug)->first();

        if (!$post) {
            return response()->json([
                'message' => 'Post not found'
            ], 404);
        }

        // Only allow comments on published posts for non-authors/admins
        if ($post->status !== 'published') {
            if (!Auth::check() || (Auth::id() !== $post->user_id && !Auth::user()->is_admin)) {
                return response()->json([
                    'message' => 'Post not found'
                ], 404);
            }
        }

        $query = Comment::with(['user:id,name', 'approvedReplies' => function ($query) {
            $query->with('user:id,name')
                  ->latest()
                  ->take(5);
        }])
        ->where('post_id', $post->id);

        // Default to top-level comments only (no parent)
        if (!$request->boolean('include_replies', false)) {
            $query->topLevel();
        }

        // Filter by status (only show approved comments to public)
        if (Auth::check() && (Auth::id() === $post->user_id || Auth::user()->is_admin)) {
            // Authors and admins can see all comment statuses
            if ($request->filled('status')) {
                $query->where('status', $request->status);
            }
        } else {
            // Public users only see approved comments
            $query->approved();
        }

        // Filter by sentiment
        if ($request->filled('sentiment')) {
            $query->withSentiment($request->sentiment);
        }

        // Sort
        $sortBy = $request->get('sort_by', 'created_at');
        $sortOrder = $request->get('sort_order', 'desc');
        $query->orderBy($sortBy, $sortOrder);

        // Paginate
        $perPage = min($request->get('per_page', 20), 100);
        $comments = $query->paginate($perPage);

        return response()->json([
            'comments' => $comments->items(),
            'pagination' => [
                'total' => $comments->total(),
                'per_page' => $comments->perPage(),
                'current_page' => $comments->currentPage(),
                'last_page' => $comments->lastPage(),
                'has_more_pages' => $comments->hasMorePages(),
            ],
            'stats' => [
                'total_comments' => Comment::where('post_id', $post->id)->count(),
                'approved_comments' => Comment::where('post_id', $post->id)->approved()->count(),
                'pending_comments' => Comment::where('post_id', $post->id)->pending()->count(),
            ]
        ]);
    }

    /**
     * Store a newly created comment in storage.
     */
    public function store(Request $request, string $postSlug): JsonResponse
    {
        $post = Post::where('slug', $postSlug)->first();

        if (!$post) {
            return response()->json([
                'message' => 'Post not found'
            ], 404);
        }

        // Only allow commenting on published posts
        if ($post->status !== 'published') {
            return response()->json([
                'message' => 'Comments are only allowed on published posts'
            ], 403);
        }

        $validator = Validator::make($request->all(), [
            'content' => 'required|string|min:3|max:2000',
            'parent_id' => 'nullable|exists:comments,id',
        ]);

        if ($validator->fails()) {
            return response()->json([
                'message' => 'Validation failed',
                'errors' => $validator->errors()
            ], 422);
        }

        $data = $validator->validated();

        // Validate parent comment belongs to the same post
        if (!empty($data['parent_id'])) {
            $parentComment = Comment::find($data['parent_id']);
            if (!$parentComment || $parentComment->post_id !== $post->id) {
                return response()->json([
                    'message' => 'Invalid parent comment'
                ], 422);
            }
        }

        // Check if user has already commented recently (spam prevention)
        $recentComment = Comment::where('user_id', Auth::id())
            ->where('post_id', $post->id)
            ->where('created_at', '>', now()->subMinutes(5))
            ->first();

        if ($recentComment) {
            return response()->json([
                'message' => 'Please wait a few minutes before posting another comment'
            ], 429);
        }

        DB::beginTransaction();
        try {
            $comment = Comment::create([
                'post_id' => $post->id,
                'user_id' => Auth::id(),
                'content' => $data['content'],
                'parent_id' => $data['parent_id'] ?? null,
                'status' => Comment::STATUS_APPROVED, // Auto-approve for now
            ]);

            // Create comment interaction for user tracking
            UserInteraction::create([
                'user_id' => Auth::id(),
                'post_id' => $post->id,
                'interaction_type' => UserInteraction::TYPE_COMMENT,
                'metadata' => [
                    'comment_id' => $comment->id,
                    'word_count' => $comment->word_count,
                ]
            ]);

            // TODO: Integrate with ML service for sentiment analysis
            // For now, set neutral sentiment
            $comment->update([
                'sentiment_score' => 0.5,
                'sentiment_label' => Comment::SENTIMENT_NEUTRAL,
                'sentiment_confidence' => 0.8,
            ]);

            DB::commit();

            return response()->json([
                'message' => 'Comment created successfully',
                'comment' => $comment->load(['user:id,name', 'post:id,title,slug'])
            ], 201);

        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json([
                'message' => 'Failed to create comment',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display the specified comment.
     */
    public function show(string $id): JsonResponse
    {
        $comment = Comment::with([
            'user:id,name,email,created_at',
            'post:id,title,slug,user_id',
            'post.user:id,name',
            'parent:id,content,user_id',
            'parent.user:id,name',
            'approvedReplies' => function ($query) {
                $query->with('user:id,name')
                      ->latest();
            }
        ])->find($id);

        if (!$comment) {
            return response()->json([
                'message' => 'Comment not found'
            ], 404);
        }

        // Check permissions
        $isAuthor = Auth::check() && Auth::id() === $comment->user_id;
        $isPostAuthor = Auth::check() && Auth::id() === $comment->post->user_id;
        $isAdmin = Auth::check() && Auth::user()->is_admin;
        $isApprovedComment = $comment->status === Comment::STATUS_APPROVED;

        if (!$isApprovedComment && !$isAuthor && !$isPostAuthor && !$isAdmin) {
            return response()->json([
                'message' => 'Comment not found'
            ], 404);
        }

        return response()->json([
            'comment' => $comment,
            'permissions' => [
                'can_edit' => $isAuthor,
                'can_delete' => $isAuthor || $isPostAuthor || $isAdmin,
                'can_moderate' => $isPostAuthor || $isAdmin,
            ]
        ]);
    }

    /**
     * Update the specified comment.
     */
    public function update(Request $request, string $id): JsonResponse
    {
        $comment = Comment::find($id);

        if (!$comment) {
            return response()->json([
                'message' => 'Comment not found'
            ], 404);
        }

        // Check authorization - only comment author can edit
        if (Auth::id() !== $comment->user_id) {
            return response()->json([
                'message' => 'Unauthorized'
            ], 403);
        }

        // Only allow editing within 30 minutes of creation
        if ($comment->created_at->diffInMinutes(now()) > 30) {
            return response()->json([
                'message' => 'Comments can only be edited within 30 minutes of posting'
            ], 403);
        }

        $validator = Validator::make($request->all(), [
            'content' => 'required|string|min:3|max:2000',
        ]);

        if ($validator->fails()) {
            return response()->json([
                'message' => 'Validation failed',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $comment->update([
                'content' => $request->content,
                'is_edited' => true,
                'edited_at' => now(),
            ]);

            return response()->json([
                'message' => 'Comment updated successfully',
                'comment' => $comment->load(['user:id,name', 'post:id,title,slug'])
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Failed to update comment',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Remove the specified comment.
     */
    public function destroy(string $id): JsonResponse
    {
        $comment = Comment::with('post')->find($id);

        if (!$comment) {
            return response()->json([
                'message' => 'Comment not found'
            ], 404);
        }

        $isAuthor = Auth::id() === $comment->user_id;
        $isPostAuthor = Auth::check() && Auth::id() === $comment->post->user_id;
        $isAdmin = Auth::check() && Auth::user()->is_admin;

        // Check authorization
        if (!$isAuthor && !$isPostAuthor && !$isAdmin) {
            return response()->json([
                'message' => 'Unauthorized'
            ], 403);
        }

        try {
            // Soft delete by updating status instead of hard delete
            if ($isAuthor && !$isPostAuthor && !$isAdmin) {
                // Authors can only mark as deleted, not permanently remove
                $comment->update([
                    'status' => Comment::STATUS_REJECTED,
                    'content' => '[Comment deleted by author]'
                ]);
            } else {
                // Post authors and admins can permanently delete
                $comment->delete();
            }

            return response()->json([
                'message' => 'Comment deleted successfully'
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Failed to delete comment',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get authenticated user's comments.
     */
    public function userComments(Request $request): JsonResponse
    {
        $user = Auth::user();

        $query = Comment::where('user_id', $user->id)
            ->with(['post:id,title,slug,featured_image,user_id'])
            ->with('post.user:id,name');

        // Filter by status
        if ($request->filled('status')) {
            $query->where('status', $request->status);
        }

        // Filter by sentiment
        if ($request->filled('sentiment')) {
            $query->withSentiment($request->sentiment);
        }

        // Include replies or only top-level comments
        if (!$request->boolean('include_replies', true)) {
            $query->topLevel();
        }

        // Sort
        $sortBy = $request->get('sort_by', 'created_at');
        $sortOrder = $request->get('sort_order', 'desc');
        $query->orderBy($sortBy, $sortOrder);

        // Paginate
        $perPage = min($request->get('per_page', 20), 50);
        $comments = $query->paginate($perPage);

        return response()->json([
            'comments' => $comments->items(),
            'pagination' => [
                'total' => $comments->total(),
                'per_page' => $comments->perPage(),
                'current_page' => $comments->currentPage(),
                'last_page' => $comments->lastPage(),
            ],
            'stats' => [
                'total_comments' => Comment::where('user_id', $user->id)->count(),
                'approved_comments' => Comment::where('user_id', $user->id)->approved()->count(),
                'pending_comments' => Comment::where('user_id', $user->id)->pending()->count(),
                'total_words' => Comment::where('user_id', $user->id)->get()->sum('word_count'),
            ]
        ]);
    }

    /**
     * Admin: Get all comments with admin filters.
     */
    public function adminIndex(Request $request): JsonResponse
    {
        $this->authorize('admin', Comment::class);

        $query = Comment::with([
            'user:id,name,email',
            'post:id,title,slug,user_id',
            'post.user:id,name'
        ]);

        // Filter by status
        if ($request->filled('status')) {
            $query->where('status', $request->status);
        }

        // Filter by sentiment
        if ($request->filled('sentiment')) {
            $query->withSentiment($request->sentiment);
        }

        // Filter by user
        if ($request->filled('user_id')) {
            $query->where('user_id', $request->user_id);
        }

        // Filter by post
        if ($request->filled('post_id')) {
            $query->where('post_id', $request->post_id);
        }

        // Search content
        if ($request->filled('search')) {
            $search = $request->search;
            $query->where('content', 'like', "%{$search}%");
        }

        // Filter by confidence level
        if ($request->filled('min_confidence')) {
            $query->where('sentiment_confidence', '>=', $request->min_confidence);
        }

        // Include only replies or top-level
        if ($request->filled('parent_id')) {
            if ($request->parent_id === 'null') {
                $query->topLevel();
            } else {
                $query->where('parent_id', $request->parent_id);
            }
        }

        // Sort
        $sortBy = $request->get('sort_by', 'created_at');
        $sortOrder = $request->get('sort_order', 'desc');
        $query->orderBy($sortBy, $sortOrder);

        // Paginate
        $perPage = min($request->get('per_page', 50), 200);
        $comments = $query->paginate($perPage);

        return response()->json([
            'comments' => $comments->items(),
            'pagination' => [
                'total' => $comments->total(),
                'per_page' => $comments->perPage(),
                'current_page' => $comments->currentPage(),
                'last_page' => $comments->lastPage(),
            ],
        ]);
    }

    /**
     * Admin: Update comment status.
     */
    public function updateStatus(Request $request, string $id): JsonResponse
    {
        $this->authorize('admin', Comment::class);

        $comment = Comment::find($id);

        if (!$comment) {
            return response()->json([
                'message' => 'Comment not found'
            ], 404);
        }

        $validator = Validator::make($request->all(), [
            'status' => ['required', Rule::in([
                Comment::STATUS_PENDING,
                Comment::STATUS_APPROVED,
                Comment::STATUS_REJECTED,
                Comment::STATUS_SPAM
            ])],
            'reason' => 'nullable|string|max:500',
        ]);

        if ($validator->fails()) {
            return response()->json([
                'message' => 'Validation failed',
                'errors' => $validator->errors()
            ], 422);
        }

        $data = $validator->validated();

        try {
            $comment->update([
                'status' => $data['status'],
            ]);

            // Log moderation action
            activity()
                ->performedOn($comment)
                ->causedBy(Auth::user())
                ->withProperties([
                    'old_status' => $comment->getOriginal('status'),
                    'new_status' => $data['status'],
                    'reason' => $data['reason'] ?? null,
                ])
                ->log('Comment status updated');

            return response()->json([
                'message' => 'Comment status updated successfully',
                'comment' => $comment->load(['user:id,name', 'post:id,title,slug'])
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Failed to update comment status',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}

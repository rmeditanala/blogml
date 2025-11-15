<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\V1\PostController;
use App\Http\Controllers\Api\V1\CommentController;
use App\Http\Controllers\Api\V1\AuthController;
use App\Http\Controllers\Api\V1\RecommendationController;
use App\Http\Controllers\Api\V1\UploadController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/

Route::prefix('v1')->group(function () {

    // Public routes
    Route::get('/posts', [PostController::class, 'index']);
    Route::get('/posts/{post}', [PostController::class, 'show']);
    Route::get('/posts/{post}/comments', [CommentController::class, 'index']);

    // Authentication routes
    Route::post('/auth/register', [AuthController::class, 'register']);
    Route::post('/auth/login', [AuthController::class, 'login']);

    // Protected routes
    Route::middleware('auth:sanctum')->group(function () {

        // User profile and authentication
        Route::get('/auth/user', [AuthController::class, 'user']);
        Route::post('/auth/logout', [AuthController::class, 'logout']);
        Route::put('/auth/profile', [AuthController::class, 'updateProfile']);

        // Post management
        Route::post('/posts', [PostController::class, 'store']);
        Route::put('/posts/{post}', [PostController::class, 'update']);
        Route::delete('/posts/{post}', [PostController::class, 'destroy']);

        // Comment management
        Route::post('/posts/{post}/comments', [CommentController::class, 'store']);
        Route::put('/comments/{comment}', [CommentController::class, 'update']);
        Route::delete('/comments/{comment}', [CommentController::class, 'destroy']);

        // User interactions
        Route::post('/posts/{post}/like', [PostController::class, 'like']);
        Route::delete('/posts/{post}/like', [PostController::class, 'unlike']);
        Route::post('/posts/{post}/view', [PostController::class, 'view']);
        Route::post('/posts/{post}/bookmark', [PostController::class, 'bookmark']);

        // Recommendations (protected)
        Route::get('/recommendations/personalized', [RecommendationController::class, 'personalized']);
        Route::post('/recommendations/similar', [RecommendationController::class, 'similar']);

        // User's own content
        Route::get('/user/posts', [PostController::class, 'userPosts']);
        Route::get('/user/comments', [CommentController::class, 'userComments']);
        Route::get('/user/interactions', [PostController::class, 'userInteractions']);

        // AI generation (protected)
        Route::post('/ai/generate-post', [PostController::class, 'generatePost']);
        Route::post('/ai/generate-outline', [PostController::class, 'generateOutline']);

        // Image upload (protected)
        Route::post('/upload', [UploadController::class, 'upload']);
        Route::delete('/upload', [UploadController::class, 'destroy']);
    });

    // Admin routes (protected + admin middleware)
    Route::middleware(['auth:sanctum', 'admin'])->group(function () {
        Route::get('/admin/posts', [PostController::class, 'adminIndex']);
        Route::put('/admin/posts/{post}/status', [PostController::class, 'updateStatus']);
        Route::get('/admin/comments', [CommentController::class, 'adminIndex']);
        Route::put('/admin/comments/{comment}/status', [CommentController::class, 'updateStatus']);
    });
});

// Health check endpoint
Route::get('/health', function () {
    return response()->json([
        'status' => 'healthy',
        'timestamp' => now()->toIso8601String(),
        'version' => '1.0.0'
    ]);
});

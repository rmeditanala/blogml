<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Post extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'title',
        'slug',
        'content',
        'excerpt',
        'status',
        'is_ai_generated',
        'view_count',
        'like_count',
        'comment_count',
        'published_at',
        'featured_image',
        'image_analysis',
        'meta_title',
        'meta_description',
    ];

    protected $casts = [
        'is_ai_generated' => 'boolean',
        'view_count' => 'integer',
        'like_count' => 'integer',
        'comment_count' => 'integer',
        'published_at' => 'datetime',
        'image_analysis' => 'json',
    ];

    /**
     * Get the user that owns the post.
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Get the comments for the post.
     */
    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    /**
     * Get the approved comments for the post.
     */
    public function approvedComments(): HasMany
    {
        return $this->hasMany(Comment::class)->where('status', 'approved');
    }

    /**
     * Get the interactions for the post.
     */
    public function interactions(): HasMany
    {
        return $this->hasMany(UserInteraction::class);
    }

    /**
     * Get the media files for the post.
     */
    public function media(): HasMany
    {
        return $this->hasMany(Media::class);
    }

    /**
     * The tags that belong to the post.
     */
    public function tags(): BelongsToMany
    {
        return $this->belongsToMany(Tag::class);
    }

    /**
     * Get the trending score for the post (based on recent interactions).
     */
    public function getTrendingScoreAttribute(): float
    {
        $sevenDaysAgo = now()->subDays(7);

        $recentViews = $this->interactions()
            ->where('interaction_type', 'view')
            ->where('created_at', '>=', $sevenDaysAgo)
            ->count();

        $recentLikes = $this->interactions()
            ->where('interaction_type', 'like')
            ->where('created_at', '>=', $sevenDaysAgo)
            ->count();

        $recentComments = $this->interactions()
            ->where('interaction_type', 'comment')
            ->where('created_at', '>=', $sevenDaysAgo)
            ->count();

        return ($recentViews * 1) + ($recentLikes * 5) + ($recentComments * 10);
    }

    /**
     * Get the average sentiment score for comments on this post.
     */
    public function getAverageSentimentAttribute(): ?float
    {
        return $this->comments()
            ->whereNotNull('sentiment_score')
            ->avg('sentiment_score');
    }

    /**
     * Get sentiment distribution for comments.
     */
    public function getSentimentDistributionAttribute(): array
    {
        $distribution = $this->comments()
            ->whereNotNull('sentiment_label')
            ->selectRaw('sentiment_label, COUNT(*) as count')
            ->groupBy('sentiment_label')
            ->pluck('count', 'sentiment_label')
            ->toArray();

        return [
            'positive' => $distribution['POSITIVE'] ?? 0,
            'negative' => $distribution['NEGATIVE'] ?? 0,
            'neutral' => $distribution['NEUTRAL'] ?? 0,
        ];
    }

    /**
     * Scope a query to only include published posts.
     */
    public function scopePublished($query)
    {
        return $query->where('status', 'published')
                    ->whereNotNull('published_at')
                    ->where('published_at', '<=', now());
    }

    /**
     * Scope a query to only include trending posts.
     */
    public function scopeTrending($query, $days = 7)
    {
        return $query->published()
                    ->where('created_at', '>=', now()->subDays($days))
                    ->orderByDesc('view_count')
                    ->orderByDesc('like_count');
    }

    /**
     * Scope a query to only include AI generated posts.
     */
    public function scopeAiGenerated($query)
    {
        return $query->where('is_ai_generated', true);
    }

    /**
     * Scope a query to only include human-written posts.
     */
    public function scopeHumanWritten($query)
    {
        return $query->where('is_ai_generated', false);
    }

    /**
     * Get the route key for the model.
     */
    public function getRouteKeyName()
    {
        return 'slug';
    }

    /**
     * Boot the model.
     */
    protected static function boot()
    {
        parent::boot();

        static::creating(function ($post) {
            if (empty($post->slug)) {
                $post->slug = \Str::slug($post->title);
            }
        });

        static::updating(function ($post) {
            if ($post->isDirty('title') && empty($post->slug)) {
                $post->slug = \Str::slug($post->title);
            }
        });
    }
}
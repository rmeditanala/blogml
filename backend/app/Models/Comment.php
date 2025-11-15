<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Comment extends Model
{
    use HasFactory;

    protected $fillable = [
        'post_id',
        'user_id',
        'content',
        'status',
        'parent_id',
        'sentiment_score',
        'sentiment_label',
        'sentiment_confidence',
        'is_edited',
        'edited_at',
    ];

    protected $casts = [
        'sentiment_score' => 'float',
        'sentiment_confidence' => 'float',
        'is_edited' => 'boolean',
        'edited_at' => 'datetime',
    ];

    const STATUS_PENDING = 'pending';
    const STATUS_APPROVED = 'approved';
    const STATUS_REJECTED = 'rejected';
    const STATUS_SPAM = 'spam';

    const SENTIMENT_POSITIVE = 'POSITIVE';
    const SENTIMENT_NEGATIVE = 'NEGATIVE';
    const SENTIMENT_NEUTRAL = 'NEUTRAL';

    /**
     * Get the post that owns the comment.
     */
    public function post(): BelongsTo
    {
        return $this->belongsTo(Post::class);
    }

    /**
     * Get the user that owns the comment.
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Get the parent comment.
     */
    public function parent(): BelongsTo
    {
        return $this->belongsTo(Comment::class, 'parent_id');
    }

    /**
     * Get the replies to the comment.
     */
    public function replies(): HasMany
    {
        return $this->hasMany(Comment::class, 'parent_id');
    }

    /**
     * Get the approved replies to the comment.
     */
    public function approvedReplies(): HasMany
    {
        return $this->hasMany(Comment::class, 'parent_id')
                    ->where('status', self::STATUS_APPROVED);
    }

    /**
     * Check if comment is a reply.
     */
    public function isReply(): bool
    {
        return !is_null($this->parent_id);
    }

    /**
     * Check if comment has replies.
     */
    public function hasReplies(): bool
    {
        return $this->replies()->count() > 0;
    }

    /**
     * Get sentiment badge color based on sentiment label.
     */
    public function getSentimentColorAttribute(): string
    {
        return match($this->sentiment_label) {
            self::SENTIMENT_POSITIVE => 'green',
            self::SENTIMENT_NEGATIVE => 'red',
            self::SENTIMENT_NEUTRAL => 'gray',
            default => 'gray'
        };
    }

    /**
     * Get status badge color.
     */
    public function getStatusColorAttribute(): string
    {
        return match($this->status) {
            self::STATUS_APPROVED => 'green',
            self::STATUS_PENDING => 'yellow',
            self::STATUS_REJECTED => 'red',
            self::STATUS_SPAM => 'red',
            default => 'gray'
        };
    }

    /**
     * Scope a query to only include approved comments.
     */
    public function scopeApproved($query)
    {
        return $query->where('status', self::STATUS_APPROVED);
    }

    /**
     * Scope a query to only include pending comments.
     */
    public function scopePending($query)
    {
        return $query->where('status', self::STATUS_PENDING);
    }

    /**
     * Scope a query to only include top-level comments (no parent).
     */
    public function scopeTopLevel($query)
    {
        return $query->whereNull('parent_id');
    }

    /**
     * Scope a query to only include comments with specific sentiment.
     */
    public function scopeWithSentiment($query, string $sentiment)
    {
        return $query->where('sentiment_label', $sentiment);
    }

    /**
     * Scope a query to include comments with high confidence sentiment.
     */
    public function scopeWithHighConfidence($query, float $threshold = 0.8)
    {
        return $query->where('sentiment_confidence', '>=', $threshold);
    }

    /**
     * Get formatted sentiment label.
     */
    public function getFormattedSentimentAttribute(): string
    {
        return match($this->sentiment_label) {
            self::SENTIMENT_POSITIVE => '😊 Positive',
            self::SENTIMENT_NEGATIVE => '😞 Negative',
            self::SENTIMENT_NEUTRAL => '😐 Neutral',
            default => '❓ Unknown'
        };
    }

    /**
     * Get the word count of the comment.
     */
    public function getWordCountAttribute(): int
    {
        return str_word_count(strip_tags($this->content));
    }

    /**
     * Boot the model.
     */
    protected static function boot()
    {
        parent::boot();

        static::created(function ($comment) {
            // Update post comment count
            $comment->post->increment('comment_count');
        });

        static::updated(function ($comment) {
            // Mark as edited if content changed
            if ($comment->isDirty('content') && !$comment->is_edited) {
                $comment->update([
                    'is_edited' => true,
                    'edited_at' => now()
                ]);
            }
        });

        static::deleted(function ($comment) {
            // Update post comment count
            if ($comment->post) {
                $comment->post->decrement('comment_count');
            }
        });
    }
}
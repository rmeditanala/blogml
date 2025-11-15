<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class UserInteraction extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'post_id',
        'interaction_type',
        'metadata',
    ];

    protected $casts = [
        'metadata' => 'array',
    ];

    const TYPE_VIEW = 'view';
    const TYPE_LIKE = 'like';
    const TYPE_SHARE = 'share';
    const TYPE_COMMENT = 'comment';
    const TYPE_BOOKMARK = 'bookmark';

    /**
     * Get the user that owns the interaction.
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Get the post that owns the interaction.
     */
    public function post(): BelongsTo
    {
        return $this->belongsTo(Post::class);
    }

    /**
     * Scope a query to only include specific interaction types.
     */
    public function scopeOfType($query, string $type)
    {
        return $query->where('interaction_type', $type);
    }

    /**
     * Scope a query to get interactions within the last N days.
     */
    public function scopeRecent($query, int $days = 7)
    {
        return $query->where('created_at', '>=', now()->subDays($days));
    }

    /**
     * Boot the model.
     */
    protected static function boot()
    {
        parent::boot();

        static::created(function ($interaction) {
            switch ($interaction->interaction_type) {
                case self::TYPE_VIEW:
                    $interaction->post->increment('view_count');
                    break;
                case self::TYPE_LIKE:
                    $interaction->post->increment('like_count');
                    break;
            }
        });

        static::deleted(function ($interaction) {
            if ($interaction->post) {
                switch ($interaction->interaction_type) {
                    case self::TYPE_VIEW:
                        $interaction->post->decrement('view_count');
                        break;
                    case self::TYPE_LIKE:
                        $interaction->post->decrement('like_count');
                        break;
                }
            }
        });
    }
}
<?php

namespace Database\Factories;

use App\Models\Post;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Comment>
 */
class CommentFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        $comments = [
            'Great article! This really helped me understand the concept better.',
            'Thanks for sharing this. I\'ve been struggling with this topic for a while.',
            'Excellent explanation! The examples really make it clear.',
            'This is exactly what I was looking for. Keep up the good work!',
            'I have a question about the implementation details. Could you elaborate more?',
            'This approach seems promising. Have you considered the security implications?',
            'Perfect timing! I was just researching this topic yesterday.',
            'The code examples are really helpful. Thanks for putting this together.',
            'I disagree with some points here, but overall a good perspective.',
            'This is a game-changer for our development process. Thanks!',
            'Could you write a follow-up article on advanced techniques?',
            'I implemented this and it works perfectly. Much appreciated!',
            'Some parts are a bit confusing. Maybe add more diagrams?',
            'This saves me so much time. I was going to build this from scratch.',
            'Interesting perspective. I hadn\'t thought about it this way before.',
            'The performance gains are impressive. We should adopt this.',
            'Great job explaining complex concepts in simple terms.',
            'I\'d love to see more articles on this topic.',
            'This solved a major issue we were having. Thank you!',
            'Well-written and comprehensive. Bookmarked for future reference!'
        ];

        return [
            'post_id' => Post::factory(),
            'user_id' => User::factory(),
            'content' => fake()->randomElement($comments) . ' ' . fake()->sentence(rand(3, 8)),
            'status' => fake()->randomElement(['pending', 'approved', 'approved', 'approved']), // 75% approved
            'parent_id' => null, // Top-level comments by default
            'sentiment_score' => fake()->optional(0.8)->randomFloat(3, -1, 1),
            'sentiment_label' => fake()->optional(0.8)->randomElement(['POSITIVE', 'NEGATIVE', 'NEUTRAL']),
            'sentiment_confidence' => fake()->optional(0.8)->randomFloat(3, 0.5, 1.0),
            'is_edited' => false,
        ];
    }

    /**
     * Indicate that the comment is approved.
     */
    public function approved(): static
    {
        return $this->state(fn (array $attributes) => [
            'status' => 'approved',
        ]);
    }

    /**
     * Indicate that the comment has sentiment analysis.
     */
    public function withSentiment(): static
    {
        return $this->state(fn (array $attributes) => [
            'sentiment_score' => fake()->randomFloat(3, -1, 1),
            'sentiment_label' => fake()->randomElement(['POSITIVE', 'NEGATIVE', 'NEUTRAL']),
            'sentiment_confidence' => fake()->randomFloat(3, 0.6, 1.0),
        ]);
    }

    /**
     * Create a reply to an existing comment.
     */
    public function reply(): static
    {
        return $this->state(fn (array $attributes) => [
            'parent_id' => Comment::factory(),
        ]);
    }
}

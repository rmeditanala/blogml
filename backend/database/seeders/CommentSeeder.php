<?php

namespace Database\Seeders;

use App\Models\Post;
use App\Models\Comment;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class CommentSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $publishedPosts = Post::where('status', 'published')->get();
        $users = \App\Models\User::all();

        // Create 3-8 comments for each published post
        $publishedPosts->each(function ($post) use ($users) {
            $commentCount = rand(3, 8);

            // Create top-level comments
            for ($i = 0; $i < $commentCount; $i++) {
                $comment = Comment::factory()
                    ->approved()
                    ->withSentiment()
                    ->create([
                        'post_id' => $post->id,
                        'user_id' => $users->random()->id,
                    ]);

                // Occasionally create replies (30% chance)
                if (rand(1, 10) <= 3 && $i > 0) {
                    Comment::factory()
                        ->count(rand(1, 2))
                        ->approved()
                        ->withSentiment()
                        ->create([
                            'post_id' => $post->id,
                            'user_id' => $users->random()->id,
                            'parent_id' => $comment->id,
                        ]);
                }
            }
        });

        // Create some pending comments
        Comment::factory()
            ->count(15)
            ->create([
                'user_id' => $users->random()->id,
                'post_id' => $publishedPosts->random()->id,
            ]);

        // Update comment counts on posts
        Post::all()->each(function ($post) {
            $approvedCommentCount = Comment::where('post_id', $post->id)
                ->where('status', 'approved')
                ->count();
            $post->update(['comment_count' => $approvedCommentCount]);
        });

        $totalComments = Comment::count();
        $approvedComments = Comment::where('status', 'approved')->count();
        $pendingComments = Comment::where('status', 'pending')->count();

        $this->command->info("Created {$totalComments} comments total:");
        $this->command->info("  - {$approvedComments} approved comments");
        $this->command->info("  - {$pendingComments} pending comments");
        $this->command->info("  - Comments across {$publishedPosts->count()} published posts");
    }
}

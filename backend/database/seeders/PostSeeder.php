<?php

namespace Database\Seeders;

use App\Models\User;
use App\Models\Post;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class PostSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $users = User::all();

        // Create 10 posts for each user (100 posts total)
        $users->each(function ($user) {
            // Create a mix of published and draft posts
            Post::factory()
                ->count(7) // 7 published posts
                ->published()
                ->create(['user_id' => $user->id]);

            Post::factory()
                ->count(3) // 3 draft posts
                ->create(['user_id' => $user->id]);
        });

        // Create some AI-generated posts
        $aiGeneratedPosts = 15;
        Post::factory()
            ->count($aiGeneratedPosts)
            ->aiGenerated()
            ->published()
            ->create(['user_id' => $users->random()->id]);

        $totalPosts = Post::count();
        $publishedPosts = Post::where('status', 'published')->count();
        $aiPosts = Post::where('is_ai_generated', true)->count();

        $this->command->info("Created {$totalPosts} posts total:");
        $this->command->info("  - {$publishedPosts} published posts");
        $this->command->info("  - {$aiPosts} AI-generated posts");
        $this->command->info("  - " . ($totalPosts - $publishedPosts) . " draft posts");
        $this->command->info("Posts distributed across " . $users->count() . " users");
    }
}

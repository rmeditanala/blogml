<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class UserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $userNames = [
            'Alex Thompson' => 'alex.thompson',
            'Sarah Chen' => 'sarah.chen',
            'Michael Rodriguez' => 'michael.rodriguez',
            'Emily Watson' => 'emily.watson',
            'David Kim' => 'david.kim',
            'Jessica Martinez' => 'jessica.martinez',
            'Ryan O\'Brien' => 'ryan.obrien',
            'Lisa Anderson' => 'lisa.anderson',
            'James Wilson' => 'james.wilson',
            'Maria Garcia' => 'maria.garcia'
        ];

        foreach ($userNames as $name => $username) {
            User::factory()->create([
                'name' => $name,
                'email' => $username . '@techblog.com',
            ]);
        }

        $this->command->info('Created 10 users with technology blog credentials');
    }
}

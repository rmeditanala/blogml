<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('comments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('post_id')->constrained()->onDelete('cascade');
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->text('content');
            $table->enum('status', ['pending', 'approved', 'rejected', 'spam'])->default('pending');
            $table->foreignId('parent_id')->nullable()->constrained('comments')->onDelete('cascade');
            $table->decimal('sentiment_score', 5, 4)->nullable();
            $table->enum('sentiment_label', ['POSITIVE', 'NEGATIVE', 'NEUTRAL'])->nullable();
            $table->decimal('sentiment_confidence', 5, 4)->nullable();
            $table->boolean('is_edited')->default(false);
            $table->timestamp('edited_at')->nullable();
            $table->timestamps();

            // Indexes
            $table->index(['post_id', 'status']);
            $table->index('user_id');
            $table->index('parent_id');
            $table->index('sentiment_label');
            $table->index('created_at');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('comments');
    }
};

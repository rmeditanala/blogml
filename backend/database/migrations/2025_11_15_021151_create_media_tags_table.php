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
        Schema::create('media_tags', function (Blueprint $table) {
            $table->id();
            $table->foreignId('media_id')->constrained()->onDelete('cascade');
            $table->string('tag');
            $table->decimal('confidence', 5, 4)->nullable();
            $table->boolean('is_auto_generated')->default(false);
            $table->string('source_model')->nullable();
            $table->timestamps();

            $table->index(['media_id', 'tag']);
            $table->index('is_auto_generated');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('media_tags');
    }
};

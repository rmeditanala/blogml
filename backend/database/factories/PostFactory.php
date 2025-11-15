<?php

namespace Database\Factories;

use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Post>
 */
class PostFactory extends Factory
{
    /**
     * Technology-focused blog post data
     */
    private array $techPosts = [
        [
            'title' => 'Getting Started with React Hooks: A Comprehensive Guide',
            'content' => 'React Hooks have revolutionized the way we write React components. In this comprehensive guide, we\'ll explore everything from basic useState and useEffect hooks to advanced custom hooks. Learn how to manage state, handle side effects, and create reusable logic in your functional components.',
            'tags' => ['react', 'javascript', 'frontend', 'hooks']
        ],
        [
            'title' => 'Microservices Architecture: Best Practices and Patterns',
            'content' => 'Microservices architecture has become the de facto standard for building scalable applications. This post covers essential patterns including service discovery, circuit breakers, API gateways, and distributed data management. Learn when to use microservices and how to avoid common pitfalls.',
            'tags' => ['microservices', 'architecture', 'backend', 'devops']
        ],
        [
            'title' => 'Kubernetes Deployment Strategies: Rolling Updates vs Blue-Green',
            'content' => 'Deploying applications to Kubernetes requires careful planning. Compare different deployment strategies including rolling updates, blue-green deployments, and canary releases. Understand the trade-offs and learn how to implement zero-downtime deployments.',
            'tags' => ['kubernetes', 'devops', 'deployment', 'containers']
        ],
        [
            'title' => 'Web Security Fundamentals: OWASP Top 10 Explained',
            'content' => 'Security should be a primary concern for every web developer. This detailed breakdown of the OWASP Top 10 vulnerabilities covers injection attacks, broken authentication, sensitive data exposure, and more. Learn practical prevention strategies and implementation techniques.',
            'tags' => ['security', 'cybersecurity', 'web-development', 'owasp']
        ],
        [
            'title' => 'Machine Learning in Production: From Model to Deployment',
            'content' => 'Taking ML models from development to production involves numerous challenges. Explore model serving, monitoring, A/B testing, and continuous learning systems. Learn about frameworks like TensorFlow Serving, MLflow, and Kubernetes for ML workloads.',
            'tags' => ['machine-learning', 'mlops', 'ai', 'production']
        ],
        [
            'title' => 'Vue 3 Composition API vs Options API: When to Use Which',
            'content' => 'Vue 3 introduces the Composition API as a powerful alternative to the Options API. This in-depth comparison covers use cases, code organization, reusability, and performance considerations. Make informed decisions about your Vue.js application architecture.',
            'tags' => ['vue', 'javascript', 'frontend', 'composition-api']
        ],
        [
            'title' => 'Docker Best Practices: Building Optimized Container Images',
            'content' => 'Master Docker container optimization with these essential best practices. Learn about multi-stage builds, layer caching, security scanning, and image size reduction. Build smaller, faster, and more secure Docker images for production.',
            'tags' => ['docker', 'containers', 'devops', 'optimization']
        ],
        [
            'title' => 'API Security: Authentication, Authorization, and Rate Limiting',
            'content' => 'Securing REST APIs requires multiple layers of protection. Implement JWT authentication, OAuth 2.0 authorization, role-based access control, and rate limiting. Learn about API gateway security and defense against common attacks.',
            'tags' => ['api', 'security', 'authentication', 'backend']
        ],
        [
            'title' => 'Database Performance Optimization: Indexes and Query Tuning',
            'content' => 'Slow database queries can cripple application performance. Learn advanced indexing strategies, query optimization techniques, execution plan analysis, and database monitoring. Master SQL performance tuning for PostgreSQL, MySQL, and other relational databases.',
            'tags' => ['database', 'performance', 'sql', 'optimization']
        ],
        [
            'title' => 'CI/CD Pipeline Automation with GitHub Actions',
            'content' => 'Automate your development workflow with GitHub Actions. Build comprehensive CI/CD pipelines for testing, building, and deploying applications. Learn workflow syntax, action composition, and best practices for scalable automation.',
            'tags' => ['cicd', 'github-actions', 'automation', 'devops']
        ],
        [
            'title' => 'Frontend Performance: Web Vitals and Optimization Techniques',
            'content' => 'User experience depends on fast-loading websites. Master Core Web Vitals optimization, lazy loading, code splitting, and resource compression. Learn to audit performance and implement practical improvements for better user engagement.',
            'tags' => ['frontend', 'performance', 'web-vitals', 'optimization']
        ],
        [
            'title' => 'Serverless Architecture: AWS Lambda and Beyond',
            'content' => 'Serverless computing offers scalability and cost efficiency. Explore AWS Lambda, Azure Functions, and Google Cloud Functions. Learn about event-driven architectures, cold starts, and serverless best practices for production applications.',
            'tags' => ['serverless', 'aws', 'lambda', 'cloud']
        ],
        [
            'title' => 'TypeScript Advanced Patterns: Generics and Decorators',
            'content' => 'Take your TypeScript skills to the next level with advanced type system features. Master generics, conditional types, mapped types, and decorators. Build type-safe applications with better maintainability and developer experience.',
            'tags' => ['typescript', 'javascript', 'frontend', 'advanced']
        ],
        [
            'title' => 'Network Security: Firewalls, VPNs, and Zero Trust Architecture',
            'content' => 'Protect your infrastructure with comprehensive network security strategies. Learn about firewall configuration, VPN implementation, intrusion detection, and zero trust security models. Build defense-in-depth security architectures.',
            'tags' => ['network-security', 'cybersecurity', 'infrastructure', 'zero-trust']
        ],
        [
            'title' => 'GraphQL vs REST: Choosing the Right API Architecture',
            'content' => 'API design choices impact application architecture and performance. Compare GraphQL and REST APIs across dimensions like flexibility, performance, caching, and client complexity. Make informed decisions for your next API project.',
            'tags' => ['graphql', 'rest', 'api-design', 'backend']
        ]
    ];

    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        $postIndex = fake()->numberBetween(0, count($this->techPosts) - 1);
        $techPost = $this->techPosts[$postIndex];

        // Add some variation to the content
        $variations = [
            ' In this post, we\'ll dive deep into practical implementation details.',
            ' Let\'s explore real-world examples and best practices.',
            ' This guide covers everything you need to know to get started.',
            ' Learn from industry experts and avoid common mistakes.',
            ' Master these concepts with hands-on examples and exercises.'
        ];

        $variedContent = $techPost['content'] . fake()->randomElement($variations);

        return [
            'user_id' => User::factory(),
            'title' => $techPost['title'],
            'slug' => fake()->slug(),
            'content' => $variedContent,
            'excerpt' => fake()->text(150),
            'status' => fake()->randomElement(['draft', 'published']),
            'is_ai_generated' => fake()->boolean(20), // 20% chance of AI-generated
            'view_count' => fake()->numberBetween(0, 5000),
            'like_count' => fake()->numberBetween(0, 500),
            'comment_count' => 0, // Will be updated when comments are created
            'published_at' => fake()->randomElement([now(), now()->subDays(rand(1, 90)), null]),
            'meta_title' => fake()->text(60),
            'meta_description' => fake()->text(160),
        ];
    }

    /**
     * Indicate that the post is published.
     */
    public function published(): static
    {
        return $this->state(fn (array $attributes) => [
            'status' => 'published',
            'published_at' => now()->subDays(rand(1, 90)),
        ]);
    }

    /**
     * Indicate that the post is AI generated.
     */
    public function aiGenerated(): static
    {
        return $this->state(fn (array $attributes) => [
            'is_ai_generated' => true,
        ]);
    }
}

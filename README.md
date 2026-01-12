# Laravel API Skill for Claude

A comprehensive Claude skill for building production-grade Laravel REST APIs with clean architecture, type safety, and Laravel best practices.

## 🎯 What This Skill Does

This skill guides Claude in building Laravel REST APIs using opinionated architecture patterns combined with Laravel's official code quality standards. It implements:

- **Stateless Design** - No hidden dependencies, explicit data flow
- **Boundary-First Architecture** - Clear separation of HTTP, business logic, and data layers
- **Resource-Scoped Organization** - Routes and controllers organized by resource
- **Version Discipline** - Namespace-based versioning with HTTP Sunset headers
- **Type Safety** - Strict types, return type declarations, PSR-12 compliance
- **Code Quality** - Laravel simplifier patterns for maintainable code

## 📦 Installation

### Option 1: Claude.ai / Claude App

1. Download [laravel-api.skill](https://github.com/juststeveking/laravel-api-skill/releases/latest/download/laravel-api.skill)
2. Open Claude.ai or Claude app → Settings → Skills
3. Click "Add Skill" or "Import Skill"
4. Upload the `laravel-api.skill` file
5. Start building Laravel APIs!

### Option 2: Claude Code Plugin

If you're using Claude Code, you can install via the marketplace:

```bash
/plugin marketplace add juststeveking/laravel-api-skill
/plugin install laravel-api@juststeveking
```

## 🚀 Quick Start

Once installed, simply tell Claude what you want to build:

```
Build a Laravel API for managing tasks with CRUD operations
```

```
Create a Laravel API endpoint for user authentication with JWT
```

```
Review and refactor this Laravel controller to follow best practices
```

The skill automatically triggers when you mention Laravel API development.

## 🏗️ Architecture Patterns

### Core Components

**Models** - Simple data access with ULIDs
```php
final class Task extends Model
{
    use HasFactory;
    use HasUlids;
}
```

**Controllers** - Invokable, single responsibility
```php
final readonly class StoreController
{
    public function __invoke(StoreTaskRequest $request): JsonResponse
    {
        $task = $this->createTask->handle($request->payload());
        return new JsonDataResponse($task, 201);
    }
}
```

**Form Requests** - Validation + DTO transformation
```php
final class StoreTaskRequest extends FormRequest
{
    public function payload(): StoreTaskPayload
    {
        return new StoreTaskPayload(/* ... */);
    }
}
```

**Actions** - Single-purpose business logic
```php
final readonly class CreateTask
{
    public function handle(StoreTaskPayload $payload): Task
    {
        return Task::create($payload->toArray());
    }
}
```

**DTOs** - Explicit data transfer
```php
final readonly class StoreTaskPayload
{
    public function __construct(
        public string $title,
        public ?string $description,
    ) {}
}
```

### Project Structure

```
app/
├── Actions/
│   └── Tasks/
│       └── CreateTask.php
├── Http/
│   ├── Controllers/
│   │   └── Tasks/
│   │       └── V1/
│   │           └── StoreController.php
│   ├── Requests/
│   │   └── Tasks/
│   │       └── V1/
│   │           └── StoreTaskRequest.php
│   ├── Payloads/
│   │   └── Tasks/
│   │       └── StoreTaskPayload.php
│   └── Responses/
│       ├── JsonDataResponse.php
│       └── JsonErrorResponse.php
└── Models/
    └── Task.php

routes/
└── api/
    ├── routes.php
    └── tasks.php
```

## 📚 What's Included

### SKILL.md
Main skill file with:
- Quick start workflow
- Core architecture principles
- Code quality standards
- Step-by-step component creation
- API versioning patterns
- Authentication setup

### References
- **architecture.md** - Comprehensive architectural patterns and principles
- **code-examples.md** - Complete working examples for every component
- **code-quality.md** - Laravel best practices, refactoring patterns, PSR-12 standards

### Templates
Ready-to-use scaffolding templates:
- Controller.php
- FormRequest.php  
- Payload.php
- Action.php
- Model.php

## ✨ Key Features

### Type Safety
All code uses `declare(strict_types=1)` and explicit return types:
```php
public function handle(StoreTaskPayload $payload): Task
```

### Match Expressions
Replace nested ternaries with readable match expressions:
```php
$status = match (true) {
    $task->completed_at && $task->verified => 'verified',
    $task->completed_at => 'completed',
    default => 'pending',
};
```

### Consistent Responses
Standardized JSON responses using Responsable classes:
```php
// Success
return new JsonDataResponse(data: $task, status: 201);

// Error (Problem+JSON RFC 7807)
return new JsonErrorResponse(errors: [...], status: 422);
```

### Versioned Endpoints
Namespace-based versioning with deprecation warnings:
```php
Route::middleware(['auth:api', 'http.sunset:2025-12-31'])->group(function () {
    Route::get('/tasks', V1\IndexController::class);
});
```

## 🎓 Learning Resources

The skill includes comprehensive guides on:
- PSR-12 compliance
- Code review checklists
- Refactoring patterns
- Common anti-patterns
- Tool configurations (Pint, PHPStan)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This skill is open-source software licensed under the MIT license.

## 🙏 Acknowledgments

- Inspired by Laravel's official [claude-code simplifier](https://github.com/laravel/claude-code)
- Built with patterns from real-world Laravel API development
- Follows PSR-12 and Laravel best practices

## 📬 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/laravel-api-skill/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/laravel-api-skill/discussions)

---

Made with ❤️ for the Laravel community
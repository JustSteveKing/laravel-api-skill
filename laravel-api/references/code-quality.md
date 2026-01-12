# Laravel Code Quality & Refactoring

This guide covers code quality standards and refactoring patterns for Laravel APIs, inspired by Laravel's official code simplifier and PSR-12 standards.

## Core Principles

### 1. Preserve Functionality
When refactoring, NEVER change what code does - only how it does it. All original features, outputs, and behaviors must remain intact.

**Example:**
```php
// Before refactoring
public function calculateTotal($items) {
    $total = 0;
    foreach ($items as $item) {
        $total += $item['price'] * $item['quantity'];
    }
    return $total;
}

// After refactoring - behavior unchanged
public function calculateTotal(array $items): float
{
    return array_reduce(
        array: $items,
        callback: fn($total, $item) => $total + ($item['price'] * $item['quantity']),
        initial: 0.0,
    );
}
```

### 2. Explicit Over Implicit
Prefer clear, readable code over clever shortcuts. Code is read far more often than it's written.

**Example:**
```php
// ❌ Avoid: Too compact
$result = $a ?? $b ?: $c;

// ✅ Prefer: Clear intent
$result = $a ?? ($b ?: $c);
// Or better yet
$result = $a !== null ? $a : ($b !== false ? $b : $c);
```

### 3. Type Declarations Always
Use return types on all methods and parameter types where beneficial. Enable strict types.

**Example:**
```php
// ❌ Avoid: No types
class TaskService
{
    public function findById($id)
    {
        return Task::find($id);
    }
}

// ✅ Prefer: Full type safety
final readonly class TaskService
{
    public function findById(string $id): ?Task
    {
        return Task::find($id);
    }
}
```

## Refactoring Patterns

### Match Expressions Over Nested Ternaries

Nested ternary operators are notoriously hard to read. Use match expressions for clarity.

**Example 1: Status Determination**
```php
// ❌ Avoid: Nested ternary
$status = $task->completed_at 
    ? ($task->verified ? 'verified' : 'completed')
    : ($task->started_at ? 'in_progress' : 'pending');

// ✅ Prefer: Match expression
$status = match (true) {
    $task->completed_at && $task->verified => 'verified',
    $task->completed_at => 'completed',
    $task->started_at => 'in_progress',
    default => 'pending',
};
```

**Example 2: Permission Levels**
```php
// ❌ Avoid: Complex ternary chain
$access = $user->is_admin 
    ? 'full' 
    : ($user->is_manager 
        ? 'limited' 
        : ($user->is_viewer ? 'read' : 'none'));

// ✅ Prefer: Match with role
$access = match ($user->role) {
    'admin' => 'full',
    'manager' => 'limited',
    'viewer' => 'read',
    default => 'none',
};
```

### Extract Complex Conditions

When conditional logic becomes complex, extract it into well-named methods.

**Example:**
```php
// ❌ Avoid: Inline complexity
class TaskController
{
    public function update(Task $task): Response
    {
        if (
            auth()->user()->id === $task->owner_id 
            || (auth()->user()->role === 'admin' && auth()->user()->department === $task->department)
            || (auth()->user()->role === 'manager' && auth()->user()->manages($task->project))
        ) {
            $task->update($data);
        }
    }
}

// ✅ Prefer: Extracted methods
class TaskController
{
    public function update(Task $task): Response
    {
        if ($this->canUpdateTask($task)) {
            $task->update($data);
        }
    }

    private function canUpdateTask(Task $task): bool
    {
        $user = auth()->user();

        return $this->isTaskOwner($task, $user)
            || $this->isAuthorizedAdmin($task, $user)
            || $this->isProjectManager($task, $user);
    }

    private function isTaskOwner(Task $task, User $user): bool
    {
        return $user->id === $task->owner_id;
    }

    private function isAuthorizedAdmin(Task $task, User $user): bool
    {
        return $user->role === 'admin' 
            && $user->department === $task->department;
    }

    private function isProjectManager(Task $task, User $user): bool
    {
        return $user->role === 'manager' 
            && $user->manages($task->project);
    }
}
```

### Named Constants Over Magic Values

Replace magic numbers and strings with named constants.

**Example:**
```php
// ❌ Avoid: Magic values
if ($task->priority > 7) {
    $this->escalate($task);
}

if ($user->status === 'A') {
    $this->activate($user);
}

// ✅ Prefer: Named constants
class TaskPriority
{
    public const LOW = 1;
    public const MEDIUM = 5;
    public const HIGH = 7;
    public const CRITICAL = 10;
}

class UserStatus
{
    public const ACTIVE = 'A';
    public const INACTIVE = 'I';
    public const SUSPENDED = 'S';
}

if ($task->priority > TaskPriority::HIGH) {
    $this->escalate($task);
}

if ($user->status === UserStatus::ACTIVE) {
    $this->activate($user);
}
```

### Simplify Collection Operations

Use Laravel's collection methods instead of manual loops when appropriate.

**Example:**
```php
// ❌ Avoid: Manual loops
$activeUserIds = [];
foreach ($users as $user) {
    if ($user->status === 'active') {
        $activeUserIds[] = $user->id;
    }
}

// ✅ Prefer: Collection methods
$activeUserIds = collect($users)
    ->filter(fn($user) => $user->status === 'active')
    ->pluck('id')
    ->toArray();
```

## PSR-12 Standards

### File Structure

Every PHP file should follow this structure:

```php
<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tasks\V1;

use App\Actions\Tasks\CreateTask;
use App\Http\Requests\Tasks\V1\StoreTaskRequest;
use Illuminate\Http\JsonResponse;

final readonly class StoreController
{
    // Class contents
}
```

**Key elements:**
1. Opening tag with no closing tag
2. `declare(strict_types=1)` immediately after opening tag
3. Namespace declaration
4. Use statements (alphabetically sorted)
5. One blank line before class declaration
6. Class declaration with visibility keywords

### Naming Conventions

**Classes:**
- Use PascalCase
- Controllers: `{Resource}{Action}Controller` (e.g., `StoreTaskController`)
- Actions: `{Action}{Resource}` (e.g., `CreateTask`)
- DTOs: `{Action}{Resource}Payload` (e.g., `StoreTaskPayload`)

**Methods:**
- Use camelCase
- Be descriptive: `getUserById()` not `get()`
- Boolean methods: start with `is`, `has`, `can`, `should`

**Variables:**
- Use camelCase
- Be descriptive: `$activeUsers` not `$au`
- Avoid abbreviations unless universally known

### Method Organization

Order methods by visibility and purpose:

```php
final class TaskService
{
    // 1. Constructor
    public function __construct(
        private TaskRepository $repository,
    ) {}

    // 2. Public methods
    public function createTask(StoreTaskPayload $payload): Task
    {
        return $this->repository->create($payload->toArray());
    }

    public function updateTask(Task $task, UpdateTaskPayload $payload): Task
    {
        return $this->repository->update($task, $payload->toArray());
    }

    // 3. Protected methods
    protected function validateTask(Task $task): bool
    {
        return $task->status !== 'archived';
    }

    // 4. Private methods
    private function logTaskCreation(Task $task): void
    {
        Log::info('Task created', ['task_id' => $task->id]);
    }
}
```

## Code Review Checklist

When reviewing Laravel API code, check for:

### Type Safety
- [ ] All methods have return type declarations
- [ ] Parameter types are declared where beneficial
- [ ] File starts with `declare(strict_types=1)`
- [ ] DTOs use readonly properties with types

### Readability
- [ ] No nested ternary operators (use match instead)
- [ ] Complex conditions extracted to named methods
- [ ] Magic values replaced with named constants
- [ ] Variable and method names are descriptive

### Laravel Conventions
- [ ] Models use HasUlids trait
- [ ] Controllers are invokable with single responsibility
- [ ] Form Requests have payload() method returning DTO
- [ ] Actions have single handle() method
- [ ] Response classes implement Responsable

### Structure
- [ ] Proper namespace organization
- [ ] Imports alphabetically sorted
- [ ] One blank line between class sections
- [ ] PSR-12 formatting followed

### Best Practices
- [ ] Model::shouldBeStrict() enabled in AppServiceProvider
- [ ] No business logic in models
- [ ] No direct request access in controllers/actions
- [ ] Explicit eager loading (no N+1 queries)
- [ ] API routes versioned and scoped by resource

## Refactoring Workflow

1. **Read and Understand** - Fully understand what the code does before changing it
2. **Write Tests** - If tests don't exist, write them first to preserve behavior
3. **Make One Change** - Refactor one pattern at a time
4. **Verify Tests Pass** - Ensure functionality is preserved
5. **Commit** - Small, focused commits make review easier
6. **Repeat** - Continue until code meets quality standards

## Common Anti-Patterns

### Anti-Pattern: Business Logic in Models

```php
// ❌ Avoid
class Task extends Model
{
    public function complete(): void
    {
        $this->completed_at = now();
        $this->save();
        
        // Send notification
        Mail::to($this->assignee)->send(new TaskCompleted($this));
        
        // Update project status
        $this->project->checkCompletion();
    }
}

// ✅ Prefer: Logic in Actions
final readonly class CompleteTask
{
    public function __construct(
        private TaskNotificationService $notifications,
        private ProjectStatusService $projectStatus,
    ) {}

    public function handle(Task $task): Task
    {
        $task->update(['completed_at' => now()]);
        
        $this->notifications->sendCompletionEmail($task);
        $this->projectStatus->updateIfNeeded($task->project);
        
        return $task->fresh();
    }
}
```

### Anti-Pattern: God Controllers

```php
// ❌ Avoid: Controller doing everything
class TaskController
{
    public function store(Request $request)
    {
        $validated = $request->validate([...]);
        
        $task = Task::create($validated);
        
        Mail::to($task->assignee)->send(new TaskAssigned($task));
        
        Cache::forget('tasks:' . $task->project_id);
        
        return response()->json($task, 201);
    }
}

// ✅ Prefer: Thin controller with dedicated classes
final readonly class StoreController
{
    public function __construct(
        private CreateTask $createTask,
    ) {}

    public function __invoke(StoreTaskRequest $request): JsonResponse
    {
        $task = $this->createTask->handle($request->payload());
        
        return new JsonDataResponse(data: $task, status: 201);
    }
}
```

### Anti-Pattern: Inconsistent Response Formats

```php
// ❌ Avoid: Different structures per endpoint
Route::get('/tasks', fn() => Task::all());  // Returns array
Route::get('/tasks/{task}', fn(Task $task) => ['data' => $task]);  // Returns object
Route::post('/tasks', fn() => response()->json(['task' => $created]));  // Different key

// ✅ Prefer: Consistent Responsable classes
Route::get('/tasks', fn() => new JsonDataResponse(Task::all()));
Route::get('/tasks/{task}', fn(Task $task) => new JsonDataResponse($task));
Route::post('/tasks', fn() => new JsonDataResponse($created, 201));
```

## Tools and Automation

### Laravel Pint

Use Laravel Pint for automated code formatting:

```bash
composer require laravel/pint --dev
./vendor/bin/pint
```

Configure in `pint.json`:
```json
{
    "preset": "laravel",
    "rules": {
        "declare_strict_types": true,
        "no_unused_imports": true,
        "ordered_imports": true
    }
}
```

### PHPStan

Use PHPStan for static analysis:

```bash
composer require --dev phpstan/phpstan
./vendor/bin/phpstan analyse
```

Configure in `phpstan.neon`:
```neon
parameters:
    level: 8
    paths:
        - app
    checkMissingIterableValueType: false
```

### Larastan

Use Larastan for Laravel-specific analysis:

```bash
composer require --dev nunomaduro/larastan
./vendor/bin/phpstan analyse
```
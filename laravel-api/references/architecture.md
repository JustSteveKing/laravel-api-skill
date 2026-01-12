# Steve's Laravel API Architecture

## Core Principles

### 1. Stateless by Design
- No hidden dependencies in models or services
- Explicit data flow through DTOs
- Query building over implicit scopes
- Strict mode enabled to catch N+1 issues early

### 2. Boundary-First Approach
- Clear separation between HTTP, business logic, and data layers
- Form Requests handle validation and transform to DTOs
- DTOs carry data between layers
- Actions/Services contain business logic
- Models are data access only

### 3. Resource-Scoped Organization
- Route files scoped to resources (e.g., `routes/api/tasks.php`)
- Controllers scoped to resources and versions (e.g., `App/Http/Controllers/Tasks/V1`)
- All versions of a resource in one place for easy reference

### 4. Version Discipline
- Versioning through namespacing (V1, V2, etc.)
- HTTP Sunset headers for deprecation warnings
- Keep old versions working, don't break existing clients

### 5. Code Quality Standards (Laravel Best Practices)
- **Preserve Functionality** - Refactorings change HOW, never WHAT
- **Explicit Over Implicit** - Clear code beats clever code
- **Type Safety** - Use return types, parameter types, declare(strict_types=1)
- **Avoid Nested Ternaries** - Use match expressions for readability
- **PSR-12 Compliance** - Follow PHP-FIG standards strictly
- **Proper Namespacing** - Organize imports, use full type hints

## Project Structure

```
app/
├── Actions/               # Single-purpose business logic
│   └── Tasks/
│       └── CreateTask.php
├── Services/              # Complex business logic (only when needed)
│   └── TaskService.php
├── Http/
│   ├── Controllers/       # Invokable, versioned, resource-scoped
│   │   └── Tasks/
│   │       ├── V1/
│   │       │   ├── StoreController.php
│   │       │   ├── IndexController.php
│   │       │   └── ShowController.php
│   │       └── V2/
│   │           └── StoreController.php
│   ├── Requests/          # Validation + transformation to DTOs
│   │   └── Tasks/
│   │       └── V1/
│   │           └── StoreTaskRequest.php
│   ├── Payloads/          # DTOs for data transfer
│   │   └── Tasks/
│   │       └── StoreTaskPayload.php
│   ├── Responses/         # Responsable classes
│   │   ├── JsonDataResponse.php
│   │   └── JsonErrorResponse.php
│   └── Middleware/
│       └── HttpSunset.php
├── Models/
│   └── Task.php
└── Providers/
    └── AppServiceProvider.php  # Model::shouldBeStrict()

routes/
├── api/
│   ├── routes.php         # Main API routing file
│   └── tasks.php          # All task routes, all versions
```

## Component Patterns

### Models
- Always use ULIDs instead of auto-incrementing IDs
- Use `Model::shouldBeStrict()` in AppServiceProvider to prevent N+1 issues
- Keep models simple - data access only
- No business logic in models

### Controllers
- Always invokable (single action per controller)
- Organized by resource and version: `Tasks/V1/StoreController.php`
- Minimal logic - coordinate between Form Request, Action/Service, and Response
- Type-hint Form Request in `__invoke` method

### Form Requests
- Handle validation rules
- Include `payload()` method that returns a DTO from `app/Http/Payloads`
- Transform and sanitize input data
- Return strongly-typed DTOs for type safety

### DTOs (Data Transfer Objects)
- Simple data classes in `app/Http/Payloads`
- Public properties for data
- `toArray()` method for serialization
- No business logic - pure data carriers
- Make data flow explicit and trackable

### Actions
- Single-purpose classes in `app/Actions`
- One public method: `handle()`
- Contain focused business logic
- Return domain objects or DTOs
- Prefer Actions over Services

### Services
- Only use when logic is too large/complex for an Action
- Coordinate multiple Actions or complex workflows
- Still maintain single responsibility

### Response Classes
- Implement `Responsable` interface
- `asResponse()` returns `JsonResponse`
- Standard format: `{data, meta, errors}`
- Consistent API responses across the application

### Routing
- Main entry: `routes/api/routes.php`
- Resource files: `routes/api/{resource}.php`
- Group by version within resource files
- Apply version-specific middleware
- HTTP Sunset middleware for deprecations

### Error Handling
- Use `application/problem+json` format (RFC 7807)
- Convert exceptions in application exception handler
- Consistent error structure across API
- Proper HTTP status codes

### Query Building
- Use Spatie Query Builder for filtering, sorting, includes
- Start with `Model::query()` 
- Create custom query builders only when needed
- Explicit eager loading with `allowedIncludes()`
- Avoid hidden query scopes

## Authentication
- JWT tokens via PHP Open Source Saver package
- Stateless authentication
- Token in Authorization header: `Bearer {token}`
- Refresh token flow for long-lived sessions

## Common Patterns

### Creating a New Endpoint

1. Add route in `routes/api/{resource}.php`
2. Create invokable controller in `App/Http/Controllers/{Resource}/V1/`
3. Create Form Request with validation + `payload()` method
4. Create DTO in `App/Http/Payloads/{Resource}/`
5. Create Action in `App/Actions/{Resource}/`
6. Create Response class (or use existing)
7. Wire it together in controller

### Versioning an Endpoint

1. Create V2 namespace: `App/Http/Controllers/{Resource}/V2/`
2. Copy and modify controller from V1
3. Update Form Request if validation changes
4. Update DTO if structure changes
5. Add V2 route group in `routes/api/{resource}.php`
6. Add Sunset header to V1 routes

### Adding Query Capabilities

```php
// In controller
use Spatie\QueryBuilder\QueryBuilder;

$tasks = QueryBuilder::for(Task::class)
    ->allowedFilters(['status', 'priority'])
    ->allowedSorts(['created_at', 'due_date'])
    ->allowedIncludes(['project', 'assignee'])
    ->paginate();
```

## Anti-Patterns to Avoid

- ❌ Auto-incrementing IDs (use ULIDs)
- ❌ Business logic in models
- ❌ Multiple actions per controller
- ❌ Direct request data access in controllers/actions
- ❌ Hidden query scopes
- ❌ Service classes when an Action would do
- ❌ Breaking changes without versioning
- ❌ Inconsistent response formats
- ❌ Missing N+1 query prevention
- ❌ Nested ternary operators
- ❌ Missing type declarations
- ❌ Overly compact code that sacrifices readability

## Code Simplification Patterns

### Match Expressions Over Nested Ternaries

```php
// ❌ Avoid: Hard to read
$priority = $task->urgent ? 'high' : ($task->important ? 'medium' : 'low');

// ✅ Prefer: Clear and explicit
$priority = match (true) {
    $task->urgent => 'high',
    $task->important => 'medium',
    default => 'low',
};
```

### Extract Complex Conditions

```php
// ❌ Avoid: Inline complexity
if ($user->role === 'admin' || ($user->role === 'manager' && $user->department === 'sales')) {
    // ...
}

// ✅ Prefer: Named method
if ($this->canAccessSalesData($user)) {
    // ...
}

private function canAccessSalesData(User $user): bool
{
    return $user->role === 'admin' 
        || ($user->role === 'manager' && $user->department === 'sales');
}
```

### Explicit Type Declarations

```php
// ❌ Avoid: Missing types
class UpdateTask
{
    public function handle($task, $payload)
    {
        // ...
    }
}

// ✅ Prefer: Full type safety
final readonly class UpdateTask
{
    public function handle(Task $task, UpdateTaskPayload $payload): Task
    {
        // ...
    }
}
```

### Declare Strict Types

Always start files with:

```php
<?php

declare(strict_types=1);

namespace App\Actions\Tasks;
```
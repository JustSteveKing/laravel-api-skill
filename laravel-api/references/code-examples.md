# Code Examples

This document contains complete, working examples of each component in Steve's Laravel API architecture.

## Model with ULID

```php
<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

final class Task extends Model
{
    use HasFactory;
    use HasUlids;

    protected $fillable = [
        'title',
        'description',
        'status',
        'priority',
        'due_date',
        'project_id',
        'assignee_id',
    ];

    protected $casts = [
        'due_date' => 'datetime',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }

    public function assignee(): BelongsTo
    {
        return $this->belongsTo(User::class, 'assignee_id');
    }
}
```

## Form Request with DTO

```php
<?php

declare(strict_types=1);

namespace App\Http\Requests\Tasks\V1;

use App\Http\Payloads\Tasks\StoreTaskPayload;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

final class StoreTaskRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:255'],
            'description' => ['nullable', 'string', 'max:1000'],
            'status' => [
                'required',
                'string',
                Rule::in(['pending', 'in_progress', 'completed']),
            ],
            'priority' => [
                'required',
                'string',
                Rule::in(['low', 'medium', 'high']),
            ],
            'due_date' => ['nullable', 'date', 'after:today'],
            'project_id' => ['required', 'string', 'exists:projects,id'],
            'assignee_id' => ['nullable', 'string', 'exists:users,id'],
        ];
    }

    public function payload(): StoreTaskPayload
    {
        return new StoreTaskPayload(
            title: $this->string('title')->toString(),
            description: $this->string('description')->toString(),
            status: $this->string('status')->toString(),
            priority: $this->string('priority')->toString(),
            dueDate: $this->date('due_date'),
            projectId: $this->string('project_id')->toString(),
            assigneeId: $this->string('assignee_id')->toString(),
        );
    }
}
```

## DTO (Data Transfer Object)

```php
<?php

declare(strict_types=1);

namespace App\Http\Payloads\Tasks;

use DateTimeInterface;

final readonly class StoreTaskPayload
{
    public function __construct(
        public string $title,
        public ?string $description,
        public string $status,
        public string $priority,
        public ?DateTimeInterface $dueDate,
        public string $projectId,
        public ?string $assigneeId,
    ) {}

    public function toArray(): array
    {
        return [
            'title' => $this->title,
            'description' => $this->description,
            'status' => $this->status,
            'priority' => $this->priority,
            'due_date' => $this->dueDate?->format('Y-m-d'),
            'project_id' => $this->projectId,
            'assignee_id' => $this->assigneeId,
        ];
    }
}
```

## Action Class

```php
<?php

declare(strict_types=1);

namespace App\Actions\Tasks;

use App\Http\Payloads\Tasks\StoreTaskPayload;
use App\Models\Task;

final readonly class CreateTask
{
    public function handle(StoreTaskPayload $payload): Task
    {
        return Task::create($payload->toArray());
    }
}
```

## Invokable Controller

```php
<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tasks\V1;

use App\Actions\Tasks\CreateTask;
use App\Http\Requests\Tasks\V1\StoreTaskRequest;
use App\Http\Responses\JsonDataResponse;
use Illuminate\Http\JsonResponse;

final readonly class StoreController
{
    public function __construct(
        private CreateTask $createTask,
    ) {}

    public function __invoke(StoreTaskRequest $request): JsonResponse
    {
        $task = $this->createTask->handle(
            payload: $request->payload(),
        );

        return new JsonDataResponse(
            data: $task,
            status: 201,
        );
    }
}
```

## Response Classes

### Success Response

```php
<?php

namespace App\Http\Responses;

use Illuminate\Contracts\Support\Responsable;
use Illuminate\Http\JsonResponse;

final readonly class JsonDataResponse implements Responsable
{
    public function __construct(
        private mixed $data,
        private ?array $meta = null,
        private int $status = 200,
    ) {
    }

    public function toResponse($request): JsonResponse
    {
        $response = ['data' => $this->data];

        if ($this->meta !== null) {
            $response['meta'] = $this->meta;
        }

        return new JsonResponse(
            data: $response,
            status: $this->status,
        );
    }
}
```

### Error Response

```php
<?php

namespace App\Http\Responses;

use Illuminate\Contracts\Support\Responsable;
use Illuminate\Http\JsonResponse;

final readonly class JsonErrorResponse implements Responsable
{
    public function __construct(
        private array $errors,
        private int $status = 400,
        private ?array $meta = null,
    ) {
    }

    public function toResponse($request): JsonResponse
    {
        $response = ['errors' => $this->errors];

        if ($this->meta !== null) {
            $response['meta'] = $this->meta;
        }

        return new JsonResponse(
            data: $response,
            status: $this->status,
        );
    }
}
```

## Routes

### Main API Routes File

```php
<?php
// routes/api/routes.php

use Illuminate\Support\Facades\Route;

Route::prefix('v1')->group(function () {
    require __DIR__ . '/tasks.php';
    require __DIR__ . '/projects.php';
});

Route::prefix('v2')->group(function () {
    require __DIR__ . '/tasks.php';
});
```

### Resource Routes File

```php
<?php
// routes/api/tasks.php

use App\Http\Controllers\Tasks\V1;
use Illuminate\Support\Facades\Route;

// V1 Routes
Route::middleware(['auth:api', 'http.sunset:2025-12-31'])->group(function () {
    Route::get('/tasks', V1\IndexController::class);
    Route::post('/tasks', V1\StoreController::class);
    Route::get('/tasks/{task}', V1\ShowController::class);
    Route::patch('/tasks/{task}', V1\UpdateController::class);
    Route::delete('/tasks/{task}', V1\DestroyController::class);
});

// V2 Routes (when needed)
// Route::middleware(['auth:api'])->group(function () {
//     Route::get('/tasks', \App\Http\Controllers\Tasks\V2\IndexController::class);
//     Route::post('/tasks', \App\Http\Controllers\Tasks\V2\StoreController::class);
// });
```

## Index Controller with Query Builder

```php
<?php

namespace App\Http\Controllers\Tasks\V1;

use App\Http\Responses\JsonDataResponse;
use App\Models\Task;
use Illuminate\Http\JsonResponse;
use Spatie\QueryBuilder\QueryBuilder;

final class IndexController
{
    public function __invoke(): JsonResponse
    {
        $tasks = QueryBuilder::for(Task::class)
            ->allowedFilters([
                'status',
                'priority',
                'project_id',
                'assignee_id',
            ])
            ->allowedSorts([
                'created_at',
                'due_date',
                'priority',
            ])
            ->allowedIncludes([
                'project',
                'assignee',
            ])
            ->paginate();

        return new JsonDataResponse(
            data: $tasks->items(),
            meta: [
                'current_page' => $tasks->currentPage(),
                'per_page' => $tasks->perPage(),
                'total' => $tasks->total(),
                'last_page' => $tasks->lastPage(),
            ],
        );
    }
}
```

## Show Controller

```php
<?php

namespace App\Http\Controllers\Tasks\V1;

use App\Http\Responses\JsonDataResponse;
use App\Models\Task;
use Illuminate\Http\JsonResponse;
use Spatie\QueryBuilder\QueryBuilder;

final class ShowController
{
    public function __invoke(string $task): JsonResponse
    {
        $task = QueryBuilder::for(Task::where('id', $task))
            ->allowedIncludes([
                'project',
                'assignee',
            ])
            ->firstOrFail();

        return new JsonDataResponse(
            data: $task,
        );
    }
}
```

## Update Controller

```php
<?php

namespace App\Http\Controllers\Tasks\V1;

use App\Actions\Tasks\UpdateTask;
use App\Http\Requests\Tasks\V1\UpdateTaskRequest;
use App\Http\Responses\JsonDataResponse;
use App\Models\Task;
use Illuminate\Http\JsonResponse;

final readonly class UpdateController
{
    public function __construct(
        private UpdateTask $updateTask,
    ) {
    }

    public function __invoke(UpdateTaskRequest $request, Task $task): JsonResponse
    {
        $updatedTask = $this->updateTask->handle(
            task: $task,
            payload: $request->payload(),
        );

        return new JsonDataResponse(
            data: $updatedTask,
        );
    }
}
```

## Update Action

```php
<?php

namespace App\Actions\Tasks;

use App\Http\Payloads\Tasks\UpdateTaskPayload;
use App\Models\Task;

final readonly class UpdateTask
{
    public function handle(Task $task, UpdateTaskPayload $payload): Task
    {
        $task->update($payload->toArray());

        return $task->fresh();
    }
}
```

## Destroy Controller

```php
<?php

namespace App\Http\Controllers\Tasks\V1;

use App\Models\Task;
use Illuminate\Http\JsonResponse;

final class DestroyController
{
    public function __invoke(Task $task): JsonResponse
    {
        $task->delete();

        return new JsonResponse(status: 204);
    }
}
```

## HTTP Sunset Middleware

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class HttpSunset
{
    public function handle(Request $request, Closure $next, string $date): Response
    {
        $response = $next($request);

        $response->headers->set('Sunset', $date);
        $response->headers->set(
            'Deprecation',
            'This API version is deprecated and will be removed on ' . $date
        );

        return $response;
    }
}
```

## AppServiceProvider Setup

```php
<?php

namespace App\Providers;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        //
    }

    public function boot(): void
    {
        // Prevent lazy loading and N+1 queries
        Model::shouldBeStrict();
    }
}
```

## Exception Handler (Problem+JSON)

```php
<?php

namespace App\Exceptions;

use Illuminate\Auth\AuthenticationException;
use Illuminate\Database\Eloquent\ModelNotFoundException;
use Illuminate\Foundation\Exceptions\Handler as ExceptionHandler;
use Illuminate\Http\JsonResponse;
use Illuminate\Validation\ValidationException;
use Symfony\Component\HttpKernel\Exception\HttpException;
use Throwable;

class Handler extends ExceptionHandler
{
    protected $dontFlash = [
        'current_password',
        'password',
        'password_confirmation',
    ];

    public function register(): void
    {
        $this->reportable(function (Throwable $e) {
            //
        });
    }

    public function render($request, Throwable $e): JsonResponse
    {
        if ($request->is('api/*')) {
            return $this->renderApiException($e);
        }

        return parent::render($request, $e);
    }

    private function renderApiException(Throwable $e): JsonResponse
    {
        $status = $this->getStatusCode($e);
        $title = $this->getTitle($e);
        $detail = $e->getMessage();

        $problem = [
            'type' => 'about:blank',
            'title' => $title,
            'status' => $status,
            'detail' => $detail,
        ];

        if ($e instanceof ValidationException) {
            $problem['errors'] = $e->errors();
        }

        return new JsonResponse(
            data: $problem,
            status: $status,
            headers: ['Content-Type' => 'application/problem+json'],
        );
    }

    private function getStatusCode(Throwable $e): int
    {
        if ($e instanceof HttpException) {
            return $e->getStatusCode();
        }

        if ($e instanceof ModelNotFoundException) {
            return 404;
        }

        if ($e instanceof AuthenticationException) {
            return 401;
        }

        if ($e instanceof ValidationException) {
            return 422;
        }

        return 500;
    }

    private function getTitle(Throwable $e): string
    {
        return match (true) {
            $e instanceof ValidationException => 'Validation Failed',
            $e instanceof ModelNotFoundException => 'Resource Not Found',
            $e instanceof AuthenticationException => 'Authentication Required',
            $e instanceof HttpException => $e->getMessage(),
            default => 'Internal Server Error',
        };
    }
}
```

## Service Class Example (when needed)

```php
<?php

namespace App\Services;

use App\Actions\Tasks\CreateTask;
use App\Actions\Tasks\AssignTask;
use App\Actions\Tasks\NotifyAssignee;
use App\Http\Payloads\Tasks\StoreTaskPayload;
use App\Models\Task;

final readonly class TaskService
{
    public function __construct(
        private CreateTask $createTask,
        private AssignTask $assignTask,
        private NotifyAssignee $notifyAssignee,
    ) {
    }

    /**
     * Create a task and handle all related side effects
     */
    public function createAndAssign(StoreTaskPayload $payload, string $assigneeId): Task
    {
        $task = $this->createTask->handle($payload);

        $task = $this->assignTask->handle($task, $assigneeId);

        $this->notifyAssignee->handle($task);

        return $task;
    }
}
```
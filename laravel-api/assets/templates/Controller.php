<?php

declare(strict_types=1);

namespace App\Http\Controllers\{Resource}\V1;

use App\Actions\{Resource}\{Action};
use App\Http\Requests\{Resource}\V1\{Request};
use App\Http\Responses\JsonDataResponse;
use Illuminate\Http\JsonResponse;

final readonly class {Controller}
{
    public function __construct(
        private {Action} ${action},
    ) {}

    public function __invoke({Request} $request): JsonResponse
    {
        ${result} = $this->{action}->handle(
            payload: $request->payload(),
        );

        return new JsonDataResponse(
            data: ${result},
            status: 201,
        );
    }
}
# Changelog

All notable changes to the Laravel API Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-12

### Added
- Initial release of Laravel API Skill
- Complete API architecture patterns (stateless, boundary-first, resource-scoped)
- Code quality standards with PSR-12 compliance
- Type safety with declare(strict_types=1) throughout
- Action classes using `handle()` method convention
- Comprehensive reference documentation:
  - architecture.md - Core patterns and principles
  - code-examples.md - Working examples for all components
  - code-quality.md - Best practices and refactoring patterns
- Ready-to-use templates for scaffolding:
  - Controller, FormRequest, Payload, Action, Model
- JWT authentication setup guide
- API versioning with HTTP Sunset headers
- Match expression patterns for readable conditionals
- Standardized JSON responses (Responsable classes)
- ULID support for models
- Code review checklists
- Tool configurations (Laravel Pint, PHPStan, Larastan)

### Design Decisions
- Using `handle()` instead of `execute()` for Action classes
- All classes marked as `final` where appropriate
- Readonly properties on DTOs and Action classes
- Strict type declarations on all files
- Explicit return types on all methods
- Resource-scoped routing organization
- Invokable controllers (single responsibility)

[1.0.0]: https://github.com/juststeveking/laravel-api-skill/releases/tag/v1.0.0
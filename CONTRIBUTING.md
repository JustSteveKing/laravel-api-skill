# Contributing to Laravel API Skill

Thank you for considering contributing to the Laravel API Skill! This document outlines the process for contributing.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, error messages)
- **Describe the behavior you observed** and what you expected to see
- **Include your environment details** (Claude version, Laravel version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a step-by-step description** of the suggested enhancement
- **Explain why this enhancement would be useful** to most users
- **List some examples** of how it would be used

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding standards below
3. **Test your changes** by actually using the skill in Claude
4. **Update documentation** if you're changing functionality
5. **Write a clear commit message** describing what and why

#### Coding Standards

When contributing code to the skill:

**For SKILL.md and reference files:**
- Keep examples concise but complete
- Use PHP 8.1+ features (readonly, enums, etc.)
- Always include `declare(strict_types=1)`
- Use explicit return types
- Follow PSR-12 formatting
- Prefer clarity over brevity

**For templates:**
- Include `declare(strict_types=1)` at the top
- Use `final` keyword where appropriate
- Include clear placeholder comments
- Follow the established naming patterns

**For documentation:**
- Be clear and concise
- Use code examples liberally
- Explain the "why" not just the "what"
- Keep formatting consistent with existing docs

### Architecture Decisions

When suggesting changes to the core architecture:

1. **Open an issue first** to discuss the change
2. **Explain the problem** being solved
3. **Provide rationale** for the approach
4. **Consider backward compatibility**
5. **Update relevant documentation**

## Skill Organization Principles

### Progressive Disclosure

The skill uses a three-level loading system:

1. **Metadata** (name + description) - Always in context
2. **SKILL.md body** - Loaded when skill triggers  
3. **Reference files** - Loaded as needed

Keep SKILL.md focused on quick-start patterns. Move detailed information to reference files.

### File Size Guidelines

- **SKILL.md**: < 500 lines (currently ~310)
- **Reference files**: < 1000 lines each
- **Templates**: Minimal but complete

If a file exceeds these limits, consider splitting content.

### Conciseness

Context window is a public good. Every token counts:

- Challenge each piece of information: "Does Claude really need this?"
- Prefer examples over explanations
- Remove redundancy between files
- Link to reference files instead of duplicating

## Testing Changes

Before submitting a PR:

1. **Package the skill** using the packaging script
2. **Install it in Claude** (claude.ai or Claude app)
3. **Test real scenarios**:
   - Build a simple API
   - Create different endpoint types (CRUD)
   - Test code review scenarios
   - Verify templates work correctly
4. **Verify all examples** are valid PHP code
5. **Check for typos** and broken links

## Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Testing improvements
- `chore`: Maintenance tasks

**Examples:**
```
feat(actions): add handle() method convention

Replace execute() with handle() throughout all Action examples
to align with Laravel community conventions.

BREAKING CHANGE: Action classes now use handle() instead of execute()
```

```
docs(readme): add installation instructions for Claude Code

Add section explaining how to install via Claude Code marketplace
```

## Release Process

Releases follow [Semantic Versioning](https://semver.org/):

- **Major** (1.0.0): Breaking changes to skill structure or API
- **Minor** (1.1.0): New features, backward compatible
- **Patch** (1.0.1): Bug fixes, backward compatible

Maintainers will:
1. Update CHANGELOG.md
2. Create a git tag
3. Package the skill
4. Create a GitHub release
5. Attach the packaged .skill file

## Questions?

Don't hesitate to ask questions! You can:

- Open a [GitHub Discussion](https://github.com/juststeveking/laravel-api-skill/discussions)
- Comment on relevant issues
- Reach out to maintainers

## Code of Conduct

Be respectful, constructive, and professional. We're all here to learn and improve.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
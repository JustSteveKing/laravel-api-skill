#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file from the laravel-api folder

Usage:
    python scripts/package_skill.py

This will package the laravel-api/ directory into laravel-api.skill in the repo root.
"""

import sys
import zipfile
import re
from pathlib import Path


def validate_skill(skill_path):
    """
    Basic validation of a skill
    
    Returns: (valid: bool, message: str)
    """
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read content
    content = skill_md.read_text(encoding='utf-8')
    
    # Check for frontmatter
    if not content.startswith('---'):
        return False, "No YAML frontmatter found at start of SKILL.md"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format - must be between --- markers"

    frontmatter_text = match.group(1)
    
    # Basic YAML parsing (simple key: value pairs)
    frontmatter = {}
    for line in frontmatter_text.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()
    
    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"
    
    # Validate name format (kebab-case)
    name = frontmatter['name']
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
    
    if name.startswith('-') or name.endswith('-') or '--' in name:
        return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    
    if len(name) > 64:
        return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."
    
    # Check description
    description = frontmatter['description']
    if '<' in description or '>' in description:
        return False, "Description cannot contain angle brackets (< or >)"
    
    if len(description) > 1024:
        return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."
    
    return True, "Skill is valid!"


def package_skill(skill_path, output_dir=None):
    """
    Package a skill folder into a .skill file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the .skill file (defaults to current directory)

    Returns:
        Path to the created .skill file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Run validation before packaging
    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"✅ {message}\n")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    # Create the .skill file (zip format)
    try:
        with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the skill directory
            for file_path in skill_path.rglob('*'):
                if file_path.is_file():
                    # Calculate the relative path within the zip
                    arcname = file_path.relative_to(skill_path.parent)
                    zipf.write(file_path, arcname)
                    print(f"  Added: {arcname}")

        print(f"\n✅ Successfully packaged skill to: {skill_filename}")
        print(f"   File size: {skill_filename.stat().st_size / 1024:.1f} KB")
        return skill_filename

    except Exception as e:
        print(f"❌ Error creating .skill file: {e}")
        return None


def main():
    """Main entry point"""
    # Determine repo root (where this script is located)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    # Default paths
    skill_path = repo_root / "laravel-api"
    output_dir = repo_root
    
    # Allow override via command line
    if len(sys.argv) >= 2:
        skill_path = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        output_dir = Path(sys.argv[2])
    
    print("📦 Laravel API Skill Packager")
    print(f"   Skill directory: {skill_path}")
    print(f"   Output directory: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)

    if result:
        print("\n🎉 Done! Your skill is ready to distribute.")
        print(f"   Upload {result.name} to Claude.ai → Settings → Skills")
        sys.exit(0)
    else:
        print("\n❌ Packaging failed. Please fix the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
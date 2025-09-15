# Publishing Genox to PyPI

This project now uses `uv` for building and publishing packages, replacing the traditional `setup.py` workflow.

## Prerequisites

1. Install `uv` if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create a PyPI account at https://pypi.org (if you don't have one)

3. Generate an API token:
   - Go to https://pypi.org/manage/account/
   - Scroll to "API tokens" section
   - Click "Add API token"
   - Give it a name (e.g., "genox-publish")
   - Set scope to "Project: genox" (recommended for security)
   - Save the token securely

## Building the Package

```bash
# Build the package (creates wheel and source distribution)
uv build

# For publishing, build without uv sources
uv build --no-sources
```

This creates two files in the `dist/` directory:
- `genox-X.Y.Z-py3-none-any.whl` (wheel distribution)
- `genox-X.Y.Z.tar.gz` (source distribution)

## Version Management

Update the version before publishing:

```bash
# Check current version
uv version

# Bump version (examples)
uv version --bump patch  # 0.2.3 -> 0.2.4
uv version --bump minor  # 0.2.3 -> 0.3.0
uv version --bump major  # 0.2.3 -> 1.0.0

# Or set specific version
uv version 0.3.0
```

The version is stored in `pyproject.toml`.

## Publishing to PyPI

### Test with TestPyPI (Recommended First)

1. Create a TestPyPI account at https://test.pypi.org

2. Build and publish to TestPyPI:
   ```bash
   uv build --no-sources
   uv publish --publish-url https://test.pypi.org/legacy/ \
     --token <YOUR_TEST_PYPI_TOKEN>
   ```

3. Test installation:
   ```bash
   uv pip install --index-url https://test.pypi.org/simple/ genox
   ```

### Publish to Production PyPI

```bash
# Build the package
uv build --no-sources

# Publish to PyPI
uv publish --token <YOUR_PYPI_TOKEN>

# Or using environment variable
export UV_PUBLISH_TOKEN=<YOUR_PYPI_TOKEN>
uv publish
```

## Testing the Published Package

After publishing, test the installation:

```bash
# Create a fresh virtual environment
uv venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from PyPI
uv pip install genox

# Test the CLI
genox --help

# Test import
uv run --with genox --no-project -- python -c "import genox; print(genox.__version__)"
```

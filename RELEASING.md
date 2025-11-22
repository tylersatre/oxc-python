# Release Process

This document describes how to publish a new release of oxc-python to PyPI.

## Prerequisites

- Admin access to the GitHub repository
- PyPI trusted publishing configured (see `CI-CD-SETUP-GUIDE.md`)
- All tests passing on the main branch

## Release Checklist

### 1. Prepare the Release

- [ ] Ensure all desired changes are merged to `main`
- [ ] Ensure CI is passing on `main` (check GitHub Actions)
- [ ] Update `CHANGELOG.md` with release notes
  - Document new features, bug fixes, breaking changes
  - Follow [Keep a Changelog](https://keepachangelog.com/) format
- [ ] Commit and push changelog: `git commit -am "docs: update CHANGELOG for v0.1.0" && git push`

**Note:** You do NOT need to update version numbers in `Cargo.toml` or `pyproject.toml`. The release workflow automatically extracts the version from your git tag.

### 2. Create and Push a Git Tag

Determine the version number following [Semantic Versioning](https://semver.org/):
- **Patch** (0.1.X): Bug fixes, no breaking changes
- **Minor** (0.X.0): New features, no breaking changes
- **Major** (X.0.0): Breaking changes

```bash
# Create a tag (example: v0.1.0)
git tag v0.1.0

# Push the tag to GitHub
git push origin v0.1.0
```

**Important:** The tag MUST start with `v` (e.g., `v0.1.0`, not `0.1.0`)

### 3. Create a GitHub Release

1. Go to https://github.com/tylersatre/oxc-python/releases
2. Click **"Draft a new release"**
3. Click **"Choose a tag"** and select the tag you just pushed (e.g., `v0.1.0`)
4. Set the release title: `v0.1.0` or `Release 0.1.0`
5. Add release notes in the description:
   - Copy relevant sections from `CHANGELOG.md`
   - Highlight major changes or breaking changes
   - Include upgrade instructions if needed
6. If this is a pre-release (beta, rc, alpha):
   - Check **"Set as a pre-release"**
7. Click **"Publish release"**

### 4. Monitor the Release Pipeline

Once you publish the GitHub release, the automated release workflow starts:

1. **Go to the Actions tab**: https://github.com/tylersatre/oxc-python/actions
2. **Find the "Release" workflow** that just started
3. **Monitor the build progress**:
   - Build wheels for Linux (x86_64, aarch64)
   - Build wheels for macOS (universal2)
   - Build wheels for Windows (x86_64)
   - Build source distribution
   - Publish to PyPI
   - Upload assets to GitHub release

The entire process typically takes **30-40 minutes**.

### 5. Verify the Release

After the workflow completes successfully:

**Check PyPI:**
1. Visit https://pypi.org/project/oxc-python/
2. Verify the new version is listed
3. Check that all expected wheels are present:
   - `oxc_python-X.Y.Z-cp310-abi3-manylinux_2_28_x86_64.whl`
   - `oxc_python-X.Y.Z-cp310-abi3-manylinux_2_28_aarch64.whl`
   - `oxc_python-X.Y.Z-cp310-abi3-macosx_11_0_universal2.whl`
   - `oxc_python-X.Y.Z-cp310-abi3-win_amd64.whl`
   - `oxc-python-X.Y.Z.tar.gz` (source distribution)

**Check GitHub Release:**
1. Go to https://github.com/tylersatre/oxc-python/releases
2. Verify wheels are attached as release assets
3. Verify release notes are correct

**Test Installation:**
```bash
# Create a fresh virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install the new version
pip install oxc-python==X.Y.Z

# Test basic functionality
python -c "import oxc_python; print('Success!')"

# Clean up
deactivate
rm -rf test-env
```

### 6. Announce the Release

- [ ] Post announcement on relevant channels (Twitter, Discord, etc.)
- [ ] Update documentation if needed
- [ ] Close any resolved issues/PRs related to this release

## Pre-releases

For pre-release versions (alpha, beta, release candidate):

**Tag format examples:**
- `v0.1.0-alpha.1`
- `v0.1.0-beta.1`
- `v0.1.0-rc.1`

**GitHub Release:**
- Always check **"Set as a pre-release"** when creating the release

**PyPI:**
- Pre-releases will be published to PyPI automatically
- Users must explicitly request pre-releases: `pip install oxc-python==0.1.0rc1`
- Pre-releases don't show up in default `pip install oxc-python` (only stable releases)

## Troubleshooting

### Build Fails on a Specific Platform

1. Check the GitHub Actions logs for the specific platform
2. Common issues:
   - Rust compilation errors (check if dependencies changed)
   - Python compatibility issues (check abi3 configuration)
   - Platform-specific code issues

**Recovery:**
- Fix the issue in a new commit
- Delete the failed release and tag
- Create a new tag with the fix (e.g., `v0.1.1`)
- Try the release process again

### PyPI Publish Fails

**"Version already exists":**
- You cannot overwrite a published version on PyPI
- Increment the version and create a new release (e.g., `v0.1.1`)

**"Trusted publisher configuration does not match":**
- Verify trusted publishing is set up correctly on PyPI
- Check that workflow name is exactly `release.yml`
- Check that environment name is exactly `release`
- See `CI-CD-SETUP-GUIDE.md` for detailed setup

**"Insufficient permissions":**
- Verify the `release` environment exists in GitHub
- Ensure trusted publishing is configured on PyPI
- Check that `permissions: id-token: write` is set in workflow

### Wheels Missing from PyPI

- Check the Actions logs to see if wheel builds completed
- Verify artifacts were uploaded correctly
- Check if the publish step actually ran (may be waiting for approval)

## Emergency Rollback

If a release has critical issues:

1. **DO NOT delete the PyPI release** (PyPI doesn't allow re-uploading the same version)
2. **Yank the release on PyPI**:
   - Go to https://pypi.org/manage/project/oxc-python/releases/
   - Find the problematic version
   - Click "Options" → "Yank release"
   - Provide a reason (e.g., "Critical bug, use v0.1.1 instead")
3. **Create a hotfix release** with the next patch version
4. **Update documentation** to note the yanked version

## Version Management

**Version management is fully automated** - the git tag is the source of truth!

- `Cargo.toml` keeps a placeholder version (`0.0.0`) in the repository
- `pyproject.toml` uses `dynamic = ["version"]` to pull from `Cargo.toml`
- When you create a release, the workflow automatically:
  1. Extracts the version from the git tag (e.g., `v0.1.0` → `0.1.0`)
  2. Updates `Cargo.toml` with the extracted version before building
  3. Builds wheels and source distribution with the correct version
- The version on PyPI will match your git tag (without the `v` prefix)
- Example: Git tag `v0.1.0` → PyPI version `0.1.0`

**You only need to create the git tag** - everything else is automatic!

## Support

For questions or issues with the release process:
- Check `CI-CD-SETUP-GUIDE.md` for setup details
- Check GitHub Actions logs for detailed error messages
- Open an issue at https://github.com/tylersatre/oxc-python/issues

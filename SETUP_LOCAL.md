# Local Development Setup (Without Docker)

This guide walks through setting up the Jekyll site locally using **rbenv** (no Docker).
Tested on Ubuntu 22.04 / WSL2, also suitable for GitHub Codespaces.

## 1. Clone the Repository

The repo uses SSH for cloning. Make sure you have an SSH key set up with GitHub (check with `cat ~/.ssh/id_rsa.pub` or `cat ~/.ssh/id_ed25519.pub`; if not, see [GitHub's SSH guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)).

The repo contains **git submodules** (Jupyter notebook repos under `assets/jupyter/`). Use `--recurse-submodules` when cloning to pull them in automatically:

```bash
git clone --recurse-submodules git@github.com:MarkusThill/MarkusThill.github.io.git
cd MarkusThill.github.io
```

If you already cloned without submodules, initialize them after the fact:

```bash
git submodule update --init --recursive
```

The submodules are:

| Submodule | Path |
|-----------|------|
| `MarkusThill.github.io-jupyter` | `assets/jupyter/MarkusThill.github.io-jupyter` |
| `DTMFCuda` | `assets/jupyter/DTMFCuda` |

These contain Jupyter notebooks referenced by blog posts. The Jekyll build will fail or produce incomplete pages if they are missing.

## 2. System Dependencies

Install the build tools and libraries required to compile Ruby and native gem extensions:

```bash
sudo apt-get update
sudo apt-get install -y \
  build-essential \
  git \
  git-lfs \
  libssl-dev \
  libreadline-dev \
  zlib1g-dev \
  libyaml-dev \
  libffi-dev \
  imagemagick
```

`imagemagick` is needed by the `jekyll-imagemagick` plugin for responsive image generation.

## 3. rbenv and Ruby

### Install rbenv and ruby-build

```bash
git clone https://github.com/rbenv/rbenv.git ~/.rbenv
cd ~/.rbenv && src/configure && make -C src
cd -
git clone https://github.com/rbenv/ruby-build.git ~/.rbenv/plugins/ruby-build
```

The `src/configure && make -C src` step compiles a small C extension that speeds up rbenv's shim dispatch. It's optional but recommended.

Add rbenv to your shell. Append to `~/.bashrc`:

```bash
# enable rbenv
if [ -d "$HOME/.rbenv/" ]; then
    export PATH="$HOME/.rbenv/bin:$PATH"
    eval "$(rbenv init - bash)"
fi
```

Restart your shell (or `source ~/.bashrc`).

### Install Ruby

The repo pins a minimum version in `.ruby-version` (currently **3.1.4**). Newer Ruby 3.x versions work fine and are preferred — just update `.ruby-version` accordingly:

```bash
# Install the version you want (3.1.4 or newer):
rbenv install 3.3.6
# Update the version file to match:
echo "3.3.6" > .ruby-version
```

Verify:

```bash
cd /path/to/MarkusThill.github.io
ruby --version
```

rbenv automatically picks up the version from `.ruby-version` when you're in the repo directory.

## 4. Bundler and Gems

```bash
gem install bundler
bundle install
```

This installs Jekyll and all plugins defined in the `Gemfile`.

## 5. Node.js and Prettier (for formatting)

Node.js is needed for Prettier (code formatting). **Use nvm** (Node Version Manager) rather than the system `apt` package, which ships an outdated version that can cause issues:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# Restart your shell, then:
nvm install --lts
```

Then install the formatter:

```bash
npm install
```

This installs `prettier` and `@shopify/prettier-plugin-liquid` from `package.json`.

## 6. Python and Jupyter (optional)

Only needed if you have Jupyter notebook posts (the `jekyll-jupyter-notebook` plugin renders `.ipynb` files during build):

```bash
pip install -r requirements.txt
```

This installs `nbconvert`, `pyyaml`, `scholarly`, and `rendercv`. Make sure `jupyter` is on your PATH.

## 7. Running the Site

### Start the dev server

```bash
bundle exec jekyll serve
```

The site will be available at **http://localhost:4000** (or the port shown in the output).

### Incremental builds (faster rebuilds)

```bash
bundle exec jekyll serve --incremental
```

This only rebuilds pages that changed, which is much faster during content editing. Note: changes to `_config.yml`, layouts, or includes may require a full rebuild (restart without `--incremental`).

### Related posts with LSI

```bash
bundle exec jekyll serve --lsi
```

The `--lsi` flag enables Latent Semantic Indexing for the "Related Posts" section. It produces better recommendations but makes the build noticeably slower. Combine with `--incremental` for a reasonable workflow:

```bash
bundle exec jekyll serve --lsi --incremental
```

### Previewing draft posts

```bash
bundle exec jekyll serve --drafts
```

This renders posts from `_drafts/` as if they were published, so you can preview them locally before moving them to `_posts/`.

### Formatting before commit

```bash
npx prettier . --write
```

Note: Prettier is configured to skip `.md` files (via `.prettierignore`) because it tends to break LaTeX equations in blog posts.

## 8. Deploying to GitHub Pages

Deployment is **automatic**. The GitHub Actions workflow (`.github/workflows/deploy.yml`) triggers on every push to `master` that changes site content (posts, assets, config, layouts, etc.).

The workflow:
1. Checks out the repo **with submodules** (`submodules: recursive`)
2. Sets up Ruby 3.3.5 and Python 3.13
3. Installs ImageMagick and `nbconvert` (for Jupyter)
4. Builds with `bundle exec jekyll build` in production mode
5. Purges unused CSS with PurgeCSS
6. Deploys the `_site/` folder to GitHub Pages via `github-pages-deploy-action`

So to publish a new blog post, just push to `master`:

```bash
# Format, commit, push
npx prettier . --write
git add _posts/my-new-post.md assets/img/my-new-post/
git commit -m "feat: new blog post on topic X"
git push origin master
```

The deploy typically takes 2-3 minutes. Monitor progress in the **Actions** tab on GitHub.

**Things to watch out for:**
- Submodule changes (new notebooks) need a separate commit in the submodule repo first, then update the reference in the main repo with `git add assets/jupyter/<submodule> && git commit`
- The CI uses `imagemagick` and `nbconvert` — if the build succeeds locally with these, it will succeed in CI
- The workflow only triggers for relevant file changes (not README, INSTALL, etc.) — see the `paths` filter in `deploy.yml`

## 9. Syncing with Upstream al-folio

This site is based on the [al-folio](https://github.com/alshedivat/al-folio) theme. To pull in upstream improvements and bug fixes, add the upstream remote (one-time) and merge periodically:

```bash
# One-time: add the upstream remote
git remote add upstream https://github.com/alshedivat/al-folio.git

# Sync: fetch and merge
git fetch upstream
git merge upstream/main
```

If the histories have diverged significantly (e.g., after a fork), you may need:

```bash
git merge upstream/main --allow-unrelated-histories
```

After merging, expect conflicts in files you've customized (`_config.yml`, `_pages/about.md`, `_includes/`, etc.). Resolve them, then:

```bash
bundle install          # in case Gemfile changed upstream
bundle exec jekyll serve  # verify everything still builds
git add -u && git commit -m "fix: resolved merge conflicts after upstream sync"
git push
```

## 10. Common Issues

| Problem | Solution |
|---------|----------|
| `bundle install` fails with OpenSSL errors | Make sure `libssl-dev` is installed, then `rbenv install <version>` again |
| `gem install` fails with zlib errors | Install `zlib1g-dev`: `sudo apt-get install zlib1g-dev` |
| ImageMagick warnings during build | Ensure `imagemagick` is installed: `convert --version` |
| Jupyter notebooks not rendering | Check that `jupyter` is on PATH: `which jupyter` |
| `bundle exec jekyll serve` fails after gem updates | Run `bundle install` again, or `bundle update` |
| Port already in use | Kill the old process or use `--port 4001` |
| Permission errors on `.jekyll-cache` or `Gemfile.lock` | Fix ownership: `sudo chown -R $(whoami) .` — this can happen on WSL after switching between Docker (root) and local (user) builds |
| Stale cache causes build errors | Remove the cache and rebuild: `rm -rf .jekyll-cache/ && bundle exec jekyll serve` |
| Submodules are empty directories | Run `git submodule update --init --recursive` |

## Quick Reference

| Tool | Tested with | Minimum | Managed by |
|------|-------------|---------|------------|
| Ruby | 3.1.4 | 3.1+ | rbenv (`.ruby-version`) |
| Bundler | 2.6.x | any recent | gem |
| Jekyll | latest | per Gemfile | Gemfile |
| Node.js | 12.x | 12+ (any LTS) | system / nvm |
| Prettier | 3.8.x | per package.json | package.json |
| ImageMagick | 6.x | 6+ | apt |

Newer versions are generally preferred. The versions listed under "Tested with" reflect a known working configuration.

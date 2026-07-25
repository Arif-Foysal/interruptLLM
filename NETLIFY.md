# Deploy to Netlify

This guide walks you through deploying the InterruptLLM study-materials website to [Netlify](https://www.netlify.com/).

## Before you start

Make sure you have:

- A GitHub repository containing this project.
- A Netlify account (free tier is fine).
- The `netlify.toml` file in the project root.

## Quick overview

| Setting | Value |
|---|---|
| Build command | `bash scripts/sync_study_materials_to_quartz.sh && cd quartz && npm install && npx quartz build` |
| Publish directory | `quartz/public` |
| Node version | `22` (set in `netlify.toml`) |

The `netlify.toml` file already contains these settings, so Netlify will detect them automatically.

## Step 1: Set the correct base URL

Open `quartz/quartz.config.yaml` and find the `baseUrl` line:

```yaml
baseUrl: interruptllm-study.netlify.app
```

Replace `interruptllm-study` with the site name you plan to use on Netlify. If you add a custom domain later, update this to your custom domain.

> [!important]
> The `baseUrl` is used for OpenGraph/Twitter metadata and canonical links. The site will still render if it is wrong, but social previews and SEO will be slightly off.

## Step 2: Push to GitHub

Commit and push all the website files:

```bash
git add netlify.toml quartz/ scripts/ DEPLOY.md NETLIFY.md .gitignore
git commit -m "Add Netlify-ready Quartz website for study materials"
git push origin main
```

> [!tip]
> You do not need to commit `quartz/public/` or `quartz/node_modules/` — they are ignored by `.gitignore` and will be rebuilt on Netlify.

## Step 3: Connect Netlify to GitHub

1. Log in to [Netlify](https://app.netlify.com/).
2. Click **Add new site → Import an existing project**.
3. Choose **GitHub** and authorize Netlify.
4. Select the `ICCIT` repository.
5. Netlify will read the `netlify.toml` file and pre-fill:
   - Build command
   - Publish directory
   - Node version
6. Click **Deploy site**.

## Step 4: Wait for the first build

Netlify will run the build command. A successful build log will look like this:

```
10:12:35 AM: Syncing study_materials -> quartz/content ...
10:12:35 AM: Done. Files copied: 43
10:12:40 AM: npm install
10:12:45 AM: Quartz v5.0.0
10:12:48 AM: Parsed 43 Markdown files
10:12:50 AM: Emitted 157 files to `public`
```

If the build fails, check the **Deploy log** in Netlify and see the troubleshooting section below.

## Step 5: Visit the site

After the build succeeds, Netlify gives you a URL like:

```
https://interruptllm-study.netlify.app
```

Open it in your browser. You should see the homepage and be able to click through the curriculum.

## Step 6: Update the site after editing the vault

Whenever you edit files in `study_materials/`:

1. Commit and push the changes to GitHub.
2. Netlify will automatically rebuild and redeploy the site.

You do not need to manually sync `quartz/content/` because the build command runs:

```bash
bash scripts/sync_study_materials_to_quartz.sh
```

before building.

## Optional: use a custom domain

1. In Netlify, go to **Site configuration → Domain management**.
2. Click **Add custom domain** and follow the DNS instructions.
3. Update `quartz/quartz.config.yaml`:

   ```yaml
   baseUrl: your-domain.com
   ```

4. Commit and push the change.

## Troubleshooting

### Build fails with "Cannot find module"

Make sure the `npm install` step is included in the build command. The `netlify.toml` already includes it.

### Site is blank or 404

1. Check the Netlify deploy log for errors.
2. Verify the **Publish directory** is `quartz/public` and that `quartz/public/index.html` exists after the build.
3. Check that `baseUrl` in `quartz/quartz.config.yaml` matches your Netlify domain.

### Wiki links are broken

Quartz resolves `[[wiki-links]]` by file stem. If you rename a file in `study_materials/`, update all links pointing to it and push.

### Mermaid diagrams are not rendering

Quartz has built-in Mermaid support. If a diagram fails, validate the Mermaid syntax in a [Mermaid live editor](https://mermaid.live/).

### Math/LaTeX is not rendering

The `quartz.config.yaml` has KaTeX enabled. Ensure your LaTeX is inside `$...$` or `$$...$$` blocks.

### Date warnings in the build log

You may see warnings like `content/00-curriculum-overview.md isn't yet tracked by git, dates will be inaccurate`. These are harmless. They will disappear once the files are committed and the build runs on Netlify with git history.

### Want to test locally first?

Run:

```bash
bash scripts/sync_study_materials_to_quartz.sh
cd quartz
npx quartz build --serve
```

Then open `http://localhost:8080`.

## Netlify-specific notes

- The `netlify.toml` sets `NODE_VERSION = "22"` because Quartz requires Node.js >= 22.
- Static assets are cached for 1 year, and the content index is cached for 1 hour.
- The build command always syncs the latest `study_materials/` before building, so your website stays in sync with the vault.

## Need help?

- Netlify docs: https://docs.netlify.com/
- Quartz docs: https://quartz.jzhao.xyz/
- Repository: https://github.com/mdzero591/ICCIT

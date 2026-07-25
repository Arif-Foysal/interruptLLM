# Deploying the Study Materials Website

The `study_materials/` Obsidian vault is also published as a static website using [Quartz](https://quartz.jzhao.xyz/).

## Quick local preview

```bash
cd quartz
npm install
npx quartz build
npx quartz build --serve
```

Then open `http://localhost:8080`.

## What is in `quartz/`

| Path | Purpose |
|---|---|
| `quartz/content/` | Copy of the `study_materials/` vault used as website content |
| `quartz/quartz.config.yaml` | Site configuration (title, URL, plugins, theme) |
| `quartz/public/` | **Generated** build output (do not edit, ignored by git) |
| `quartz/node_modules/` | **Generated** dependencies (ignored by git) |

> [!important]
> Do not edit files in `quartz/content/` directly. Edit the source files in `study_materials/` and re-copy when you make changes.

## How to update the site after editing the vault

If you change files in `study_materials/`, update the website content:

```bash
bash scripts/sync_study_materials_to_quartz.sh
```

Then rebuild:

```bash
cd quartz
npx quartz build
```

## Deployment options

### Option A: GitHub Pages (recommended)

1. **Set the base URL** in `quartz/quartz.config.yaml`:

   ```yaml
   baseUrl: mdzero591.github.io/ICCIT
   ```

   If you use a custom domain (e.g., `interruptllm-study.example.com`), set it here.

2. **Enable GitHub Pages** in your repository settings:
   - Go to **Settings → Pages**.
   - Under **Build and deployment**, select **GitHub Actions**.

3. **Push the workflow** (already in `.github/workflows/deploy.yml`):

   ```bash
   git add .github/workflows/deploy.yml quartz/ .gitignore
   git commit -m "Add Quartz website for study materials"
   git push origin main
   ```

4. **Wait** for the GitHub Actions workflow to finish.

5. **Visit** your site at `https://mdzero591.github.io/ICCIT/` (or your custom domain).

### Option B: Vercel

1. Connect your GitHub repository to Vercel.
2. Set the **framework preset** to `Other`.
3. Set the **root directory** to `quartz`.
4. Set the **build command** to:

   ```bash
   npm install && npx quartz build
   ```

5. Set the **output directory** to `public`.
6. Update `baseUrl` in `quartz/quartz.config.yaml` to your Vercel domain.

### Option C: Netlify (detailed guide in [NETLIFY.md](NETLIFY.md))

1. Set the **base URL** in `quartz/quartz.config.yaml`:

   ```yaml
   baseUrl: interruptllm-study.netlify.app
   ```

   Replace `interruptllm-study` with your Netlify site name.

2. Connect your GitHub repository to Netlify. The `netlify.toml` in the project root already tells Netlify:
   - Build command: `bash scripts/sync_study_materials_to_quartz.sh && cd quartz && npm install && npx quartz build`
   - Publish directory: `quartz/public`
   - Node.js version: 22

3. Push the `netlify.toml` file and the rest of the project to your repository:

   ```bash
   git add netlify.toml quartz/ scripts/ DEPLOY.md .gitignore
   git commit -m "Add Netlify-ready Quartz website for study materials"
   git push origin main
   ```

4. In Netlify, create a new site from Git and select your repository.

5. Netlify will detect the `netlify.toml` settings automatically. You usually do not need to change anything in the UI.

6. Wait for the build to finish and visit the generated URL.

### Option D: Manual upload

Build the site locally:

```bash
cd quartz
npx quartz build
```

Then upload the contents of `quartz/public/` to any static host.

## Troubleshooting

### Wiki links are broken

Quartz resolves `[[wiki-links]]` by file name. If you rename a file, update the links in the source vault and re-copy the content.

### Mermaid diagrams are not rendering

Quartz has built-in Mermaid support. If a diagram fails, check that the Mermaid syntax is valid. Avoid mixing Mermaid inside callouts or complex HTML.

### Math/LaTeX is not rendering

The `quartz.config.yaml` has KaTeX enabled. Make sure LaTeX is inside `$...$` or `$$...$$` blocks.

### Site is blank or 404

1. Check that `baseUrl` matches your actual deployment URL.
2. Verify `quartz/public/` was generated and contains `index.html`.
3. For GitHub Pages, ensure the workflow has permissions to write pages and id-token.

## Customization

- **Theme:** edit the `theme` section in `quartz/quartz.config.yaml`.
- **Plugins:** see the [Quartz plugin documentation](https://quartz.jzhao.xyz/plugins/).
- **Footer links:** edit the `footer` plugin options in `quartz.config.yaml`.

## Need help?

- Quartz documentation: https://quartz.jzhao.xyz/
- Quartz Discord: https://discord.gg/cRFFHYye7t
- Repository: https://github.com/mdzero591/ICCIT

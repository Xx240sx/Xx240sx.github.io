# Your Name — Portfolio

A responsive, single-page portfolio built with embedded CSS and a tiny inline script. It has no build step, package dependencies, or external assets.

## Customize the site

Edit `index.html` and replace the sample name, biography, project details, and `hello@example.com` address with your own. The styles are included in the HTML file, so no separate asset folder is needed.

## Generate a sitemap

Python 3.9 or newer is recommended. The generator uses only Python's standard library.

From this folder, run:

```bash
python generate.py --base-url https://YOUR-USERNAME.github.io/YOUR-REPOSITORY
```

For a GitHub Pages user or organization site, omit the repository name:

```bash
python generate.py --base-url https://YOUR-USERNAME.github.io
```

The script scans the selected site directory for HTML pages and writes `sitemap.xml` there. To scan a different folder, such as `docs`, pass `--directory docs`:

```bash
python generate.py --base-url https://YOUR-USERNAME.github.io/YOUR-REPOSITORY --directory docs
```

Run the script again after adding or updating pages, then include the generated sitemap in your GitHub repository.

## Publish with GitHub Pages

1. Add `index.html`, `generate.py`, and this README to your repository (or put the published site files in the folder you plan to use).
2. Generate `sitemap.xml` using the public URL for your site.
3. Push the files to GitHub.
4. In the repository, open **Settings → Pages**. Under **Build and deployment**, select **Deploy from a branch**, then choose the branch and folder containing `index.html` (the repository root or `/docs`) and save.
5. After GitHub Pages finishes deploying, open the site URL shown in the Pages settings.

For a project repository, the published URL is usually `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/`. For a repository named `YOUR-USERNAME.github.io`, it is usually `https://YOUR-USERNAME.github.io/`.

# emanueleagle.net

Personal website built with a 90s web aesthetic. Content is defined in JSON configs and compiled to static HTML.

## How it works

`build.py` reads JSON files from `config/` and generates static HTML into `html/`. You never edit HTML directly — all content changes happen in the JSON files. Push to `main` and the GitHub Action builds and deploys automatically.

## File structure

```
config/
  site.json              # Global: nav links, footer text
  pages/                 # One JSON file per page
    index.json           # Home page
    about.json           # About page
    projects.json        # Projects list
    blog.json            # Blog index (auto-generated from config/blog/)
    photos.json          # Photo gallery
  blog/                  # One JSON file per blog post
    YYYY-MM-DD-slug.json
  pages/images/          # Images for the gallery
.github/workflows/
  build.py               # Compiles JSON → HTML
  deploy.yaml            # CI/CD: builds and syncs to S3 on push to main
```

## Making edits

### Site-wide (nav, footer)

Edit `config/site.json`. The `nav` array controls the navigation bar. The `footer` field is the footer text.

### Home / About pages (`two-column` layout)

Edit `config/pages/index.json` or `config/pages/about.json`.

- `left_blurbs` — short italic lines in the left column
- `right_content` — paragraphs in the right column. Each string is a separate paragraph. HTML tags (like `<b>` and `<a>`) are allowed inside the strings.

### Projects page (`list` layout)

Edit `config/pages/projects.json`.

- `intro` — text shown above the table
- `items` — list of `{ "name": "...", "description": "..." }` entries

### Photos page (`gallery` layout)

Edit `config/pages/photos.json`.

- `tags` — the list of filter options shown in the dropdown. `"All"` should always be first.
- `photos` — list of photo entries:

```json
{
  "src": "images/filename.jpeg",
  "species": "American Bittern",
  "caption": "A short description",
  "date": "2026-03-01",
  "tags": ["Birds", "Nature"]
}
```

Place image files in `config/pages/images/`. The `tags` on each photo must match values in the top-level `tags` list for filtering to work.

### Blog posts

Create a new file in `config/blog/` named `YYYY-MM-DD-post-slug.json`:

```json
{
  "title": "Post Title",
  "date": "2026-03-24",
  "content": [
    "First paragraph.",
    "Second paragraph."
  ]
}
```

Each string in `content` is a separate paragraph. The blog index page updates automatically.

## Deploy

Push to `main`. The GitHub Action:
1. Runs `terraform apply` (infrastructure)
2. Runs `build.py` (compiles JSON → HTML)
3. Syncs `html/` to S3
4. Invalidates the CloudFront cache

## Infrastructure

- **S3** — static file hosting
- **CloudFront** — CDN + HTTPS
- **ACM** — SSL certificate
- **Route53** — DNS

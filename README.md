# emanueleagle.net

Personal website built with a 90s web aesthetic. Content is defined in JSON configs and compiled to static HTML.

## Structure

```
config/
  site.json              # Nav links, footer, global settings
  pages/                 # Page content configs
    index.json
    about.json
    projects.json
    blog.json
    birds.json
  blog/                  # One JSON file per blog post
    2026-03-23-first-post.json
infra/                   # Terraform (S3, CloudFront, Route53, ACM)
.github/workflows/
  build.py               # Generates HTML from JSON configs
  deploy.yaml            # CI/CD pipeline
html/                    # Build output (gitignored)
```

## Adding a Blog Post

Create a new file in `config/blog/`:

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

Push to `main` and it deploys automatically.

## Infrastructure

- **S3** - Static file hosting
- **CloudFront** - CDN + HTTPS
- **ACM** - Free SSL certificate
- **Route53** - DNS

## Deploy

Push to `main` triggers the GitHub Action which:
1. Runs `terraform apply` for infrastructure
2. Builds HTML from JSON configs
3. Syncs to S3
4. Invalidates CloudFront cache

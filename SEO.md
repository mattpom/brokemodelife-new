# SEO maintenance

Canonical origin: https://brokemodelife.com/

Run `python scripts/check-seo.py` before publishing. The same check runs on HTML, sitemap, robots and canonical-domain changes in GitHub Actions.

Each indexable page needs one unique title and description, one absolute HTTPS canonical URL, valid JSON structured data where present, and an entry in sitemap.xml. Use the canonical origin above. The homepage canonical ends in `/`; other pages retain their existing `.html` URLs.

Keep redirects, error pages and pages marked noindex out of the sitemap. A moved page should point its canonical and redirect at the real destination. Add each new article to the relevant topic or archive page with an ordinary HTML link.

Keep Googlebot and Bingbot allowed in robots.txt and keep its sitemap declaration current. Preserve the existing policy that allows AI search crawlers and blocks AI training crawlers.

Preserve site-specific design, wording, existing social images and analytics. Do not invent article dates or reset every sitemap lastmod on each deployment. Add lastmod only when the date of a substantial page change is known.

Search Console URL Inspection and sitemap submission require access to the verified property. A successful technical check establishes crawlability; it does not establish Google indexing or rankings.

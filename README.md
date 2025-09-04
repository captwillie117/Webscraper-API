# Web Scraper API

This is a Flask-based API that scrapes a given website for:

- Emails
- Phone numbers
- Social media links (Facebook, Twitter/X, Instagram)

## Endpoint

### POST /scrape

**Request Body:**

```json
{
  "url": "https://example.com"
}
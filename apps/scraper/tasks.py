from celery import shared_task
from django.db import transaction
from .scraper import AmazonScraper
from .models import Product


@shared_task(name="scrape_search_page")
def scrape_search_page(query, page_number, max_pages=3):
    try:
        scraper = AmazonScraper()
        results = scraper.search_for_products(query, max_pages)

        with transaction.atomic():
            for result in results:
                if result["page"] == page_number:
                    product = Product.objects.create(title=result["title"], price=result["price"])

                    scrape_product_details.delay(result["url"], product.id)

        if page_number < max_pages:
            scrape_search_page.delay(query, page_number + 1, max_pages)

        return f"Processed page {page_number} with {len(results)} products"

    except Exception as e:
        print(f"Error processing page {page_number}: {str(e)}")
        return None


@shared_task(bind=True, name="scrape_product_details", max_retries=3)
def scrape_product_details(self, url, product_id):
    try:
        scraper = AmazonScraper()
        details = scraper.get_product_details(url)

        if details:
            with transaction.atomic():
                product = Product.objects.get(id=product_id)
                product.description = details.description
                product.seller = details.seller
                product.rating = details.rating
                product.review_count = details.review_count
                product.images = details.images
                product.status = "completed"
                product.save()

            return f"Updated details for product {product_id}"

    except Product.DoesNotExist:
        print(f"Product {product_id} not found")
        return None
    except Exception as e:
        retry_countdown = 60 * (2**self.request.retries)
        self.retry(exc=e, countdown=retry_countdown)


@shared_task(name="start_amazon_scraping")
def start_amazon_scraping(query, max_pages=3):
    scrape_search_page.delay(query, 1, max_pages)
    return f"Started scraping for query: {query} (max {max_pages} pages)"

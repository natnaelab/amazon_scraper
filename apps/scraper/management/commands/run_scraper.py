from django.core.management.base import BaseCommand
from apps.scraper.tasks import start_amazon_scraping


class Command(BaseCommand):
    help = "Run the scraper using Celery"

    def add_arguments(self, parser):
        parser.add_argument("--query", type=str, help="Search query for Amazon products")
        parser.add_argument("--max-pages", type=int, default=3, help="Maximum number of pages to scrape")

    def handle(self, *args, **options):
        query = options["query"]
        max_pages = options["max_pages"]

        try:
            self.stdout.write(self.style.SUCCESS(f"Starting the scraper for query: {query}..."))
            task = start_amazon_scraping.delay(query, max_pages)
            self.stdout.write(self.style.SUCCESS(f"Scraping task initiated successfully! Task ID: {task.id}"))
            self.stdout.write(self.style.SUCCESS("The scraping process is running in the background."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error initiating scraping task: {str(e)}"))

import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver as sw
from dotenv import load_dotenv


load_dotenv()


class AmazonScraper:
    def __init__(self):
        self.scrapersapi_api_key = os.getenv("SCRAPERSAPI_API_KEY")
        self.proxy_opts = {
            "proxy": {
                "http": os.getenv('HTTP_PROXY'),
                "https": os.getenv('HTTPS_PROXY'),
                "no_proxy": "localhost,127.0.0.1",
            }
        }
        self.chrome_opts = Options()
        self.chrome_opts.add_argument("--no-sandbox")
        self.chrome_opts.add_argument("start-maximized")
        self.chrome_opts.add_argument("--disable-extensions")
        self.chrome_opts.add_argument('--disable-application-cache')
        self.chrome_opts.add_argument('--disable-gpu')
        self.chrome_opts.add_argument("--disable-dev-shm-usage")
        # self.chrome_opts.add_argument("--headless=new")
        self.driver = None
        self.wait = None

    def _init_driver(self):
        if not self.driver:
            self.driver = sw.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.chrome_opts,
                # seleniumwire_options=self.proxy_opts,
            )

    def _quit_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None

    def run(self):
        try:
            self._init_driver()
            self.driver.get("https://www.amazon.com/")
            results = self.search_for_products("laptop", max_pages=3)
            print(results)
        finally:
            if self.driver:
                self.driver.quit()

    def search_for_products(self, query, max_pages=1):
        try:
            self._init_driver()
            self.driver.get("https://www.amazon.com/")

            search_box = self.wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
            search_box.clear()
            search_box.send_keys(query)

            search_button = self.wait.until(EC.element_to_be_clickable((By.ID, "nav-search-submit-button")))
            search_button.click()

            results = []
            current_page = 1

            while current_page <= max_pages:
                products = self.wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
                    )
                )

                for product in products:
                    try:
                        title = product.find_element(By.CSS_SELECTOR, "h2 span").text

                        try:
                            price_element_whole = product.find_element(By.CSS_SELECTOR, "span.a-price-whole")
                            price_element_fraction = product.find_element(By.CSS_SELECTOR, "span.a-price-fraction")
                            price = float(
                                str(price_element_whole.text.replace(",", "")) + "." + str(price_element_fraction.text)
                            )
                        except:
                            price = 0.0

                        url = product.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                        results.append(
                            {"title": title, "price": price, "url": url, "status": "pending", "page": current_page}
                        )
                    except Exception as e:
                        continue

                try:
                    next_button = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a.s-pagination-next"))
                    )

                    if "a-disabled" in next_button.get_attribute("class"):
                        break

                    if current_page < max_pages:
                        next_button.click()
                        self.wait.until(EC.staleness_of(products[0]))
                        current_page += 1
                    else:
                        break
                except Exception as e:
                    print(f"No more pages available or error: {str(e)}")
                    break

            return results

        except Exception as e:
            print(f"Error searching for products: {str(e)}")
            return []
        finally:
            self._quit_driver()

    def get_product_details(self, url):
        try:
            self._init_driver()
            self.driver.get(url)

            title = self.wait.until(EC.presence_of_element_located((By.ID, "productTitle"))).text

            try:
                price_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "span.a-price-whole"))
                )
                price = float(price_element.text.replace(",", ""))
            except:
                price = 0.0

            try:
                description = self.wait.until(EC.presence_of_element_located((By.ID, "productDescription"))).text
            except:
                description = ""

            try:
                seller = self.wait.until(EC.presence_of_element_located((By.ID, "sellerProfileTriggerId"))).text
            except:
                seller = "Amazon.com"

            try:
                rating_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "span.a-icon-alt"))
                ).text
                rating = float(rating_element.split(" ")[0])
            except:
                rating = 0.0

            try:
                review_count_element = self.wait.until(
                    EC.presence_of_element_located((By.ID, "acrCustomerReviewText"))
                ).text
                review_count = int(review_count_element.split(" ")[0].replace(",", ""))
            except:
                review_count = 0

            try:
                image_elements = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#imgTagWrapperId img"))
                )
                images = [img.get_attribute("src") for img in image_elements if img.get_attribute("src")]
            except:
                images = []

            # Create Product instance
            from .models import Product

            product = Product(
                title=title,
                description=description,
                price=price,
                seller=seller,
                rating=rating,
                review_count=review_count,
                images=",".join(images),
            )

            return product
        except Exception as e:
            print(f"Error getting product details: {str(e)}")
            return None
        finally:
            self._quit_driver()

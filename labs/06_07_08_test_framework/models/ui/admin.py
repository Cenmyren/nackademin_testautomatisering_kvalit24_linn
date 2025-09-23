
class AdminPage:
    def __init__(self, page):
        self.page = page

        self.admin_grid_products = page.locator(".product-grid .product-item")
        self.admin_input_product_name = page.get_by_role("textbox", name="Product Name")
        self.admin_btn_add_product = page.get_by_role("button", name="Create Product")

    def get_current_product_count(self):
        return self.admin_grid_products.count()

    def create_product(self, product_name):
        self.admin_input_product_name.fill(product_name)
        self.admin_btn_add_product.click()

    def delete_product_by_name(self, product_name):
        # Find the product item
        product_locator = self.page.locator(".product-item", has_text=product_name)

        # Find the Delete button inside that product item
        delete_button = product_locator.get_by_role("button", name="Delete")

        # Wait until the Delete button is visible and enabled
        delete_button.wait_for(state="visible", timeout=10000)

        # Click the Delete button
        delete_button.click()

        # Wait until the product is removed from the DOM
        deleted_product = self.page.locator(".product-grid .product-item").filter(has_text=product_name)
        deleted_product.wait_for(state="detached", timeout=10000)  # waits until the element disappears

        return deleted_product
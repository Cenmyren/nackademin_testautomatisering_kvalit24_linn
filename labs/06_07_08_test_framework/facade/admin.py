from models.api.admin import AdminAPI
from models.ui.admin import AdminPage
import os

class AdminFacade:
    def __init__(self, page):
        self.page = page
        self.admin_page = AdminPage(page)
        self.base_url = os.getenv("APP_BACK_URL", "http://localhost:8000")
        self.frontend_url = os.getenv("APP_FRONT_URL", "http://localhost:5173/")
        self.api = AdminAPI(base_url=self.base_url)

    def login_via_token(self):
        # Get token from API
        self.api.get_admin_token()

        # Set token in localStorage before page loads
        self.page = self.context.new_page()
        self.context.add_init_script(f"window.localStorage.setItem('token', '{self.api.token}');")

        # Navigate to frontend
        self.page.goto(self.frontend_url)

        # Reinitialize AdminPage with the new page
        self.admin_page = AdminPage(self.page)

        # Wait for admin page to render
        self.page.locator(".product-grid, .some-admin-header").wait_for(state="visible", timeout=15000)


    def create_product_for_test_via_api(self, product_name):
        response = self.api.create_product(product_name)
        assert response.status_code == 200, "Failed to create product via API"
        self.page.goto(self.frontend_url) # update page to see new product
        return product_name
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
        self.api.get_admin_token() # call api-model

        # Clear localStorage and set token before page loads
        self.page.add_init_script("""
        window.localStorage.clear();
        window.localStorage.setItem('token', '%s');
        """ % self.api.token)

        self.page.goto(self.frontend_url) # load frontend

        # error check, can remove later
        response = self.page.evaluate("""async () => {
            const res = await fetch('/products', {
                headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
            });
            return res.status;
        }""")
        print("Products fetch status:", response)

        self.page.locator(".product-grid, .some-admin-header").wait_for(state="visible", timeout=15000)


    def create_product_for_test_via_api(self, product_name):
        response = self.api.create_product(product_name)
        assert response.status_code == 200, "Failed to create product via API"
        self.page.goto(self.frontend_url) # update page to see new product
        return product_name
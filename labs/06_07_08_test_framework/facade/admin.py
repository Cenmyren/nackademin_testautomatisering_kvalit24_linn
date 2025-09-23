from models.api.admin import AdminAPI
from models.ui.admin import AdminPage
import os
import time

class AdminFacade:
    def __init__(self, page):
        self.page = page
        self.admin_page = AdminPage(page)
        self.base_url = os.getenv("APP_BACK_URL", "http://localhost:8000")
        self.frontend_url = os.getenv("APP_FRONT_URL", "http://localhost:5173/")
        self.api = AdminAPI(base_url=self.base_url)

    def login_via_token(self):
        # 1. Get token from API
        self.api.get_admin_token()
        assert self.api.token, "No token received from API"

        # 2. Inject token BEFORE SPA scripts run
        self.page.add_init_script(
            f"window.localStorage.setItem('token', '{self.api.token}')"
        )

        # 3. Go to the frontend root (SPA entry)
        self.page.goto(self.frontend_url, wait_until="networkidle")

        # 4. Debug: show URL and localStorage
        print("Page URL after goto:", self.page.url)
        local_storage = self.page.evaluate("() => Object.assign({}, window.localStorage)")
        print("localStorage content:", local_storage)

        # 5. Wait for the SPA to render the admin page
        # Instead of assuming .product-grid appears immediately, poll the DOM
        timeout = 30
        interval = 1
        elapsed = 0
        while elapsed < timeout:
            grids = self.page.query_selector_all(".product-grid")
            if grids:
                print("✅ Logged in and product grid is visible")
                return
            time.sleep(interval)
            elapsed += interval

        # 6. If timeout, raise error with HTML snapshot
        html = self.page.content()
        print("⚠️ Product grid not found. Current HTML head snippet:\n", html[:500])
        raise TimeoutError("Product grid did not appear within 30s")


    # def login_via_token(self):
    #     # 1. Get token from API
    #     self.api.get_admin_token()
    #     assert self.api.token, "No token received from API"

    #     # 2. Inject token BEFORE navigation
    #     self.page.add_init_script(
    #         f"window.localStorage.setItem('token', '{self.api.token}')"
    #     )

    #     # 3. Go to frontend and wait until network idle
    #     self.page.goto(self.frontend_url, wait_until="networkidle")

    #     time.sleep(1)

    #     print("Page URL after goto:", self.page.url)
    #     print("HTML content head snippet:", self.page.inner_html("head"))
    #     print(self.page.evaluate("() => Object.assign({}, window.localStorage)"))

    #     # 4. Verify token is actually in localStorage
    #     browser_token = self.page.evaluate("() => window.localStorage.getItem('token')")
    #     assert browser_token == self.api.token, f"Token mismatch! Browser: {browser_token}"

    #     # 5. Wait for the product grid container to appear
    #     self.page.wait_for_selector(".product-grid", timeout=30000)
    #     print("✅ Logged in and product grid is visible")

    def create_product_for_test_via_api(self, product_name):
        # 1. Create product via API
        response = self.api.create_product(product_name)
        assert response.status_code == 200, f"Failed to create product via API: {response.text}"

        # 2. Refresh frontend to see new product
        self.page.goto(self.frontend_url, wait_until="networkidle")

        # 3. Wait until the new product appears in the grid
        timeout = 30
        interval = 1
        elapsed = 0
        while elapsed < timeout:
            items = self.admin_page.admin_grid_products.all()
            names = [item.inner_text() for item in items]
            if product_name in names:
                print(f"✅ Product '{product_name}' is visible in the grid")
                return product_name
            time.sleep(interval)
            elapsed += interval

        # If not found after timeout
        raise TimeoutError(f"Product '{product_name}' did not appear in the frontend after {timeout} seconds")



# from models.api.admin import AdminAPI
# from models.ui.admin import AdminPage
# import os

# class AdminFacade:
#     def __init__(self, page):
#         self.page = page
#         self.admin_page = AdminPage(page)
#         self.base_url = os.getenv("APP_BACK_URL", "http://localhost:8000")
#         self.frontend_url = os.getenv("APP_FRONT_URL", "http://localhost:5173/")
#         self.api = AdminAPI(base_url=self.base_url)

    
#     def login_via_token(self):
#         self.api.get_admin_token() # call api-model
#         self.page.add_init_script(f""" window.localStorage.setItem('token', '{self.api.token}')""") # put token directly in local storage
#         self.page.goto(self.frontend_url) # load frontend


#     def create_product_for_test_via_api(self, product_name):
#         response = self.api.create_product(product_name)
#         assert response.status_code == 200, "Failed to create product via API"
#         self.page.goto(self.frontend_url) # update page to see new product
#         return product_name
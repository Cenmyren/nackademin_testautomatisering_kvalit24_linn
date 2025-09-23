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
        # 1️⃣ Get token from API
        self.api.get_admin_token()
        assert self.api.token, "No token received from API"

        # 2️⃣ Inject token BEFORE SPA scripts run
        self.page.add_init_script(
            f"window.localStorage.setItem('token', '{self.api.token}')"
        )

        # 3️⃣ Go to the SPA root
        self.page.goto(self.frontend_url, wait_until="domcontentloaded")

        # 4️⃣ Poll for .product-grid (admin view) to appear
        timeout = 30  # seconds
        interval = 1  # seconds
        elapsed = 0
        while elapsed < timeout:
            grids = self.page.query_selector_all(".product-grid")
            if grids:
                print("✅ Logged in via token and product grid is visible")
                return
            time.sleep(interval)
            elapsed += interval

        # 5️⃣ Timeout error with snapshot
        html = self.page.content()
        print("⚠️ Product grid did not appear. Current HTML snippet:\n", html[:500])
        raise TimeoutError("Product grid did not appear within 30s")



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
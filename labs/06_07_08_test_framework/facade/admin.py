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
        # 1️⃣ Get admin token from API
        self.api.get_admin_token()

        # 2️⃣ Intercept frontend API calls to localhost:8000
        #    and redirect them to your backend container
        self.page.route("http://localhost:8000/*", 
            lambda route: route.continue_(url=route.request.url.replace("localhost", "app-backend"))
        )

        # 3️⃣ Clear local storage
        self.page.add_init_script("window.localStorage.clear()")

        # 4️⃣ Insert token directly into local storage
        self.page.add_init_script(f"""window.localStorage.setItem('token', '{self.api.token}')""")

        # 5️⃣ Load frontend
        self.page.goto(self.frontend_url)

        # 6️⃣ Optional: reload to ensure JS picks up token
        self.page.reload()


    def create_product_for_test_via_api(self, product_name):
        response = self.api.create_product(product_name)
        assert response.status_code == 200, "Failed to create product via API"
        self.page.goto(self.frontend_url) # update page to see new product
        return product_name
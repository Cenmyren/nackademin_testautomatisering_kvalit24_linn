import os
from libs.utils import generate_string_with_prefix
from models.ui.home import HomePage
from models.ui.signup import SignupPage
from models.api.user import UserAPI

class UsersFacade:
    def __init__(self, page):
        self.page = page
        self.signup_page = SignupPage(page)
        self.login_page = HomePage(page)
        self.base_url = os.getenv("APP_BACK_URL", "http://localhost:8000")
        self.frontend_url = os.getenv("APP_FRONT_URL", "http://app-frontend:80")
        self.user_api = UserAPI(self.base_url)

    def login_as_new_user(self):
        username = generate_string_with_prefix("user")
        password = "password123"

        # Navigate explicitly to frontend
        self.page.goto(self.frontend_url, wait_until="networkidle")

        self.login_page.go_to_signup()
        self.signup_page.signup(username, password)
        self.signup_page.go_to_home()

        self.login_page.login(username, password)
        return username, password

    def login_via_token(self, username, password):
        # Call API login
        self.user_api.login(username, password)
        token = self.user_api.token

        # Set token in localStorage before page load
        self.page.add_init_script(f"""window.localStorage.setItem('token', '{token}')""")
        self.page.goto(self.frontend_url, wait_until="networkidle")

    def get_user_products_names(self):
        response = self.user_api.get_user_products()
        return [p["name"] for p in response.json()["products"]]
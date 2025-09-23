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
        self.frontend_url = os.getenv("APP_FRONT_URL", "http://localhost:5173/")
        self.user_api = UserAPI(self.base_url)

    def login_as_new_user(self):
        username = generate_string_with_prefix("user")
        password = "password123"

        # Detect environment: local vs Jenkins
        backend_host = "app-backend" if os.getenv("CI") else "localhost"

        # Add reroute so frontend API calls go to the right backend
        self.page.route("http://localhost:8000/*",
            lambda route: route.continue_(
                url=route.request.url.replace("localhost", backend_host)
            ))

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

        # Detect environment: local vs Jenkins
        backend_host = "app-backend" if os.getenv("CI") else "localhost"

        # Intercept API calls and reroute if needed
        self.page.route("http://localhost:8000/*",
            lambda route: route.continue_(
                url=route.request.url.replace("localhost", backend_host)
            )
        )

        # Set token in localStorage before page load
        self.page.add_init_script("window.localStorage.clear()")
        self.page.add_init_script(f"""window.localStorage.setItem('token', '{token}')""")
        self.page.goto(self.frontend_url, wait_until="networkidle")
        self.page.reload()

    def get_user_products_names(self):
        response = self.user_api.get_user_products()
        return [p["name"] for p in response.json()["products"]]
    

# import os
# import libs.utils
# from models.api.user import UserAPI
# import pytest

# BACKEND_URL = os.getenv("APP_BACK_URL", "http://localhost:8000")

# def test_signup():
    
#     # GIVEN I AM A NEW POTENTIAL CUSTOMER
#     username = libs.utils.generate_string_with_prefix()
#     password = "test_1234?"

#     user_api = UserAPI(BACKEND_URL)

#     # WHEN I SIGNUP IN THE APP
#     signup_api_response = user_api.signup(username, password)
#     assert signup_api_response.status_code == 200

#     # THEN I SHOULD BE ABLE TO LOG IN WITH MY NEW USER
#     login_api_response = user_api.login(username, password)
#     assert login_api_response.status_code == 200

#     login_data = login_api_response.json()
#     assert "access_token" in login_data, "API response did not include a token"
#     assert login_data["access_token"], "Access token is empty"


# def test_login():

#     # GIVEN I AM AN AUTHENTICATHED USER
#     # (Assumes this user already exists in the DB)
#     username = "user_1"
#     password = "pass_1"

#     user_api = UserAPI(BACKEND_URL)

#     # WHEN I LOG INTO THE APPLICATION
#     login_response = user_api.login(username, password)
#     assert login_response.status_code == 200
#     assert user_api.token is not None, "No token stored after login"

#     # THEN I SHOULD SEE ALL MY PRODUCTS
#     products_response = user_api.get_user_products()
#     assert products_response.status_code == 200
#     assert "products" in products_response.json(), "Products key not found in response"

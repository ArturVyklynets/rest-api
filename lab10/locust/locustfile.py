from locust import HttpUser, task, between

class LibraryUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        response = self.client.post("/token", data={
            "username": "testusername",
            "password": "testpass"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            print("Failed to get access token")

    @task
    def get_books(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        self.client.get("/books?limit=5&cursor=0", headers=headers)

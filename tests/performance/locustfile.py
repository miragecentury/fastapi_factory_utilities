"""Provides locust performance tests for the API."""

from locust import HttpUser, constant_throughput, task  # pyright: ignore


class SystemUser(HttpUser):
    """Provides locust performance tests for the API."""

    wait_time = constant_throughput(1)  # pyright: ignore

    @task(1)
    def health(self) -> None:
        """Get the health of the system."""
        self.client.get("/api/v1/sys/health")

    @task(1)
    def readiness(self) -> None:
        """Get the readiness of the system."""
        self.client.get("/api/v1/sys/readiness")


class BookUser(HttpUser):
    """Provides locust performance tests for the API."""

    wait_time = constant_throughput(1)  # pyright: ignore

    @task(10)
    def get_books(self) -> None:
        """Get all books."""
        self.client.get("/api/v1/books")

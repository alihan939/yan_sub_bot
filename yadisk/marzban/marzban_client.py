from marzban.api import MarzbanAPI
from marzban.models import UserResponse

class MarzbanClient:
    def __init__(self, config):
        protocol = "https" if config.ssl else "http"
        base_url = f"{protocol}://{config.host}:{config.port}"
        self.api = MarzbanAPI(base_url=base_url)
        self.username = config.username
        self.password = config.password
        
    async def connect(self):
        await self.api.connect(self.username, self.password)
        
    async def sync_data(self):
        await self.connect()
        
    async def get_user(self, username: str) -> UserResponse | None:
        return await self.api.get_user(username)
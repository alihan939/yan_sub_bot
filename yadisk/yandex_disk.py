import httpx

class YandexDiskClient:
    def __init__(self, oauth_token: str):
        self.base_url = "https://cloud-api.yandex.net/v1/disk"
        self.headers = {"Authorization": f"OAuth {oauth_token}"}
        
    async def upload_and_publish(self, path: str, content: str) -> str:
        async with httpx.AsyncClient() as client:
            # Загрузка файла
            upload_url = f"{self.base_url}/resources/upload?path={path}&overwrite=true"
            response = await client.get(upload_url, headers=self.headers)
            upload_href = response.json()["href"]
            
            await client.put(upload_href, content=content.encode())
            
            # Публикация файла
            publish_url = f"{self.base_url}/resources/publish?path={path}"
            await client.put(publish_url, headers=self.headers)
            
            # Получение публичной ссылки
            meta_url = f"{self.base_url}/resources?path={path}"
            meta = await client.get(meta_url, headers=self.headers)
            return meta.json()["public_url"]

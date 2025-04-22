import httpx
from .models import *


class MarzbanAPI:
    def __init__(self, base_url: str):
        self.password = ''
        self.username = ''
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
        self.token = ''

    def _get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    async def _request(self, method: str, url: str, data: Optional[BaseModel] = None,
                       params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        headers = self._get_headers()
        json_data = data.model_dump(exclude_none=True) if data else None
        params = {par: params[par] for par in params.keys() if params[par]} if params else {}
        # try:
        response = await self.client.request(method, url, headers=headers, json=json_data, params=params)
        # except httpx.ConnectError as ex:
        #     probably disconnected from marzban
        #     return httpx.Response(status_code=200, json=json.loads('{}'))

        if response.status_code == 401:
            # try:
            await self.connect(username=self.username, password=self.password)
            # except Exception:
            #     # probably disconnected from marzban
            #     return httpx.Response(status_code=200, json=json.loads('{}'))
            response = await self._request(method=method, url=url, data=data, params=params)
            return response
        return response

    async def connect(self, username: str, password: str) -> str:
        self.username = username
        self.password = password
        url = "/api/admin/token"
        payload = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
        response = await self.client.post(url, data=payload)
        if response.status_code == 401:
            raise Exception(f'Failed to connect to Marzban: incorrect username or password')
        response.raise_for_status()
        self.token = Token(**response.json()).access_token
        return self.token

    async def get_current_admin(self) -> Admin:
        url = "/api/admin"
        response = await self._request("GET", url)
        return Admin(**response.json())

    async def create_admin(self, admin: AdminCreate) -> Admin:
        url = "/api/admin"
        response = await self._request("POST", url, data=admin)
        return Admin(**response.json())

    async def modify_admin(self, username: str, admin: AdminModify) -> Admin:
        url = f"/api/admin/{username}"
        response = await self._request("PUT", url, data=admin)
        return Admin(**response.json())

    async def remove_admin(self, username: str) -> None:
        url = f"/api/admin/{username}"
        await self._request("DELETE", url)

    async def get_admins(self, offset: Optional[int] = None, limit: Optional[int] = None,
                         username: Optional[str] = None) -> List[Admin]:
        url = "/api/admins"
        params = {"offset": offset, "limit": limit, "username": username}
        response = await self._request("GET", url, params=params)
        return [Admin(**admin) for admin in response.json()]

    async def get_system_stats(self) -> SystemStats:
        url = "/api/system"
        response = await self._request("GET", url)
        return SystemStats(**response.json())

    async def get_inbounds(self) -> Dict[str, List[ProxyInbound]]:
        url = "/api/inbounds"
        response = await self._request("GET", url)
        return response.json()

    async def get_hosts(self) -> Dict[str, List[ProxyHost]]:
        url = "/api/hosts"
        response = await self._request("GET", url)
        return response.json()

    async def modify_hosts(self, hosts: Dict[str, List[ProxyHost]]) -> Dict[str, List[ProxyHost]]:
        url = "/api/hosts"
        response = await self._request("PUT", url=url, data=hosts)
        return response.json()

    async def get_core_stats(self) -> CoreStats:
        url = "/api/core"
        response = await self._request("GET", url)
        return CoreStats(**response.json())

    async def restart_core(self) -> None:
        url = "/api/core/restart"
        await self._request("POST", url)

    async def get_core_config(self) -> Dict[str, Any]:
        url = "/api/core/config"
        response = await self._request("GET", url)
        return response.json()

    async def modify_core_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        url = "/api/core/config"
        response = await self._request("PUT", url, data=config)
        return response.json()

    async def add_user(self, user: UserCreate) -> UserResponse:
        url = "/api/user"
        response = await self._request("POST", url, data=user)
        return UserResponse(**response.json())

    async def get_user(self, username: str) -> UserResponse | None:
        url = f"/api/user/{username}"
        response = await self._request("GET", url)
        if response.status_code == 200:
            # print(response.json())
            return UserResponse(**response.json())
        else:
            return None

    async def get_users_by_admin(self, admin: str) -> list[UserResponse] | None:
        url = f"/api/users"
        params = {"admin": admin}
        try:
            response = await self._request("GET", url, params=params)
            if response.status_code == 200:
                return [UserResponse(**user) for user in response.json()['users']]
            else:
                return None
        except Exception:
            return None

    async def modify_user(self, username: str, user: UserModify) -> UserResponse:
        url = f"/api/user/{username}"
        response = await self._request("PUT", url, data=user)
        return UserResponse(**response.json())

    async def remove_user(self, username: str) -> None:
        url = f"/api/user/{username}"
        await self._request("DELETE", url)

    async def reset_user_data_usage(self, username: str) -> UserResponse:
        url = f"/api/user/{username}/reset"
        response = await self._request("POST", url)
        return UserResponse(**response.json())

    async def revoke_user_subscription(self, username: str) -> UserResponse:
        url = f"/api/user/{username}/revoke_sub"
        response = await self._request("POST", url)
        return UserResponse(**response.json())

    async def get_users(self, offset: Optional[int] = None, limit: Optional[int] = None,
                        username: Optional[List[str]] = None, status: Optional[str] = None,
                        sort: Optional[str] = None, admin: Optional[str] = None) -> list[UserResponse] | None:
        url = "/api/users"
        params = {"offset": offset, "limit": limit, "username": username, "status": status, "sort": sort, "admin": admin}
        response = await self._request("GET", url, params=params)
        if response.status_code == 200:
            return [UserResponse(**user) for user in response.json()['users']]
        else:
            return None

    async def reset_users_data_usage(self) -> None:
        url = "/api/users/reset"
        await self._request("POST", url)

    async def get_user_usage(self, username: str, start: Optional[str] = None,
                             end: Optional[str] = None) -> UserUsagesResponse:
        url = f"/api/user/{username}/usage"
        params = {"start": start, "end": end}
        response = await self._request("GET", url, params=params)
        return UserUsagesResponse(**response.json())

    async def set_owner(self, username: str, admin_username: str) -> UserResponse:
        url = f"/api/user/{username}/set-owner"
        params = {"admin_username": admin_username}
        response = await self._request("PUT", url, params=params)
        return UserResponse(**response.json())

    async def get_expired_users(self, expired_before: Optional[str] = None, expired_after: Optional[str] = None) -> \
    List[str]:
        url = "/api/users/expired"
        params = {"expired_before": expired_before, "expired_after": expired_after}
        response = await self._request("GET", url, params=params)
        return response.json()

    async def delete_expired_users(self, expired_before: Optional[str] = None, expired_after: Optional[str] = None) -> \
    List[str]:
        url = "/api/users/expired"
        params = {"expired_before": expired_before, "expired_after": expired_after}
        response = await self._request("DELETE", url, params=params)
        return response.json()

    async def get_user_templates(self, offset: Optional[int] = None, limit: Optional[int] = None) -> List[
        UserTemplateResponse]:
        url = "/api/user_template"
        params = {"offset": offset, "limit": limit}
        response = await self._request("GET", url, params=params)
        return [UserTemplateResponse(**template) for template in response.json()]

    async def add_user_template(self, template: UserTemplateCreate) -> UserTemplateResponse:
        url = "/api/user_template"
        response = await self._request("POST", url, data=template)
        return UserTemplateResponse(**response.json())

    async def get_user_template(self, template_id: int) -> UserTemplateResponse:
        url = f"/api/user_template/{template_id}"
        response = await self._request("GET", url)
        return UserTemplateResponse(**response.json())

    async def modify_user_template(self, template_id: int, template: UserTemplateModify) -> UserTemplateResponse:
        url = f"/api/user_template/{template_id}"
        response = await self._request("PUT", url, data=template)
        return UserTemplateResponse(**response.json())

    async def remove_user_template(self, template_id: int) -> None:
        url = f"/api/user_template/{template_id}"
        await self._request("DELETE", url)

    async def get_node_settings(self) -> Dict[str, Any]:
        url = "/api/node/settings"
        response = await self._request("GET", url)
        return response.json()

    async def add_node(self, node: NodeCreate) -> NodeResponse:
        url = "/api/node"
        response = await self._request("POST", url, data=node)
        return NodeResponse(**response.json())

    async def get_node(self, node_id: int) -> NodeResponse:
        url = f"/api/node/{node_id}"
        response = await self._request("GET", url)
        return NodeResponse(**response.json())

    async def modify_node(self, node_id: int, node: NodeModify) -> NodeResponse:
        url = f"/api/node/{node_id}"
        response = await self._request("PUT", url, data=node)
        return NodeResponse(**response.json())

    async def remove_node(self, node_id: int) -> None:
        url = f"/api/node/{node_id}"
        await self._request("DELETE", url)

    async def reconnect_node(self, node_id: int) -> None:
        url = f"/api/node/{node_id}/reconnect"
        await self._request("POST", url)

    async def get_nodes(self) -> List[NodeResponse]:
        url = "/api/nodes"
        response = await self._request("GET", url)
        return [NodeResponse(**node) for node in response.json()]

    async def get_usage(self, start: Optional[str] = None, end: Optional[str] = None) -> NodesUsageResponse:
        url = "/api/nodes/usage"
        params = {"start": start, "end": end}
        response = await self._request("GET", url, params=params)
        return NodesUsageResponse(**response.json())

    async def close(self):
        await self.client.aclose()

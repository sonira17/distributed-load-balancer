import httpx
from logger import logger 
class HealthChecker:
    async def is_healthy(self,server:str)->bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{server}/health",
                    timeout=2
                )

                return response.status_code == 200

        except httpx.RequestError:
            logger.warning(
                f"server {server} is not healthy"
            )
            return False

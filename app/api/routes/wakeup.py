from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.api.schemas import WakeupResponse, WakeupTriggerRequest
from app.container import Container
from app.services.wakeup_service import WakeupService

router = APIRouter()


@router.post("/wakeup/trigger", response_model=WakeupResponse)
@inject
async def trigger_wakeup(
    body: WakeupTriggerRequest,
    demo: bool = False,
    service: WakeupService = Depends(Provide[Container.wakeup_service]),
) -> WakeupResponse:
    result = await service.trigger_wakeup(
        body.user_id,
        body.day_of_week,
        body.weather,
        demo=demo,
    )
    return WakeupResponse.from_result(result)

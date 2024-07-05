from .statistics import router as statistics_router
from .satellite import router as satellite_router
from .mines import router as mines_router
from .gee import router as gee_router

all_routers = [
    statistics_router,
    satellite_router,
    mines_router,
    gee_router,
]

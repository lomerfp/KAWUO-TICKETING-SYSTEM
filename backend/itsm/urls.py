from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssetViewSet,
    DepartmentViewSet,
    KnowledgeArticleViewSet,
    LoginView,
    MaintenanceRecordViewSet,
    NotificationViewSet,
    RegisterView,
    ServiceRequestViewSet,
    TicketViewSet,
    StaffDepartmentViewSet,
    TicketCategoryViewSet,
    TicketPriorityViewSet,
    dashboard_summary,
    me,
    ticket_report,
)

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="departments")
router.register(r"ticket-departments", StaffDepartmentViewSet, basename="ticket-departments")
router.register(r"categories", TicketCategoryViewSet, basename="categories")
router.register(r"priorities", TicketPriorityViewSet, basename="priorities")
router.register(r"tickets", TicketViewSet, basename="tickets")
router.register(r"assets", AssetViewSet, basename="assets")
router.register(r"maintenance", MaintenanceRecordViewSet, basename="maintenance")
router.register(r"service-requests", ServiceRequestViewSet, basename="service-requests")
router.register(r"knowledge-base", KnowledgeArticleViewSet, basename="knowledge-base")
router.register(r"notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/me/", me, name="me"),
    path("dashboard/summary/", dashboard_summary, name="dashboard-summary"),
    path("reports/tickets.csv", ticket_report, name="ticket-report"),
    path("", include(router.urls)),
]

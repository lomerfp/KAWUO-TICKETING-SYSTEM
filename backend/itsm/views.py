from datetime import timedelta
import csv

from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Asset, Department, KnowledgeArticle, MaintenanceRecord, Notification, ServiceRequest, Ticket, TicketCategory, TicketComment, TicketPriority, User
from .permissions import IsITAdminUser, IsITSupportUser, IsManagementUser, IsOwnerOrSupport
from .serializers import (
    AssetSerializer,
    DepartmentSerializer,
    KnowledgeArticleSerializer,
    LoginSerializer,
    MaintenanceRecordSerializer,
    NotificationSerializer,
    ServiceRequestSerializer,
    TicketCategorySerializer,
    TicketCommentSerializer,
    TicketCreateSerializer,
    TicketPrioritySerializer,
    TicketSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


def create_notification(user, title, message):
    if user is None:
        return None
    return Notification.objects.create(user=user, title=title, message=message)


def health_check(request):
    return JsonResponse({"status": "ok"})


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    tickets = Ticket.objects.all()
    user = request.user

    if user.role == "staff":
        tickets = tickets.filter(requester=user)

    data = {
        "total_tickets": tickets.count(),
        "open_tickets": tickets.filter(status__in=["NEW", "ACKNOWLEDGED", "ASSIGNED", "IN_PROGRESS", "WAITING_FOR_USER"]).count(),
        "resolved_tickets": tickets.filter(status="RESOLVED").count(),
        "closed_tickets": tickets.filter(status="CLOSED").count(),
        "critical_tickets": tickets.filter(priority__name="CRITICAL").count(),
        "by_status": list(tickets.values("status").annotate(count=Count("id")).order_by("status")),
        "recent_tickets": TicketSerializer(tickets[:5], many=True).data,
    }
    return Response(data)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsITAdminUser]


class TicketCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TicketCategory.objects.filter(is_active=True).order_by("name")
    serializer_class = TicketCategorySerializer
    permission_classes = [IsAuthenticated]


class TicketPriorityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TicketPriority.objects.all().order_by("response_hours")
    serializer_class = TicketPrioritySerializer
    permission_classes = [IsAuthenticated]


class StaffDepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.filter(is_active=True).order_by("name")
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


@api_view(["GET"])
@permission_classes([IsITSupportUser])
def ticket_report(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="kawuo-ticket-report.csv"'
    writer = csv.writer(response)
    writer.writerow(["Ticket", "Title", "Requester", "Department", "Category", "Priority", "Status", "Assigned To", "Created", "Resolved", "Resolution"])

    def csv_value(value):
        value = "" if value is None else str(value)
        if value.startswith(("=", "+", "-", "@", "\t", "\r")):
            return "'" + value
        return value

    tickets = Ticket.objects.select_related(
        "requester", "department", "category", "priority", "assigned_to"
    ).order_by("-created_at")
    for ticket in tickets.iterator():
        writer.writerow([csv_value(value) for value in [
            ticket.ticket_number,
            ticket.title,
            ticket.requester.username,
            ticket.department.name,
            ticket.category.name,
            ticket.priority.name,
            ticket.get_status_display(),
            ticket.assigned_to.username if ticket.assigned_to else "",
            ticket.created_at.isoformat(),
            ticket.date_resolved.isoformat() if ticket.date_resolved else "",
            ticket.resolution,
        ]])
    return response


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("requester", "department", "category", "priority", "assigned_to").prefetch_related("comments").all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSupport]

    def get_queryset(self):
        user = self.request.user
        if user.role in {"it_support", "it_admin", "management"}:
            return Ticket.objects.select_related("requester", "department", "category", "priority", "assigned_to").prefetch_related("comments").all()
        return Ticket.objects.select_related("requester", "department", "category", "priority", "assigned_to").prefetch_related("comments").filter(requester=user)

    def get_permissions(self):
        if self.action in {"acknowledge", "assign", "resolve", "close", "reopen"}:
            return [IsITSupportUser()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return TicketCreateSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        ticket = serializer.save(requester=self.request.user)
        for user in User.objects.filter(role__in=["it_support", "it_admin", "management"]):
            create_notification(
                user,
                "New ticket created",
                f"Ticket {ticket.ticket_number} was submitted by {self.request.user.get_full_name() or self.request.user.username}.",
            )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def acknowledge(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = "ACKNOWLEDGED"
        if not ticket.date_acknowledged:
            ticket.date_acknowledged = timezone.now()
        if not ticket.sla_deadline:
            ticket.sla_deadline = timezone.now() + timedelta(hours=ticket.priority.response_hours)
        ticket.save()
        create_notification(ticket.requester, "Ticket acknowledged", f"Your ticket {ticket.ticket_number} is being reviewed by IT.")
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketCommentSerializer(data={"body": request.data.get("body")})
        if serializer.is_valid():
            TicketComment.objects.create(ticket=ticket, author=request.user, body=serializer.validated_data["body"])
            recipient = ticket.requester if request.user != ticket.requester else ticket.assigned_to
            if recipient and recipient != request.user:
                create_notification(recipient, "Ticket update", f"A new comment was added to {ticket.ticket_number}.")
            return Response({"status": "comment added"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsITSupportUser])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        assignee_id = request.data.get("assigned_to")
        if not assignee_id:
            return Response({"error": "assigned_to is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            assignee = User.objects.get(pk=assignee_id, role__in=["it_support", "it_admin"], is_active=True)
        except User.DoesNotExist:
            return Response({"error": "Select an active IT support user."}, status=status.HTTP_400_BAD_REQUEST)
        ticket.assigned_to = assignee
        ticket.status = "ASSIGNED"
        if not ticket.date_assigned:
            ticket.date_assigned = timezone.now()
        if not ticket.sla_deadline:
            ticket.sla_deadline = timezone.now() + timedelta(hours=ticket.priority.response_hours)
        ticket.save()
        create_notification(ticket.requester, "Ticket assigned", f"Ticket {ticket.ticket_number} has been assigned to {assignee.get_full_name() or assignee.username}.")
        create_notification(assignee, "Ticket assigned to you", f"You have been assigned ticket {ticket.ticket_number}.")
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=["post"], permission_classes=[IsITSupportUser])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        resolution = request.data.get("resolution", "").strip()
        if not resolution:
            return Response({"error": "resolution is required"}, status=status.HTTP_400_BAD_REQUEST)
        ticket.status = "RESOLVED"
        ticket.date_resolved = timezone.now()
        ticket.resolution = resolution
        ticket.technical_notes = request.data.get("technical_notes", ticket.technical_notes)
        if not ticket.sla_deadline:
            ticket.sla_deadline = timezone.now()
        ticket.save()
        if ticket.resolution:
            TicketComment.objects.create(ticket=ticket, author=request.user, body=f"Resolution: {ticket.resolution}")
        create_notification(ticket.requester, "Ticket resolved", f"Ticket {ticket.ticket_number} has been resolved. Please confirm completion.")
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=["post"], permission_classes=[IsITSupportUser])
    def close(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status != "RESOLVED":
            return Response({"error": "Only resolved tickets can be closed."}, status=status.HTTP_400_BAD_REQUEST)
        ticket.status = "CLOSED"
        ticket.date_closed = timezone.now()
        ticket.save()
        create_notification(ticket.requester, "Ticket closed", f"Ticket {ticket.ticket_number} has been closed.")
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=["post"], permission_classes=[IsITSupportUser])
    def reopen(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status in {"RESOLVED", "CLOSED"}:
            ticket.status = "IN_PROGRESS"
            ticket.date_closed = None
            ticket.save()
            return Response(TicketSerializer(ticket).data)
        return Response({"error": "Only resolved or closed tickets can be reopened."}, status=status.HTTP_400_BAD_REQUEST)


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related("assigned_user", "department").all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRecord.objects.select_related("asset", "technician").all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [IsAuthenticated, IsITSupportUser]


class ServiceRequestViewSet(viewsets.ModelViewSet):
    queryset = ServiceRequest.objects.select_related("requester", "department").all()
    serializer_class = ServiceRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in {"it_support", "it_admin", "management"}:
            return ServiceRequest.objects.select_related("requester", "department").all()
        return ServiceRequest.objects.select_related("requester", "department").filter(requester=user)


class KnowledgeArticleViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeArticle.objects.select_related("author").filter(is_published=True)
    serializer_class = KnowledgeArticleSerializer
    permission_classes = [IsAuthenticated]


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.filter(is_read=False).order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

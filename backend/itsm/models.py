from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = (
        ("staff", "Staff"),
        ("it_support", "IT Support"),
        ("it_admin", "IT Administrator"),
        ("management", "Management"),
    )

    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="staff")
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name="users")
    phone_number = models.CharField(max_length=30, blank=True)
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"


class TicketCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TicketPriority(models.Model):
    name = models.CharField(max_length=30, unique=True)
    response_hours = models.IntegerField(default=24)
    sla_color = models.CharField(max_length=20, default="#4f46e5")

    def __str__(self):
        return self.name


class TicketStatus(models.Model):
    name = models.CharField(max_length=30, unique=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    STATUS_CHOICES = (
        ("NEW", "New"),
        ("ACKNOWLEDGED", "Acknowledged"),
        ("ASSIGNED", "Assigned"),
        ("IN_PROGRESS", "In Progress"),
        ("WAITING_FOR_USER", "Waiting for User"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
    )

    ticket_number = models.CharField(max_length=30, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="requested_tickets", on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="tickets")
    category = models.ForeignKey(TicketCategory, on_delete=models.PROTECT, related_name="tickets")
    priority = models.ForeignKey(TicketPriority, on_delete=models.PROTECT, related_name="tickets")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="NEW")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="assigned_tickets", on_delete=models.SET_NULL)
    sla_deadline = models.DateTimeField(null=True, blank=True)
    date_acknowledged = models.DateTimeField(null=True, blank=True)
    date_assigned = models.DateTimeField(null=True, blank=True)
    date_resolved = models.DateTimeField(null=True, blank=True)
    date_closed = models.DateTimeField(null=True, blank=True)
    resolution = models.TextField(blank=True)
    root_cause = models.TextField(blank=True)
    technical_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            year = timezone.now().year
            prefix = f"KAWUO-IT-{year}-"
            last_ticket = Ticket.objects.filter(ticket_number__startswith=prefix).order_by("-ticket_number").first()
            next_number = 1
            if last_ticket:
                suffix = last_ticket.ticket_number.split("-")[-1]
                if suffix.isdigit():
                    next_number = int(suffix) + 1
            self.ticket_number = f"{prefix}{next_number:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number}: {self.title}"


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.ticket.ticket_number}"


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name="attachments", on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to="ticket_attachments/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.ticket.ticket_number}"


class Asset(models.Model):
    STATUS_CHOICES = (
        ("IN_STOCK", "In Stock"),
        ("ASSIGNED", "Assigned"),
        ("IN_REPAIR", "In Repair"),
        ("UNDER_MAINTENANCE", "Under Maintenance"),
        ("LOST", "Lost"),
        ("RETIRED", "Retired"),
        ("DISPOSED", "Disposed"),
    )

    asset_id = models.CharField(max_length=50, unique=True)
    asset_tag = models.CharField(max_length=50, unique=True)
    serial_number = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    warranty_end = models.DateField(null=True, blank=True)
    condition = models.CharField(max_length=50, default="GOOD")
    location = models.CharField(max_length=150, blank=True)
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="assigned_assets", on_delete=models.SET_NULL)
    department = models.ForeignKey(Department, null=True, blank=True, related_name="assets", on_delete=models.SET_NULL)
    supplier = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="IN_STOCK")
    operating_system = models.CharField(max_length=150, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.asset_tag or self.asset_id


class MaintenanceRecord(models.Model):
    asset = models.ForeignKey(Asset, related_name="maintenance_records", on_delete=models.CASCADE)
    maintenance_type = models.CharField(max_length=50, default="preventive")
    date = models.DateField(default=timezone.now)
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="maintenance_records", on_delete=models.SET_NULL, null=True, blank=True)
    problem = models.TextField()
    work_performed = models.TextField(blank=True)
    parts_used = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    downtime_minutes = models.IntegerField(default=0)
    result = models.CharField(max_length=100, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Maintenance for {self.asset.asset_tag}: {self.problem}"


class ServiceRequest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    request_type = models.CharField(max_length=80)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="service_requests", on_delete=models.CASCADE)
    department = models.ForeignKey(Department, null=True, blank=True, related_name="service_requests", on_delete=models.SET_NULL)
    status = models.CharField(max_length=30, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class KnowledgeArticle(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=80, default="general")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="audit_logs", on_delete=models.SET_NULL)
    action = models.CharField(max_length=120)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"


class SLAConfig(models.Model):
    priority = models.ForeignKey(TicketPriority, on_delete=models.CASCADE, related_name="sla_configs")
    response_hours = models.IntegerField(default=24)
    resolution_hours = models.IntegerField(default=120)
    description = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.priority.name} SLA"

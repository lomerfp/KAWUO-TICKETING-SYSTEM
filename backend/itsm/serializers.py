from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Asset, Department, KnowledgeArticle, MaintenanceRecord, Notification, ServiceRequest, Ticket, TicketAttachment, TicketCategory, TicketComment, TicketPriority, User


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code", "description", "is_active"]


class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "department",
            "phone_number",
            "is_active",
        ]


class TicketCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCategory
        fields = ["id", "name", "parent", "is_active"]


class TicketPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketPriority
        fields = ["id", "name", "response_hours", "sla_color"]


class TicketCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = TicketComment
        fields = ["id", "author", "body", "created_at"]


class TicketAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = ["id", "file", "uploaded_by", "created_at"]


class TicketSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    category = TicketCategorySerializer(read_only=True)
    priority = TicketPrioritySerializer(read_only=True)
    comments = TicketCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_number",
            "title",
            "description",
            "requester",
            "department",
            "category",
            "priority",
            "status",
            "assigned_to",
            "sla_deadline",
            "date_acknowledged",
            "date_assigned",
            "date_resolved",
            "date_closed",
            "resolution",
            "root_cause",
            "technical_notes",
            "created_at",
            "updated_at",
            "comments",
        ]


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["title", "description", "department", "category", "priority"]

    def create(self, validated_data):
        validated_data["requester"] = self.context["request"].user
        return Ticket.objects.create(**validated_data)


class AssetSerializer(serializers.ModelSerializer):
    assigned_user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Asset
        fields = [
            "id",
            "asset_id",
            "asset_tag",
            "serial_number",
            "type",
            "brand",
            "model",
            "purchase_date",
            "purchase_cost",
            "warranty_end",
            "condition",
            "location",
            "assigned_user",
            "department",
            "supplier",
            "status",
            "operating_system",
            "ip_address",
            "mac_address",
            "notes",
        ]


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = "__all__"


class ServiceRequestSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)

    class Meta:
        model = ServiceRequest
        fields = ["id", "title", "description", "request_type", "requester", "department", "status", "created_at"]


class KnowledgeArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = KnowledgeArticle
        fields = ["id", "title", "summary", "content", "author", "category", "is_published", "created_at"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "message", "is_read", "created_at"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is disabled.")
        attrs["user"] = user
        return attrs


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", "role", "department", "phone_number"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

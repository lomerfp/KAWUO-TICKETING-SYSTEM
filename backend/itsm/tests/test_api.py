from rest_framework import status
from rest_framework.test import APITestCase

from itsm.models import Department, Notification, Ticket, TicketCategory, TicketPriority, User


class AuthAndTicketAPITests(APITestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Operations", code="OPS")
        self.category = TicketCategory.objects.create(name="Network")
        self.priority = TicketPriority.objects.create(name="HIGH", response_hours=2)

        self.staff = User.objects.create_user(
            username="staff_user",
            password="StrongPass123",
            role="staff",
            department=self.department,
        )
        self.support = User.objects.create_user(
            username="support_user",
            password="StrongPass123",
            role="it_support",
            department=self.department,
        )

    def test_login_returns_token_payload(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "staff_user", "password": "StrongPass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_staff_can_create_ticket(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.post(
            "/api/tickets/",
            {
                "title": "Internet outage",
                "description": "The office internet is down.",
                "department": self.department.id,
                "category": self.category.id,
                "priority": self.priority.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 1)
        self.assertEqual(Ticket.objects.first().requester, self.staff)

    def test_it_support_can_list_all_tickets(self):
        Ticket.objects.create(
            title="Printer issue",
            description="The printer keeps offline.",
            requester=self.staff,
            department=self.department,
            category=self.category,
            priority=self.priority,
        )
        self.client.force_authenticate(user=self.support)
        response = self.client.get("/api/tickets/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_ticket_creation_creates_support_notification_and_dashboard_summary(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.post(
            "/api/tickets/",
            {
                "title": "Internet outage",
                "description": "The office internet is down.",
                "department": self.department.id,
                "category": self.category.id,
                "priority": self.priority.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(user__role="it_support").exists())

        self.client.force_authenticate(user=self.support)
        summary = self.client.get("/api/dashboard/summary/", format="json")
        self.assertEqual(summary.status_code, status.HTTP_200_OK)
        self.assertIn("total_tickets", summary.data)
        self.assertIn("open_tickets", summary.data)

    def test_ticket_lifecycle_supports_acknowledge_assign_and_close(self):
        ticket = Ticket.objects.create(
            title="Email delivery issue",
            description="Mail not sending.",
            requester=self.staff,
            department=self.department,
            category=self.category,
            priority=self.priority,
        )
        self.client.force_authenticate(user=self.support)

        acknowledge = self.client.post(f"/api/tickets/{ticket.pk}/acknowledge/", format="json")
        self.assertEqual(acknowledge.status_code, status.HTTP_200_OK)
        self.assertEqual(Ticket.objects.get(pk=ticket.pk).status, "ACKNOWLEDGED")

        assign = self.client.post(
            f"/api/tickets/{ticket.pk}/assign/",
            {"assigned_to": self.support.pk},
            format="json",
        )
        self.assertEqual(assign.status_code, status.HTTP_200_OK)
        self.assertEqual(Ticket.objects.get(pk=ticket.pk).assigned_to, self.support)

        resolved = self.client.post(
            f"/api/tickets/{ticket.pk}/resolve/",
            {"resolution": "SMTP settings corrected."},
            format="json",
        )
        self.assertEqual(resolved.status_code, status.HTTP_200_OK)
        self.assertEqual(Ticket.objects.get(pk=ticket.pk).status, "RESOLVED")

        close = self.client.post(f"/api/tickets/{ticket.pk}/close/", format="json")
        self.assertEqual(close.status_code, status.HTTP_200_OK)
        self.assertEqual(Ticket.objects.get(pk=ticket.pk).status, "CLOSED")

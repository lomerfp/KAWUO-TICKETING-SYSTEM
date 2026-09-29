from django.test import TestCase

from itsm.models import Department, Ticket, TicketCategory, TicketPriority, User


class TicketModelTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Finance", code="FIN")
        self.category = TicketCategory.objects.create(name="Hardware")
        self.priority = TicketPriority.objects.create(name="HIGH", response_hours=2)
        self.requester = User.objects.create_user(
            username="bob",
            password="StrongPass123",
            role="staff",
            department=self.department,
        )

    def test_ticket_number_is_generated(self):
        ticket = Ticket.objects.create(
            title="Laptop issue",
            description="Wi-Fi not connecting.",
            requester=self.requester,
            department=self.department,
            category=self.category,
            priority=self.priority,
        )
        self.assertTrue(ticket.ticket_number.startswith("KAWUO-IT-"))
        self.assertGreater(len(ticket.ticket_number), 15)

    def test_user_role_defaults_to_staff(self):
        user = User.objects.create_user(username="alice", password="StrongPass123")
        self.assertEqual(user.role, "staff")

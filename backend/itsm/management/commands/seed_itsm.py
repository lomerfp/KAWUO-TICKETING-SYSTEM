from django.core.management.base import BaseCommand

from itsm.models import Department, KnowledgeArticle, TicketCategory, TicketPriority, User


class Command(BaseCommand):
    help = "Populate the KAWUO ITSM application with safe demo data."

    def handle(self, *args, **options):
        Department.objects.get_or_create(name="Operations", code="OPS", defaults={"description": "Core operations team"})
        Department.objects.get_or_create(name="Finance", code="FIN", defaults={"description": "Finance and administration"})
        Department.objects.get_or_create(name="Programs", code="PROG", defaults={"description": "Programs management"})

        for name, response_hours in {"LOW": 24, "MEDIUM": 8, "HIGH": 2, "CRITICAL": 1}.items():
            TicketPriority.objects.get_or_create(name=name, defaults={"response_hours": response_hours})

        for name in ["Hardware", "Software", "Network", "Email", "Printing", "Website/System", "User Support"]:
            TicketCategory.objects.get_or_create(name=name)

        staff_user, _ = User.objects.get_or_create(
            username="staff_demo",
            defaults={"email": "staff@example.com", "role": "staff", "is_active": True, "password": "demo12345"},
        )
        if not staff_user.has_usable_password():
            staff_user.set_password("demo12345")
            staff_user.save()

        support_user, _ = User.objects.get_or_create(
            username="support_demo",
            defaults={"email": "support@example.com", "role": "it_support", "is_active": True, "password": "demo12345"},
        )
        if not support_user.has_usable_password():
            support_user.set_password("demo12345")
            support_user.save()

        KnowledgeArticle.objects.get_or_create(
            title="How to connect to KAWUO Wi-Fi",
            defaults={
                "summary": "Wireless connection steps for staff laptops and phones.",
                "content": "Select the KAWUO-WIFI network, enter the shared office password and verify the connection before starting work.",
                "category": "network",
                "is_published": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo KAWUO ITSM seed data created."))

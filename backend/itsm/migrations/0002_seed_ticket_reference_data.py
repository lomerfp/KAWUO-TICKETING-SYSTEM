from django.db import migrations


def seed_ticket_reference_data(apps, schema_editor):
    Department = apps.get_model("itsm", "Department")
    TicketCategory = apps.get_model("itsm", "TicketCategory")
    TicketPriority = apps.get_model("itsm", "TicketPriority")

    for name, code, description in [
        ("Operations", "OPS", "Core operations team"),
        ("Finance", "FIN", "Finance and administration"),
        ("Programs", "PROG", "Programs management"),
    ]:
        Department.objects.get_or_create(
            code=code,
            defaults={"name": name, "description": description, "is_active": True},
        )

    for name in ["Hardware", "Software", "Network", "Email", "Printing", "Website/System", "User Support"]:
        TicketCategory.objects.get_or_create(name=name, defaults={"is_active": True})

    for name, response_hours in [("LOW", 24), ("MEDIUM", 8), ("HIGH", 2), ("CRITICAL", 1)]:
        TicketPriority.objects.get_or_create(
            name=name,
            defaults={"response_hours": response_hours, "sla_color": "#086b61"},
        )


class Migration(migrations.Migration):
    dependencies = [("itsm", "0001_initial")]

    operations = [migrations.RunPython(seed_ticket_reference_data, migrations.RunPython.noop)]

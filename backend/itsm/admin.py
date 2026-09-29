from django.contrib import admin

from .models import (
    Asset,
    AuditLog,
    Department,
    KnowledgeArticle,
    MaintenanceRecord,
    Notification,
    SLAConfig,
    ServiceRequest,
    Ticket,
    TicketAttachment,
    TicketCategory,
    TicketComment,
    TicketPriority,
    TicketStatus,
    User,
)

admin.site.register(User)
admin.site.register(Department)
admin.site.register(TicketCategory)
admin.site.register(TicketPriority)
admin.site.register(TicketStatus)
admin.site.register(Ticket)
admin.site.register(TicketComment)
admin.site.register(TicketAttachment)
admin.site.register(Asset)
admin.site.register(MaintenanceRecord)
admin.site.register(ServiceRequest)
admin.site.register(KnowledgeArticle)
admin.site.register(Notification)
admin.site.register(AuditLog)
admin.site.register(SLAConfig)

from django.contrib import admin
from leads.models import *


class AttachmentInline(admin.StackedInline):
    model = Attachment


class LeadAdmin(admin.ModelAdmin):
    inlines = [AttachmentInline, ]


admin.site.register(Source)
admin.site.register(Event)
admin.site.register(Lead, LeadAdmin)

# SoS
admin.site.register(ProximityToSource)
admin.site.register(UnitOfAnalysis)
admin.site.register(DataCollectionTechnique)
admin.site.register(SamplingType)
admin.site.register(AssessmentFrequency)
admin.site.register(AssessmentStatus)
admin.site.register(AssessmentConfidentiality)
admin.site.register(SectorQuantification)
admin.site.register(SectorAnalyticalValue)
admin.site.register(SectorCovered)
admin.site.register(SurveyOfSurvey)

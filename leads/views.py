from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.core.files import File
from django.contrib.auth.models import User

import json
import os

from users.log import CreationActivity, EditionActivity,\
    DeletionActivity
from users.models import UserProfile

from leads.models import Lead, Event, Country, Attachment,\
    SimplifiedLead, LeadImage, ProximityToSource, UnitOfAnalysis,\
    DataCollectionTechnique, SamplingType, SectorQuantification,\
    SectorAnalyticalValue, AssessmentFrequency, AssessmentConfidentiality,\
    AssessmentStatus, SurveyOfSurvey, SectorCovered, UnitOfReporting, \
    Coordination

from entries.models import AdminLevel, AdminLevelSelection, AffectedGroup

from report.models import DisasterType

from entries.strippers import WebDocument, HtmlStripper, PdfStripper,\
    DocxStripper, PptxStripper

from entries.refresh_pcodes import refresh_pcodes
from deep.filename_generator import generate_filename
from leads.templatetags.check_acaps import allow_acaps

from excel_writer import ExcelWriter, RowCollection


def get_simplified_lead(lead, context):
    # Find simplified version of the lead content.
    # Make sure to catch any exception.

    try:
        images = None
        if lead.lead_type == "URL":
            doc = WebDocument(lead.url)

            if doc.html:
                context["lead_simplified"], images = \
                    HtmlStripper(doc.html).simplify()
            elif doc.pdf:
                context["lead_simplified"], images = \
                    PdfStripper(doc.pdf).simplify()
            elif doc.docx:
                context["lead_simplified"], images = \
                    DocxStripper(doc.docx).simplify()
            elif doc.pptx:
                context["lead_simplified"], images = \
                    PptxStripper(doc.pptx).simplify()

        elif lead.lead_type == "MAN":
            context["lead_simplified"] = lead.description

        elif lead.lead_type == "ATT":
            attachment = lead.attachment
            try:
                name, extension = os.path.splitext(attachment.upload.name)
            except:
                extension = ""

            if extension == ".pdf":
                context["lead_simplified"], images = \
                    PdfStripper(attachment.upload).simplify()
            elif extension in [".html", ".htm"]:
                context["lead_simplified"], images = \
                    HtmlStripper(attachment.upload.read()).simplify()
            elif extension in [".docx", ]:
                context["lead_simplified"], images = \
                    DocxStripper(attachment.upload).simplify()
            elif extension in [".pptx", ]:
                context["lead_simplified"], images = \
                    PptxStripper(attachment.upload).simplify()
            elif extension in ['.txt', ]:
                context["lead_simplified"] = attachment.upload.read()

        LeadImage.objects.filter(lead=lead).delete()
        if images:
            for image in images:
                lead_image = LeadImage(lead=lead)
                lead_image.image.save(os.path.basename(image.name),
                                      File(image), True)
                lead_image.save()

    except Exception as e:
        # raise e
        # print(e)
        # print("Error while simplifying")
        pass


def get_lead_form_data():
    """ Get data required to construct "Add Lead" form.
    """

    data = {}
    # data["sources"] = Source.objects.all()
    data["confidentialities"] = Lead.CONFIDENTIALITIES
    data["statuses"] = Lead.STATUSES
    data["users"] = User.objects.exclude(first_name="", last_name="")
    return data


class LeadsView(View):
    @method_decorator(login_required)
    def get(self, request, event):

        if int(event) != 0 and Event.objects.filter(pk=event).count() == 0:
            raise Http404('Event does not exist')

        context = {}
        context["current_page"] = "leads"
        context["all_events"] = Event.get_events_for(request.user)
        if int(event) != 0:
            context["event"] = Event.objects.get(pk=event)
            if context['event'] not in context['all_events']:
                return HttpResponseForbidden()
            UserProfile.set_last_event(request, context["event"])

        context.update(get_lead_form_data())
        return render(request, "leads/leads.html", context)

    @method_decorator(login_required)
    def post(self, request, event):
        return redirect('leads:leads', event)


class SoSView(View):
    @method_decorator(login_required)
    def get(self, request, event):

        if Event.objects.filter(pk=event).count() == 0:
            raise Http404('Event does not exist')

        if not allow_acaps(request.user):
            return HttpResponseForbidden()

        context = {}
        context["current_page"] = "sos"
        context["event"] = Event.objects.get(pk=event)
        context["all_events"] = Event.get_events_for(request.user)
        if context['event'] not in context['all_events']:
            return HttpResponseForbidden()
        UserProfile.set_last_event(request, context["event"])
        context.update(get_lead_form_data())
        return render(request, "leads/sos.html", context)


class AddSoS(View):
    @method_decorator(login_required)
    def get(self, request, event, lead_id, sos_id=None):

        if Event.objects.filter(pk=event).count() == 0:
            raise Http404('Event does not exist')
        if Lead.objects.filter(pk=lead_id).count() == 0:
            raise Http404('Lead does not exist')

        refresh_pcodes()
        if not allow_acaps(request.user):
            return HttpResponseForbidden()

        context = {}
        context["current_page"] = "sos"
        context["event"] = Event.objects.get(pk=event)
        if context['event'] not in Event.get_events_for(request.user):
            return HttpResponseForbidden()

        context["lead"] = Lead.objects.get(pk=lead_id)
        lead = context["lead"]

        try:
            simplified_lead = SimplifiedLead.objects.get(lead=lead)
            context["lead_simplified"] = simplified_lead.text
        except:
            get_simplified_lead(lead, context)
            if "lead_simplified" in context:
                try:
                    SimplifiedLead(lead=lead,
                                   text=context["lead_simplified"]).save()
                except:
                    pass

        if lead.lead_type == 'URL':
            context['lead_url'] = lead.url
        elif lead.lead_type == 'ATT':
            context['lead_url'] = request.build_absolute_uri(
                lead.attachment.upload.url)

        if context.get('lead_url'):
            context['format'] = context['lead_url'].rpartition('.')[-1]

        # Get fields options
        context["proximities"] = ProximityToSource.objects.all()
        context["units_of_analysis"] = UnitOfAnalysis.objects.all()
        context["units_of_reporting"] = UnitOfReporting.objects.all()
        context["data_collection_techniques"] = \
            DataCollectionTechnique.objects.all()
        context["sampling_types"] = SamplingType.objects.all()
        context["quantifications"] = SectorQuantification.objects.all()
        context["analytical_values"] = SectorAnalyticalValue.objects.all()
        context["coordinations"] = Coordination.objects.all()
        context["frequencies"] = AssessmentFrequency.objects.all()
        context["confidentialities"] = AssessmentConfidentiality.objects.all()
        context["statuses"] = AssessmentStatus.objects.all()
        context["sectors_covered"] = SectorCovered.objects.all()
        context["affected_groups"] = AffectedGroup.objects.all()
        context["disaster_types"] = DisasterType.objects.all()

        try:
            context["default_quantification"] = \
                SectorQuantification.objects.get(is_default=True)
            context["default_analytical_value"] = \
                SectorAnalyticalValue.objects.get(is_default=True)
        except:
            pass

        if sos_id:
            context["sos"] = SurveyOfSurvey.objects.get(pk=sos_id)

            sos = context["sos"]
            ags = json.loads(sos.affected_groups)
            sos.selected_affected_groups = []
            for ag in ags:
                sos.selected_affected_groups.append(
                    AffectedGroup.objects.get(name=ag)
                )

        return render(request, "leads/add-sos.html", context)

    @method_decorator(login_required)
    def post(self, request, event, lead_id, sos_id=None):
        if sos_id:
            sos = SurveyOfSurvey.objects.get(pk=sos_id)
            activity = EditionActivity()
        else:
            sos = SurveyOfSurvey()
            activity = CreationActivity()

        sos.lead = Lead.objects.get(pk=lead_id)

        sos.title = request.POST["assesment-title"]
        sos.lead_organization = request.POST["lead-organization"]
        sos.partners = request.POST["other-assesment-partners"]
        sos.donors = request.POST["donors"]
        sos.affected_groups = request.POST["affected_groups"]

        if request.POST["disaster-type"] and \
                request.POST["disaster-type"] != "":
            sos.disaster_type = DisasterType.objects\
                .get(pk=request.POST["disaster-type"])

        if request.POST["start-of-field"] and \
                request.POST["start-of-field"] != "":
            sos.start_data_collection = request.POST["start-of-field"]
        else:
            sos.start_data_collection = None

        if request.POST["end-of-field"] and request.POST["end-of-field"] != "":
            sos.end_data_collection = request.POST["end-of-field"]
        else:
            sos.end_data_collection = None

        if request.POST["coordination"] and \
                request.POST["coordination"] != "":
            sos.coordination = Coordination.objects\
                .get(pk=request.POST["coordination"])
        else:
            sos.coordination = None

        if request.POST["assesment-frequency"] and \
                request.POST["assesment-frequency"] != "":
            sos.frequency = AssessmentFrequency.objects\
                .get(pk=request.POST["assesment-frequency"])
        else:
            sos.frequency = None

        if request.POST["assesment-status"] and \
                request.POST["assesment-status"] != "":
            sos.status = AssessmentStatus.objects.get(
                pk=request.POST["assesment-status"])
        else:
            sos.status = None

        if request.POST["assesment-confidentiality"] and \
                request.POST["assesment-confidentiality"] != "":
            sos.confidentiality = AssessmentConfidentiality.objects.get(
                pk=request.POST["assesment-confidentiality"])
        else:
            sos.confidentiality = None

        if request.POST["source-proximity"] and \
                request.POST["source-proximity"] != "":
            sos.proximity_to_source = ProximityToSource.objects.get(
                pk=request.POST["source-proximity"])
        else:
            sos.proximity = None

        if request.POST["sampling-type"] and \
                request.POST["sampling-type"] != "":
            sos.sampling_type = SamplingType.objects.get(
                pk=request.POST["sampling-type"])
        else:
            sos.sampling_type = None

        sos.created_by = request.user
        sos.sectors_covered = request.POST["sectors_covered"]
        sos.save()

        activity.set_target(
            'survey-of-survey', sos.pk, sos.title,
            reverse('leads:edit_sos', args=[event, sos.lead.pk, sos.pk])
        ).log_for(request.user, event=sos.lead.event)

        # Map selections
        map_data = json.loads(request.POST["map_data"])
        temp = sos.map_selections.all()
        sos.map_selections.clear()
        temp.delete()
        for area in map_data:
            m = area.split(':')
            admin_level = AdminLevel.objects.get(
                country=Country.objects.get(code=m[0]),
                level=int(m[1])
            )
            try:
                if len(m) == 4:
                    selection = AdminLevelSelection.objects.get(
                        admin_level=admin_level, pcode=m[3]
                    )
                else:
                    selection = AdminLevelSelection.objects.get(
                        admin_level=admin_level, name=m[2]
                    )
            except:
                if len(m) == 4:
                    selection = AdminLevelSelection(admin_level=admin_level,
                                                    name=m[2], pcode=m[3])
                else:
                    selection = AdminLevelSelection(admin_level=admin_level,
                                                    name=m[2])
                selection.save()

            sos.map_selections.add(selection)

        # affected_groups = json.loads(request.POST["affected_groups"])
        # sos.affected_groups.clear()
        # for group in affected_groups:
        #     sos.affected_groups.add(AffectedGroup.objects.get(name=group))

        sos.unit_of_analysis.clear()
        if request.POST["analysis-unit"] and \
                request.POST["analysis-unit"] != "null":
            pks = request.POST["analysis-unit"].split(",")
            for pk in pks:
                sos.unit_of_analysis.add(UnitOfAnalysis.objects.get(pk=pk))

        sos.data_collection_technique.clear()
        if request.POST["data-collection-technique"] and \
                request.POST["data-collection-technique"] != "null":
            pks = request.POST["data-collection-technique"].split(",")
            for pk in pks:
                sos.data_collection_technique.add(
                    DataCollectionTechnique.objects.get(pk=pk))

        sos.unit_of_reporting.clear()
        if request.POST["reporting-unit"] and \
                request.POST["reporting-unit"] != "null":
            pks = request.POST["reporting-unit"].split(",")
            for pk in pks:
                sos.unit_of_reporting.add(UnitOfReporting.objects.get(pk=pk))

        return redirect('leads:sos', event)


class AddLead(View):
    @method_decorator(login_required)
    def get(self, request, event, id=None):

        if Event.objects.filter(pk=event).count() == 0:
            raise Http404('Event does not exist')
        if id:
            if Lead.objects.filter(pk=id).count() == 0:
                raise Http404('Lead does not exist')

        context = {}
        context["current_page"] = "leads"
        context["event"] = Event.objects.get(pk=event)
        context["events"] = Event.objects.all()
        if context['event'] not in Event.get_events_for(request.user):
            return HttpResponseForbidden()
        UserProfile.set_last_event(request, context["event"])
        if id:
            context["lead"] = Lead.objects.get(pk=id)
        context.update(get_lead_form_data())

        # context["cancel_url"] = reverse("leads:leads", args=[event])
        return render(request, "leads/add-lead.html", context)

    @method_decorator(login_required)
    def post(self, request, event, id=None):

        error = ""

        # Get editing lead or create new lead.
        if id:
            lead = Lead.objects.get(pk=id)
            activity = EditionActivity()
        else:
            lead = Lead()
            activity = CreationActivity()

        lead.name = request.POST["name"]

        # lead.event = Event.objects.get(pk=event)

        if "event" in request.POST and request.POST["event"] != "":
            lead.event = Event.objects.get(pk=request.POST["event"])
        else:
            lead.event = Event.objects.get(pk=event)

        if "source" in request.POST and request.POST["source"] != "":
            lead.source_name = request.POST["source"]
        else:
            lead.source_name = None

        lead.confidentiality = request.POST["confidentiality"]

        if "assigned-to" in request.POST and \
                request.POST["assigned-to"] != "":
            lead.assigned_to = User.objects.get(pk=request.POST["assigned-to"])
        else:
            lead.assigned_to = None

        if "publish-date" in request.POST and \
                request.POST["publish-date"] != "":
            lead.published_at = request.POST["publish-date"]
        else:
            lead.published_at = None

        lead.created_by = request.user

        if "lead-type" in request.POST and \
                request.POST["lead-type"] == "manual":
            lead.description = request.POST["description"]
            lead.lead_type = Lead.MANUAL_LEAD

        # TODO: Remove not condition.
        # Currently for the chrome plugin to work, the default type
        # when not provided is website.
        if "lead-type" not in request.POST or \
                request.POST["lead-type"] == "website":
            lead.url = request.POST["url"]
            lead.website = request.POST["website"]
            lead.lead_type = Lead.URL_LEAD

        if "lead-type" in request.POST and \
                request.POST["lead-type"] == "manual":
            lead.description = request.POST["description"]
            lead.lead_type = Lead.MANUAL_LEAD

        if "lead-type" in request.POST and \
                request.POST["lead-type"] == "attachment":
            lead.lead_type = Lead.ATTACHMENT_LEAD

        if "lead-type" in request.POST and \
                request.POST["lead-type"] == "survey-of-surveys":
            pass

        lead.save()

        activity.set_target(
            'lead', lead.pk, lead.name,
            reverse('leads:edit', args=[lead.event.pk, lead.pk])
        ).log_for(request.user, event=lead.event)

        if lead.lead_type == Lead.ATTACHMENT_LEAD:
            for file in request.FILES:
                Attachment.objects.filter(lead__pk=lead.pk).delete()
                attachment = Attachment()
                attachment.lead = lead
                attachment.upload = request.FILES[file]
                attachment.save()
                break

        # Finally try to get the simplified lead
        # But remember to delete the old one
        SimplifiedLead.objects.filter(lead=lead).delete()
        temp = {}
        get_simplified_lead(lead, temp)

        if "lead_simplified" in temp and temp["lead_simplified"]:
            try:
                SimplifiedLead(lead=lead, text=temp["lead_simplified"]).save()
            except:
                pass

        if "clone_to" in request.POST and request.POST.get('clone_to'):
            clone_to = request.POST['clone_to'].split(',')
            clone_to = [int(x) for x in clone_to]
            for pk in clone_to:
                try:
                    lead.clone_to(Event.objects.get(pk=pk))
                except Exception as e:
                    pass

        if error != "":
            context = {}
            context["current_page"] = "leads"
            context["event"] = Event.objects.get(pk=event)
            UserProfile.set_last_event(request, context["event"])
            context["all_events"] = Event.objects.all()
            context["error"] = error
            return render(request, "leads/add-lead.html",
                          context)

        if "redirect-url" in request.POST:
            return JsonResponse({
                "url": reverse('entries:add', args=[event, lead.pk])
            })
        if "add-entry" in request.POST:
            if len(request.FILES) > 0:
                return JsonResponse({'url': reverse('entries:add',
                                                    args=[event, lead.pk])})
            return redirect('entries:add', event, lead.pk)

        return redirect("leads:leads", event=event)


class MarkProcessed(View):
    @method_decorator(login_required)
    def post(self, request, event):
        lead = Lead.objects.get(pk=request.POST["id"])
        lead.status = request.POST["status"]
        lead.save()

        activity = EditionActivity().set_target(
            'lead', lead.pk, lead.name,
            reverse('leads:edit', args=[lead.event.pk, lead.pk])
        )

        if lead.status == 'PRO':
            activity.set_remarks('marked processed')
        elif lead.status == 'PEN':
            activity.set_remarks('marked pending')

        activity.log_for(request.user, event=lead.event)

        return redirect('leads:leads', event=event)


class DeleteLead(View):
    @method_decorator(login_required)
    def post(self, request, event):

        lead = Lead.objects.get(pk=request.POST["id"])
        activity = DeletionActivity().set_target(
            'lead', lead.pk, lead.name
        )
        event = lead.event
        lead.delete()

        activity.log_for(request.user, event=event)

        # lead.status = Lead.DELETED
        # lead.save()
        return redirect('leads:leads', event=event.pk)


class DeleteSoS(View):
    @method_decorator(login_required)
    def post(self, request, event):
        if not allow_acaps(request.user):
            return HttpResponseForbidden()

        sos = SurveyOfSurvey.objects.get(pk=request.POST["id"])
        activity = DeletionActivity().set_target(
            'survey-of-survey', sos.pk, sos.title,
        )
        event = sos.lead.event
        sos.delete()

        activity.log_for(request.user, event=event)
        return redirect('leads:sos', event=event.pk)


class ExportSosXls(View):
    def get(self, request, event):
        ew = ExcelWriter()

        ws = ew.get_active()
        soses = SurveyOfSurvey.objects.filter(lead__event__pk=event)

        titles = [
            "Id", "Title", "Lead organization",
            "Other partners", "Proximity to source", "Unit of analysis",
            "Start of field data collection", "End of field data collection",
            "Data collection technique", "Assessment frequency",
            "Assessment status", "Assessment confidentiality", "Sampling type",
            "Affected groups",
        ]

        sectors_covered = SectorCovered.objects.all()
        for sc in sectors_covered:
            titles.append(sc.name + " - Quantification")
            titles.append(sc.name + " - Analytical Value")

        countries = Event.objects.get(pk=event).countries.all()
        for country in countries:
            admin_levels = country.adminlevel_set.all()
            for admin_level in admin_levels:
                titles.append(admin_level.name)

        # Create title row
        for i, t in enumerate(titles):
            ws.cell(row=1, column=i+1).value = t

        ew.auto_fit_cells_in_row(1)

        # Fill data
        for i, sos in enumerate(soses):
            rows = RowCollection(1)
            rows.add_values([sos.pk, sos.title, sos.lead_organization,
                             sos.partners,
                             sos.proximity_to_source.name
                             if sos.proximity_to_source else ""])

            rows.permute_and_add(sos.unit_of_analysis.all())
            rows.add_values([sos.start_data_collection
                             if sos.start_data_collection else "",
                             sos.end_data_collection
                             if sos.end_data_collection else ""])
            rows.permute_and_add(sos.data_collection_technique.all())
            rows.add_values([sos.frequency.name if sos.frequency else "",
                             sos.status.name if sos.status else "",
                             sos.confidentiality.name
                             if sos.confidentiality else "",
                             sos.sampling_type.name
                             if sos.sampling_type else ""])

            ags = json.loads(sos.affected_groups)
            affected_groups = []
            for ag in ags:
                affected_groups.append(AffectedGroup.objects.get(name=ag))
            rows.permute_and_add(affected_groups)

            scs = json.loads(sos.sectors_covered)
            scids = [s["id"] for s in scs]
            for sc in sectors_covered:
                if sc.identifier in scids:
                    s = scs[scids.index(sc.identifier)]
                    try:
                        q = SectorQuantification.objects.get(
                            pk=s["quantification"])
                        q = q.name
                    except:
                        q = ""

                    try:
                        a = SectorAnalyticalValue.objects.get(
                            pk=s["analytical_value"])
                        a = a.name
                    except:
                        a = ""
                    rows.add_values([q, a])
                else:
                    rows.add_values(["", ""])

            for country in countries:
                admin_levels = country.adminlevel_set.all()
                for admin_level in admin_levels:
                    selections = []
                    for map_selection in sos.map_selections.all():
                        if admin_level == map_selection.admin_level:
                            selections.append(map_selection.name)
                    rows.permute_and_add(selections)

            ew.append(rows.rows)

        return ew.get_http_response(
            generate_filename('Assessment Registry Export'))

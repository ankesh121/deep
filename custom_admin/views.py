from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse

from leads.models import *
from entries.models import *
from report.models import *
from usergroup.models import *
from users.log import *

import json


class ProjectPanelView(View):
    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_superuser:
            return HttpResponseForbidden()

        context = {}
        context["current_page"] = "project-panel"

        context["events"] = Event.objects.filter(admins__pk=request.user.pk).order_by('name')
        context["usergroups"] = UserGroup.objects.filter(admins__pk=request.user.pk).order_by('name')

        context["entry_templates"] = EntryTemplate.objects.filter(usergroup__members__pk=request.user.pk)
        context["countries"] = Country.objects.filter(reference_country=None)
        context["disaster_types"] = DisasterType.objects.all()
        context["users"] = User.objects.all()

        if "selected" in request.GET:
            context["selected_event"] = int(request.GET["selected"])

        if "selected_group" in request.GET:
            context["selected_group"] = int(request.GET["selected_group"])

        return render(request, "custom_admin/project-panel.html", context)

    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_superuser:
            return HttpResponseForbidden()

        response = redirect('custom_admin:project_panel')
        pk = request.POST["project-pk"]

        if "save" in request.POST:
            if pk == "new":
                event = Event()
                activity = CreationActivity()
            else:
                event = Event.objects.get(pk=int(pk))
                activity = EditionActivity()

            event.name = request.POST["project-name"]
            event.description = request.POST["project-description"]

            if request.POST["project-status"] and request.POST["project-status"] != "":
                event.status = int(request.POST["project-status"])

            if request.POST["disaster-type"] and request.POST["disaster-type"] != "":
                event.disaster_type = DisasterType.objects.get(pk=int(request.POST["disaster-type"]))
            else:
                event.disaster_type = None

            if request.POST["project-start-date"] and request.POST["project-start-date"] != "":
                event.start_date = request.POST["project-start-date"]
            else:
                event.start_date = None

            if request.POST["project-end-date"] and request.POST["project-end-date"] != "":
                event.end_date = request.POST["project-end-date"]
            else:
                event.end_date = None

            if request.POST["glide-number"] and request.POST["glide-number"] != "":
                event.glide_number = request.POST["glide-number"]
            else:
                event.glide_number = None

            if request.POST["spillover"] and request.POST["spillover"] != "":
                event.spill_over = Event.objects.get(pk=int(request.POST["spillover"]))
            else:
                event.spill_over = None

            if 'entry-template' in request.POST:
                if request.POST["entry-template"] and request.POST["entry-template"] != "":
                    event.entry_template = EntryTemplate.objects.get(pk=int(request.POST["entry-template"]))
                else:
                    event.entry_template = None
            event.save()

            if event.admins.count() == 0:
                event.admins.add(request.user)

            activity.set_target(
                'project', event.pk, event.name,
                reverse('custom_admin:project_panel') + '?selected=' + str(event.pk)
            ).log_for(request.user, event=event)

            # event.assignee.clear()
            # if "assigned-to" in request.POST and request.POST["assigned-to"]:
            #     for assigned_to in request.POST.getlist("assigned-to"):
            #         event.assignee.add(User.objects.get(pk=int(assigned_to)))

            event.admins.clear()
            if "admins" in request.POST and request.POST["admins"]:
                for admin in request.POST.getlist("admins"):
                    event.admins.add(User.objects.get(pk=int(admin)))

            event.members.clear()
            if "members" in request.POST and request.POST["members"]:
                for member in request.POST.getlist("members"):
                    event.members.add(User.objects.get(pk=int(member)))

            event.countries.clear()
            if "countries" in request.POST and request.POST["countries"]:
                for country in request.POST.getlist("countries"):
                    event.countries.add(Country.objects.get(pk=country))

            prev_groups = event.usergroup_set.all()
            for ug in prev_groups:
                ug.projects.remove(event)

            new_groups = []
            if "user-groups" in request.POST and request.POST["user-groups"]:
                for pk in request.POST.getlist("user-groups"):
                    usergroup = UserGroup.objects.get(pk=pk)
                    usergroup.projects.add(event)

                    new_groups.append(usergroup)
                    if usergroup not in prev_groups:
                        AdditionActivity().set_target(
                            'project', event.pk, event.name,
                            reverse('custom_admin:project_panel') + '?selected=' + str(event.pk)
                        ).log_for(request.user, event=event, group=usergroup)

            for ug in prev_groups:
                if ug not in new_groups:
                    RemovalActivity().set_target(
                        'project', event.pk, event.name,
                        reverse('custom_admin:project_panel') + '?selected=' + str(event.pk)
                    ).log_for(request.user, event=event, group=ug)

            response["Location"] += "?selected="+str(event.pk)

        elif "delete" in request.POST:
            if pk != "new":
                Event.objects.get(pk=int(pk)).delete()

        return response


class CountryManagementView(View):
    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_superuser:
            return HttpResponseForbidden()

        context = {}
        context["current_page"] = "country-management"
        context["events"] = Event.objects.all()

        if request.user.is_superuser:
            context["countries"] = Country.objects.all()
        else:
            context["countries"] = Country.objects.filter(reference_country=None)

        if "selected" in request.GET:
            context["selected_country"] = request.GET["selected"]

        return render(request, "custom_admin/country-management.html", context)

    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_superuser:
            return HttpResponseForbidden()

        response = redirect('custom_admin:country_management')

        if 'save' in request.POST:
            code = request.POST['country-code']
            try:
                country = Country.objects.get(code=code)
            except:
                country = Country(code=code)

            country.name = request.POST['country-name']

            # Country Region Data
            region_data = {
                'WB Region': request.POST.get('country-wb-region'),
                'WB IncomeGroup': request.POST.get('country-wb-income-group'),
                'UN-OCHA Region': request.POST.get('country-ocha-region'),
                'EC-ECHO Region': request.POST.get('country-echo-region'),
                'UN Geographical Region':
                    request.POST.get('country-un-geographical-region'),
                'UN Geographical Sub-Region':
                    request.POST.get('country-un-geographical-sub-region'),
            }

            # Key figures
            key_figures = {
                'hdi_index': request.POST['hdi-index'],
                'hdi_rank': request.POST['hdi-rank'],
                'u5m': request.POST['u5m'],

                'number_of_refugees': request.POST['number-of-refugees'],
                'number_of_idps': request.POST['number-of-idps'],
                'number_of_returned_refugees':
                    request.POST['number-of-returned-refugees'],

                'inform_score': request.POST['inform-score'],
                'inform_risk_index': request.POST['inform-risk-index'],
                'inform_hazard_and_exposure':
                    request.POST['inform-hazard-and-exposure'],
                'inform_vulnerability':
                    request.POST['inform-vulnerability'],
                'inform_lack_of_coping_capacity':
                    request.POST['inform-lack-of-coping-capacity'],

                'total_population': request.POST['total-population'],
                'population_source': request.POST['population-source'],
            }

            country.regions = json.dumps(region_data)
            country.key_figures = json.dumps(key_figures)
            country.media_sources = request.POST['media-sources']

            country.save()

            # Admin areas
            admin_level_pks = request.POST.getlist('admin-level-pk')
            admin_levels = request.POST.getlist('admin-level')
            admin_level_names = request.POST.getlist('admin-level-name')
            property_names = request.POST.getlist('property-name')
            property_pcodes = request.POST.getlist('property-pcode')
            geojsons = request.FILES.getlist('geojson')
            geojsons_selected = request.POST.getlist('geojson-selected')

            # Deletion are checkboxes and need to be handled differently
            # See html comment for more info
            temp = request.POST.getlist('delete-admin-level')
            delete_admin_levels = []
            t = 0
            while t < len(temp):
                if temp[t] == '0':
                    delete_admin_levels.append(False)
                else:
                    t += 1
                    delete_admin_levels.append(True)
                t += 1

            # Post each admin level
            geojson_file = 0
            for i, pk in enumerate(admin_level_pks):

                to_delete = delete_admin_levels[i] or admin_levels[i] == '' \
                    or admin_level_names[i] == '' or property_names[i] == ''

                if pk == "new":
                    admin_level = AdminLevel()
                    if to_delete:
                        continue
                else:
                    admin_level = AdminLevel.objects.get(pk=int(pk))
                    if to_delete:
                        admin_level.delete()
                        continue

                admin_level.country = country
                admin_level.level = int(admin_levels[i])
                admin_level.name = admin_level_names[i]
                admin_level.property_name = property_names[i]
                admin_level.property_pcode = property_pcodes[i]

                if geojsons_selected[i] == 'true':
                    admin_level.geojson = geojsons[geojson_file]
                    geojson_file += 1
                admin_level.save()

            response["Location"] += "?selected="+str(country.pk)

        elif 'delete' in request.POST:
            try:
                country = Country.objects.get(code=request.POST['country-code']).delete()
            except:
                pass

        return response


class EntryTemplateView(View):
    @method_decorator(login_required)
    def get(self, request, template_id):
        context = {}
        template = EntryTemplate.objects.get(pk=template_id)
        if request.user not in template.get_admins():
            return HttpResponseForbidden()

        context['entry_template'] = template
        context['num_entries'] = EntryInformation.objects.filter(
            entry__template=template).distinct().count()
        context['redirect_location'] = request.GET.get('redirect')
        return render(request, "custom_admin/entry-template.html", context)

    @method_decorator(login_required)
    def post(self, request, template_id=None):
        data = json.loads(request.POST.get('data'))

        entry_template = EntryTemplate.objects.get(pk=template_id)
        if request.user not in entry_template.get_admins():
            return HttpResponseForbidden()

        entry_template.elements = json.dumps(data['elements'])
        entry_template.name = data['name']
        if data.get('snapshots'):
            entry_template.snapshot_pageone = data['snapshots']['pageOne']
            entry_template.snapshot_pagetwo = data['snapshots']['pageTwo']
        entry_template.save()

        redirect_location = request.POST.get('redirect')
        if redirect_location and redirect_location != 'null':
            return redirect(redirect_location)

        return redirect('custom_admin:entry_template', template_id=template_id)

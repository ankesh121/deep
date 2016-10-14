from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import serializers

import os
import json

from leads.models import *
from entries.models import *
from geojson_handler import GeoJsonHandler


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('source',)


class LeadSerializer(serializers.ModelSerializer):
    """ Lead serializer used by the REST api
    """

    attachment = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = ('id', 'name', 'source', 'assigned_to',
                  'published_at', 'confidentiality', 'status', 'description',
                  'url', 'website', 'created_at', 'created_by', 'attachment',
                  'assigned_to_name', 'created_by_name', 'event', 'lead_type')

        # TODO: Automatically set created_by.

    def get_attachment(self, lead):
        try:
            a = lead.attachment
            return [
                    os.path.basename(a.upload.name),
                    a.upload.url
                    ]
        except:
            return None

    def get_assigned_to_name(self, lead):
        if lead.assigned_to:
            return lead.assigned_to.get_full_name()
        else:
            return ""

    def get_created_by_name(self, lead):
        if lead.created_by:
            return lead.created_by.get_full_name()
        else:
            return ""


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'name',)


class SosSerializer(serializers.ModelSerializer):
    countries = serializers.SerializerMethodField()
    areas = serializers.SerializerMethodField()
    areas_summary = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    sectors_covered = serializers.SerializerMethodField()
    affected_groups = serializers.SerializerMethodField()
    unit_of_analysis = serializers.SerializerMethodField()
    data_collection_technique = serializers.SerializerMethodField()
    lead = LeadSerializer()
    lead_id = serializers.IntegerField(source='lead.id', read_only=True)

    proximity_to_source = serializers.CharField(source='proximity_to_source.name', read_only=True)
    data_collection_technique = serializers.CharField(source='data_collection_technique.name', read_only=True)
    sampling_type = serializers.CharField(source='sampling_type.name', read_only=True)
    frequency = serializers.CharField(source='frequency.name', read_only=True)
    status = serializers.CharField(source='status.name', read_only=True)
    confidentiality = serializers.CharField(source='confidentiality.name', read_only=True)

    class Meta:
        model = SurveyOfSurvey
        depth = 1
        fields = ('id', 'created_at', 'created_by_name',
                  'title', 'lead_organization', 'partners',
                  'proximity_to_source', 'unit_of_analysis', 'start_data_collection',
                  'end_data_collection', 'data_collection_technique',
                  'sectors_covered',
                  'sampling_type', 'frequency', 'status', 'confidentiality',
                  'countries', 'areas', 'areas_summary', 'sectors_covered',
                  'affected_groups', 'lead', 'lead_id')


    def get_countries(self, sos):
        return {s.admin_level.country.pk: s.admin_level.country.name for s in sos.map_selections.all()}

    def get_areas(self, sos):
        summary = self.context['request'].query_params.get('summary')
        if summary:
            return
        if sos.map_selections.count() == 0:
            return

        data = {}
        children_properties = []
        for s in sos.map_selections.all():
            if s.admin_level.name not in data:
                data[s.admin_level.name] = {"country": s.admin_level.country.pk, "locations": [], "pcodes": []}

            if s.admin_level.property_pcode != "":
                features = GeoJsonHandler(s.admin_level.geojson.read().decode()).filter_features(s.admin_level.property_name, s.name)
                data[s.admin_level.name]["pcodes"].extend([f["properties"][s.admin_level.property_pcode] for f in features])
            # else:
            data[s.admin_level.name]["locations"].append(s.name)
            
            child_admin = AdminLevel.objects.filter(level=s.admin_level.level+1, country=s.admin_level.country)
            if child_admin.count() > 0:
                children_properties.append((child_admin[0], s.admin_level.property_name, s.name))

        # Get children areas if exist as well
        for cp in children_properties:
            geojson = GeoJsonHandler(cp[0].geojson.read().decode())
            features = geojson.filter_features(cp[1], cp[2])

            if cp[0].name not in data:
                data[cp[0].name] = {"country": cp[0].country.pk, "locations": [], "pcodes": []}

            if cp[0].property_pcode != "":
                data[cp[0].name]["pcodes"].extend([f["properties"][cp[0].property_pcode] for f in features])
            # else:
            data[cp[0].name]["locations"].extend([f["properties"][cp[0].property_name] for f in features])
        return data

    def get_country_names(self, sos):
        cs = [s.admin_level.country.name for s in sos.map_selections.all()]
        return list(set(cs))

    def get_areas_summary(self, sos):
        return ", ".join([s.name for s in sos.map_selections.all()] + self.get_country_names(sos))

    def get_created_by_name(self, sos):
        return sos.created_by.get_full_name()

    def get_sectors_covered(self, sos):
        scs = json.loads(sos.sectors_covered)
        data = {}
        for sc in scs:
            # TODO: check if values are default instead of "1"
            if (sc["quantification"] and not SectorQuantification.objects.get(pk=sc["quantification"]).is_default) \
                or \
                (sc["analytical_value"] and not SectorAnalyticalValue.objects.get(pk=sc["analytical_value"]).is_default):
                data[sc["title"]] = {
                    "quantification": SectorQuantification.objects.get(pk=sc["quantification"]).name,
                    "analytical_value": SectorAnalyticalValue.objects.get(pk=sc["analytical_value"]).name
                }
        return data

        # data = []
        # for sc in scs:
        #     if sc["quantification"] or sc["analytical_value"]:
        #         data.append(sc["title"])

        # return ", ".join(data)

    def get_affected_groups(self, sos):
        return json.loads(sos.affected_groups)
        # return ", ".join(json.loads(sos.affected_groups))

    def get_unit_of_analysis(self, sos):
        return [u.name for u in sos.unit_of_analysis.all()]

    def get_data_collection_technique(self, sos):
        return [d.name for d in sos.data_collection_technique.all()]

from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import serializers

from entries.models import *
from geojson_handler import GeoJsonHandler


class InformationAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformationAttribute
        fields = ('subpillar', 'sector', 'subsectors')
        depth = 2


class EntryInformationSerializer(serializers.ModelSerializer):
    attributes = InformationAttributeSerializer(source='informationattribute_set', many=True)

    class Meta:
        model = EntryInformation
        fields = ('excerpt', 'date', 'reliability', 'severity', 'number',
                  'vulnerable_groups', 'specific_needs_groups', 'affected_groups',
                  'map_selections', 'attributes')
        depth = 1


class EntrySerializer(serializers.ModelSerializer):
    lead_title = serializers.CharField(source='lead.name', read_only=True)
    informations = EntryInformationSerializer(source='entryinformation_set', many=True)
    modified_by = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = ('id', 'modified_at', 'modified_by', 'lead', 'lead_title', 'informations')

    def get_modified_by(self, entry):
        print(entry.modified_by)
        return entry.modified_by.get_full_name()

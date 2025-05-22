from rest_framework import serializers
from .models import Country, NameCountryProbability, UniqueName


class UniqueNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniqueName
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class NameCountryProbabilitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = NameCountryProbability
        fields = ['probability', 'country']


class FinalAnswerSerializer(serializers.Serializer):
    name = serializers.CharField()
    requests_count = serializers.IntegerField()
    country_predictions = NameCountryProbabilitySerializer(many=True)


class PopularNameSerializer(serializers.Serializer):
    name = serializers.CharField()
    frequency = serializers.IntegerField()

import requests
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import UniqueName, Country, NameCountryProbability
from .serializers import CountrySerializer, FinalAnswerSerializer, PopularNameSerializer
from datetime import timedelta
from django.utils import timezone


logger = logging.getLogger(__name__)
nationalize_url = f'https://api.nationalize.io/?name='
restcountries_url = f'https://restcountries.com/v3.1/alpha/'

def parse_name_data(name: str) -> dict or None:
    """
    Parsing name data from nationalize API
    """
    try:
        response = requests.get(f'{nationalize_url}{name}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while parsing name data for: {name}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error for name {name} in nationalize API: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException while parsing name {name}: {e}")
        return None
    except ValueError as e:
        logger.error(f"Could not decode JSON from Nationalize API for name '{name}': {e}")
        return None


def parse_country_data(code: str) -> dict or None:
    """
    Parsing country data from restcountries API
    """
    try:
        response = requests.get(f'{restcountries_url}{code}')
        response.raise_for_status()

        raw_data = response.json()[0]
        data = {
            'code': raw_data.get('cca2'),
            'name_common': raw_data['name'].get('common'),
            'name_official': raw_data['name'].get('official'),
            'possible_names': raw_data.get('altSpellings', []),
            'region': raw_data.get('region', ''),
            'capital_name': raw_data.get('capital', [''])[0] if raw_data.get('capital') else '',
            'capital_latitude': raw_data.get('latlng', [None])[0],
            'capital_longitude': raw_data.get('latlng', [None, None])[1],
            'independent': raw_data.get('independent'),
            'google_maps_url': raw_data['maps'].get('googleMaps'),
            'open_maps_url': raw_data['maps'].get('openStreetMaps'),
            'flag_png_url': raw_data['flags'].get('png'),
            'flag_svg_url': raw_data['flags'].get('svg'),
            'flag_alt_text': raw_data['flags'].get('alt'),
            'coat_of_arms_png_url': raw_data['coatOfArms'].get('png'),
            'coat_of_arms_svg_url': raw_data['coatOfArms'].get('svg'),
            'borders': raw_data.get('borders', [])
        }
        return data
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while parsing country data for: {code}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP error for country {code} in restcountries API: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException while parsing country {code}: {e}")
        return None
    except (ValueError, IndexError, KeyError, TypeError) as e:
        logger.error(f"Error parsing data for country {code}: {e}")
        return None


def create_or_update_country_and_probability_objects(name_object: UniqueName, data: dict) -> None:
    """
    Creating or updating country and probability objects
    """
    for nationalize_data_country in data.get('country'):
        country_code = nationalize_data_country['country_id']
        probability = nationalize_data_country.get('probability')

        # Getting or creating a country object:
        try:
            country_object = Country.objects.get(code=country_code)
        except Country.DoesNotExist:
            country_data = parse_country_data(country_code)
            if not country_data:
                logger.error(f'Nationalize API error while parsing {country_code} data')
                continue

            country_serializer = CountrySerializer(data=country_data)
            if country_serializer.is_valid(raise_exception=True):
                country_serializer.save()
                logger.info(f'Country object with code {country_code} was created successfully')

            country_object = country_serializer.instance

        # Getting or creating a probability object:
        probability_object, created = NameCountryProbability.objects.get_or_create(
            name=name_object,
            country=country_object,
            defaults={'probability': probability}
        )
        if created:
            logger.info(
                f'NameCountryProbability object for {name_object.name} and {country_code} was created successfully'
            )

    return None


class NameStatsView(APIView):
    def get(self, request, *args, **kwargs):
        name_param = request.query_params.get('name')
        if not name_param:
            logger.error('Name parameter is missing')
            return Response({'error': 'Name parameter is missing'},status=status.HTTP_400_BAD_REQUEST)

        name_object = UniqueName.objects.filter(name=name_param).first()
        if name_object:
            # Name exists in DB and data is fresh
            if timezone.now() - name_object.last_accessed_at < timedelta(days=1):
                name_object.last_accessed_at = timezone.now()
                name_object.request_count += 1
                name_object.save(update_fields=['last_accessed_at', 'request_count'])

            # Name exists in DB and data is not fresh
            else:
                nationalize_data = parse_name_data(name_param)
                if not nationalize_data:
                    return Response({'error': 'Nationalize API error'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                create_or_update_country_and_probability_objects(name_object, nationalize_data)

        # If no name data in base
        else:
            nationalize_data = parse_name_data(name_param)
            if not nationalize_data:
                return Response({'error': 'Nationalize API error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            name_object = UniqueName.objects.create(name=name_param)
            logger.info(f'Name object with name {name_param} was created successfully')
            create_or_update_country_and_probability_objects(name_object, nationalize_data)

        # Creating final answer
        probabilities = name_object.country_probabilities.all()
        final_data = {
            'name': name_object.name,
            'requests_count': name_object.request_count,
            'country_predictions': probabilities
        }
        final_serializer = FinalAnswerSerializer(instance=final_data)

        logger.info(f'Answer for {name_param} returned successfully')
        return Response(final_serializer.data, status=status.HTTP_200_OK)


class PopularNamesByCountryView(APIView):
    def get(self, request, *args, **kwargs):
        country_code = request.query_params.get('country')

        if not country_code:
            logger.error('Country code parameter is missing')
            return Response({'error': 'Country code parameter is missing'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            country_object = Country.objects.get(code=country_code)

        except Country.DoesNotExist:
            logger.error('Country with such code does not exist in database')
            return Response(
                {'error': 'Country with such code does not exist in database'},
                status=status.HTTP_404_NOT_FOUND
            )

        names_qs = UniqueName.objects.filter(country_probabilities__country=country_object).order_by('-request_count')
        if not names_qs.exists():
            logger.info(f'No names found for {country_code}')
            return Response({'error': f'No names found for {country_code}'}, status=status.HTTP_404_NOT_FOUND)

        else:
            final_data = []
            for name_object in names_qs:
                final_data.append({
                    'name': name_object.name,
                    'frequency': name_object.request_count
                })

            serializer = PopularNameSerializer(data=final_data, many=True)
            if serializer.is_valid(raise_exception=True):
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Unexpected error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

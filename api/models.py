from django.db import models


class UniqueName(models.Model):
    name = models.CharField(primary_key=True, max_length=64)
    request_count = models.IntegerField(default=1)
    last_accessed_at = models.DateTimeField(auto_now=True)
    associated_countries = models.ManyToManyField('Country', through='NameCountryProbability')

    def __str__(self):
        return self.name


class Country(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    associated_names = models.ManyToManyField('UniqueName', through='NameCountryProbability')

    #names
    name_common = models.CharField(max_length=256)
    name_official = models.CharField(max_length=512)
    possible_names = models.JSONField(default=list, blank=True)

    #geography
    region = models.CharField(max_length=256, blank=True)
    capital_name = models.CharField(max_length=256, blank=True)
    capital_latitude = models.FloatField(null=True, blank=True)
    capital_longitude = models.FloatField(null=True, blank=True)

    independent = models.BooleanField(null=True, blank=True)

    #links
    google_maps_url = models.URLField(max_length=512, null=True, blank=True)
    open_maps_url = models.URLField(max_length=512, null=True, blank=True)

    #flags and coat of arms
    flag_png_url = models.URLField(max_length=512, null=True, blank=True)
    flag_svg_url = models.URLField(max_length=512, null=True, blank=True)
    flag_alt_text = models.CharField(max_length=2000, null=True, blank=True)
    coat_of_arms_png_url = models.URLField(max_length=512, null=True, blank=True)
    coat_of_arms_svg_url = models.URLField(max_length=512, null=True, blank=True)

    #borders
    borders = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name_common


class NameCountryProbability(models.Model):
    name = models.ForeignKey(UniqueName, on_delete=models.CASCADE, related_name="country_probabilities")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="name_associations")
    probability = models.FloatField()

    class Meta:
        unique_together = ('name', 'country')
        verbose_name = "Name-Country probability"
        verbose_name_plural = "Name-Country probabilities"

    def __str__(self):
        return f"{self.name.name} - {self.country.name_common}, Probability: {self.probability}"
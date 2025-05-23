from django.db import models

class ITResource(models.Model):
    ResourceName = models.CharField(max_length=255)
    ItemBarcode = models.CharField(max_length=100)
    ResourceTypeName = models.CharField(max_length=100)
    CurrentItemStatus = models.CharField(max_length=50)
    PatronDistrictId = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'Drm.ResourceItemView'
        app_label = 'mssql_views'  # optional if you use routers

from django.db import models
from datetime import datetime
from core.utils import stdDateTime
from django.utils.text import slugify

class Operator(models.Model):
    name = models.CharField("Name", max_length=40, primary_key=True, unique=True)
    
    # Calculated Fields
    link_slug = models.CharField("Link Slug", max_length=30, unique=True, editable=False)   
    abs_link = models.CharField("Link", max_length=30, unique=True, editable=False)
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.link_slug = slugify(self.name)
        self.abs_link = "/operator/" + self.link_slug
        super(Operator, self).save(*args, **kwargs)

class Location(models.Model):
    # Calculated Fields
    link_slug = models.CharField("Link Slug", max_length=30, unique=True, editable=False)   
    abs_link = models.CharField("Link", max_length=30, unique=True, editable=False)
    
    # Entered Fields
    loc_id = models.CharField("ID", max_length=40, primary_key=True)
    name = models.CharField("Name", max_length=50, unique=True)
    machine = models.BooleanField("Machine", default=True)
    
    # Relationships
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Operator")
    
    def __str__(self):
        return self.loc_id
    
    def save(self, *args, **kwargs):
        self.link_slug = slugify(self.loc_id)
        self.abs_link = "/location/" + self.link_slug
        super(Location, self).save(*args, **kwargs)


class Job(models.Model):
    # Calculated Fields
    link_slug = models.CharField("Link Slug", max_length=30, unique=True, editable=False)   
    abs_link = models.CharField("Link", max_length=30, unique=True, editable=False)
    
    # Entered Fields
    work_no = models.CharField("Work No", max_length=50, primary_key=True)
    company = models.CharField("Company", max_length=50)
    job_name = models.CharField("Job Name", max_length=50)
    quantity = models.IntegerField("Qty.")
    job_log = models.JSONField("Job Log", blank=True, null=True)
    
    # Relationships
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Operator")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Location")
    
    def __str__(self):
        return self.work_no + " " + self.job_name
    
    def save(self, *args, **kwargs):
        self.link_slug = slugify(self.work_no)
        self.abs_link = "/job/" + self.link_slug
        super(Job, self).save(*args, **kwargs)

class Operation(models.Model):
    # Calculated Fields
    op_id = models.CharField("Operation ID", max_length=30, primary_key=True)
    link_slug = models.CharField("Link Slug", max_length=30, unique=True, editable=False)   
    abs_link = models.CharField("Link", max_length=30, unique=True, editable=False)
    
    # Relationships
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Operator")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Location")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Job")
    
    # Entered Fieldss
    issue_no = models.CharField("Issue No.", max_length=1)
    op_no = models.IntegerField("Op No.")
    part_no = models.IntegerField("Part No.")
    upload_id = models.IntegerField("Upload ID")        

    # Entered Fields - Optional
    op_name = models.CharField("Op Name", max_length=50, blank=True, null=True)
    drg_no = models.CharField("Drg No.", max_length=50, blank=True, null=True)
    start_time = models.DateTimeField("Start Time", blank=True, null=True)
    end_time = models.DateTimeField("Planned Finish", blank=True, null=True)
    planned_set = models.FloatField("Planned Set Mins", blank=True, null=True)
    planned_run = models.FloatField("Planned Run Mins", blank=True, null=True)
    insp_bool = models.BooleanField("Inspection T/F", default = False)
    op_note = models.CharField("Note", max_length=50, blank=True, null=True)
      
    def __str__ (self):
        return self.op_id
    
    def save(self, *args, **kwargs):
        self.link_slug = slugify(self.op_id)
        self.abs_link = "/operation/" + self.link_slug
        super(Operation, self).save(*args, **kwargs)


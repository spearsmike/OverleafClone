from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class DocumentModel(models.Model):
    docName = models.CharField(max_length=240, default="New Document")
    uploadDate = models.DateField(auto_now_add=True)
    editDateTime = models.DateTimeField(auto_now=True)
    contents = models.CharField(max_length=8192)
    author = models.ForeignKey(User, related_name="author_set", on_delete=models.CASCADE)
    editors = models.ManyToManyField(get_user_model(), related_name="editors_set")
    public = models.BooleanField()
    
    def __str__(self):
        return self.docName

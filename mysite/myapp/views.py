from datetime import datetime, timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponsePermanentRedirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse

from . import models
from . import forms

def logout_view(request):
    logout(request)
    return redirect("/login/")

@login_required
def my_documents(request):
    document_form = forms.CreateDocumentForm()
    context = {
        "title":"My Documents",
        "view":"mydocs",
        "form":document_form,
    }

    return render(request, "document_list.html", context=context)

@login_required
def public_documents(request):
    context = {
        "title":"Public Documents",
        "view":"publicdocs",
    }

    return render(request, "document_list.html", context=context)

@login_required
def all_documents(request):
    context = {
        "title":"My & Public Documents",
        "view":"alldocs",
    }

    return render(request, "document_list.html", context=context)

def create_document_list(document_objects):
    document_list = {}
    document_list["documents"] = []
    for doc in document_objects:
        editor_objects = doc.editors.all()
        temp_doc = {}
        temp_doc["docName"] = doc.docName
        temp_doc["author"] = doc.author.username
        temp_doc["id"] = doc.id
        temp_doc["uploadDate"] = doc.uploadDate
        temp_doc["public"] = doc.public
        temp_doc["editDateTime"] = doc.editDateTime.strftime("%Y-%m-%d")
        time_last_edit = datetime.now(timezone.utc) - doc.editDateTime
        last_edit_string = ""
        suffix = " ago"
        if(time_last_edit.days):
            last_edit_string = str(int(time_last_edit.days)) + " day"
            if(time_last_edit.days > 1):
                last_edit_string += "s"
        elif(time_last_edit.total_seconds()/60 >= 1):
            time_diff_m = divmod(time_last_edit.total_seconds(), 60)[0]
            last_edit_string = str(int(time_diff_m)) + " minute"
            if(time_diff_m > 1):
                last_edit_string += "s"
            if(time_diff_m/60 >= 1):
                time_diff_h = divmod(time_diff_m, 60)[0]
                last_edit_string = str(int(time_diff_h)) + " hour"
                if(time_diff_h > 1):
                    last_edit_string += "s"
        elif(time_last_edit.total_seconds() < 1):
            last_edit_string = "just now"
            suffix = ""
        else:
            last_edit_string = str(int(time_last_edit.total_seconds())) + " seconds"
        temp_doc["lastEdited"] = last_edit_string + suffix

        temp_doc["editors"] = []
        for editor in editor_objects:
            temp_editor = {}
            temp_editor["editor"] = editor.username
            #temp_editor["id"] = editor.id
            temp_doc["editors"] += [temp_editor]
        
        document_list["documents"] += [temp_doc]
    return document_list

@login_required
def all_documents_json(request):
    document_objects = models.DocumentModel.objects.filter(
        author=request.user) | models.DocumentModel.objects.filter(public=True).order_by('uploadDate')
    document_list = create_document_list(document_objects)
    return JsonResponse(document_list)

@login_required
def my_documents_json(request):
    document_objects = models.DocumentModel.objects.filter(author=request.user).order_by('uploadDate')
    document_list = create_document_list(document_objects)
    return JsonResponse(document_list)

@login_required
def public_documents_json(request):
    document_objects = models.DocumentModel.objects.filter(public=True).order_by('uploadDate')
    document_list = create_document_list(document_objects)
    return JsonResponse(document_list)

@login_required
def edit_doc(request, doc_id):
    if request.method == "POST":
        if request.user.is_authenticated :
            save_form = forms.SaveDocumentForm(request.POST)
            if save_form.is_valid():
                save_form.save(request, doc_id)
                save_form = forms.SaveDocumentForm()
            else:
                save_form = forms.SaveDocumentForm()
        else:
            save_form = forms.SaveDocumentForm()
    else:
        save_form = forms.SaveDocumentForm()

    try:
        document = models.DocumentModel.objects.get(id=doc_id)
    except models.DocumentModel.DoesNotExist:
        document = None

    if document:
        if document.editors.filter(username=request.user) or document.public==True:
            save_form.initial = {'body':document.body}
            context = {
                "title":document.docName,
                "body":document.body,
                "doc_id":document.id,
                "form":save_form,
            }
        else:
            context = {
                "title":"Permision Denied",
                "body":"",
            }
    else:
        context = {
            "title":"Document Doesn't Exist",
            "body":"",
        }

    return render(request, "edit.html", context=context)

@login_required
def view_doc(request, doc_id):
    try:
        document = models.DocumentModel.objects.get(id=doc_id)
    except models.DocumentModel.DoesNotExist:
        document = None

    if document:
        if document.editors.filter(username=request.user) or document.public==True:
            context = {
                "title":document.docName,
                "body":document.body,
            }
        else:
            context = {
                "title":"Permision Denied",
                "body":"",
            }
    else:
        context = {
            "title":"Document Doesn't Exist",
            "body":"",
        }

    return render(request, "view.html", context=context)

@login_required
def dashboard(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            document_form = forms.CreateDocumentForm(request.POST)
            if document_form.is_valid():
                document_form.save(request)
                document_form = forms.CreateDocumentForm()
            else:
                document_form = forms.CreateDocumentForm()
        else:
            document_form = forms.CreateDocumentForm()
    else:
        document_form = forms.CreateDocumentForm()

    document = (models.DocumentModel.objects.filter(author=request.user) | models.DocumentModel.objects.filter(public=True).order_by('uploadDate')).first()
    context = {
        "title":"Landing",
        "document":document,
        "form":document_form,
    }

    return render(request, "dashboard.html", context=context)

def page(request, page=0):
    title = "Title"
    content = list(range((page+1)*10)[page*10:page*10+10])
    context = {
        "title":title,
        "body":content,
        "seen":True,
        "prev":page-1,
        "next":page+1
    }
    return render(request, "page.html", context=context)

def register(request):
    if request.method == "POST":
        form_instance = forms.RegistrationForm(request.POST)
        if form_instance.is_valid():
            user = form_instance.save()
            login(request, user)
            return redirect("/")
    else:
        form_instance = forms.RegistrationForm()
    
    context = {
        "form":form_instance,
    }
    return render(request, "registration/register.html", context=context)

def chat(request):
    return render(request, "chat.html")

def chat_room(request, doc_id):
    try:
        document = models.DocumentModel.objects.get(id=doc_id)
    except models.DocumentModel.DoesNotExist:
        document = None

    if document:
        if document.editors.filter(username=request.user) or document.public==True:
            context = {
                "title":document.docName,
                "body":document.body,
                "room_name":doc_id,
            }
        else:
            context = {
                "title":"Permision Denied",
                "body":"",
                "room_name":doc_id,
            }
    else:
        context = {
            "title":"Document Doesn't Exist",
            "body":"",
            "room_name":doc_id,
        }

    return render(request, "room.html", context=context)

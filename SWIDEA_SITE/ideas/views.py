from django.shortcuts import render, redirect
from .models import Idea, DevTool
from .forms import IdeaForm, DevToolForm

# Create your views here.
def ideas_list(request):
    sort = request.GET.get("sort","")
    ideas = Idea.objects.all()

    if sort == "interest":
        ideas = ideas.order_by("-interest")
    elif sort =="name":
        ideas = ideas.order_by("-title")
    elif sort =="createdAt":
        ideas = ideas.order_by("-id")
    elif sort =="starred":
        ideas = ideas.order_by("-isstarred")
    context = {
        "ideas" : ideas,
    }
    return render(request, "ideas_list.html", context)

def idea_detail(request, pk):
    idea = Idea.objects.get(id=pk)
    context = {
        "idea" : idea,
    }
    return render(request, "idea_detail.html", context)

def idea_create(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("ideas:ideas_list")
    else:
        form = IdeaForm()
    context = { "form": form }
    return render(request, "idea_form.html", context)

def idea_update(request, pk):
    idea = Idea.objects.get(id=pk)
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES, instance=idea)
        if form.is_valid():
            form.save()
            return redirect("ideas:idea_detail",pk=pk)
        else:
            print("POST:", request.POST)
            print("FILES:", request.FILES)
            print("errors:", form.errors)  
    else:
        form = IdeaForm(instance=idea)
    context = { "form" : form }
    return render(request,"idea_form.html",context)

def idea_delete(request, pk):
    if request.method == "POST":
        idea = Idea.objects.get(id=pk)
        idea.delete()
    return redirect("ideas:ideas_list")



def devtool_list(request):
    devtools = DevTool.objects.all()
    context = {
        "devtools" : devtools,
    }
    return render(request, "devtool_list.html", context)

def devtool_create(request):
    if request.method == "POST":
        form = DevToolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("ideas:devtool_list")
    else:
        form = DevToolForm()
    context = {"form":form}
    return render(request, "devtool_form.html",context)
        

def devtool_detail(request, pk):
    devtool = DevTool.objects.get(id=pk)
    idea_list = devtool.ideas.all()
    context = { 
        "devtool" : devtool ,
        "idea_list" : idea_list,
    }
    return render(request,"devtool_detail.html", context)

def devtool_update(request, pk):
    devtool = DevTool.objects.get(id=pk)
    if request.method == "POST":
        form = DevToolForm(request.POST, instance=devtool)
        if form.is_valid:
            form.save()
            return redirect("ideas:devtool_detail",pk=pk)
    else:
        form = DevToolForm(instance=devtool)
    context = { "form" : form }
    return render(request,"devtool_form.html",context)

def devtool_delete(request, pk):
    if request.method == "POST":
        devtool = DevTool.objects.get(id=pk)
        devtool.delete()
    return redirect("ideas:devtool_list")
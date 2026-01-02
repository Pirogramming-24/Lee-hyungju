from django.shortcuts import render, redirect
from django.db.models import Exists, OuterRef
from .models import Idea, DevTool, IdeaStar
from .forms import IdeaForm, DevToolForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

# Create your views here.
def ideas_list(request):
    sort = request.GET.get("sort","")
    ideas = Idea.objects.all()
    starred_ids = set(
        IdeaStar.objects.values_list("idea_id", flat=True)
    )

    if sort == "interest":
        ideas = ideas.order_by("-interest")
    elif sort =="name":
        ideas = ideas.order_by("title")
    elif sort =="createdAt":
        ideas = ideas.order_by("-id")
    elif sort =="starred":
        ideas = Idea.objects.annotate(
            is_starred=Exists(
                IdeaStar.objects.filter(idea=OuterRef("pk"))
            )
        ).order_by("-is_starred", "-id")
    context = {
        "ideas" : ideas,
        "starred_ids": starred_ids,
        "sort" : sort,
    }
    return render(request, "ideas_list.html", context)

def idea_detail(request, pk):
    idea = Idea.objects.get(id=pk)
    starred_ids = set(
        IdeaStar.objects.values_list("idea_id", flat=True)
    )
    context = {
        "idea" : idea,
        "starred_ids": starred_ids,
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

@require_POST
def idea_star_toggle_api(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    star_qs = IdeaStar.objects.filter(idea=idea)
    if star_qs.exists():
        star_qs.delete()
        starred = False
    else:
        IdeaStar.objects.create(idea=idea)
        starred = True

    star_count = IdeaStar.objects.filter(idea=idea).count()

    return JsonResponse({
        "ok": True,
        "idea_id": idea.id,
        "starred": starred,
        "star_count": star_count,
    })

@require_POST
def idea_interest_api(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    action = request.POST.get("action")

    if action == "plus":
        idea.interest += 1
    elif action == "minus":
        idea.interest = max(0, idea.interest - 1)  # 음수 방지

    idea.save()

    return JsonResponse({
        "ok": True,
        "interest": idea.interest,
    })

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
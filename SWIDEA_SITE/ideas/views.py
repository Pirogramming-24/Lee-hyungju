from django.shortcuts import render
from .models import Idea, DevTool

# Create your views here.
def ideas_list(request):
    # sort = request.Get.
    ideas = Idea.objects.all()
    context = {
        "ideas" : ideas,
    }
    return render(request, "ideas_list.html", context)

# def idea_detail(request, pk):
#     idea = Idea.objects.get(id=pk)
#     context = {
#         "idea" : idea,
#     }
#     return render(request, "idea_detail.html", context)
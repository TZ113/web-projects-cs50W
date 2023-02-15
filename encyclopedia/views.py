from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from . import util
import random



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry_page(request, title):
    
    if util.get_entry(title):
        return render(request, "encyclopedia/entry_page.html", {
            "title": title,
            "content":util.md_to_html(util.get_entry(title))
        })
    elif util.get_entry(title.capitalize()):
        return render(request, "encyclopedia/entry_page.html", {
            "title": title.capitalize(),
            "content":util.md_to_html(util.get_entry(title.capitalize()))
        })   
    elif util.get_entry(title.title()):
        return render(request, "encyclopedia/entry_page.html", {
            "title": title.title(),
            "content":util.md_to_html(util.get_entry(title.title()))
        })   
    elif util.get_entry(title.upper()):
        return render(request, "encyclopedia/entry_page.html", {
            "title": title.upper(),
            "content":util.md_to_html(util.get_entry(title.upper()))
        })
    elif util.get_entry(title.lower()):
        return render(request, "encyclopedia/entry_page.html", {
            "title": title.lower(),
            "content":util.md_to_html(util.get_entry(title.lower()))
        })
    else:
        return HttpResponseNotFound("<h1 style=\"position:absolute; color:grey; top:100px; left:700px;\">Page not found</h1>")
        
        
def search(request):
    query = request.GET.get("q")

    if util.get_entry(query):
        return render(request, "encyclopedia/entry_page.html", {
            "title":query,
            "content":util.md_to_html(util.get_entry(query))
        })
    elif util.get_entry(query.capitalize()):
        return render(request, "encyclopedia/entry_page.html", {
            "title": query.capitalize(),
            "content":util.md_to_html(util.get_entry(query.capitalize()))
        })
    elif util.get_entry(query.title()):
        return render(request, "encyclopedia/entry_page.html", {
            "title": query.title(),
            "content":util.md_to_html(util.get_entry(query.title()))
        })
    elif util.get_entry(query.upper()):
        return render(request, "encyclopedia/entry_page.html", {
            "title": query.upper(),
            "content":util.md_to_html(util.get_entry(query.upper()))
        })
    elif util.get_entry(query.lower()):
        return render(request, "encyclopedia/entry_page.html", {
            "title": query.lower(),
            "content":util.md_to_html(util.get_entry(query.lower()))
        })
    else:
        entries = util.list_entries()
        results = []
        for entry in entries:
            if query in entries or query.title() in entries or query.capitalize() in entry or query.upper() in entry or query.lower() in entry: 
                results.append(entry)
                
    return render(request, "encyclopedia/results.html", {
        "results": results})    

        
def create_page(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        entries = util.list_entries()
        if not title:
            return HttpResponse("<h3 style=\"position:absolute; color:grey; top:100px; left:700px;\">Cannot Create a Page Without any Title</h3>")
        elif not content:
            return HttpResponse( "<h3 style=\"position:absolute; color:grey; top:100px; left:700px;\">Cannot Create an Empty Page</h3>")
        elif title in entries or title.capitalize() in entries or title.title() in entries or title.upper() in entries or title.lower() in entries:
            return HttpResponse("<h3 style=\"position:absolute; color:grey; top:100px; left:700px;\">Page Already Exists.</h3>")
        util.save_entry(title, content)
        return redirect('entry_page', title=title)
    
    return render(request, "encyclopedia/create_page.html")


def edit_page(request, title):
    return render(request, "encyclopedia/edit_page.html", {
        "title": title,
        "content": util.get_entry(title)
    })
    
    
def save_edited_page(request):
    title = request.POST.get("title")
    content = request.POST.get("content")
    util.save_entry(title, content)
    return redirect('entry_page', title=title)


def rnd_page(request):
    entries = util.list_entries()
    title = random.choice(entries)
    return redirect('entry_page', title=title)


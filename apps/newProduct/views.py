from django.core.checks import messages
from django.contrib import messages
from django.db.models.query_utils import check_rel_lookup_compatibility
from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from apps.newProduct.models import Product, Category, SubCategory, SubSubCategory, Comment, CommentForm


def index(request):
    return HttpResponse("My Product Page")


def addcomment(request, id):
    url = request.META.get('HTTP_REFERER')  # get last url
    
    if request.method == 'POST':  # check post
        form = CommentForm(request.POST)
        if form.is_valid():
            data = Comment()  # create relation with model
            data.subject = form.cleaned_data['subject']
            data.comment = form.cleaned_data['comment']
            data.rate = form.cleaned_data['rate']
            data.ip = request.META.get('REMOTE_ADDR')
            data.product_id = id
            current_user = request.user
            data.user_id = current_user.id
            data.save()  # save data to table
            messages.success(
                request, "Your review has been submitted.")
            return HttpResponseRedirect(url)

    return HttpResponseRedirect(url)

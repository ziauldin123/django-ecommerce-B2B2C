from django.core.checks import messages
from django.contrib import messages
from django.db.models.query_utils import check_rel_lookup_compatibility
from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render

from apps.newProduct.models import  Product,Category,SubCategory,SubSubCategory,Comment,CommentForm


def index(request):
   return  HttpResponse("My Product Page")


# def category(request,category_slug):
#    category=get_object_or_404(Category,slug=category_slug)
#    products=Product.objects.filter(visible=True)

#    return render(
#       request,
#       'product/category.html',
#       {
#          'category':category,
#          'products':products
#       }
#    )   

# def subcategory(request,category_slug, subcategory_slug):
#    category=get_object_or_404(SubCategory,slug=subcategory_slug)

#    products=Product.objects.filter(visible=True)

#    return render(
#       request,
#       'product/subcategory.html',
#       {
#          'category':category,
#          'products':products
#       }
#    )

# def subsubcategory(request,category_slug, subcategory_slug, subsubcategory_slug):
#    category=get_object_or_404(SubSubCategory,slug=subsubcategory_slug)
#    products=Product.objects.filter(visible=True)

#    return render(
#       request,
#       'product/subsubcategory.html',
#       {
#          'category':category,
#          'products':products
#       }
#    )

def addcomment(request,id):
   url = request.META.get('HTTP_REFERER')  # get last url
   #return HttpResponse(url)
   if request.method == 'POST':  # check post
      form = CommentForm(request.POST)
      if form.is_valid():
         data = Comment()  # create relation with model
         data.subject = form.cleaned_data['subject']
         data.comment = form.cleaned_data['comment']
         data.rate = form.cleaned_data['rate']
         data.ip = request.META.get('REMOTE_ADDR')
         data.product_id=id
         current_user= request.user
         data.user_id=current_user.id
         data.save()  # save data to table
         messages.success(request, "Your review has ben sent. Thank you for your interest.")
         return HttpResponseRedirect(url)

   return HttpResponseRedirect(url)    

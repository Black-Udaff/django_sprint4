from django.shortcuts import render, get_object_or_404
from blog.models import Post, Category
from django.utils import timezone
from .forms import PostForm
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)

NUMBER_OF_POSTS = 5

class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = 10
    queryset = (
        Post.objects.select_related("author", "location", "category")
        .filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
    )


def post_detail(request, pk):
    template = "blog/detail.html"
    post = get_object_or_404(
        Post.objects.select_related().filter(
            pk=pk,
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
    )
    context = {"post": post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = "blog/category.html"
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    post_list = Post.objects.filter(
        pub_date__lte=timezone.now(), is_published=True, category=category
    )
    context = {"category": category, "post_list": post_list}
    return render(request, template, context)


def create_post(request):
    template = "blog/create.html"
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
    form = PostForm()
    context = {'form': form}
    return render(request, template, context)

def profile():
    pass

from django.shortcuts import render, get_object_or_404
from blog.models import Post, Category, User
from django.utils import timezone
from .forms import PostForm
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.paginator import Paginator
from .forms import UserForm
from django.urls import reverse_lazy

NUMBER_OF_POSTS = 5


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = 10
    queryset = Post.objects.select_related(
        "author", "location", "category"
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
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





# def create_post(request):
#     template = "blog/create.html"
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             form.save()
#     form = PostForm()
#     context = {'form': form}
#     return render(request, template, context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    
    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])

def profile(request, user_name):
    # Получить объект пользователя
    user = get_object_or_404(User, username=user_name)
    
    # Получить все публикации этого пользователя
    posts = Post.objects.filter(author=user, is_published=True)
    
    # Применить пагинацию
    paginator = Paginator(posts, 10)  # Показать 10 публикаций на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    
    return render(request, 'blog/profile.html', context)



def edit_profile(request):

    template = 'blog/user.html'
    # user = User.objects.get(username=request.user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()

    form = UserForm(instance=request.user)
    return render(request, template, {'form': form})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    login_url = 'login'
    # success_url = reverse_lazy('blog:profile',) # ne redirektit!!!!

    def get_object(self, queryset=None):
        return self.request.user
    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])
    


# class ProfileView(ListView):
#     model = Post
#     template_name = "blog/profile.html"
#     context_object_name = "posts"
#     paginate_by = 10  # Количество постов на странице

#     def get_queryset(self):
#         user_name = self.kwargs['user_name']
#         user = User.objects.get(username=user_name)
#         return Post.objects.filter(author=user)
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = User.objects.get(username=request.user)
        
#         context["profile"] = user
#         return context
class PostDeleteView(LoginRequiredMixin, DeleteView):
    pass



class PostUpdateView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    def get_object(self, queryset=None):
        return self.request.post 

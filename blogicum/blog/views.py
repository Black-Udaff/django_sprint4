from django.shortcuts import render, get_object_or_404
from blog.models import Post, Category, User, Comment
from django.utils import timezone
from .forms import PostForm, CommentForm
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

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


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"

    def get_queryset(self):
        return Post.objects.select_related().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Записываем в переменную form пустой объект формы.
        context['form'] = CommentForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['comments'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.comments.select_related('author')
        )
        return context


# def category_posts(request, category_slug):
#     template = "blog/category.html"
#     category = get_object_or_404(
#         Category, slug=category_slug, is_published=True
#     )
#     post_list = Post.objects.filter(
#         pub_date__lte=timezone.now(), is_published=True, category=category
#     )
#     context = {"category": category, "post_list": post_list}
#     return render(request, template, context)


class CategoryPostsView(ListView):
    model = Post
    template_name = "blog/category.html"
    context_object_name = "post_list"
    paginate_by = 10  # например, 10 постов на страницу
    
    def get_queryset(self):
        # Получаем категорию по slug
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True)
        
        # Фильтруем посты по категории
        return Post.objects.filter(pub_date__lte=timezone.now(), is_published=True, category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])


def profile(request, user_name):
    user = get_object_or_404(User, username=user_name)
    posts = Post.objects.filter(author=user, is_published=True)
    paginator = Paginator(posts, 10)
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


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete'] = True
        context['form'] = PostForm(instance=self.get_object())
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['pk'],
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['pk']}
        )


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    context_object_name = 'comment'

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, id=comment_id)

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse_lazy('blog:post_detail', kwargs={'pk': post_id})

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

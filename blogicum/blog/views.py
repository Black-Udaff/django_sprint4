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
        context['congratulations'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.comments.select_related('author')
        )
        return context


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
# class PostDeleteView(LoginRequiredMixin, DeleteView):
#     model = Post
#     success_url = reverse_lazy('blog:index')
#     template_name = "blog/create.html"


#     def dispatch(self, request, *args, **kwargs):
#         # Получаем объект по первичному ключу и автору или вызываем 404 ошибку.
#         get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
#         # Если объект был найден, то вызываем родительский метод,
#         # чтобы работа CBV продолжилась.
#         return super().dispatch(request, *args, **kwargs)


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

    def get_object(self, queryset=None):
        return self.request.post


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['id'],
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )

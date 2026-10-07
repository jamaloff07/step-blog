from django.shortcuts import get_object_or_404
# from rest_framework import generics, status
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from blog.models import Post, Category, Tag
from .serializers import PostSerializer, CategorySerializer, TagSerializer, CommentSerializer

# "İki dəfə yaz": blog/views.py-dakı səhifələrin API əkizləri.
#   HTML view:  obyektləri götür → template-ə göndər → render()      → brauzer səhifə görür
#   API view:   obyektləri götür → serializer-ə ver  → Response()    → mobil / JS tətbiq JSON alır
#
# @api_view(["GET", "POST"]) — bu view hansı HTTP metodları qəbul edir. Başqası gəlsə → 405.
# request.data  — gələn JSON (request.POST-un API variantı)
# Response(...) — dict/list → JSON. Browsable API-də isə HTML səhifə kimi görünür.
#
# Nişanlar:  [DƏRS 14] müəllim · [DƏRS 14] praktikadan sonra müəllim · [PRAKTİKA 14] tələbə · [EV 14] tapşırıq 1–3 / bonus · [REFERANS 14] tələbəyə verilmir


# ═════════════════════════ POSTLAR ═════════════════════════

# [DƏRS 14] əkizi: blog/views.py → PostListView (siyahı) + PostCreateView (yaratma) — API-də ikisi bir view-dur
# @api_view(["GET", "POST"])
# def post_list(request):
#     if request.method == "GET":
#         posts = Post.objects.all()                                # hamısı (Dərs 15-də yalnız dərc olunmuşlar qalacaq)
#         serializer = PostSerializer(posts, many=True)             # many=True → siyahı (list), tək obyekt deyil
#         return Response(serializer.data)                          # .data = JSON-a hazır list[dict]

#     serializer = PostSerializer(data=request.data)                # gələn JSON-u serializer-ə ver (form = PostForm(request.POST) kimi)
#     if serializer.is_valid():                                     # bütün yoxlamalar keçdi?
#         serializer.save()                                         # bazaya yaz (ModelForm.save() kimi)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)        # 201 = yaradıldı
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)      # 400 = sən səhv göndərdin



class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_published=True)
    serializer_class = PostSerializer
    
    @action(detail=True, methods=["get"])
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = post.comments.filter(is_active=True, parent=None)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
        
    
    
# class PostDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer

# [DƏRS 14] əkizi: post_detail + PostUpdateView + PostDeleteView — API-də üçü bir view-dur
# @api_view(["GET", "PUT", "DELETE"])
# def post_detail(request, post_id):
#     post = get_object_or_404(Post, id=post_id)                    # tapmasa DRF 404 JSON qaytarır: {"detail": "..."}

#     if request.method == "GET":
#         serializer = PostSerializer(post)                         # bir obyekt → many yazılmır
#         return Response(serializer.data)

#     if request.method == "PUT":
#         serializer = PostSerializer(post, data=request.data)      # instance + data → yenilə (PostForm(request.POST, instance=post) kimi)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)                      # 200 (default)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     post.delete()                                                 # DELETE
#     return Response(status=status.HTTP_204_NO_CONTENT)            # 204 = oldu, amma göndərməyə məzmun yoxdur


# ═════════════════════════ KATEQORİYALAR ═════════════════════════

# [PRAKTİKA 14] — post_list-in əkizi (tələbə yazır)
@api_view(["GET", "POST"])
def category_list(request):
    if request.method == "GET":
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# [DƏRS 14] praktikadan SONRA müəllim yazır — post_detail-in əkizi (“qalanını mən yazıram, siz baxırsınız”)
@api_view(["GET", "PUT", "DELETE"])
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "GET":
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    category.delete()                                             # postu olan kateqoriya → on_delete=PROTECT → 500 (Dərs 10)
    return Response(status=status.HTTP_204_NO_CONTENT)


# ═════════════════════════ TEQLƏR ═════════════════════════

# [EV 14] tapşırıq 1 — category_list-in əkizi
@api_view(["GET", "POST"])
def tag_list(request):
    if request.method == "GET":
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

    serializer = TagSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# [EV 14] tapşırıq 2 — category_detail-in əkizi
@api_view(["GET", "PUT", "DELETE"])
def tag_detail(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)

    if request.method == "GET":
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    tag.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def tag_posts(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    posts = tag.posts.filter(is_published=True)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


# ═════════════════════════ DİGƏR ═════════════════════════

# [EV 14] tapşırıq 3 — sadə saylar (saytdakı /stats/ səhifəsi varsa — onun əkizi). Model yoxdur, serializer də lazım deyil: adi dict
@api_view(["GET"])
def stats(request):
    data = {
        "post_count": Post.objects.filter(is_published=True).count(),
        "category_count": Category.objects.count(),
        "tag_count": Tag.objects.count(),
    }
    return Response(data)

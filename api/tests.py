# Yalnız müəllim üçün — dərsdə YAZILMIR, tələbəyə göstərilmir.
# API-nin hər ünvanını yoxlayır:  uv run manage.py test api
# (blog/tests.py Dərs 13-dən qalır — HTML tərəf də işləməlidir:  uv run manage.py test)
from rest_framework.test import APITestCase

from blog.models import Post, Category, Tag


class Lesson14ApiTests(APITestCase):
    fixtures = ["demo_full"]

    # ── [DƏRS 14] postlar ──
    def test_post_list(self):
        r = self.client.get("/api/posts/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 9)
        self.assertEqual(r.json()[0]["title"], "VS Code-da 7 faydalı qısayol")      # ordering = -created_at
        self.assertEqual(r.json()[0]["author"], 4)                                   # hələ id-dir (Dərs 16-da username olacaq)

    def test_post_create(self):
        data = {"title": "API ilə yazılan post", "author": 1, "category": 1, "tags": [1, 2], "content": "Postman-dan gəldi."}
        r = self.client.post("/api/posts/", data, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(r.json()["views"], 0)
        post = Post.objects.get(title="API ilə yazılan post")
        self.assertEqual(post.tags.count(), 2)
        self.assertEqual(post.author.username, "nigar")

    def test_post_create_invalid(self):
        r = self.client.post("/api/posts/", {"title": "Başlıqsız"}, format="json")  # content, author, category yoxdur
        self.assertEqual(r.status_code, 400)
        self.assertIn("content", r.json())
        self.assertIn("author", r.json())
        self.assertEqual(Post.objects.count(), 9)

    def test_post_detail_put_delete(self):
        r = self.client.get("/api/posts/1/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["title"], "Python-da ilk addım")
        self.assertEqual(self.client.get("/api/posts/999/").status_code, 404)
        self.assertIn("detail", self.client.get("/api/posts/999/").json())

        data = {"title": "Python-da ilk addım (yenilənib)", "author": 1, "category": 1, "content": "Yeni mətn."}
        r = self.client.put("/api/posts/1/", data, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(Post.objects.get(id=1).title, "Python-da ilk addım (yenilənib)")

        r = self.client.delete("/api/posts/1/")
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Post.objects.filter(id=1).exists())
        self.assertEqual(self.client.patch("/api/posts/2/", {}).status_code, 405)   # icazə verilməyən metod

    # ── [PRAKTİKA 14] category_list · [DƏRS 14] category_detail ──
    def test_category_api(self):
        self.assertEqual(len(self.client.get("/api/categories/").json()), 3)
        r = self.client.post("/api/categories/", {"name": "İdman", "slug": "idman"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Category.objects.count(), 4)
        self.assertEqual(self.client.post("/api/categories/", {"name": "slugsuz"}, format="json").status_code, 400)
        self.assertEqual(self.client.get("/api/categories/1/").json()["name"], "Proqramlaşdırma")
        self.assertEqual(self.client.get("/api/categories/99/").status_code, 404)
        r = self.client.put("/api/categories/1/", {"name": "Kod", "slug": "kod"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Category.objects.get(id=1).name, "Kod")
        new_id = Category.objects.get(slug="idman").id
        self.assertEqual(self.client.delete(f"/api/categories/{new_id}/").status_code, 204)

    # ── [EV 14] teqlər, stats ──
    def test_tag_api(self):
        self.assertEqual(len(self.client.get("/api/tags/").json()), 5)
        r = self.client.post("/api/tags/", {"name": "vscode", "slug": "vscode"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.client.get("/api/tags/1/").json()["name"], "python")
        r = self.client.put("/api/tags/1/", {"name": "python3", "slug": "python3"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Tag.objects.get(id=1).name, "python3")
        self.assertEqual(self.client.delete("/api/tags/1/").status_code, 204)
        self.assertEqual(self.client.get("/api/tags/1/").status_code, 404)

    def test_stats(self):
        r = self.client.get("/api/stats/")
        self.assertEqual(r.json(), {"post_count": 9, "category_count": 3, "tag_count": 5})

    def test_html_blog_still_works(self):
        for url in ["/", "/post/1/", "/categories/", "/tag/python/"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

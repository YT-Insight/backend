import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── YouTube data ─────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Channel",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("youtube_channel_id", models.CharField(max_length=255, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("thumbnail_url", models.URLField(blank=True)),
                ("subscriber_count", models.BigIntegerField(default=0)),
                ("video_count", models.IntegerField(default=0)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Video",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("channel", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="videos",
                    to="analysis.channel",
                )),
                ("youtube_video_id", models.CharField(max_length=255, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("view_count", models.BigIntegerField(null=True, blank=True)),
                ("like_count", models.BigIntegerField(null=True, blank=True)),
                ("comment_count", models.BigIntegerField(null=True, blank=True)),
                ("published_at", models.DateTimeField(null=True, blank=True)),
                ("thumbnail_url", models.URLField(blank=True)),
            ],
            options={"abstract": False},
        ),

        # ── Analysis records ─────────────────────────────────────────────────
        migrations.CreateModel(
            name="Analysis",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="analyses",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("channel", models.ForeignKey(
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="analyses",
                    to="analysis.channel",
                    null=True,
                    blank=True,
                )),
                ("input_url", models.URLField()),
                ("videos_analyzed", models.IntegerField(default=0)),
                ("comments_analyzed", models.IntegerField(default=0)),
                ("status", models.CharField(
                    max_length=20,
                    choices=[
                        ("pending", "Pending"),
                        ("processing", "Processing"),
                        ("completed", "Completed"),
                        ("failed", "Failed"),
                    ],
                    default="pending",
                    db_index=True,
                )),
                ("error_message", models.TextField(blank=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="AnalysisVideo",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("analysis", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="analysis_videos",
                    to="analysis.analysis",
                )),
                ("video", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="analysis_videos",
                    to="analysis.video",
                )),
                ("comments_fetched", models.IntegerField(default=0)),
            ],
            options={
                "abstract": False,
                "unique_together": {("analysis", "video")},
            },
        ),

        # ── Comments ──────────────────────────────────────────────────────���──
        migrations.CreateModel(
            name="Comment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("analysis_video", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="comments",
                    to="analysis.analysisvideo",
                )),
                ("text", models.TextField()),
                ("author", models.CharField(max_length=255, blank=True)),
                ("like_count", models.IntegerField(default=0)),
                ("published_at", models.DateTimeField(null=True, blank=True)),
            ],
            options={"abstract": False},
        ),

        # ── AI result models ─────────────────────────────────────────────────
        migrations.CreateModel(
            name="AnalysisResult",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("analysis", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="result",
                    to="analysis.analysis",
                )),
                ("summary", models.TextField(blank=True)),
                ("sentiment", models.CharField(
                    max_length=20,
                    choices=[
                        ("positive", "Positive"),
                        ("negative", "Negative"),
                        ("mixed", "Mixed"),
                        ("neutral", "Neutral"),
                    ],
                    default="neutral",
                )),
                ("audience_type", models.CharField(max_length=255, blank=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="AnalysisTopic",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("analysis", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="topics",
                    to="analysis.analysis",
                )),
                ("topic", models.CharField(max_length=255)),
                ("relevance_score", models.DecimalField(max_digits=4, decimal_places=2)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="AnalysisQuestion",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("analysis", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="questions",
                    to="analysis.analysis",
                )),
                ("question", models.CharField(max_length=500)),
                ("answer", models.TextField(blank=True)),
                ("category", models.CharField(max_length=50, blank=True, default="custom")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="AnalysisSuggestion",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("analysis", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="suggestions",
                    to="analysis.analysis",
                )),
                ("suggestion", models.TextField()),
                ("category", models.CharField(max_length=50, blank=True, default="content")),
            ],
            options={"abstract": False},
        ),

        # ── Indexes ───────────────────────────────────────────────────────────
        migrations.AddIndex(
            model_name="channel",
            index=models.Index(fields=["youtube_channel_id"], name="channel_yt_id_idx"),
        ),
        migrations.AddIndex(
            model_name="video",
            index=models.Index(fields=["youtube_video_id"], name="video_yt_id_idx"),
        ),
        migrations.AddIndex(
            model_name="analysis",
            index=models.Index(fields=["user", "status"], name="analysis_user_status_idx"),
        ),
        migrations.AddIndex(
            model_name="analysis",
            index=models.Index(fields=["user", "-created_at"], name="analysis_user_date_idx"),
        ),
    ]

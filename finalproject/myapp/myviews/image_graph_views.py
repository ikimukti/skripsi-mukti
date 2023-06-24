from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus
from django.views.generic import ListView
from django.contrib.auth.models import User
from myapp.models import Image, ImagePreprocessing, Segmentation, SegmentationResult
from django.db.models import Q


class ImageGraphClassView(ListView):
    model = Image
    template_name = "myapp/image/image_graph.html"
    context_object_name = "images"
    paginate_by = 10
    extra_context = {
        "title": "Image Graph",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
    }

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.extra_context)
            return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        search_query = self.request.GET.get("search")
        queryset = Image.objects.all()

        if search_query:
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi yang diinginkan.
            queryset = queryset.filter(
                Q(color__icontains=search_query)
            ).prefetch_related(
                "imagepreprocessing_set",
                "imagepreprocessing_set__segmentation_set",
                "imagepreprocessing_set__segmentation_set__segmentationresult_set",
            )
            # change the page_obj add the search_query
            self.extra_context["search"] = search_query

        # print queryset 1 data saja tampilkan lengkap dengan relasi
        data = queryset.first()

        # Cetak informasi dari model Image
        print("Image:")
        print(f"ID: {data.id}")
        print(f"Uploader: {data.uploader.username}")
        # Cetak informasi lainnya dari model Image

        # Cetak informasi dari model ImagePreprocessing
        image_preprocessing = data.imagepreprocessing_set.first()
        print("\nImage Preprocessing:")
        print(f"ID: {image_preprocessing.id}")
        # Cetak informasi lainnya dari model ImagePreprocessing

        # Cetak informasi dari model Segmentation
        segmentation = image_preprocessing.segmentations.first()
        print("\nSegmentation:")
        print(f"ID: {segmentation.id}")
        # Cetak informasi lainnya dari model Segmentation

        # Cetak informasi dari model SegmentationResult
        segmentation_result = segmentation.segmentationresult_set.first()
        print("\nSegmentation Result:")
        print(f"ID: {segmentation_result.id}")
        # Cetak informasi lainnya dari model SegmentationResult

        # Ambil semua nilai unik dari field color, width, height
        color_dict = queryset.values_list("color", flat=True).distinct()
        color_dict = list(color_dict)
        width_dict = queryset.values_list("width", flat=True).distinct()
        width_dict = list(width_dict)
        height_dict = queryset.values_list("height", flat=True).distinct()
        height_dict = list(height_dict)
        size_dict = queryset.values_list("size", flat=True).distinct()
        # convert size_dict to KB and MB
        size_dict = [size / 1024 if size > 1024 else size for size in size_dict]
        # size_dict float 2 digit
        size_dict = [round(size, 2) for size in size_dict]
        size_dict = list(size_dict)
        channel_dict = queryset.values_list("channel", flat=True).distinct()
        channel_dict = list(channel_dict)
        format_dict = queryset.values_list("format", flat=True).distinct()
        format_dict = list(format_dict)
        dpi_dict = queryset.values_list("dpi", flat=True).distinct()
        dpi_dict = list(dpi_dict)
        distance_dict = queryset.values_list("distance", flat=True).distinct()
        distance_dict = list(distance_dict)
        uploader_dict = queryset.values_list("uploader__username", flat=True).distinct()
        uploader_dict = list(uploader_dict)
        # Buat dictionary untuk memetakan nilai color, width, height menjadi angka
        color_mapping = {color: index for index, color in enumerate(color_dict)}
        width_mapping = {width: index for index, width in enumerate(width_dict)}
        height_mapping = {height: index for index, height in enumerate(height_dict)}
        size_mapping = {size: index for index, size in enumerate(size_dict)}
        channel_mapping = {channel: index for index, channel in enumerate(channel_dict)}
        format_mapping = {format: index for index, format in enumerate(format_dict)}
        dpi_mapping = {dpi: index for index, dpi in enumerate(dpi_dict)}
        distance_mapping = {
            distance: index for index, distance in enumerate(distance_dict)
        }
        uploader_mapping = {
            uploader: index for index, uploader in enumerate(uploader_dict)
        }

        # Ambil semua nilai dari field color, width, height
        color_data = queryset.values_list("color", flat=True)
        width_data = queryset.values_list("width", flat=True)
        height_data = queryset.values_list("height", flat=True)
        size_data = queryset.values_list("size", flat=True)
        size_data = [size / 1024 if size > 1024 else size for size in size_data]
        size_data = [round(size, 2) for size in size_data]
        channel_data = queryset.values_list("channel", flat=True)
        format_data = queryset.values_list("format", flat=True)
        dpi_data = queryset.values_list("dpi", flat=True)
        distance_data = queryset.values_list("distance", flat=True)
        uploader_data = queryset.values_list("uploader__username", flat=True)
        color_data = list(color_data)
        width_data = list(width_data)
        height_data = list(height_data)
        size_data = list(size_data)
        channel_data = list(channel_data)
        format_data = list(format_data)
        dpi_data = list(dpi_data)
        distance_data = list(distance_data)
        uploader_data = list(uploader_data)

        # Ubah color_data menjadi angka sesuai dengan color_mapping
        color_data_int = [color_mapping[color] for color in color_data]
        width_data_int = [width_mapping[width] for width in width_data]
        height_data_int = [height_mapping[height] for height in height_data]
        size_data_int = [size_mapping[size] for size in size_data]
        channel_data_int = [channel_mapping[channel] for channel in channel_data]
        format_data_int = [format_mapping[format] for format in format_data]
        dpi_data_int = [dpi_mapping[dpi] for dpi in dpi_data]
        distance_data_int = [distance_mapping[distance] for distance in distance_data]
        uploader_data_int = [uploader_mapping[uploader] for uploader in uploader_data]

        # Buat labels berdasarkan color_data_int
        labels = [
            "{} {}".format(color_dict[color_data_int[i]], i + 1)
            for i in range(len(color_data_int))
        ]

        # context chart_js
        self.extra_context["chartjs"] = {
            "data_color": color_data_int,
            "dict_color": color_dict,
            "data_width": width_data_int,
            "dict_width": width_dict,
            "data_height": height_data_int,
            "dict_height": height_dict,
            "data_size": size_data_int,
            "dict_size": size_dict,
            "data_channel": channel_data_int,
            "dict_channel": channel_dict,
            "data_format": format_data_int,
            "dict_format": format_dict,
            "data_dpi": dpi_data_int,
            "dict_dpi": dpi_dict,
            "data_distance": distance_data_int,
            "dict_distance": distance_dict,
            "data_uploader": uploader_data_int,
            "dict_uploader": uploader_dict,
            "labels": labels,
        }

        return queryset


class ImageGraphColorClassView(ListView):
    template_name = "myapp/manage/manage_users.html"
    context_object_name = "users"
    paginate_by = 10
    extra_context = {
        "title": "Manage Users",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
    }

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.extra_context)
            return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        search_query = self.request.GET.get("search")
        queryset = User.objects.all()

        if search_query:
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi yang diinginkan.
            queryset = queryset.filter(
                Q(username__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
            )
            # change the page_obj add the search_query
            self.extra_context["search"] = search_query

        return queryset

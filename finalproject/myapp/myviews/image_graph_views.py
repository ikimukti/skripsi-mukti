from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus
from django.views.generic import ListView
from django.contrib.auth.models import User
from myapp.models import Image, ImagePreprocessing, Segmentation, SegmentationResult
from django.db.models import Q, Prefetch, Count, Subquery, OuterRef, F


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
    model = Image
    template_name = "myapp/image/image_graph_color.html"
    context_object_name = "images"
    paginate_by = 10
    extra_context = {
        "title": "Image Graph Color",
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
        segmentation_types = SegmentationResult.objects.values(
            "segmentation_type"
        ).distinct()

        # Retrieve all ImagePreprocessing objects that have segmentation results
        image_preprocessings = ImagePreprocessing.objects.filter(
            segmentations__segmentation_type__in=segmentation_types
        ).distinct()

        # Get the corresponding Image objects
        images = Image.objects.filter(
            imagepreprocessing__in=image_preprocessings
        ).distinct()

        # Query for segmentation results
        queryset = SegmentationResult.objects.filter(
            image__in=images, segmentation_type__in=segmentation_types, rank=1
        ).order_by("image", "rank")
        ccolor_dict = queryset.values_list("image__color", flat=True).distinct()
        ccolor_dict = list(ccolor_dict)
        # ambil semua nilai unik color dari list color_dict
        ccolor_dict = list(set(ccolor_dict))
        self.extra_context["color_dict"] = ccolor_dict
        print(ccolor_dict)
        if search_query:
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi color
            # Query for segmentation results
            queryset = SegmentationResult.objects.filter(
                image__in=images,
                segmentation_type__in=segmentation_types,
                rank=1,
                image__color=search_query,
            ).order_by("image", "rank")

        if search_query == "all":
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi color
            # Query for segmentation results
            queryset = SegmentationResult.objects.filter(
                image__in=images,
                rank=1,
            ).order_by("image", "rank")

        # Ambil semua nilai unik dari field unik
        color_dict = queryset.values_list("image__color", flat=True).distinct()
        # ambil semua nilai unik color dari list color_dict
        segmentation_dict = queryset.values_list(
            "segmentation_type", flat=True
        ).distinct()
        width_dict = queryset.values_list("image__width", flat=True).distinct()
        height_dict = queryset.values_list("image__height", flat=True).distinct()
        size_dict = queryset.values_list("image__size", flat=True).distinct()
        # convert size_dict to KB and MB
        size_dict = [size / 1024 if size > 1024 else size for size in size_dict]
        # size_dict float 2 digit
        size_dict = [round(size, 2) for size in size_dict]
        channel_dict = queryset.values_list("image__channel", flat=True).distinct()
        format_dict = queryset.values_list("image__format", flat=True).distinct()
        dpi_dict = queryset.values_list("image__dpi", flat=True).distinct()
        distance_dict = queryset.values_list("image__distance", flat=True).distinct()
        uploader_dict = queryset.values_list(
            "image__uploader__username", flat=True
        ).distinct()
        color_dict = list(color_dict)
        segmentation_dict = list(segmentation_dict)
        width_dict = list(width_dict)
        height_dict = list(height_dict)
        size_dict = list(size_dict)
        channel_dict = list(channel_dict)
        format_dict = list(format_dict)
        dpi_dict = list(dpi_dict)
        distance_dict = list(distance_dict)
        uploader_dict = list(uploader_dict)

        # Buat dictionary untuk memetakan nilai menjadi angka
        color_mapping = {color: index for index, color in enumerate(color_dict)}
        segmentation_mapping = {
            segmentation: index for index, segmentation in enumerate(segmentation_dict)
        }
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

        # Ambil semua nilai dari field
        color_data = queryset.values_list("image__color", flat=True)
        segmentation_data = queryset.values_list("segmentation_type", flat=True)
        width_data = queryset.values_list("image__width", flat=True)
        height_data = queryset.values_list("image__height", flat=True)
        size_data = queryset.values_list("image__size", flat=True)
        size_data = [size / 1024 if size > 1024 else size for size in size_data]
        size_data = [round(size, 2) for size in size_data]
        channel_data = queryset.values_list("image__channel", flat=True)
        format_data = queryset.values_list("image__format", flat=True)
        dpi_data = queryset.values_list("image__dpi", flat=True)
        distance_data = queryset.values_list("image__distance", flat=True)
        uploader_data = queryset.values_list("image__uploader__username", flat=True)
        color_data = list(color_data)
        segmentation_data = list(segmentation_data)
        width_data = list(width_data)
        height_data = list(height_data)
        size_data = list(size_data)
        channel_data = list(channel_data)
        format_data = list(format_data)
        dpi_data = list(dpi_data)
        distance_data = list(distance_data)
        uploader_data = list(uploader_data)

        # Ubah data menjadi angka sesuai dengan mapping
        color_data_int = [color_mapping[color] for color in color_data]
        segmentation_data_int = [
            segmentation_mapping[segmentation] for segmentation in segmentation_data
        ]
        width_data_int = [width_mapping[width] for width in width_data]
        height_data_int = [height_mapping[height] for height in height_data]
        size_data_int = [size_mapping[size] for size in size_data]
        channel_data_int = [channel_mapping[channel] for channel in channel_data]
        format_data_int = [format_mapping[format] for format in format_data]
        dpi_data_int = [dpi_mapping[dpi] for dpi in dpi_data]
        distance_data_int = [distance_mapping[distance] for distance in distance_data]
        uploader_data_int = [uploader_mapping[uploader] for uploader in uploader_data]

        # Buat labels berdasarkan color_data_int
        # Buat labels berdasarkan color_data_int
        # Membuat label berdasarkan color_data_int
        labels = []
        cn = 0
        cc = 1
        for i in range(len(color_data_int)):
            color_label = color_dict[color_data_int[i]]
            segmentation_label = segmentation_dict[segmentation_data_int[i]]
            if cn == len(segmentation_types):
                cn = 0
                cc += 1
            else:
                cn += 1
            label = "{} {} {}".format(color_label, segmentation_label, cc)
            labels.append(label)
        f1_score_data = list()
        rand_score_data = list()
        jaccard_score_data = list()
        resize_data = list()
        resize_width_data = list()
        resize_height_data = list()
        resize_percent_data = list()
        gaussian_filter_data = list()
        gaussian_filter_size_data = list()
        median_filter_data = list()
        median_filter_size_data = list()
        mean_filter_data = list()
        mean_filter_size_data = list()
        brightness_data = list()
        brightness_percent_data = list()
        contrast_data = list()
        contrast_percent_data = list()
        for query in queryset:
            for segmentation in query.segmentations.all():
                f1_score_data.append(segmentation.f1_score)
                rand_score_data.append(segmentation.rand_score)
                jaccard_score_data.append(segmentation.jaccard_score)
                resize_data.append(segmentation.image_preprocessing.resize)
                resize_width_data.append(segmentation.image_preprocessing.resize_width)
                resize_height_data.append(
                    segmentation.image_preprocessing.resize_height
                )
                resize_percent_data.append(
                    segmentation.image_preprocessing.resize_percent
                )
                gaussian_filter_data.append(
                    segmentation.image_preprocessing.gaussian_filter
                )
                gaussian_filter_size_data.append(
                    segmentation.image_preprocessing.gaussian_filter_size
                )
                median_filter_data.append(
                    segmentation.image_preprocessing.median_filter
                )
                median_filter_size_data.append(
                    segmentation.image_preprocessing.median_filter_size
                )
                mean_filter_data.append(segmentation.image_preprocessing.mean_filter)
                mean_filter_size_data.append(
                    segmentation.image_preprocessing.mean_filter_size
                )
                brightness_data.append(segmentation.image_preprocessing.brightness)
                brightness_percent_data.append(
                    segmentation.image_preprocessing.brightness_percent
                )
                contrast_data.append(segmentation.image_preprocessing.contrast)
                contrast_percent_data.append(
                    segmentation.image_preprocessing.contrast_percent
                )

        f1_score_data = [f1_score * 100 for f1_score in f1_score_data]
        rand_score_data = [rand_score * 100 for rand_score in rand_score_data]
        jaccard_score_data = [
            jaccard_score * 100 for jaccard_score in jaccard_score_data
        ]

        # Mencari indeks dengan skor tertinggi untuk masing-masing metrik
        best_f1_index = max(range(len(f1_score_data)), key=lambda i: f1_score_data[i])
        best_rand_index = max(
            range(len(rand_score_data)), key=lambda i: rand_score_data[i]
        )
        best_jaccard_index = max(
            range(len(jaccard_score_data)), key=lambda i: jaccard_score_data[i]
        )

        # Membandingkan ketiga indeks untuk mencari yang terbaik
        if (
            f1_score_data[best_f1_index] > rand_score_data[best_rand_index]
            and f1_score_data[best_f1_index] > jaccard_score_data[best_jaccard_index]
        ):
            best_index = best_f1_index
            best_metric = "F1 Score"
        elif (
            rand_score_data[best_rand_index] > f1_score_data[best_f1_index]
            and rand_score_data[best_rand_index]
            > jaccard_score_data[best_jaccard_index]
        ):
            best_index = best_rand_index
            best_metric = "Rand Score"
        else:
            best_index = best_jaccard_index
            best_metric = "Jaccard Score"

        # Mencari indeks dengan skor terendah untuk masing-masing metrik
        worst_f1_index = min(range(len(f1_score_data)), key=lambda i: f1_score_data[i])
        worst_rand_index = min(
            range(len(rand_score_data)), key=lambda i: rand_score_data[i]
        )
        worst_jaccard_index = min(
            range(len(jaccard_score_data)), key=lambda i: jaccard_score_data[i]
        )

        # Membandingkan ketiga indeks untuk mencari yang terburuk
        if (
            f1_score_data[worst_f1_index] < rand_score_data[worst_rand_index]
            and f1_score_data[worst_f1_index] < jaccard_score_data[worst_jaccard_index]
        ):
            worst_index = worst_f1_index
            worst_metric = "F1 Score"
        elif (
            rand_score_data[worst_rand_index] < f1_score_data[worst_f1_index]
            and rand_score_data[worst_rand_index]
            < jaccard_score_data[worst_jaccard_index]
        ):
            worst_index = worst_rand_index
            worst_metric = "Rand Score"
        else:
            worst_index = worst_jaccard_index
            worst_metric = "Jaccard Score"

        self.extra_context["total_data"] = len(queryset) / len(segmentation_types)

        self.extra_context["best"] = {
            "index": best_index,
            "color": color_dict[color_data_int[best_index]],
            "segmentation": segmentation_dict[segmentation_data_int[best_index]],
            "width": width_dict[width_data_int[best_index]],
            "height": height_dict[height_data_int[best_index]],
            "size": size_dict[size_data_int[best_index]],
            "channel": channel_dict[channel_data_int[best_index]],
            "format": format_dict[format_data_int[best_index]],
            "dpi": dpi_dict[dpi_data_int[best_index]],
            "distance": distance_dict[distance_data_int[best_index]],
            "uploader": uploader_dict[uploader_data_int[best_index]],
            "f1_score": f1_score_data[best_index],
            "rand_score": rand_score_data[best_index],
            "jaccard_score": jaccard_score_data[best_index],
            "best_metric": best_metric,
            "resize": resize_data[best_index],
            "resize_width": resize_width_data[best_index],
            "resize_height": resize_height_data[best_index],
            "resize_percent": resize_percent_data[best_index],
            "gaussian_filter": gaussian_filter_data[best_index],
            "gaussian_filter_size": gaussian_filter_size_data[best_index],
            "median_filter": median_filter_data[best_index],
            "median_filter_size": median_filter_size_data[best_index],
            "mean_filter": mean_filter_data[best_index],
            "mean_filter_size": mean_filter_size_data[best_index],
            "brightness": brightness_data[best_index],
            "brightness_percent": brightness_percent_data[best_index],
            "contrast": contrast_data[best_index],
            "contrast_percent": contrast_percent_data[best_index],
        }

        self.extra_context["worst"] = {
            "index": worst_index,
            "color": color_dict[color_data_int[worst_index]],
            "segmentation": segmentation_dict[segmentation_data_int[worst_index]],
            "width": width_dict[width_data_int[worst_index]],
            "height": height_dict[height_data_int[worst_index]],
            "size": size_dict[size_data_int[worst_index]],
            "channel": channel_dict[channel_data_int[worst_index]],
            "format": format_dict[format_data_int[worst_index]],
            "dpi": dpi_dict[dpi_data_int[worst_index]],
            "distance": distance_dict[distance_data_int[worst_index]],
            "uploader": uploader_dict[uploader_data_int[worst_index]],
            "f1_score": f1_score_data[worst_index],
            "rand_score": rand_score_data[worst_index],
            "jaccard_score": jaccard_score_data[worst_index],
            "worst_metric": worst_metric,
            "resize": resize_data[worst_index],
            "resize_width": resize_width_data[worst_index],
            "resize_height": resize_height_data[worst_index],
            "resize_percent": resize_percent_data[worst_index],
            "gaussian_filter": gaussian_filter_data[worst_index],
            "gaussian_filter_size": gaussian_filter_size_data[worst_index],
            "median_filter": median_filter_data[worst_index],
            "median_filter_size": median_filter_size_data[worst_index],
            "mean_filter": mean_filter_data[worst_index],
            "mean_filter_size": mean_filter_size_data[worst_index],
            "brightness": brightness_data[worst_index],
            "brightness_percent": brightness_percent_data[worst_index],
            "contrast": contrast_data[worst_index],
            "contrast_percent": contrast_percent_data[worst_index],
        }

        # context chart_js
        self.extra_context["chartjs"] = {
            "data_color": color_data_int,
            "dict_color": color_dict,
            "data_segmentation": segmentation_data_int,
            "dict_segmentation": segmentation_dict,
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
            "data_f1_score": f1_score_data,
            "data_jaccard_score": jaccard_score_data,
            "data_rand_score": rand_score_data,
            "labels": labels,
        }

        # count
        count = queryset.count()
        print("count: ", count)

        return queryset

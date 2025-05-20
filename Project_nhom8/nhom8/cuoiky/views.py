# inventory/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib import messages
from .models import HangHoa # Import model HangHoa của bạn
from django.urls import reverse_lazy
from django.contrib.auth.models import User


from django.db.models import Q # Để dùng OR trong query

# Giả sử TINH_TRANG_TONKHO_CHOICES được định nghĩa ở đây hoặc import từ models
# TINH_TRANG_TONKHO_CHOICES = [ ('CON_HANG', 'Còn hàng'), ('HET_HANG', 'Hết hàng'), ...]

from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from .models import HangHoa, NhapKho, XuatKho, KiemKe  # Import các model của bạn
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tongquan')  # Chuyển hướng đến trang chính sau khi đăng nhập
        else:
            return render(request, 'login.html', {'error': 'Tên đăng nhập hoặc mật khẩu không đúng.'})
    return render(request, 'login.html')

from .forms import ProfileForm
@login_required
def profile_view(request):
    """Hiển thị và cập nhật thông tin profile của người dùng."""

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user)

        if profile_form.is_valid():
            user = profile_form.save(commit=False)
            # Đảm bảo lưu trường phone
            user.phone = profile_form.cleaned_data.get('phone', '')
            user.save()

            messages.success(request, 'Thông tin cá nhân đã được cập nhật thành công!')
            return redirect('profile')
        else:
            messages.error(request, 'Có lỗi xảy ra khi cập nhật thông tin. Vui lòng kiểm tra lại.')
    else:
        profile_form = ProfileForm(instance=request.user)

    context = {
        'profile_form': profile_form,
    }

    return render(request, 'profile.html', context)

@login_required
def dashboard_view(request):
    """
    View này xử lý logic để lấy dữ liệu thống kê từ các model và truyền vào template.
    """
    now = timezone.now()


    # Tính toán tổng số lượng nhập và xuất (đã duyệt)
    total_import = NhapKho.objects.filter(tinh_trang='DA_NHAP').count()
    total_export = XuatKho.objects.filter(tinh_trang='CHO_DUYET').count()

    # Thống kê số lượng hàng hóa theo tình trạng
    con_hang_count = HangHoa.objects.filter(tinh_trang='CON_HANG').count()
    gan_het_hang_count = HangHoa.objects.filter(tinh_trang='GAN_HET_HANG').count()
    het_hang_count = HangHoa.objects.filter(tinh_trang='HET_HANG').count()
    tong_hang_hoa_count = HangHoa.objects.all().count()

    # Thống kê nhập kho trong tháng
    phieu_nhap_thang_count = NhapKho.objects.filter(ngay_tao__month=now.month, ngay_tao__year=now.year).count()
    gia_tri_nhap_thang = NhapKho.objects.filter(ngay_tao__month=now.month, ngay_tao__year=now.year, tinh_trang='DA_NHAP').aggregate(Sum('tong'))['tong__sum'] or 0
    phieu_nhap_cho_duyet_count = NhapKho.objects.filter(tinh_trang='CHO_DUYET').count()

    # Thống kê xuất kho trong tháng
    phieu_xuat_thang_count = XuatKho.objects.filter(ngay_tao__month=now.month, ngay_tao__year=now.year).count()
    gia_tri_xuat_thang = XuatKho.objects.filter(ngay_tao__month=now.month, ngay_tao__year=now.year, tinh_trang='DA_DUYET').aggregate(Sum('tong'))['tong__sum'] or 0
    phieu_xuat_cho_duyet_count = XuatKho.objects.filter(tinh_trang='CHO_DUYET').count()

    # Thống kê kiểm kê trong tháng
    phieu_kiem_ke_thang_count = KiemKe.objects.filter(ngay_tao__month=now.month, ngay_tao__year=now.year).count()
    phieu_kiem_ke_cho_duyet_count = KiemKe.objects.filter(tinh_trang='CHO_DUYET').count()

    # Truyền dữ liệu vào template
    context = {
        'total_import': total_import,
        'total_export': total_export,
        'con_hang_count': con_hang_count,
        'gan_het_hang_count': gan_het_hang_count,
        'het_hang_count': het_hang_count,
        'tong_hang_hoa_count': tong_hang_hoa_count,
        'phieu_nhap_thang_count': phieu_nhap_thang_count,
        'gia_tri_nhap_thang': gia_tri_nhap_thang,
        'phieu_nhap_cho_duyet_count': phieu_nhap_cho_duyet_count,
        'phieu_xuat_thang_count': phieu_xuat_thang_count,
        'gia_tri_xuat_thang': gia_tri_xuat_thang,
        'phieu_xuat_cho_duyet_count': phieu_xuat_cho_duyet_count,
        'phieu_kiem_ke_thang_count': phieu_kiem_ke_thang_count,
        'phieu_kiem_ke_cho_duyet_count': phieu_kiem_ke_cho_duyet_count,
    }

    return render(request, 'cuoiky/tongquan.html', context)  # Đảm bảo template của bạn ở đúng đường dẫn


from django.http import JsonResponse
from django.contrib import messages

from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST



from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect


@require_POST
def hanghoa_delete(request, ma_hang):
    try:
        hanghoa = get_object_or_404(HangHoa, ma_hang=ma_hang)
        ten_hang = hanghoa.ten_hang  # Lưu tên hàng trước khi xóa

        # Kiểm tra xem hàng hóa có liên kết với các bảng khác không
        if hasattr(hanghoa, 'chi_tiet_nhap') and hanghoa.chi_tiet_nhap.exists():
            return JsonResponse({
                'success': False,
                'error': 'Không thể xóa hàng hóa này vì đã có trong phiếu nhập kho.'
            }, status=400)

        if hasattr(hanghoa, 'chi_tiet_xuat') and hanghoa.chi_tiet_xuat.exists():
            return JsonResponse({
                'success': False,
                'error': 'Không thể xóa hàng hóa này vì đã có trong phiếu xuất kho.'
            }, status=400)

        if hasattr(hanghoa, 'chi_tiet_kiem_ke') and hanghoa.chi_tiet_kiem_ke.exists():
            return JsonResponse({
                'success': False,
                'error': 'Không thể xóa hàng hóa này vì đã có trong phiếu kiểm kê.'
            }, status=400)

        hanghoa.delete()

        return JsonResponse({
            'success': True,
            'message': f'Đã xóa thành công hàng hóa: {ten_hang}'
        })
    except HangHoa.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Không tìm thấy hàng hóa với mã: {ma_hang}'
        }, status=404)
    except Exception as e:
        print(f"Lỗi khi xóa hàng hóa: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Lỗi khi xóa hàng hóa: {str(e)}'
        }, status=500)
class HangHoaListView(generic.ListView):
    model = HangHoa
    template_name = 'cuoiky/hanghoa_list.html' # Đổi tên template
    context_object_name = 'hanghoa_list'          # Đổi tên biến context
    paginate_by = 10 # Hoặc số lượng bạn muốn

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-ma_hang')
        query_ma = self.request.GET.get('ma_hang')
        query_ten = self.request.GET.get('ten_hang')
        # Lấy tham số ngày (ví dụ lọc theo hạn sử dụng)
        query_date_from = self.request.GET.get('tu_ngay')
        query_date_to = self.request.GET.get('den_ngay')

        if query_ma:
            # Tìm kiếm gần đúng hoặc chính xác tùy bạn chọn
            queryset = queryset.filter(ma_hang__icontains=query_ma)
        if query_ten:
            queryset = queryset.filter(ten_hang__icontains=query_ten)

        # Ví dụ lọc theo khoảng hạn sử dụng (nếu cần)
        if query_date_from:
            queryset = queryset.filter(han_su_dung__gte=query_date_from)
        if query_date_to:
            queryset = queryset.filter(han_su_dung__lte=query_date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Giữ lại các tham số tìm kiếm khi chuyển trang pagination
        search_params = self.request.GET.copy()
        if 'page' in search_params:
            del search_params['page']
        context['search_params'] = search_params.urlencode()
        context['request'] = self.request # Truyền request vào context để lấy GET params trong template
        return context

from .forms import HangHoaForm


class HangHoaCreateView(generic.CreateView):
    model = HangHoa
    form_class = HangHoaForm
    template_name = 'cuoiky/hanghoa_form.html'
    success_url = reverse_lazy('hanghoa-list')

    def get_initial(self):
        initial = super().get_initial()
        # Tạo mã hàng tự động khi mở form
        last_item = HangHoa.objects.order_by('-ma_hang').first()
        if last_item and last_item.ma_hang.startswith("HH"):
            try:
                last_number = int(last_item.ma_hang.replace("HH", ""))
                new_number = last_number + 1
            except ValueError:
                new_number = 1
        else:
            new_number = 1
        initial['ma_hang'] = f"HH{new_number:04d}"
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'THÊM HÀNG HÓA MỚI'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Đã thêm hàng hóa mới thành công!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Có lỗi xảy ra khi thêm hàng hóa. Vui lòng kiểm tra lại thông tin.")
        return super().form_invalid(form)


class HangHoaUpdateView(generic.UpdateView):
    model = HangHoa
    form_class = HangHoaForm
    template_name = 'cuoiky/hanghoa_form.html'
    pk_url_kwarg = 'ma_hang'
    context_object_name = 'hanghoa'
    success_url = reverse_lazy('hanghoa-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Cập nhật: {self.object.ten_hang}'
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Đã cập nhật hàng hóa {self.object.ten_hang} thành công!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Có lỗi xảy ra khi cập nhật hàng hóa. Vui lòng kiểm tra lại thông tin.")
        return super().form_invalid(form)


# Bạn có thể thêm View xem chi tiết nếu cần
class HangHoaDetailView(generic.DetailView):
    model = HangHoa
    template_name = 'cuoiky/hanghoa_detail.html' # Tạo template này nếu cần
    pk_url_kwarg = 'ma_hang'
    context_object_name = 'hanghoa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'CHI TIẾT THÔNG TIN HÀNG HÓA : {self.object.ten_hang}'
        return context


from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Q

from .models import NhapKho, ChiTietNhap, HangHoa
from .forms import NhapKhoForm, ChiTietNhapFormSet

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.forms import inlineformset_factory
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
import openpyxl

from .models import NhapKho, ChiTietNhap, HangHoa
from .forms import NhapKhoForm, ChiTietNhapForm

# Thay đổi view xóa phiếu nhập kho
def xoa_nhapkho(request, ma_nhap):
    nhapkho = get_object_or_404(NhapKho, ma_nhap=ma_nhap)

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ.'}, status=400)

    try:
        with transaction.atomic():
            #  Nếu phiếu đã duyệt → cần trừ lại tồn kho
            if nhapkho.tinh_trang == 'DA_DUYET':
                for chitiet in nhapkho.chi_tiet_nhap.all():
                    hanghoa = chitiet.ma_hang
                    hanghoa.so_luong_he_thong -= chitiet.so_luong_nhap
                    hanghoa.save()
                    print(f"[-] Trừ {chitiet.so_luong_nhap} khỏi {hanghoa.ma_hang} → tồn kho mới: {hanghoa.so_luong_he_thong}")

            #  Xóa chi tiết trước, rồi xóa phiếu
            nhapkho.chi_tiet_nhap.all().delete()
            nhapkho.delete()
            print(f"Đã xóa phiếu nhập kho {ma_nhap} và cập nhật tồn kho")

        return JsonResponse({
            'status': 'success',
            'message': f'Phiếu nhập kho {ma_nhap} và hàng hóa liên quan đã được xóa thành công.'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Có lỗi xảy ra khi xóa phiếu nhập kho: {str(e)}'
        }, status=500)


# Danh sách phiếu nhập kho
class NhapKhoListView(ListView):
    model = NhapKho
    template_name = 'cuoiky/nhapkho_list.html'
    context_object_name = 'nhapkho_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = NhapKho.objects.all()

        # Lọc theo mã phiếu
        ma_nhap = self.request.GET.get('ma_nhap')
        if ma_nhap:
            queryset = queryset.filter(ma_nhap__icontains=ma_nhap)

        # Lọc theo nguồn nhập
        nguon_nhap = self.request.GET.get('nguon_nhap')
        if nguon_nhap:
            queryset = queryset.filter(nguon_nhap__icontains=nguon_nhap)

        # Lọc theo tình trạng
        tinh_trang = self.request.GET.get('tinh_trang')
        if tinh_trang:
            queryset = queryset.filter(tinh_trang=tinh_trang)

        # Lọc theo khoảng thời gian
        tu_ngay = self.request.GET.get('tu_ngay')
        den_ngay = self.request.GET.get('den_ngay')
        if tu_ngay:
            queryset = queryset.filter(thoi_gian__gte=tu_ngay)
        if den_ngay:
            queryset = queryset.filter(thoi_gian__lte=den_ngay)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Thêm các tham số tìm kiếm vào context để giữ lại khi phân trang
        search_params = ''
        for key, value in self.request.GET.items():
            if key != 'page':
                search_params += f'&{key}={value}'
        context['search_params'] = search_params
        return context


# Xem chi tiết phiếu nhập kho
class NhapKhoDetailView(DetailView):
    model = NhapKho
    template_name = 'cuoiky/nhapkho_detail.html'
    context_object_name = 'nhapkho'
    pk_url_kwarg = 'ma_nhap'

    def get_object(self, queryset=None):
        obj = get_object_or_404(NhapKho, ma_nhap=self.kwargs.get('ma_nhap'))
        # Đảm bảo tổng tiền được cập nhật trước khi hiển thị
        obj.tinh_lai_tong_tien()
        return obj


# Tạo phiếu nhập kho mới
# Tạo phiếu nhập kho mới
class NhapKhoCreateView(CreateView):
    model = NhapKho
    form_class = NhapKhoForm
    template_name = 'cuoiky/nhapkho_form.html'
    success_url = reverse_lazy('nhapkho-list')

    def get_initial(self):
        initial = super().get_initial()
        # Tạo mã nhập kho tự động khi mở form
        prefix = 'NK'
        last_nhap = NhapKho.objects.order_by('-ma_nhap').first()
        if last_nhap and last_nhap.ma_nhap.startswith(prefix):
            try:
                last_number = int(last_nhap.ma_nhap.replace(prefix, ''))
                new_number = last_number + 1
            except ValueError:
                new_number = 1
        else:
            new_number = 1
        initial['ma_nhap'] = f"{prefix}{new_number:04d}"
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'THÊM MỚI PHIẾU NHẬP KHO'
        if self.request.POST:
            context['chitiet_formset'] = ChiTietNhapFormSet(self.request.POST)
        else:
            context['chitiet_formset'] = ChiTietNhapFormSet(queryset=ChiTietNhap.objects.none())

        # Lấy tất cả hàng hóa với đầy đủ thông tin bao gồm đơn giá nhập
        context['all_hanghoa'] = HangHoa.objects.all().values('ma_hang', 'ten_hang', 'don_vi_tinh', 'don_gia_nhap')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        chitiet_formset = context['chitiet_formset']

        self.object = form.save(commit=False)
        self.object.tao_boi = self.request.user if self.request.user.is_authenticated else None
        self.object.save()

        chitiet_formset.instance = self.object

        if chitiet_formset.is_valid():  # Bắt buộc gọi trước!
            has_valid_details = any(
                f.cleaned_data and not f.cleaned_data.get('DELETE', False) and f.cleaned_data.get('ma_hang')
                for f in chitiet_formset.forms
            )
            if not has_valid_details:
                messages.error(self.request, "Vui lòng thêm ít nhất một hàng hóa vào phiếu nhập kho.")
                self.object.delete()
                return self.form_invalid(form)

            chitiet_formset.save()
            self.object.tinh_lai_tong_tien()
            messages.success(self.request, "Tạo phiếu nhập kho thành công!")
            return redirect('nhapkho-detail', ma_nhap=self.object.ma_nhap)
        else:
            self.object.delete()
            return self.form_invalid(form)

    def form_invalid(self, form):
        print("Lỗi trong form:", form.errors)
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('nhapkho-detail', kwargs={'ma_nhap': self.object.ma_nhap})

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden

# Hàm kiểm tra người dùng có thuộc nhóm "Quản lý kho"
def is_quan_ly_kho(user):
    return user.groups.filter(name='Quản lý kho').exists() or user.is_superuser


# Cập nhật phiếu nhập kho
class NhapKhoUpdateView(UpdateView):
    model = NhapKho
    form_class = NhapKhoForm
    template_name = 'cuoiky/nhapkho_form.html'
    pk_url_kwarg = 'ma_nhap'
    success_url = reverse_lazy('nhapkho-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Cập nhật phiếu nhập kho: {self.object.ma_nhap}"
        if self.request.POST:
            context['chitiet_formset'] = ChiTietNhapFormSet(self.request.POST, instance=self.object)
        else:
            context['chitiet_formset'] = ChiTietNhapFormSet(instance=self.object)
        # Đảm bảo truyền đầy đủ thông tin hàng hóa bao gồm đơn giá nhập
        context['all_hanghoa'] = HangHoa.objects.all().values('ma_hang', 'ten_hang', 'don_vi_tinh', 'don_gia_nhap')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        chitiet_formset = context['chitiet_formset']

        # Kiểm tra tính hợp lệ của formset trước khi lưu
        if not chitiet_formset.is_valid():
            print("Lỗi trong chi tiết nhập kho:", chitiet_formset.errors)
            for i, err in enumerate(chitiet_formset.errors):
                if err:
                    print(f"Form {i} errors:", err)
            for err in chitiet_formset.non_form_errors():
                print(f"Non-form error: {err}")
            messages.error(self.request, "Có lỗi xảy ra khi lưu chi tiết nhập kho")
            return self.form_invalid(form)

        with transaction.atomic():
            try:
                # Lưu phiếu nhập kho trước
                self.object = form.save(commit=False)
                self.object.tao_boi = self.request.user if self.request.user.is_authenticated else None
                self.object.save()
                print("Phiếu nhập kho đã được lưu:", self.object)

                # Gán instance cho formset và lưu
                chitiet_formset.instance = self.object
                saved_instances = chitiet_formset.save(commit=False)

                # Lưu từng chi tiết nhập kho
                for instance in saved_instances:
                    # Đảm bảo don_gia_nhap không null
                    if instance.don_gia_nhap is None:
                        if instance.ma_hang and instance.ma_hang.don_gia_nhap:
                            instance.don_gia_nhap = instance.ma_hang.don_gia_nhap
                        else:
                            instance.don_gia_nhap = 0

                    # Tính thanh_tien
                    instance.thanh_tien = (instance.don_gia_nhap * instance.so_luong_nhap) * (
                                1 - instance.chiet_khau / 100)
                    instance.save()
                    print(f"Chi tiết nhập kho đã được lưu: {instance}")

                # Lưu các quan hệ many-to-many nếu có
                chitiet_formset.save_m2m()

                # Cập nhật tổng tiền
                self.object.tinh_lai_tong_tien()
                print("Tổng tiền đã được cập nhật:", self.object.tong)

                messages.success(self.request, f"Phiếu nhập kho {self.object.ma_nhap} đã được cập nhật thành công.")
                return HttpResponseRedirect(self.get_success_url())
            except Exception as e:
                print(f"Lỗi khi lưu phiếu nhập kho: {e}")
                messages.error(self.request, f"Có lỗi xảy ra khi lưu phiếu nhập kho: {e}")
                return self.form_invalid(form)

    def form_invalid(self, form):
        print("Lỗi trong form:", form.errors)
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('nhapkho-detail', kwargs={'ma_nhap': self.object.ma_nhap})


# Duyệt phiếu nhập kho
@login_required
def duyet_nhapkho(request, ma_nhap):
    if not is_quan_ly_kho(request.user):
        messages.error(request, "Bạn không có quyền duyệt phiếu nhập kho.")
        return redirect('nhapkho-detail', ma_nhap=ma_nhap)
    nhapkho = get_object_or_404(NhapKho, ma_nhap=ma_nhap)
    print(f"Duyệt phiếu nhập kho: {ma_nhap}")

    if nhapkho.tinh_trang == 'CHO_DUYET':
        with transaction.atomic():
            nhapkho.tinh_trang = 'DA_DUYET'
            nhapkho.save()

            #  Cập nhật tồn kho ngay tại đây
            for chitiet in nhapkho.chi_tiet_nhap.all():
                hanghoa = chitiet.ma_hang
                hanghoa.so_luong_he_thong += chitiet.so_luong_nhap
                hanghoa.save()
                print(f"[+] Tăng {chitiet.so_luong_nhap} cho {hanghoa.ma_hang} → tồn kho mới: {hanghoa.so_luong_he_thong}")

        messages.success(request, f"Phiếu nhập kho {ma_nhap} đã được duyệt và cập nhật tồn kho.")
    else:
        print(f"Không thể duyệt phiếu nhập kho {ma_nhap} vì trạng thái là {nhapkho.tinh_trang}")
        messages.error(request, "Chỉ có thể duyệt phiếu đang ở trạng thái chờ duyệt.")

    return redirect('nhapkho-detail', ma_nhap=ma_nhap)




# Từ chối phiếu nhập kho
def tu_choi_nhapkho(request, ma_nhap):
    nhapkho = get_object_or_404(NhapKho, ma_nhap=ma_nhap)
    print(f"Từ chối phiếu nhập kho: {ma_nhap}")

    if nhapkho.tinh_trang == 'CHO_DUYET':
        nhapkho.tinh_trang = 'TU_CHOI'
        nhapkho.save()
        print(f"Đã từ chối phiếu nhập kho {ma_nhap}")
        messages.success(request, f"Phiếu nhập kho {ma_nhap} đã bị từ chối.")
    else:
        print(f"Không thể từ chối phiếu {ma_nhap} vì trạng thái là {nhapkho.tinh_trang}")
        messages.error(request, "Chỉ có thể từ chối phiếu đang ở trạng thái chờ duyệt.")

    return redirect('nhapkho-detail', ma_nhap=ma_nhap)



def import_hanghoa_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            workbook = openpyxl.load_workbook(excel_file)
            sheet = workbook.active
            created_count = 0
            updated_count = 0
            errors = []

            # Giả định dòng đầu tiên là header
            header = [cell.value for cell in sheet[1]]
            expected_headers = ['ma_hang', 'ten_hang', 'nhom_hang', 'don_vi_tinh', 'so_luong_he_thong', 'han_su_dung', 'mo_ta', 'tinh_trang', 'url_image']

            if header != expected_headers:
                messages.error(request, f"Cấu trúc file Excel không đúng. Mong đợi các cột: {', '.join(expected_headers)}")
                return redirect('nhapkho-create') # Hoặc trang nào bạn muốn

            for row_index, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                row_data = dict(zip(header, row))
                ma_hang = row_data.get('ma_hang')
                print(f"Đang xử lý dòng {row_index} với dữ liệu: {row_data}")

                if not ma_hang:
                    errors.append(f"Dòng {row_index}: Mã hàng không được để trống.")
                    continue

                try:
                    hang_hoa, created = HangHoa.objects.update_or_create(
                        ma_hang=ma_hang,
                        defaults={
                            'ten_hang': row_data.get('ten_hang', ''),
                            'nhom_hang': row_data.get('nhom_hang', ''),
                            'don_vi_tinh': row_data.get('don_vi_tinh', ''),
                            'so_luong_he_thong': row_data.get('so_luong_he_thong', 0),
                            'han_su_dung': row_data.get('han_su_dung'),
                            'mo_ta': row_data.get('mo_ta', ''),
                            'tinh_trang': row_data.get('tinh_trang', True), # Giả định True nếu không có
                            'url_image': row_data.get('url_image', '') # Cần xử lý file nếu có
                        }
                    )
                    if created:
                        created_count += 1
                        print(f"Đã tạo mới hàng hóa: {hang_hoa}")
                    else:
                        updated_count += 1
                        print(f"Đã cập nhật hàng hóa: {hang_hoa}")
                except Exception as e:
                    error_message = f"Dòng {row_index}: Lỗi khi xử lý - {e}"
                    errors.append(error_message)
                    print(error_message)

            if created_count > 0:
                messages.success(request, f"Đã thêm mới {created_count} hàng hóa từ Excel.")
            if updated_count > 0:
                messages.info(request, f"Đã cập nhật {updated_count} hàng hóa từ Excel.") # changed to info
            if errors:
                messages.error(request, "Có lỗi xảy ra trong quá trình nhập liệu từ Excel:")
                for error_message in errors: # changed variable name to avoid shadowing
                    messages.error(request, error_message)

        except Exception as e:
            error_message = f"Lỗi khi đọc file Excel: {e}"
            messages.error(request, error_message)
            print(error_message)

    return redirect('nhapkho-create') # Chuyển hướng về trang tạo phiếu nhập kho


def get_hanghoa_info(request, hanghoa_id):
    try:
        hang_hoa = HangHoa.objects.get(pk=hanghoa_id)
        data = {
            'ma_hang': hang_hoa.ma_hang,
            'ten_hang': hang_hoa.ten_hang,
            'don_gia_nhap': float(hang_hoa.don_gia_nhap) if hang_hoa.don_gia_nhap else 0,
            'don_gia_ban': float(hang_hoa.don_gia_ban) if hang_hoa.don_gia_ban else 0,
            'so_luong_he_thong': hang_hoa.so_luong_he_thong,
            'don_vi_tinh': hang_hoa.don_vi_tinh
        }
        return JsonResponse(data)
    except HangHoa.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy hàng hóa'}, status=404)



from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Q

from .models import XuatKho, ChiTietXuat, HangHoa
from .forms import XuatKhoForm, ChiTietXuatFormSet


# Xóa phiếu xuất kho
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from .models import XuatKho

def xoa_xuatkho(request, ma_xuat):
    xuatkho = get_object_or_404(XuatKho, ma_xuat=ma_xuat)

    if xuatkho.tinh_trang != 'CHO_DUYET':
        return JsonResponse({'status': 'error', 'message': 'Không thể xóa phiếu đã được duyệt hoặc đã xuất kho.'},
                            status=400)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                print(f"Các chi tiết xuất kho trước khi xóa: {xuatkho.chi_tiet_xuat.all()}")
                xuatkho.chi_tiet_xuat.all().delete()
                print("Đã xóa các chi tiết xuất kho.")
                print(f"Phiếu xuất kho trước khi xóa: {xuatkho}")
                xuatkho.delete()
                print("Đã xóa phiếu xuất kho.")
            return JsonResponse({'status': 'success', 'message': f'Phiếu xuất kho {ma_xuat} đã được xóa thành công.'})
        except Exception as e:
            print(f"Lỗi khi xóa phiếu xuất kho: {e}")
            return JsonResponse({'status': 'error', 'message': f'Có lỗi xảy ra khi xóa phiếu xuất kho: {e}'},
                                status=500)

    # Nếu không phải POST (ví dụ, truy cập trực tiếp), trả về lỗi
    return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ.'}, status=400)


# Danh sách phiếu xuất kho
class XuatKhoListView(ListView):
    model = XuatKho
    template_name = 'cuoiky/xuatkho_list.html'
    context_object_name = 'xuatkho_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = XuatKho.objects.all()

        # Lọc theo mã phiếu
        ma_xuat = self.request.GET.get('ma_xuat')
        if ma_xuat:
            queryset = queryset.filter(ma_xuat__icontains=ma_xuat)

        # Lọc theo nguồn xuất
        nguon_xuat = self.request.GET.get('nguon_xuat')
        if nguon_xuat:
            queryset = queryset.filter(nguon_xuat__icontains=nguon_xuat)

        # Lọc theo tình trạng
        tinh_trang = self.request.GET.get('tinh_trang')
        if tinh_trang:
            queryset = queryset.filter(tinh_trang=tinh_trang)

        # Lọc theo khoảng thời gian
        tu_ngay = self.request.GET.get('tu_ngay')
        den_ngay = self.request.GET.get('den_ngay')
        if tu_ngay:
            queryset = queryset.filter(thoi_gian__gte=tu_ngay)
        if den_ngay:
            queryset = queryset.filter(thoi_gian__lte=den_ngay)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Thêm các tham số tìm kiếm vào context để giữ lại khi phân trang
        search_params = ''
        for key, value in self.request.GET.items():
            if key != 'page':
                search_params += f'&{key}={value}'
        context['search_params'] = search_params
        return context


# Xem chi tiết phiếu xuất kho
class XuatKhoDetailView(DetailView):
    model = XuatKho
    template_name = 'cuoiky/xuatkho_detail.html'
    context_object_name = 'xuatkho'
    pk_url_kwarg = 'ma_xuat'

    def get_object(self, queryset=None):
        return get_object_or_404(XuatKho, ma_xuat=self.kwargs.get('ma_xuat'))


# Tạo phiếu xuất kho mới
class XuatKhoCreateView(CreateView):
    model = XuatKho
    form_class = XuatKhoForm
    template_name = 'cuoiky/xuatkho_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['chitiet_formset'] = ChiTietXuatFormSet(self.request.POST)
        else:
            context['chitiet_formset'] = ChiTietXuatFormSet()
        context['all_hanghoa'] = HangHoa.objects.filter(so_luong_he_thong__gt=0)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        chitiet_formset = context['chitiet_formset']


        with transaction.atomic():
            # Tự động tạo mã phiếu nếu không có
            if not form.instance.ma_xuat:
                today = timezone.now()
                prefix = f"XK{today.strftime('%y%m%d')}"
                last_receipt = XuatKho.objects.filter(ma_xuat__startswith=prefix).order_by('-ma_xuat').first()

                if last_receipt:
                    try:
                        last_num = int(last_receipt.ma_xuat[8:])
                        new_num = last_num + 1
                    except ValueError:
                        new_num = 1
                else:
                    new_num = 1

                form.instance.ma_xuat = f"{prefix}{new_num:03d}"

            # Lưu người tạo
            form.instance.tao_boi = self.request.user if self.request.user.is_authenticated else None
            return super().form_valid(form)

            self.object = form.save()

            if chitiet_formset.is_valid():
                chitiet_formset.instance = self.object
                chitiet_formset.save()

                # Cập nhật tổng tiền
                self.object.tinh_lai_tong_tien()

                messages.success(self.request, f"Phiếu xuất kho {self.object.ma_xuat} đã được tạo thành công.")
                return HttpResponseRedirect(self.get_success_url())
            else:
                return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('xuatkho-detail', kwargs={'ma_xuat': self.object.ma_xuat})


# Cập nhật phiếu xuất kho
class XuatKhoUpdateView(UpdateView):
    model = XuatKho
    form_class = XuatKhoForm
    template_name = 'cuoiky/xuatkho_form.html'
    pk_url_kwarg = 'ma_xuat'

    def get_object(self, queryset=None):
        return get_object_or_404(XuatKho, ma_xuat=self.kwargs.get('ma_xuat'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['chitiet_formset'] = ChiTietXuatFormSet(self.request.POST, instance=self.object)
        else:
            context['chitiet_formset'] = ChiTietXuatFormSet(instance=self.object)
        context['all_hanghoa'] = HangHoa.objects.filter(so_luong_he_thong__gt=0)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        chitiet_formset = context['chitiet_formset']

        with transaction.atomic():
            self.object = form.save()

            if chitiet_formset.is_valid():
                chitiet_formset.instance = self.object
                chitiet_formset.save()

                # Cập nhật tổng tiền
                self.object.tinh_lai_tong_tien()

                messages.success(self.request, f"Phiếu xuất kho {self.object.ma_xuat} đã được cập nhật thành công.")
                return HttpResponseRedirect(self.get_success_url())
            else:
                return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('xuatkho-detail', kwargs={'ma_xuat': self.object.ma_xuat})


# Duyệt phiếu xuất kho
def duyet_xuatkho(request, ma_xuat):
    xuatkho = get_object_or_404(XuatKho, ma_xuat=ma_xuat)

    if xuatkho.tinh_trang == 'CHO_DUYET':
        xuatkho.tinh_trang = 'DA_DUYET'
        xuatkho.save()
        messages.success(request, f"Phiếu xuất kho {ma_xuat} đã được duyệt.")
    else:
        messages.error(request, "Chỉ có thể duyệt phiếu đang ở trạng thái chờ duyệt.")

    return redirect('xuatkho-detail', ma_xuat=ma_xuat)


# Hoàn thành phiếu xuất kho
def xuat_kho(request, ma_xuat):
    xuatkho = get_object_or_404(XuatKho, ma_xuat=ma_xuat)

    if xuatkho.tinh_trang == 'DA_DUYET':
        with transaction.atomic():
            xuatkho.tinh_trang = 'DA_XUAT'
            xuatkho.save()

            # Signal sẽ tự động cập nhật số lượng hàng hóa

            messages.success(request, f"Phiếu xuất kho {ma_xuat} đã được xuất kho thành công.")
    else:
        messages.error(request, "Chỉ có thể xuất kho phiếu đã được duyệt.")

    return redirect('xuatkho-detail', ma_xuat=ma_xuat)


# Từ chối phiếu xuất kho
def tu_choi_xuatkho(request, ma_xuat):
    xuatkho = get_object_or_404(XuatKho, ma_xuat=ma_xuat)

    if xuatkho.tinh_trang == 'CHO_DUYET':
        xuatkho.tinh_trang = 'TU_CHOI'
        xuatkho.save()
        messages.success(request, f"Phiếu xuất kho {ma_xuat} đã bị từ chối.")
    else:
        messages.error(request, "Chỉ có thể từ chối phiếu đang ở trạng thái chờ duyệt.")

    return redirect('xuatkho-detail', ma_xuat=ma_xuat)



from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from .models import KiemKe, HangHoa
from .forms import KiemKeForm, ChiTietKiemKeFormSet, ChiTietKiemKeFormSetUpdate

def kiemke_list(request):
    kiemke_list = KiemKe.objects.all().order_by('-ngay_tao')
    search_ma_kiemke = request.GET.get('ma_kiemke')
    search_muc_dich = request.GET.get('muc_dich')
    search_tinh_trang = request.GET.get('tinh_trang')
    search_tu_ngay = request.GET.get('tu_ngay')
    search_den_ngay = request.GET.get('den_ngay')

    if search_ma_kiemke:
        kiemke_list = kiemke_list.filter(ma_kiemke__icontains=search_ma_kiemke)
    if search_muc_dich:
        kiemke_list = kiemke_list.filter(muc_dich__icontains=search_muc_dich)
    if search_tinh_trang:
        kiemke_list = kiemke_list.filter(tinh_trang=search_tinh_trang)
    if search_tu_ngay:
        kiemke_list = kiemke_list.filter(thoi_gian__date__gte=search_tu_ngay)
    if search_den_ngay:
        kiemke_list = kiemke_list.filter(thoi_gian__date__lte=search_den_ngay)

    paginator = Paginator(kiemke_list, 10)  # Hiển thị 10 phiếu trên mỗi trang
    page = request.GET.get('page')
    try:
        kiemke_page = paginator.page(page)
    except PageNotAnInteger:
        kiemke_page = paginator.page(1)
    except EmptyPage:
        kiemke_page = paginator.page(paginator.num_pages)

    context = {
        'kiemke_list': kiemke_page,
        'page_obj': kiemke_page,
        'is_paginated': kiemke_page.has_other_pages(),
        'paginator': paginator,
        'search_params': request.GET.urlencode()
    }
    return render(request, 'cuoiky/kiemke_list.html', context)

def kiemke_create(request):
    print(f"Request method: {request.method}")
    if request.method == 'POST':
        print("request.POST:", request.POST)
        kiemke_form = KiemKeForm(request.POST)
        chitiet_formset = ChiTietKiemKeFormSet(request.POST)
        print("kiemke_form.is_valid():", kiemke_form.is_valid())
        print("chitiet_formset.is_valid():", chitiet_formset.is_valid())
        if kiemke_form.is_valid() and chitiet_formset.is_valid():
            kiemke = kiemke_form.save(commit=False)
            kiemke.tao_boi = request.user if request.user.is_authenticated else None
            with transaction.atomic():
                kiemke.save()
                chitiet_formset.instance = kiemke
                chitiet_formset.save()
            messages.success(request, 'Phiếu kiểm kê đã được tạo thành công.')
            return redirect(reverse('kiemke-detail', kwargs={'ma_kiemke': kiemke.ma_kiemke}))
        else:
            print("kiemke_form errors:", kiemke_form.errors)
            print("chitiet_formset errors:", chitiet_formset.errors)
            messages.error(request, 'Đã có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
    else:
        kiemke_form = KiemKeForm()
        chitiet_formset = ChiTietKiemKeFormSet()

    context = {
        'kiemke_form': kiemke_form,
        'chitiet_formset': chitiet_formset,
        'all_hanghoa': HangHoa.objects.all()
    }
    return render(request, 'cuoiky/kiemke_create.html', context)

def kiemke_detail(request, ma_kiemke):
    kiemke = get_object_or_404(KiemKe, ma_kiemke=ma_kiemke)
    context = {
        'kiemke': kiemke,
    }
    return render(request, 'cuoiky/kiemke_detail.html', context)

def kiemke_update(request, ma_kiemke):
    kiemke = get_object_or_404(KiemKe, ma_kiemke=ma_kiemke)
    if request.method == 'POST':
        kiemke_form = KiemKeForm(request.POST, instance=kiemke)
        chitiet_formset = ChiTietKiemKeFormSetUpdate(request.POST, instance=kiemke)
        if kiemke_form.is_valid() and chitiet_formset.is_valid():
            try:
                with transaction.atomic():
                    kiemke_form.save()  # Lưu thông tin chung của phiếu kiểm kê
                    chitiet_formset.save()  # Lưu các chi tiết kiểm kê (cập nhật/tạo mới/xóa)
                messages.success(request, 'Phiếu kiểm kê đã được cập nhật thành công.')
                return redirect(reverse('kiemke-detail', kwargs={'ma_kiemke': kiemke.ma_kiemke}))
            except Exception as e:
                messages.error(request, f'Đã có lỗi xảy ra khi cập nhật: {e}')
        else:
            messages.error(request, 'Dữ liệu không hợp lệ. Vui lòng kiểm tra lại.')
            # Có thể bạn muốn render lại form với lỗi để người dùng sửa
            # context['kiemke_form'] = kiemke_form
            # context['chitiet_formset'] = chitiet_formset
            # return render(request, 'cuoiky/kiemke_update.html', context)
    else:
        kiemke_form = KiemKeForm(instance=kiemke)
        chitiet_formset = ChiTietKiemKeFormSetUpdate(instance=kiemke)

    context = {
        'kiemke_form': kiemke_form,
        'chitiet_formset': chitiet_formset,
        'kiemke': kiemke,
        # 'all_kho': Kho.objects.all(), # Nếu cần
    }
    return render(request, 'cuoiky/kiemke_update.html', context)

def kiemke_delete(request, ma_kiemke):
    kiemke = get_object_or_404(KiemKe, ma_kiemke=ma_kiemke)
    if request.method == 'POST':
        kiemke.delete()
        messages.success(request, f'Phiếu kiểm kê mã {ma_kiemke} đã được xóa.')
        return redirect(reverse('kiemke-list'))
    else:
        # Không nên hiển thị trang xác nhận xóa riêng, xử lý bằng modal ở list view
        return redirect(reverse('kiemke-list'))





# cuoiky/views.py

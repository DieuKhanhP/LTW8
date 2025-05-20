from django import forms
from django.forms import inlineformset_factory
from .models import NhapKho, ChiTietNhap, HangHoa, CustomUser, XuatKho, ChiTietXuat, KiemKe, ChiTietKiemKe
from .models import DON_VI_TINH_CHOICES, TINH_TRANG_TONKHO_CHOICES, NHOM_HANG_CHOICES


class ProfileForm(forms.ModelForm):
    """Form cho phép người dùng cập nhật thông tin cá nhân."""

    first_name = forms.CharField(
        label="Tên",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        label="Họ",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    phone = forms.CharField(
        label="Số điện thoại",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    position = forms.CharField(
        label="Chức vụ",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    username = forms.CharField(
        label="Tên đăng nhập",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs.get('instance')

        # Hiển thị chức vụ từ groups của user
        if user and user.groups.exists():
            self.fields['position'].initial = ', '.join([group.name for group in user.groups.all()])
        else:
            self.fields['position'].initial = 'Chưa có chức vụ'


class HangHoaForm(forms.ModelForm):
    class Meta:
        model = HangHoa
        fields = [
            'ma_hang', 'ten_hang', 'nhom_hang', 'don_vi_tinh',
            'don_gia_nhap', 'don_gia_ban', 'so_luong_he_thong',
            'han_su_dung', 'mo_ta', 'tinh_trang', 'url_image',
            'gioi_han_duoi', 'qr_code'
        ]
        widgets = {
            'ma_hang': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
            'ten_hang': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'nhom_hang': forms.Select(
                choices=NHOM_HANG_CHOICES,
                attrs={'class': 'form-select'
                       }),
            'don_vi_tinh': forms.Select(
                choices=DON_VI_TINH_CHOICES,
                attrs={'class': 'form-select'}
            ),
            'don_gia_nhap': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000'
            }),
            'don_gia_ban': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000'
            }),
            'so_luong_he_thong': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'han_su_dung': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'mo_ta': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'tinh_trang': forms.Select(
                choices=TINH_TRANG_TONKHO_CHOICES,
                attrs={'class': 'form-select'}
            ),
            'url_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'gioi_han_duoi': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'qr_code': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Đánh dấu các trường bắt buộc
        self.fields['ten_hang'].required = True
        self.fields['nhom_hang'].required = True
        self.fields['don_vi_tinh'].required = True


class NhapKhoForm(forms.ModelForm):
    class Meta:
        model = NhapKho
        fields = [
            'ma_nhap', 'nguon_nhap', 'thoi_gian', 'kho', 'sdt', 'diachi',
            'ly_do', 'ly_do_khac', 'url_hop_dong', 'url_so_cu'
        ]
        widgets = {
            'ma_nhap': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
            'nguon_nhap': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'thoi_gian': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'kho': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'sdt': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'diachi': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'ly_do': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ly_do_khac': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'url_hop_dong': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'url_so_cu': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Đánh dấu các trường bắt buộc
        self.fields['nguon_nhap'].required = True
        self.fields['thoi_gian'].required = True
        self.fields['kho'].required = True

    def clean(self):
        cleaned_data = super().clean()
        ly_do = cleaned_data.get("ly_do")
        ly_do_khac = cleaned_data.get("ly_do_khac")

        if ly_do == 'KHAC' and not ly_do_khac:
            raise forms.ValidationError("Bạn cần nhập lý do khác khi chọn lý do là 'Khác'.")

        return cleaned_data


class ChiTietNhapForm(forms.ModelForm):
    class Meta:
        model = ChiTietNhap
        fields = ['ma_hang', 'don_gia_nhap', 'so_luong_nhap', 'chiet_khau']
        widgets = {
            'ma_hang': forms.Select(attrs={
                'class': 'form-select hang-hoa-select',
                'data-live-search': 'true',
                'required': 'required'
            }),
            'don_gia_nhap': forms.NumberInput(attrs={
                'class': 'form-control don-gia',
                'min': '0',
                'step': '1000',
                'required': 'required'
            }),
            'so_luong_nhap': forms.NumberInput(attrs={
                'class': 'form-control so-luong',
                'min': '1',
                'required': 'required'
            }),
            'chiet_khau': forms.NumberInput(attrs={
                'class': 'form-control chiet-khau',
                'min': '0',
                'max': '100',
                'step': '0.1',
                'value': '0'  # Đặt giá trị mặc định
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ma_hang'].queryset = HangHoa.objects.all()
        self.fields['ma_hang'].label_from_instance = lambda obj: f"{obj.ten_hang} ({obj.ma_hang})"

        # Đặt giá trị mặc định cho chiết khấu
        if not self.initial.get('chiet_khau'):
            self.initial['chiet_khau'] = 0

    def clean(self):
        cleaned_data = super().clean()
        ma_hang = cleaned_data.get('ma_hang')
        don_gia_nhap = cleaned_data.get('don_gia_nhap')
        so_luong_nhap = cleaned_data.get('so_luong_nhap')
        chiet_khau = cleaned_data.get('chiet_khau')

        # Nếu form này là form trống (không có dữ liệu), bỏ qua việc kiểm tra
        if not any([ma_hang, don_gia_nhap, so_luong_nhap, chiet_khau]):
            self.empty_permitted = True
            return cleaned_data

        # Kiểm tra mã hàng
        if not ma_hang:
            self.add_error('ma_hang', 'Vui lòng chọn hàng hóa.')

        # Kiểm tra số lượng nhập
        if so_luong_nhap is None:
            self.add_error('so_luong_nhap', 'Vui lòng nhập số lượng.')
        elif so_luong_nhap <= 0:
            self.add_error('so_luong_nhap', 'Số lượng nhập phải lớn hơn 0.')

        # Kiểm tra đơn giá nhập
        if don_gia_nhap is None:
            if ma_hang and ma_hang.don_gia_nhap:
                cleaned_data['don_gia_nhap'] = ma_hang.don_gia_nhap
            else:
                cleaned_data['don_gia_nhap'] = 0
        elif don_gia_nhap < 0:
            self.add_error('don_gia_nhap', 'Đơn giá nhập không được âm.')

        # Kiểm tra chiết khấu
        if chiet_khau is None:
            cleaned_data['chiet_khau'] = 0
        elif chiet_khau < 0:
            self.add_error('chiet_khau', 'Chiết khấu không được âm.')
        elif chiet_khau > 100:
            self.add_error('chiet_khau', 'Chiết khấu không được lớn hơn 100%.')

        return cleaned_data

    def has_changed(self):
        """
        Tránh xem form thay đổi chỉ vì chiết khấu = 0.
        Không truy cập cleaned_data vì có thể chưa được sinh ra.
        """
        changed = super().has_changed()

        # Nếu chỉ có 'chiet_khau' thay đổi và nó là 0 trong dữ liệu gửi lên, bỏ qua
        if changed and len(self.changed_data) == 1 and 'chiet_khau' in self.changed_data:
            raw_value = self.data.get(self.add_prefix('chiet_khau'))
            if raw_value in ('0', '0.0', '', None):
                return False

        return changed

from django.forms import BaseInlineFormSet

from django.forms import BaseInlineFormSet

class BaseChiTietNhapFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        valid_count = 0
        for form in self.forms:
            # Bỏ qua form đã đánh dấu xóa
            if self.can_delete and self._should_delete_form(form):
                continue

            # Nếu không thay đổi gì → cho phép bỏ qua
            if not form.has_changed():
                form.empty_permitted = True
                continue

            ma_hang = form.cleaned_data.get('ma_hang')
            if ma_hang:
                valid_count += 1

        if valid_count == 0:
            raise forms.ValidationError("Vui lòng thêm ít nhất một hàng hóa vào phiếu nhập kho.")


# Cập nhật ChiTietNhapFormSet để xử lý lỗi tốt hơn
ChiTietNhapFormSet = forms.inlineformset_factory(
    NhapKho,
    ChiTietNhap,
    form=ChiTietNhapForm,
    formset=BaseChiTietNhapFormSet,
    extra=1,
    can_delete=True,
    validate_min=False,
    validate_max=True
)




class XuatKhoForm(forms.ModelForm):
    class Meta:
        model = XuatKho
        fields = ['ma_xuat', 'nguon_nhan', 'thoi_gian', 'sdt', 'diachi', 'ly_do', 'url_hop_dong', 'url_so_cu']
        widgets = {
            'ma_xuat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Để trống để tự động tạo'}),
            'nguon_nhan': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'thoi_gian': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local', 'required': True}),
            'sdt': forms.TextInput(attrs={'class': 'form-control'}),
            'diachi': forms.TextInput(attrs={'class': 'form-control'}),
            'ly_do': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'url_hop_dong': forms.FileInput(attrs={'class': 'form-control'}),
            'url_so_cu': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Đánh dấu các trường bắt buộc
        self.fields['nguon_nhan'].required = True
        self.fields['thoi_gian'].required = True


class ChiTietXuatForm(forms.ModelForm):
    class Meta:
        model = ChiTietXuat
        fields = ['ma_hang', 'don_gia_xuat', 'so_luong_xuat', 'chiet_khau']
        widgets = {
            'ma_hang': forms.Select(attrs={
                'class': 'form-select hang-hoa-select',
                'data-live-search': 'true'
            }),
            'don_gia_xuat': forms.NumberInput(attrs={
                'class': 'form-control don-gia',
                'min': '0',
                'step': '1000'
            }),
            'so_luong_xuat': forms.NumberInput(attrs={
                'class': 'form-control so-luong',
                'min': '1'
            }),
            'chiet_khau': forms.NumberInput(attrs={
                'class': 'form-control chiet-khau',
                'min': '0',
                'max': '100',
                'step': '0.1'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ma_hang'].queryset = HangHoa.objects.filter(so_luong_he_thong__gt=0)
        self.fields['ma_hang'].label_from_instance = lambda obj: f"{obj.ten_hang} ({obj.ma_hang})"

    def clean(self):
        cleaned_data = super().clean()
        ma_hang = cleaned_data.get('ma_hang')
        don_gia_xuat = cleaned_data.get('don_gia_xuat')
        so_luong_xuat = cleaned_data.get('so_luong_xuat')

        # Nếu đơn giá xuất không được cung cấp, sử dụng đơn giá bán từ hàng hóa
        if ma_hang and not don_gia_xuat and ma_hang.don_gia_ban:
            cleaned_data['don_gia_xuat'] = ma_hang.don_gia_ban

        # Kiểm tra số lượng xuất không vượt quá tồn kho
        if ma_hang and so_luong_xuat and so_luong_xuat > ma_hang.so_luong_he_thong:
            raise forms.ValidationError(
                f"Số lượng xuất ({so_luong_xuat}) vượt quá tồn kho ({ma_hang.so_luong_he_thong})")

        return cleaned_data


# Tạo formset cho chi tiết xuất kho
ChiTietXuatFormSet = forms.inlineformset_factory(
    XuatKho,
    ChiTietXuat,
    form=ChiTietXuatForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)


class KiemKeForm(forms.ModelForm):
    thoi_gian = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label='Thời gian kiểm kê'
    )

    class Meta:
        model = KiemKe
        fields = ['ma_kiemke', 'muc_dich', 'thoi_gian', 'tinh_trang']
        widgets = {
            'ma_kiemke': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'muc_dich': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'tinh_trang': forms.Select(attrs={'class': 'form-select'})
        }


class ChiTietKiemKeForm(forms.ModelForm):
    class Meta:
        model = ChiTietKiemKe
        fields = ['hang_hoa', 'so_luong_tai_kho', 'xu_ly']
        widgets = {
            'hang_hoa': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'so_luong_tai_kho': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'xu_ly': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hang_hoa'].queryset = HangHoa.objects.all()
        self.fields['hang_hoa'].label_from_instance = lambda obj: f"{obj.ten_hang} ({obj.ma_hang})"


ChiTietKiemKeFormSet = forms.inlineformset_factory(
    KiemKe,
    ChiTietKiemKe,
    form=ChiTietKiemKeForm,
    extra=1,
    can_delete=True
)


class ChiTietKiemKeFormUpdate(forms.ModelForm):
    class Meta:
        model = ChiTietKiemKe
        fields = ['so_luong_tai_kho', 'xu_ly']
        widgets = {
            'so_luong_tai_kho': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'xu_ly': forms.Select(attrs={'class': 'form-select'})
        }


ChiTietKiemKeFormSetUpdate = forms.inlineformset_factory(
    KiemKe,
    ChiTietKiemKe,
    form=ChiTietKiemKeFormUpdate,
    extra=0,
    can_delete=True
)
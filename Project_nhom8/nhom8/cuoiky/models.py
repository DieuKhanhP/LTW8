from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from django.contrib.auth.models import AbstractUser, Group


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Chức vụ')

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"


# Choices cho các bảng
TINH_TRANG_NHAPKHO_CHOICES = [
    ('CHO_DUYET', 'Chờ duyệt'),
    ('DA_DUYET', 'Đã duyệt'),
    ('TU_CHOI', 'Từ chối'),
]

TINH_TRANG_XUATKHO_CHOICES = [
    ('CHO_DUYET', 'Chờ duyệt'),
    ('DA_DUYET', 'Đã duyệt'),
    ('TU_CHOI', 'Từ chối'),
]

TINH_TRANG_KIEMKE_CHOICES = [
    ('CHO_DUYET', 'Chờ duyệt'),
    ('DA_DUYET', 'Đã duyệt'),
    ('TU_CHOI', 'Từ chối'),
]

TINH_TRANG_TONKHO_CHOICES = [
    ('CON_HANG', 'Còn hàng'),
    ('GAN_HET_HANG', 'Gần hết hàng'),
    ('HET_HANG', 'Hết hàng'),
]
DON_VI_TINH_CHOICES = [
    ('cai', 'cái'),
    ('kg', 'kg'),
    ('tan', 'tấn'),
    ('bao', 'bao (50kg/bao)'),
    ('m3', 'm³'),
    ('lit', 'lít'),
    ('thung', 'thùng (18 lít/thùng)'),
]
NHOM_HANG_CHOICES = [
    ('VAT_LIEU_THO', 'Vật liệu thô'),
    ('VAT_LIEU_HOAN_THIEN', 'Vật liệu hoàn thiện'),
    ('KIM_LOAI', 'Kim loại - sắt thép - inox'),
    ('DIEN_NUOC', 'Vật tư điện - nước'),
]


# 1. HangHoa (gộp với TonKho)
class HangHoa(models.Model):
    ma_hang = models.CharField(max_length=50, primary_key=True, verbose_name="Mã hàng")
    ten_hang = models.CharField(max_length=255, verbose_name="Tên hàng")
    nhom_hang = models.CharField(
        max_length=50,
        choices=NHOM_HANG_CHOICES,
        default='VAT_LIEU_THO',
        verbose_name="Nhóm hàng"
    )
    url_image = models.ImageField(upload_to='images/hanghoa/', blank=True, null=True, verbose_name="Ảnh sản phẩm")
    don_vi_tinh = models.CharField(
        max_length=50,
        choices=DON_VI_TINH_CHOICES,
        default='cái',
        verbose_name="Đơn vị tính"
    )
    don_gia_nhap = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Đơn giá nhập")
    don_gia_ban = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Đơn giá bán")
    han_su_dung = models.DateField(blank=True, null=True, verbose_name="Hạn sử dụng")
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    so_luong_he_thong = models.PositiveIntegerField(default=0, verbose_name="Số lượng hệ thống")
    tinh_trang = models.CharField(
        max_length=50,
        choices=TINH_TRANG_TONKHO_CHOICES,
        default='CON_HANG',
        verbose_name="Tình trạng tồn kho"
    )
    qr_code = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mã QR")
    gioi_han_duoi = models.PositiveIntegerField(default=0, verbose_name="Giới hạn dưới tồn kho")

    def __str__(self):
        return f"{self.ma_hang} - {self.ten_hang} (Tồn: {self.so_luong_he_thong})"

    class Meta:
        verbose_name = "Hàng Hóa"
        verbose_name_plural = "Hàng Hóa"
        ordering = ['ten_hang']

    def save(self, *args, **kwargs):
        if not self.ma_hang:
            last_item = HangHoa.objects.order_by('-ma_hang').first()
            if last_item and last_item.ma_hang.startswith("HH"):
                last_number = int(last_item.ma_hang.replace("HH", ""))
                new_number = last_number + 1
            else:
                new_number = 1
            self.ma_hang = f"HH{new_number:04d}"

        if self.so_luong_he_thong > self.gioi_han_duoi:
            self.tinh_trang = 'CON_HANG'
        elif self.so_luong_he_thong > 0:
            self.tinh_trang = 'GAN_HET_HANG'
        else:
            self.tinh_trang = 'HET_HANG'
        super().save(*args, **kwargs)


# Model Kho
class Kho(models.Model):
    KHO_CHOICES = [
        ('LUU_TRU', 'Kho lưu trữ'),
        ('DU_TRU', 'Kho dự trữ'),
        ('TRA_LAI', 'Kho trả lại'),
    ]

    ma_kho = models.CharField(max_length=50, primary_key=True, verbose_name="Mã kho")
    ten_kho = models.CharField(max_length=255, verbose_name="Tên kho")
    loai_kho = models.CharField(max_length=50, choices=KHO_CHOICES, verbose_name="Loại kho")
    gioi_han = models.PositiveIntegerField(default=10000, verbose_name="Giới hạn số lượng")
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả")

    def __str__(self):
        return f"{self.ten_kho} ({self.get_loai_kho_display()})"

    class Meta:
        verbose_name = "Kho"
        verbose_name_plural = "Kho"
        ordering = ['ten_kho']


# Model TonKhoTheoKho để theo dõi số lượng hàng hóa trong từng kho
class TonKhoTheoKho(models.Model):
    hang_hoa = models.ForeignKey(
        HangHoa,
        on_delete=models.CASCADE,
        related_name='ton_kho_theo_kho',
        verbose_name="Hàng hóa"
    )
    kho = models.ForeignKey(
        Kho,
        on_delete=models.CASCADE,
        related_name='ton_kho',
        verbose_name="Kho"
    )
    so_luong = models.PositiveIntegerField(default=0, verbose_name="Số lượng")

    def __str__(self):
        return f"{self.hang_hoa.ten_hang} tại {self.kho.ten_kho}: {self.so_luong}"

    class Meta:
        verbose_name = "Tồn kho theo kho"
        verbose_name_plural = "Tồn kho theo kho"
        unique_together = ('hang_hoa', 'kho')


# 2. KhachHang
class KhachHang(models.Model):
    ma_khachhang = models.CharField(max_length=50, primary_key=True, verbose_name="Mã khách hàng")
    ten_khachhang = models.CharField(max_length=255, verbose_name="Tên khách hàng")
    nguoi_dai_dien = models.CharField(max_length=255, blank=True, null=True, verbose_name="Người đại diện")
    sdt = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    dia_chi = models.CharField(max_length=500, blank=True, null=True, verbose_name="Địa chỉ")

    # Các trường thông tin khác của khách hàng

    def save(self, *args, **kwargs):
        if not self.ma_khachhang:
            prefix = 'KH'
            last = KhachHang.objects.filter(ma_khachhang__startswith=prefix).order_by('-ma_khachhang').first()
            if last:
                try:
                    last_number = int(last.ma_khachhang.replace(prefix, ''))
                except ValueError:
                    last_number = 0
            else:
                last_number = 0
            new_number = last_number + 1
            self.ma_khachhang = f"{prefix}{new_number:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ten_khachhang

    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Khách hàng"
        ordering = ['ten_khachhang']


# 3. NhaCungCap
class NhaCungCap(models.Model):
    ma_ncc = models.CharField(max_length=50, primary_key=True, verbose_name="Mã nhà cung cấp")
    ten_ncc = models.CharField(max_length=255, verbose_name="Tên nhà cung cấp")
    nguoi_dai_dien = models.CharField(max_length=255, blank=True, null=True, verbose_name="Người đại diện")
    sdt = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    dia_chi = models.CharField(max_length=500, blank=True, null=True, verbose_name="Địa chỉ")

    # Các trường thông tin khác của nhà cung cấp

    def save(self, *args, **kwargs):
        if not self.ma_ncc:
            prefix = 'NCC'
            last = NhaCungCap.objects.filter(ma_ncc__startswith=prefix).order_by('-ma_ncc').first()
            if last:
                try:
                    last_number = int(last.ma_ncc.replace(prefix, ''))
                except ValueError:
                    last_number = 0
            else:
                last_number = 0
            new_number = last_number + 1
            self.ma_ncc = f"{prefix}{new_number:04d}"  # NCC0001, NCC0002, ...
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ten_ncc

    class Meta:
        verbose_name = "Nhà cung cấp"
        verbose_name_plural = "Nhà cung cấp"
        ordering = ['ten_ncc']


# 4. NhapKho

class NhapKho(models.Model):
    LY_DO_NHAP_CHOICES = [
        ('NHAP_BAN_THUONG', 'Nhập bán thường'),
        ('HOAN_HANG_TU_KH', 'Hoàn hàng từ khách'),
        ('KHAC', 'Khác'),
    ]
    ma_nhap = models.CharField(max_length=50, primary_key=True, verbose_name="Mã phiếu nhập")
    nguon_nhap = models.ForeignKey(NhaCungCap, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name="Nhà cung cấp")
    thoi_gian = models.DateTimeField(default=timezone.now, verbose_name="Thời gian nhập")
    tinh_trang = models.CharField(
        max_length=50,
        choices=TINH_TRANG_NHAPKHO_CHOICES,
        default='CHO_DUYET',
        verbose_name="Tình trạng phiếu"
    )
    tong = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Tổng tiền")
    tao_boi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phieu_nhap_kho',
        verbose_name="Người tạo"
    )
    kho = models.ForeignKey(
        Kho,
        on_delete=models.PROTECT,
        related_name='phieu_nhap',
        verbose_name="Kho nhập",
        default='KHO_DEFAULT'
    )
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo phiếu")
    sdt = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại liên hệ")
    diachi = models.CharField(max_length=500, blank=True, null=True, verbose_name="Địa chỉ liên hệ")
    ly_do = models.CharField(
        max_length=50,
        choices=LY_DO_NHAP_CHOICES,
        default='NHAP_BAN_THUONG',
        verbose_name='Lý do nhập'
    )
    ly_do_khac = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Lý do nhập khác (nếu chọn Khác)'
    )
    url_hop_dong = models.FileField(upload_to='files/nhapkho/hopdong/', blank=True, null=True,
                                    verbose_name="File hợp đồng")
    url_so_cu = models.FileField(upload_to='files/nhapkho/socu/', blank=True, null=True, verbose_name="File sổ cũ")

    def tinh_lai_tong_tien(self):
        from django.db.models import Sum
        total = self.chi_tiet_nhap.aggregate(Sum('thanh_tien'))['thanh_tien__sum'] or 0.00
        self.tong = total
        self.save(update_fields=['tong'])

    def get_ly_do_nhap_display(self):
        if self.ly_do == 'KHAC' and self.ly_do_khac:
            return self.ly_do_khac
        return dict(self.LY_DO_NHAP_CHOICES).get(self.ly_do, '')

    def save(self, *args, **kwargs):
        if not self.ma_nhap:
            prefix = 'PK'
            last_nhap = NhapKho.objects.order_by('-ma_nhap').first()
            if last_nhap and last_nhap.ma_nhap.startswith(prefix):
                try:
                    last_number = int(last_nhap.ma_nhap.replace(prefix, ''))
                except ValueError:
                    last_number = 0
            else:
                last_number = 0
            new_number = last_number + 1
            self.ma_nhap = f"{prefix}{new_number:04d}"  # VD: PN0001
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ma_nhap

    class Meta:
        verbose_name = "Phiếu Nhập Kho"
        verbose_name_plural = "Phiếu Nhập Kho"
        ordering = ['-ngay_tao']


# 5. ChiTietNhap
class ChiTietNhap(models.Model):
    ma_nhap = models.ForeignKey(
        NhapKho,
        on_delete=models.CASCADE,
        related_name='chi_tiet_nhap',
        to_field='ma_nhap',
        verbose_name="Mã phiếu nhập"
    )
    ma_hang = models.ForeignKey(
        HangHoa,
        on_delete=models.PROTECT,
        related_name='chi_tiet_nhap',
        to_field='ma_hang',
        verbose_name="Mã hàng"
    )
    don_gia_nhap = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Đơn giá nhập")
    so_luong_nhap = models.PositiveIntegerField(verbose_name="Số lượng nhập")
    chiet_khau = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Chiết khấu")
    thanh_tien = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Thành tiền", editable=False)

    def clean(self):
        super().clean()
        if self.so_luong_nhap is None or self.so_luong_nhap <= 0:
            raise ValidationError({'so_luong_nhap': 'Số lượng nhập phải lớn hơn 0.'})
        if self.don_gia_nhap < 0:
            raise ValidationError({'don_gia_nhap': 'Đơn giá nhập không được âm.'})
        if self.chiet_khau < 0:
            raise ValidationError({'chiet_khau': 'Chiết khấu không được âm.'})
        if self.chiet_khau > (self.don_gia_nhap * self.so_luong_nhap):
            raise ValidationError({'chiet_khau': 'Chiết khấu không được lớn hơn giá trị hàng.'})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.thanh_tien = (self.don_gia_nhap * self.so_luong_nhap) - self.chiet_khau
            super().save(*args, **kwargs)

            # Cập nhật đơn giá nhập cho hàng hóa - không phụ thuộc trạng thái phiếu
            hang_hoa = self.ma_hang
            hang_hoa.don_gia_nhap = self.don_gia_nhap
            hang_hoa.save(update_fields=['don_gia_nhap'])

            # Cập nhật lại tổng tiền cho phiếu nhập
            self.ma_nhap.tinh_lai_tong_tien()

    def __str__(self):
        return f"Chi tiết {self.ma_nhap.ma_nhap} - {self.ma_hang.ten_hang}"

    class Meta:
        verbose_name = "Chi Tiết Nhập Kho"
        verbose_name_plural = "Chi Tiết Nhập Kho"
        unique_together = ('ma_nhap', 'ma_hang')
        ordering = ['ma_nhap', 'ma_hang']


# 6. XuatKho
class XuatKho(models.Model):
    LY_DO_XUAT_CHOICES = [
        ('XUAT_BAN_THUONG', 'Xuất bán thường'),
        ('KHAC', 'Khác'),
    ]
    ma_xuat = models.CharField(max_length=50, primary_key=True, verbose_name="Mã phiếu xuất")
    nguon_nhan = models.ForeignKey(KhachHang, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name="Khách hàng")
    thoi_gian = models.DateTimeField(default=timezone.now, verbose_name="Thời gian xuất")
    tinh_trang = models.CharField(
        max_length=50,
        choices=TINH_TRANG_XUATKHO_CHOICES,
        default='CHO_DUYET',
        verbose_name="Tình trạng phiếu"

    )
    tong = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Tổng tiền")
    tao_boi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phieu_xuat_kho',
        verbose_name="Người tạo"
    )
    kho = models.ForeignKey(
        Kho,
        on_delete=models.PROTECT,
        related_name='phieu_xuat',
        verbose_name="Kho xuất",
        default='KHO_DEFAULT'
    )
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo phiếu")
    sdt = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại người nhận")
    diachi = models.CharField(max_length=500, blank=True, null=True, verbose_name="Địa chỉ người nhận")
    ly_do = models.CharField(
        max_length=50,
        choices=LY_DO_XUAT_CHOICES,
        default='XUAT_BAN_THUONG',
        verbose_name='Lý do xuất'
    )
    ly_do_khac = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Lý do xuất khác (nếu chọn Khác)'
    )
    url_hop_dong = models.FileField(upload_to='files/xuatkho/hopdong/', blank=True, null=True,
                                    verbose_name="File hợp đồng")
    url_so_cu = models.FileField(upload_to='files/xuatkho/socu/', blank=True, null=True, verbose_name="File sổ cũ")

    def tinh_lai_tong_tien(self):
        total = self.chi_tiet_xuat.aggregate(Sum('thanh_tien'))['thanh_tien__sum'] or 0.00
        self.tong = total
        self.save(update_fields=['tong'])

    def get_ly_do_xuat_display(self):
        if self.ly_do == 'KHAC' and self.ly_do_khac:
            return self.ly_do_khac
        return dict(self.LY_DO_XUAT_CHOICES).get(self.ly_do, '')

    def save(self, *args, **kwargs):
        if not self.ma_xuat:
            prefix = 'XK'
            last_xuat = XuatKho.objects.order_by('-ma_xuat').first()
            if last_xuat and last_xuat.ma_xuat.startswith(prefix):
                try:
                    last_number = int(last_xuat.ma_xuat.replace(prefix, ''))
                except ValueError:
                    last_number = 0
            else:
                last_number = 0
            new_number = last_number + 1
            self.ma_xuat = f"{prefix}{new_number:04d}"  # VD: XK0001
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ma_xuat

    class Meta:
        verbose_name = "Phiếu Xuất Kho"
        verbose_name_plural = "Phiếu Xuất Kho"
        ordering = ['-ngay_tao']


# 7. ChiTietXuat
class ChiTietXuat(models.Model):
    ma_xuat = models.ForeignKey(
        XuatKho,
        on_delete=models.CASCADE,
        related_name='chi_tiet_xuat',
        to_field='ma_xuat',
        verbose_name="Mã phiếu xuất"
    )
    ma_hang = models.ForeignKey(
        HangHoa,
        on_delete=models.PROTECT,
        related_name='chi_tiet_xuat',
        to_field='ma_hang',
        verbose_name="Mã hàng"
    )
    don_gia_xuat = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Đơn giá xuất")
    so_luong_xuat = models.PositiveIntegerField(verbose_name="Số lượng xuất")
    chiet_khau = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Chiết khấu")
    thanh_tien = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Thành tiền", editable=False)

    def clean(self):
        if self.so_luong_xuat is None or self.so_luong_xuat <= 0:
            raise ValidationError({'so_luong_xuat': 'Số lượng xuất phải lớn hơn 0.'})
        if self.don_gia_xuat < 0:
            raise ValidationError({'don_gia_xuat': 'Đơn giá xuất không được âm.'})
        if self.chiet_khau < 0:
            raise ValidationError({'chiet_khau': 'Chiết khấu không được âm.'})
        if self.chiet_khau > (self.don_gia_xuat * self.so_luong_xuat):
            raise ValidationError({'chiet_khau': 'Chiết khấu không được lớn hơn giá trị hàng.'})
        so_luong_cu = 0
        if self.pk:
            chi_tiet_cu = ChiTietXuat.objects.get(ma_xuat=self.ma_xuat, ma_hang=self.ma_hang)
            so_luong_cu = chi_tiet_cu.so_luong_xuat
        if self.ma_hang.so_luong_he_thong + so_luong_cu < self.so_luong_xuat:
            raise ValidationError(
                {'so_luong_xuat': f'Không đủ tồn kho. Tồn kho hiện tại: {self.ma_hang.so_luong_he_thong}'})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Nếu không có đơn giá xuất, sử dụng đơn giá bán từ hàng hóa
            if not self.don_gia_xuat and self.ma_hang.don_gia_ban > 0:
                self.don_gia_xuat = self.ma_hang.don_gia_ban

            self.thanh_tien = (self.don_gia_xuat * self.so_luong_xuat) - self.chiet_khau
            super().save(*args, **kwargs)

            # Cập nhật đơn giá bán cho hàng hóa - không phụ thuộc trạng thái phiếu
            hang_hoa = self.ma_hang
            hang_hoa.don_gia_ban = self.don_gia_xuat
            hang_hoa.save(update_fields=['don_gia_ban'])

    def __str__(self):
        return f"Chi tiết {self.ma_xuat.ma_xuat} - {self.ma_hang.ten_hang}"

    class Meta:
        verbose_name = "Chi Tiết Xuất Kho"
        verbose_name_plural = "Chi Tiết Xuất Kho"
        unique_together = ('ma_xuat', 'ma_hang')
        ordering = ['ma_xuat', 'ma_hang']


# 8. KiemKe
class KiemKe(models.Model):
    MUC_DICH_CHOICES = [
        ('DINH_KY', 'Kiểm kê định kỳ'),
        ('DOT_XUAT', 'Kiểm kê đột xuất'),
        ('DAU_KY', 'Kiểm kê đầu kỳ'),
        ('CUOI_KY', 'Kiểm kê cuối kỳ'),
        ('BAO_TRI', 'Kiểm kê bảo trì, bảo dưỡng'),
    ]
    ma_kiemke = models.CharField(max_length=50, primary_key=True, verbose_name="Mã kiểm kê")
    muc_dich = models.CharField(
        max_length=20,
        choices=MUC_DICH_CHOICES,
        blank=True,
        null=True,
        verbose_name="Mục đích"
    )
    thoi_gian = models.DateTimeField(default=timezone.now, verbose_name="Thời gian kiểm kê")
    tinh_trang = models.CharField(
        max_length=50,
        choices=TINH_TRANG_KIEMKE_CHOICES,
        default='CHO_DUYET',
        verbose_name="Tình trạng phiếu"
    )
    tao_boi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phieu_kiem_ke',
        verbose_name="Người tạo"
    )
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo phiếu")

    def save(self, *args, **kwargs):
        if not self.ma_kiemke:
            prefix = 'KK'
            last = KiemKe.objects.filter(ma_kiemke__startswith=prefix).order_by('-ma_kiemke').first()
            if last:
                try:
                    last_number = int(last.ma_kiemke.replace(prefix, ''))
                except ValueError:
                    last_number = 0
            else:
                last_number = 0
            new_number = last_number + 1
            self.ma_kiemke = f"{prefix}{new_number:04d}"  # KK0001, KK0002, ...
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ma_kiemke

    class Meta:
        verbose_name = "Phiếu Kiểm Kê"
        verbose_name_plural = "Phiếu Kiểm Kê"
        ordering = ['-ngay_tao']


# 9. ChiTietKiemKe
class ChiTietKiemKe(models.Model):
    phieu_kiem_ke = models.ForeignKey(
        KiemKe,
        on_delete=models.CASCADE,
        related_name='chi_tiet_kiem_ke',
        verbose_name="Phiếu kiểm kê"
    )
    hang_hoa = models.ForeignKey(
        HangHoa,
        on_delete=models.PROTECT,
        related_name='chi_tiet_kiem_ke',
        verbose_name="Hàng hóa"
    )
    so_luong_he_thong = models.PositiveIntegerField(verbose_name="Số lượng hệ thống (lúc KK)")
    so_luong_tai_kho = models.PositiveIntegerField(verbose_name="Số lượng thực tế")
    chenh_lech = models.IntegerField(verbose_name="Chênh lệch", editable=False)
    xu_ly = models.CharField(max_length=255, blank=True, null=True, verbose_name="Hướng xử lý")

    def clean(self):
        if self.so_luong_he_thong is None:
            self.so_luong_he_thong = self.hang_hoa.so_luong_he_thong

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.chenh_lech = self.so_luong_tai_kho - self.so_luong_he_thong
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Chi tiết {self.phieu_kiem_ke.ma_kiemke} - {self.hang_hoa.ten_hang}"

    class Meta:
        verbose_name = "Chi Tiết Kiểm Kê"
        verbose_name_plural = "Chi Tiết Kiểm Kê"
        unique_together = ('phieu_kiem_ke', 'hang_hoa')
        ordering = ['phieu_kiem_ke', 'hang_hoa']


# Signals để cập nhật tổng và tồn kho tự động

@receiver(post_delete, sender=ChiTietNhap)
def update_nhapkho_total_after_delete(sender, instance, **kwargs):
    instance.ma_nhap.tinh_lai_tong_tien()
    if instance.ma_nhap.tinh_trang == 'DA_NHAP':
        try:
            hang_hoa = HangHoa.objects.get(ma_hang=instance.ma_hang.ma_hang)
            hang_hoa.so_luong_he_thong -= instance.so_luong_nhap
            hang_hoa.save()
        except HangHoa.DoesNotExist:
            pass


@receiver(post_save, sender=ChiTietXuat)
def update_xuatkho_total_and_tonkho(sender, instance, created, **kwargs):
    with transaction.atomic():
        instance.ma_xuat.tinh_lai_tong_tien()
        try:
            hang_hoa = HangHoa.objects.get(ma_hang=instance.ma_hang.ma_hang)
            if instance.ma_xuat.tinh_trang == 'DA_XUAT':
                hang_hoa.so_luong_he_thong -= instance.so_luong_xuat
            elif instance.ma_xuat.tinh_trang == 'HOAN_HANG':
                hang_hoa.so_luong_he_thong += instance.so_luong_xuat
            hang_hoa.save()
        except HangHoa.DoesNotExist:
            pass


@receiver(post_delete, sender=ChiTietXuat)
def update_xuatkho_total_after_delete(sender, instance, **kwargs):
    instance.ma_xuat.tinh_lai_tong_tien()
    if instance.ma_xuat.tinh_trang == 'DA_XUAT':
        try:
            hang_hoa = HangHoa.objects.get(ma_hang=instance.ma_hang.ma_hang)
            hang_hoa.so_luong_he_thong += instance.so_luong_xuat
            hang_hoa.save()
        except HangHoa.DoesNotExist:
            pass
    elif instance.ma_xuat.tinh_trang == 'HOAN_HANG':
        try:
            hang_hoa = HangHoa.objects.get(ma_hang=instance.ma_hang.ma_hang)
            hang_hoa.so_luong_he_thong -= instance.so_luong_xuat
            hang_hoa.save()
        except HangHoa.DoesNotExist:
            pass


@receiver(post_save, sender=KiemKe)
def update_tonkho_after_kiemke(sender, instance, **kwargs):
    if instance.tinh_trang == 'DA_DUYET':
        with transaction.atomic():
            for chi_tiet in instance.chi_tiet_kiem_ke.all():
                try:
                    hang_hoa = HangHoa.objects.get(ma_hang=chi_tiet.hang_hoa.ma_hang)
                    hang_hoa.so_luong_he_thong = chi_tiet.so_luong_tai_kho
                    hang_hoa.save()
                except HangHoa.DoesNotExist:
                    pass


@receiver(post_save, sender=HangHoa)
def update_tinh_trang_tonkho(sender, instance, **kwargs):
    # Tính toán trạng thái mới
    if instance.so_luong_he_thong > instance.gioi_han_duoi:
        new_status = 'CON_HANG'
    elif instance.so_luong_he_thong > 0:
        new_status = 'GAN_HET_HANG'
    else:
        new_status = 'HET_HANG'

    # Chỉ cập nhật nếu trạng thái thay đổi
    if instance.tinh_trang != new_status:
        instance.tinh_trang = new_status
        if not kwargs.get('raw', False):  # Tránh save khi load fixtures
            instance.save(update_fields=['tinh_trang'])

from django.contrib import admin
from .models import HangHoa , Kho , TonKhoTheoKho , NhapKho, ChiTietNhap, XuatKho, ChiTietXuat,NhaCungCap,KhachHang, KiemKe, ChiTietKiemKe, CustomUser # thay bằng tên model bạn dùng
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    # Thêm các trường tùy chỉnh vào fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('phone', 'position')}),
    )

    # Thêm các trường tùy chỉnh vào add_fieldsets
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin bổ sung', {'fields': ('phone', 'position')}),
    )

    # Hiển thị các trường trong danh sách
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'position', 'is_staff')

    # Cho phép tìm kiếm theo các trường
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')

admin.site.register(HangHoa)
admin.site.register(Kho)
admin.site.register(TonKhoTheoKho)
admin.site.register(NhapKho)
admin.site.register(ChiTietNhap)
admin.site.register(XuatKho)
admin.site.register(ChiTietXuat)
admin.site.register(NhaCungCap)
admin.site.register(KhachHang)
admin.site.register(KiemKe)
admin.site.register(ChiTietKiemKe)
admin.site.register(CustomUser, UserAdmin)





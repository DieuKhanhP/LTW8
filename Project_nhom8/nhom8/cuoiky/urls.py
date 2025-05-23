# inventory/urls.py
from django.urls import path, include
from rest_framework import routers

from . import views
from .views import login_view
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_detail'),
    path('export-bao-cao/', views.export_baocao_doc, name='export_baocao_doc'),
    # Sử dụng slug:<ma_hang> vì ma_hang là CharField và là primary_key
    # Nếu ma_hang chỉ chứa số, bạn có thể dùng <int:ma_hang> hoặc <str:ma_hang>
    # Tuy nhiên, slug an toàn hơn cho các mã có thể chứa chữ cái/ký tự đặc biệt
    path('hanghoa/', views.HangHoaListView.as_view(), name='hanghoa-list'),
    path('hanghoa/them/', views.HangHoaCreateView.as_view(), name='hanghoa-create'),
    path('hanghoa/<slug:ma_hang>/sua/', views.HangHoaUpdateView.as_view(), name='hanghoa-update'),
    path('hanghoa/<str:ma_hang>/xoa/', views.hanghoa_delete, name='hanghoa-delete'),
    path('hanghoa/<slug:ma_hang>/', views.HangHoaDetailView.as_view(), name='hanghoa-detail'), # URL xem chi tiết
    path('nhapkho/', views.NhapKhoListView.as_view(), name='nhapkho-list'),
    path('nhapkho/them/', views.NhapKhoCreateView.as_view(), name='nhapkho-create'),
    path('nhapkho/<str:ma_nhap>/', views.NhapKhoDetailView.as_view(), name='nhapkho-detail'),
    path('nhapkho/<str:ma_nhap>/sua/', views.NhapKhoUpdateView.as_view(), name='nhapkho-update'),
    path('nhapkho/<str:ma_nhap>/xoa/', views.xoa_nhapkho, name='nhapkho-delete'),
    path('nhapkho/<str:ma_nhap>/duyet/', views.duyet_nhapkho, name='duyet-nhapkho'),
    path('nhapkho/<str:ma_nhap>/tu-choi/', views.tu_choi_nhapkho, name='tu-choi-nhapkho'),
    path('xuatkho/', views.XuatKhoListView.as_view(), name='xuatkho-list'),
    path('xuatkho/them/', views.XuatKhoCreateView.as_view(), name='xuatkho-create'),
    path('xuatkho/<str:ma_xuat>/', views.XuatKhoDetailView.as_view(), name='xuatkho-detail'),
    path('xuatkho/<str:ma_xuat>/sua/', views.XuatKhoUpdateView.as_view(), name='xuatkho-update'),
    path('xuatkho/<str:ma_xuat>/xoa/', views.xoa_xuatkho, name='xuatkho-delete'),
    path('xuatkho/<str:ma_xuat>/duyet/', views.duyet_xuatkho, name='xuatkho-duyet'),
    path('xuatkho/<str:ma_xuat>/xuatkho/', views.xuat_kho, name='xuatkho-xuatkho'),
    path('xuatkho/<str:ma_xuat>/tuchoi/', views.tu_choi_xuatkho, name='xuatkho-tuchoi'),

    path('tongquan/', views.dashboard_view, name='tongquan'),  # Định nghĩa URL cho dashboard

    path('kiem-ke/', views.kiemke_list, name='kiemke-list'),
    path('kiem-ke/create/', views.kiemke_create, name='kiemke-create'),
    path('kiem-ke/<str:ma_kiemke>/', views.kiemke_detail, name='kiemke-detail'),
    path('kiem-ke/<str:ma_kiemke>/update/', views.kiemke_update, name='kiemke-update'),
    path('kiem-ke/<str:ma_kiemke>/delete/', views.kiemke_delete, name='kiemke-delete'),
    path('kiem-ke/<str:ma_kiemke>/duyet/', views.duyet_kiemke, name='duyet-kiemke'),
    path('kiem-ke/<str:ma_kiemke>/tu-choi/', views.tu_choi_kiemke, name='tu-choi-kiemke'),
    path('khachhang/', views.KhachHangListView.as_view(), name='khachhang-list'),
    path('nhacungcap/', views.NhaCungCapListView.as_view(), name='nhacungcap-list'),
    path('nhacungcap/create/', views.NhaCungCapCreateView.as_view(), name='nhacungcap-create'),
    path('nhacungcap/<str:pk>/sua/', views.NhaCungCapUpdateView.as_view(), name='nhacungcap-update'),
    path('nhacungcap/<str:pk>/xoa/', views.delete_nhacungcap, name='nhacungcap-delete'),
    path('nhacungcap/<str:pk>/', views.NhaCungCapDetailView.as_view(), name='nhacungcap-detail'),
    path('kho/', views.KhoListView.as_view(), name='kho-list'),
    path('kho/<str:ma_kho>/', views.KhoDetailView.as_view(), name='kho-detail'),







    # Thêm các URL khác nếu cần
]
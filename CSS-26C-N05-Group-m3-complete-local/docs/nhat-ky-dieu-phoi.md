# Nhật ký điều phối

Một dòng cho một lần bàn giao hoặc một mốc đã qua. Người chấm đọc tệp này khi chấm
tiêu chí kế hoạch và điều phối, nên nó là bằng chứng chứ không phải thủ tục.

| Ngày | Ai | Làm gì | Mốc liên quan |
|---|---|---|---|
| 2026-10-07 | Nguyễn Thị Khánh Linh, có hỗ trợ Copilot | Làm việc trên nhánh riêng; cấu hình thời hạn/phiên token, MFA TOTP cho tài khoản admin demo và biện pháp hạn chế khôi phục mật khẩu; bổ sung test JWT và xuất realm đã lọc credential. Bộ kiểm local hiện có 28 test; health checks và xuất bằng chứng đã qua trên các dịch vụ Compose đang chạy. Chưa xác nhận CI GitHub hoặc đăng nhập TOTP/reset end-to-end. | M3 (local; chờ nhóm review và CI) |

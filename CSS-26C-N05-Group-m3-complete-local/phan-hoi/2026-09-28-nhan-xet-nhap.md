# Nhận xét chấm nháp M1, nhóm N05 Group

Bản được xem: `main` tại `133cf34` (23:11 ngày 28/09/2026) và lần gộp pull request #1 (`69419e8`). Đây là nhận xét nháp để nhóm sửa trước hạn, **không phải điểm**. Hạn M1: 23:59 thứ Sáu 02/10/2026, tính khi pull request có tiêu đề bắt đầu bằng `M1:` được gộp vào `main` và **đã có một bạn khác trong nhóm duyệt** (Approve).

## Tình trạng: mục 2 vừa bị xóa khỏi `main`

Pull request #1 đã gộp mục 2 khoảng 1.650 từ vào `docs/bao-cao.md`. Hai mươi hai phút sau, commit `133cf34` "Update bao-cao.md" đẩy thẳng lên `main` **xóa toàn bộ 143 dòng ấy**, và pull request #2 "Revert" đang mở. Nếu `main` giữ nguyên như vậy tới hạn thì M1 **không có mô hình đe dọa**. Nếu nhóm xóa để viết lại thì làm trên nhánh mới và gộp bằng pull request trước hạn; nếu xóa nhầm thì báo thầy.

## Nhận xét trên bản đã gộp (`69419e8`)

Bản này tốt ở chỗ biện pháp đã là **cấu hình cụ thể** (thời hạn token, xoay vòng refresh token, danh sách thuật toán được phép, kiểm `aud`, redirect URI không wildcard, TOTP cho quản trị). Giữ cách viết đó. Cần sửa:

1. **Độ dài:** khoảng 1.650 từ, gấp ba giới hạn một trang. Bỏ các phần giả định và hai lớp phòng thủ khỏi M1, gộp mối đe dọa với biện pháp thành một bảng.
2. **Nhãn STRIDE:** mười mối chưa gắn chữ S, T, R, I, D, E. Mã T1 tới T6 đang dùng cho cả tác nhân lẫn mối đe dọa; đổi một bên sang tiền tố khác.
3. **Ranh giới tin cậy:** dòng "người dùng → IdP → resource server → dữ liệu → CI/CD" mới là thứ tự, chưa nói ranh giới nằm đâu và ai qua được.
4. **Xếp hạng:** chưa có khả năng xảy ra và tác động, nên chưa biết mối nào làm trước.

## `NHOM.md`

Cột "Phần việc chính" còn trống cả bốn dòng; "Đỗ trung kiên" viết hoa lại thành "Đỗ Trung Kiên" cho khớp danh sách lớp. Pull request #1 do tác giả tự gộp, không có lượt duyệt.

## Cách nộp đúng

Tạo nhánh mới từ `main`, sửa trên nhánh ấy, mở pull request tiêu đề `M1: de tai va mo hinh de doa`. Một bạn **không phải tác giả** đọc, góp ý trong pull request rồi bấm **Review changes → Approve**; sau đó mới bấm **Merge**. Pull request tự gộp mà không ai duyệt thì chưa tính là có phản biện. Không push thẳng và không force push lên `main` (quy tắc ở đầu README kho).

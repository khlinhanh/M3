<!-- CSS-MAIN-20260929 -->
# Quy tắc nhánh main của kho nhóm, từ 29/09/2026

Ba việc không làm trên nhánh `main` của kho nhóm: đẩy thẳng (push) lên `main`, ghi đè lịch sử (force push), và xóa nhánh. Mọi thay đổi vào `main` đi qua pull request, và chỉ gộp sau khi **một thành viên khác** đã đọc và bấm **Approve** (duyệt).

- Cách làm: tạo nhánh mới (nút chọn nhánh, gõ tên, ví dụ `m1-mo-hinh-de-doa`), sửa trên nhánh ấy, bấm **Compare & pull request**, nhờ một bạn đọc và duyệt, rồi bấm **Merge pull request**.
- Giảng viên đọc nhật ký hoạt động (Activity) của từng kho: mọi lần push thẳng, force push hay xóa nhánh đều hiện ở đó kèm tài khoản thực hiện. Thay đổi vào `main` không qua pull request không tính vào yêu cầu "mỗi người có ít nhất một pull request được gộp và phản biện một pull request của người khác".
- Vì sao: lịch sử `main` là bằng chứng ai làm gì, và hệ số đóng góp cá nhân đọc từ lịch sử này. Một lần force push xóa được cả commit của bạn cùng nhóm lẫn của giảng viên.
- Nhóm lỡ làm hỏng `main`: đừng tự khôi phục bằng force push. Báo thầy ngay kèm tên nhóm để thầy xử lý.
- Hạn M1 không đổi: 23:59 thứ Sáu 02/10/2026, tính khi pull request `M1:` được gộp vào `main`.

---

<!-- CSS-M1-20260928 -->
# M1: hạn nộp và cách nộp — cập nhật 28/09/2026

Thông báo này thay hạn M1 “trước S3” trong các hướng dẫn cũ của lớp UEH CSS-26C.

- Hạn M1 cho cả lớp: **23:59 thứ Sáu 02/10/2026, giờ Việt Nam (UTC+7)**.
- M1 nộp tại kho nhóm `UEH-CSS-26C/CSS-26C-<mã nhóm>`, không nộp vào kho lab cá nhân.
- Mỗi nhóm nộp **một bản chung**: điền `NHOM.md` (tên nhóm, đề tài, thành viên, phân công); viết mục 2 “Mô hình đe dọa” của `docs/bao-cao.md`, không quá một trang.
- Mô hình gồm hệ thống và ranh giới, tài sản, tác nhân đe dọa, ít nhất năm mối đe dọa theo STRIDE và biện pháp cấu hình dự kiến cho từng mối.
- Nhóm trưởng hoặc một thành viên tạo nhánh riêng, mở pull request có tiêu đề bắt đầu bằng `M1:`. Một thành viên khác đọc, phản biện; chỉnh sửa xong rồi gộp vào `main` trước hạn. Không push thẳng lên `main` đối với bài đồ án.
- Yêu cầu mỗi thành viên có ít nhất một pull request được gộp và phản biện ít nhất một pull request của người khác được xét trong **cả đồ án**, không phải mỗi người nộp một bản M1.
- Kho của cả tám nhóm đã có. Nếu chưa truy cập được, đăng nhập đúng tài khoản đã đăng ký, kiểm tra email/lời mời GitHub, rồi báo thầy kèm tên nhóm nếu vẫn gặp lỗi.

Gia hạn này chỉ áp dụng M1. Hạn lab S1–S2 vẫn là 23:59 ngày 25/09/2026 (UTC+7); các mốc khác giữ nguyên. Nhận xét chấm nháp dùng để sửa bài, không phải điểm chính thức và không tự gia hạn lab.

---

# Kho đồ án nhóm

**Học phần An toàn hệ thống máy tính, học kì 2026-27-HK1. Đồ án nhóm chiếm 50 phần trăm điểm học phần.**

Mỗi nhóm nhận một bản sao riêng của kho này. Mọi thành viên có quyền đẩy mã. Nhóm khác
không đọc được kho của nhóm bạn.

## 1. Đọc trước, năm phút

Đồ án này không phải một bài tập lớn viết cho xong. Nó là thứ thay cho bài thi cuối kì,
và nó đo đúng một việc: nhóm bạn có dựng được một hệ thống chạy thật, cấu hình an toàn,
và **chứng minh được** rằng nó an toàn hay không. Chữ chứng minh ở đây có nghĩa hẹp và
cụ thể: một người khác nhân bản kho của bạn về máy họ, chạy một lệnh, và thấy đúng thứ
bạn nói.

Đó là nguyên lý thứ năm của học phần, đừng tin hãy kiểm, áp lên chính bài nộp của bạn.

## 2. Kho này chứa gì, và bạn phải điền gì

```
CSS-26C-DoAn-Repo/
├── README.md            trang bạn đang đọc
├── NHOM.md              tên nhóm, thành viên, đề tài, phân công. ĐIỀN TRƯỚC MỌI THỨ KHÁC
├── docker-compose.yml   hệ thống của nhóm bạn
├── Makefile             các lệnh chuẩn: up, test, verify, down
├── ma-nguon/            mã của nhóm
├── cau-hinh/            MỌI tệp cấu hình đã sửa, kèm diff so với bản gốc
├── bang-chung/          log, kết quả quét, đầu ra máy đọc được
├── docs/
│   ├── bao-cao.md       báo cáo kĩ thuật, xuất ra bao-cao.pdf khi nộp
│   ├── nhat-ky-dieu-phoi.md   ai làm gì, khi nào, và mốc nào đã qua
│   └── AI-USE.md        khai dùng công cụ hỗ trợ
└── .github/workflows/   cổng an toàn chạy mỗi lần đẩy
```

## 3. Năm mốc, và vì sao có mốc

| Mốc | Hạn | Phải có |
|---|---|---|
| M0 | trước buổi S2 | `NHOM.md` điền đủ, kho đã nhận |
| M1 | 23:59 ngày 02/10/2026 (UTC+7) | chọn đề tài, nộp mô hình đe dọa một trang |
| M2 | trước buổi S5 | kiến trúc, và `make up` chạy được trong CI |
| M3 | trước buổi S7 | `make verify` xanh trong CI, báo cáo nháp đủ mục |
| M4 | trước buổi S9 hai ngày | bản nộp cuối, gắn thẻ git |

Bỏ lỡ một mốc không làm hỏng đồ án. Nó trừ vào tiêu chí kế hoạch và điều phối trong
phần báo cáo, mỗi mốc lỡ trừ 1,5 trên 5 điểm của tiêu chí đó. Mốc là thang đo có mức,
không phải cửa đạt hay không đạt.

Lý do có mốc, nói thẳng: một đồ án nhóm để dồn vào tuần cuối thì phần lớn công việc rơi
vào một hoặc hai người, và phần còn lại của nhóm học được rất ít. Mốc là cách rẻ nhất
để chia đều theo thời gian.

## 4. Chấm thế nào

Đồ án chấm trên thang 100 điểm nội bộ, quy về 50 phần trăm điểm học phần.

| Phần | Điểm nội bộ | Cấp chấm |
|---|---|---|
| Mã nguồn và bằng chứng vận hành | 40 | nhóm, nhân hệ số đóng góp cá nhân |
| Báo cáo kĩ thuật | 25 | nhóm |
| Slides | 10 | nhóm |
| Thuyết trình | 25 | 70 điểm cấp nhóm, 30 điểm cấp cá nhân |

**Điểm nhóm không có nghĩa là chia đều.** Mỗi thành viên chấm mọi thành viên trên bốn
tiêu chí là khối lượng, chất lượng, đúng hạn, hợp tác. Kết quả ấy đối chiếu với số commit
và số dòng thay đổi có nghĩa trên GitHub, rồi thành một hệ số nhân vào phần mã nguồn.

Ba điều kiện cứng cho mỗi thành viên: là tác giả của ít nhất một pull request được gộp,
là người phản biện của ít nhất một pull request của người khác, và trình bày một phần
riêng tối thiểu hai phút khi bảo vệ. Thiếu một trong ba thì hệ số không vượt 1,00.

## 5. Kỉ luật kho, ba điều

**Làm việc bằng pull request, không đẩy thẳng lên `main`.** Không phải để làm khó. Đây
là cách duy nhất để phần phản biện lẫn nhau để lại dấu vết kiểm được, và dấu vết ấy là
một trong ba điều kiện cứng ở trên.

**Không đưa bí mật thật vào kho.** Không mật khẩu thật, không khóa thật, không dữ liệu
cá nhân thật của bất kì ai. Dùng dữ liệu sinh ra hoặc dữ liệu có nhãn. Cổng an toàn
trong CI quét bí mật lộ ở mỗi lần đẩy, và một khóa đã đẩy lên thì coi như đã lộ, kể cả
khi bạn xóa ở commit sau.

**Mọi thứ trong `bang-chung/` phải tái lập được.** Một tệp log dán tay không phải bằng
chứng. Ghi lệnh đã chạy vào `Makefile` để người chấm chạy lại được.

## 6. Ranh giới

Đồ án nằm trong phạm vi học phần: cấu hình và vận hành an toàn. Bạn tác động lên hệ
thống của chính nhóm mình, trong các container của chính mình. Không quét, không dò,
không thử đăng nhập vào bất cứ hệ thống nào không phải của nhóm bạn, kể cả hệ thống của
trường và của nhóm khác, kể cả khi họ đồng ý bằng miệng.

Ranh giới không nằm ở chỗ có gây thiệt hại hay không, mà nằm ở chỗ có được phép hay không.

# Báo cáo kĩ thuật

Sáu mục dưới đây là khung bắt buộc. Xuất ra `bao-cao.pdf` khi nộp.

## 1. Bối cảnh và phạm vi

Đồ án triển khai nền tảng định danh tập trung cho ba ứng dụng dịch vụ bằng Keycloak và
OIDC. Mục tiêu của phần M3 là giảm rủi ro khi access token hoặc phiên bị chiếm, ngăn
token phát cho ứng dụng này được dùng ở API khác, và yêu cầu xác thực TOTP với tài khoản
có quyền quản trị. Kết quả được kiểm tra bằng test tự động, cấu hình realm và bằng chứng
có thể tái tạo từ các lệnh trong `Makefile`.

Phạm vi M3 gồm cấu hình thời hạn access token và phiên, xoay vòng refresh token, PKCE
S256, audience riêng cho từng API, TOTP có điều kiện theo role `admin`, giới hạn thử
đăng nhập và tắt tự phục vụ đặt lại mật khẩu; đồng thời bổ sung kiểm thử và xuất realm
đã lọc thông tin nhạy cảm. Phần này giữ nguyên ba ứng dụng, resource server và các
quyết định nền của M1/M2.

Ngoài phạm vi là triển khai production, hoàn thiện frontend đăng nhập OIDC, vận hành
quy trình hỗ trợ khôi phục mật khẩu, và kiểm thử tương tác TOTP/reset trên trình duyệt.
Các giới hạn của cấu hình demo local, gồm HTTP phát triển và redirect URI localhost,
được nêu tại mục 5.

## 2. Mô hình đe dọa

**Chủ đề B:** Nền tảng định danh tập trung cho ba dịch vụ (Keycloak + 3 ứng dụng OIDC). Hệ thống có hai vai trò `user` và `admin`; browser flow của Keycloak yêu cầu TOTP khi người dùng có role `admin`. Mỗi resource server tự xác minh access token.

### 2.1. Hệ thống và ranh giới tin cậy

**Thành phần:** Keycloak (IdP) + 3 ứng dụng (Relying Parties) + 3 resource server + dữ liệu ứng dụng + CI/CD.

**Ranh giới tin cậy (ai qua được, qua bằng gì):**
- **Người dùng → Keycloak:** môi trường local/CI M2 dùng HTTP phát triển; chưa cấu hình HTTPS production. Admin Console dùng chung cổng Keycloak được map lên loopback cho môi trường local.
- **Người dùng → resource server:** môi trường local/CI M2 dùng HTTP; mỗi API yêu cầu access token hợp lệ với issuer và audience riêng.
- **Keycloak → ứng dụng:** các redirect URI hiện là wildcard localhost phục vụ phát triển; phải thay bằng URI callback chính xác trước khi triển khai.
- **Ứng dụng ↔ ứng dụng:** không tin nhau; token của ứng dụng này không dùng cho ứng dụng khác.
- **Kho mã → CI/CD:** workflow quét lịch sử bằng Gitleaks; nếu cần giá trị bí mật thật thì lưu trong secret store của môi trường chạy, không commit vào kho.
- **File cấu hình → container runtime:** Compose dùng mật khẩu demo mặc định; mật khẩu override qua `KEYCLOAK_ADMIN_PASSWORD`, không lưu giá trị bí mật thật trong tệp cấu hình.

### 2.2. Tài sản

Access token, refresh token, ID token, thông tin đăng nhập, TOTP seed, client secret, khóa ký Keycloak, realm configuration, dữ liệu và quyền ứng dụng, log/bằng chứng.

**Tài sản quan trọng nhất:** quyền truy cập API và dữ liệu được bảo vệ bởi access token.

### 2.3. Tác nhân đe dọa

| Mã | Tác nhân |
|---|---|
| A1 | Người dùng hợp lệ lạm dụng quyền |
| A2 | Kẻ tấn công bên ngoài (thử token, reset mật khẩu) |
| A3 | Kẻ đánh cắp được token |
| A4 | Kẻ biết mật khẩu admin nhưng không có TOTP |
| A5 | Resource server cấu hình sai |
| A6 | Người đọc nhầm cấu hình/log chứa bí mật |

### 2.4. Mối đe dọa theo STRIDE và biện pháp cấu hình

| STRIDE | Mối đe dọa | Khả năng × Tác động | Biện pháp cấu hình dự kiến |
|---|---|---|---|
| **S**poofing | Kẻ tấn công giả token với `alg=none` hoặc chữ ký sai để mạo danh người dùng | Trung bình × Cao | Allowlist thuật toán (RS256); xác minh chữ ký bằng JWKS; từ chối token không chữ ký; kiểm tra `iss`, `aud`, `exp`, `nbf` |
| **T**ampering | Sửa nội dung token hoặc lợi dụng redirect URI wildcard để chuyển mã xác thực | Thấp × Cao | Bắt buộc xác minh chữ ký JWT; redirect URI cụ thể, không wildcard; tách client riêng cho từng ứng dụng |
| **R**epudiation | Phủ nhận hành động do thiếu log và bằng chứng tái lập | Trung bình × Trung bình | Ghi log hoạt động quản trị; lưu bằng chứng với `MANIFEST.txt` chứa SHA-256; dùng lệnh trong `Makefile` để tái lập |
| **I**nformation Disclosure | Lộ access token, TOTP seed, client secret qua log hoặc kho mã | Cao × Cao | Không log token; Gitleaks quét lịch sử trong CI; mật khẩu bootstrap demo có thể override bằng biến môi trường; secret production chưa được cấu hình trong M2 |
| **D**enial of Service | Lạm dụng reset mật khẩu hoặc brute-force OTP để khóa tài khoản hợp lệ | Trung bình × Trung bình | Rate limiting theo IP và tài khoản; mã reset một lần có hạn ngắn; giới hạn số lần thử OTP; phát hiện brute-force |
| **E**levation of Privilege | `user` gọi API admin; hoặc admin vượt MFA bằng cách bỏ qua TOTP | Trung bình × Cao | Kiểm tra role/scope tại resource server, không chỉ ở UI; tách endpoint admin; bắt buộc TOTP cho admin; least privilege |

### 2.5. Ưu tiên xử lý

Làm trước ở M2: **I** (lộ bí mật), **S** (giả token), **E** (vượt quyền) — vì tác động cao, ảnh hưởng toàn hệ thống.

Trạng thái M2: xác minh token, kiểm tra role và cấu trúc flow TOTP riêng cho admin đã có kiểm thử tự động; quét bí mật được chạy trong CI. Realm chưa khai báo tài khoản mẫu; tài khoản cần được enroll TOTP trước khi cấp role `admin`. Việc đăng nhập TOTP end-to-end cần xác minh khi chạy Keycloak; HTTPS và redirect URI chính xác vẫn là yêu cầu trước khi triển khai production.

Rủi ro còn lại: token hợp lệ bị đánh cắp vẫn dùng được đến khi hết hạn hoặc bị thu hồi. Sẽ kiểm chứng bằng các ca kiểm thử bổ sung ở M3.
## 3. Kiến trúc và các quyết định cấu hình, kèm lý do

Mỗi client OIDC (`app1`, `app2`, `app3`) thêm audience mapper vào **access token** của mình, lần lượt là `app1-api`, `app2-api`, `app3-api`; mapper không thêm audience vào ID token. Resource server chỉ chấp nhận RS256, tra khóa ký từ JWKS và kiểm tra `iss`, `aud`, `exp`, `iat`; nếu có `nbf`, thư viện JWT cũng kiểm tra thời điểm này. Vì audience được cấu hình riêng, token phát cho một ứng dụng không thể dùng gọi API của ứng dụng khác.

Browser flow đặt một conditional subflow sau các phương thức đăng nhập hiện có. Condition kiểm tra realm role `admin`; nếu khớp thì OTP Form là bắt buộc. User thường không đi vào nhánh MFA này. Khi tạo admin, cần thiết lập/enroll TOTP trước khi gán role `admin`; nếu OTP chưa có, luồng sẽ không cho admin xác thực thành công.

Keycloak chạy ở chế độ `start-dev` trong Compose. Mật khẩu bootstrap `admin-dev-only` là giá trị demo local/CI, có thể override bằng biến môi trường `KEYCLOAK_ADMIN_PASSWORD`; workflow CI hiện dùng giá trị demo mặc định. Không dùng giá trị này ở môi trường thật.

### 3.1. Biện pháp M3 và vòng đời token

- **Chiếm phiên/token:** các client OIDC giữ Authorization Code Flow với PKCE S256; refresh token bị xoay vòng và không cho dùng lại. Access token sống 300 giây; phiên SSO và client session có idle timeout 900 giây, tối đa 36.000 giây. `sslRequired: none` chỉ giữ nguyên môi trường phát triển local hiện có, không phải cấu hình HTTPS production.
- **Token sống quá lâu:** access token 5 phút, kèm giới hạn idle và tối đa của SSO/client session; refresh token cũ bị thu hồi khi đổi token.
- **Sai audience:** mỗi resource server chỉ chấp nhận audience riêng (`app1-api`, `app2-api`, `app3-api`); kiểm tra được trong test từ chối token của ứng dụng khác.
- **Lạm dụng khôi phục mật khẩu:** tắt self-service password reset và bật Keycloak brute-force protection. Đây là cấu hình đóng chức năng khôi phục công khai cho demo; chưa có quy trình help-desk thay thế hoặc kiểm thử khôi phục end-to-end.
- **MFA quản trị:** browser flow trong snapshot mới chỉ đưa user có realm role `admin` vào OTP Form bắt buộc. User thường không phải đăng ký TOTP theo flow này; tạo admin chưa enroll OTP sẽ buộc setup OTP trong browser login.

| Thành phần | Vòng đời/cấu hình | Ý nghĩa |
|---|---:|---|
| Access token | 300 giây | Hạn chế cửa sổ sử dụng token bị đánh cắp |
| SSO idle / tối đa | 900 / 36.000 giây | Kết thúc phiên không hoạt động và giới hạn tuổi phiên |
| Client session idle / tối đa | 900 / 36.000 giây | Giới hạn phiên tại từng ứng dụng |
| Refresh token | Rotation bật; token cũ không được reuse | Giảm khả năng dùng lại refresh token bị lộ |
| TOTP admin | 6 chữ số, đổi mỗi 30 giây | OTP policy TOTP; OTP Form chỉ áp dụng cho role `admin` |

## 4. Bằng chứng an toàn cho từng quyết định

`make test` chạy bộ `unittest` cho token RS256 hợp lệ, chữ ký sai, thuật toán không được hỗ trợ, issuer/audience sai, token hết hạn/chưa có hiệu lực, claim bắt buộc bị thiếu, `kid` không biết, kiểm tra role trên hai API, và kiểm tra cấu hình flow chỉ yêu cầu OTP cho role `admin`. Kiểm thử audience xác nhận token API này bị từ chối ở API khác. Workflow CI chạy các test này trước khi dựng Compose. Job `bi-mat-lo` quét lịch sử kho bằng Gitleaks.

Ngoài các test token/phân quyền, test cấu hình đọc realm trực tiếp để kiểm tra giá trị vòng đời phiên, chính sách khôi phục, ba audience, PKCE và cấu trúc role-condition → OTP của browser flow. Bộ kiểm có 28 ca tự động; con số này gồm unit test JWT/phân quyền và các kiểm tra cấu hình, không phải kiểm thử end-to-end toàn bộ hệ thống.

`make verify` kiểm tra Keycloak và ba endpoint health, sau đó gọi `make evidence` để tái tạo bản export đã lọc bí mật. Nó không thay thế các test token/role ở trên. Snapshot đã lọc được lưu tại `bang-chung/realm-export-filtered.json`; không đưa mật khẩu, seed TOTP hay dữ liệu cá nhân thật vào bằng chứng.

Cấu hình flow được kiểm tra tĩnh và đã import thành công vào một Keycloak 26.4 cô lập; Admin API xác nhận browser flow đang hoạt động, role-condition kiểm tra `admin`, và OTP Form là bắt buộc. Chưa có frontend OIDC hoàn chỉnh hoặc kiểm thử tương tác browser TOTP/reset; CI chỉ được xác nhận sau khi PR được mở và workflow chạy.

## 5. Giới hạn và hướng mở rộng

Demo giữ nguyên `start-dev`, HTTP loopback, wildcard redirect URI localhost và thời hạn access token 300 giây của snapshot mới. Trước production phải bật HTTPS, thay redirect URI bằng callback cụ thể, thay mật khẩu bootstrap demo bằng secret an toàn, và thực hiện quy trình khôi phục có xác minh danh tính/audit. Việc TOTP thực tế cần được kiểm tra với tài khoản admin sau khi chạy Keycloak sạch; không ghi TOTP secret hoặc mã dự phòng vào repo.

## 6. Phụ lục: đóng góp từng thành viên

Bảng dưới đây ghi nhận vai trò M1 theo `NHOM.md` và phần M3 có thể đối chiếu trong
lịch sử nhánh `m3-complete-local` tại ngày 07/10/2026. Chưa ghi nhận phần code M3 của
các thành viên khác trong lịch sử nhánh này; phần phản biện M3 sẽ được bổ sung sau khi
có review, không suy diễn từ phân công M1.

| Thành viên | Đóng góp đã ghi nhận |
|---|---|
| Đỗ Trung Kiên | Phản biện mô hình đe dọa M1 theo `NHOM.md`; chưa có commit triển khai M3 trên nhánh này. |
| Nguyễn Thị Khánh Linh | Phản biện mô hình đe dọa M1 theo `NHOM.md`; thực hiện các thay đổi M3 về cấu hình realm, kiểm thử token/cấu hình, xuất bằng chứng và cập nhật báo cáo. |
| Huỳnh Hoàng Nam | Viết mô hình đe dọa M1 theo `NHOM.md`; chưa có commit triển khai M3 trên nhánh này. |
| Lê Quốc Đạt | Phản biện mô hình đe dọa M1 theo `NHOM.md`; chưa có commit triển khai M3 trên nhánh này. |

# Phiếu Phản Ánh — K4 Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay các dòng trả lời trống bằng câu trả lời của bạn.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: .......................... Mã học viên: ..........................

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `api_token` không có giá trị mặc định nên app chết ngay khi
khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà việc
"chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

Nếu để mặc định `changeme`, app vẫn khởi động bình thường nhưng khi quên cấu hình secret trên cloud thì ai cũng có thể gọi API bằng token giả. Fail fast làm mình phát hiện lỗi ngay lúc deploy, trước khi dịch vụ thật bị lạm dụng.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/chat` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

Một dòng log JSON có thể được Grafana hoặc Datadog lọc theo `client_id` và đếm số lần `chat_completed`. Nó cũng cho phép cảnh báo khi `usd_cost` vượt ngưỡng, điều mà `print()` không tự động phân tích được.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t chat:single .
docker build -t chat:multi .
docker images | grep chat
```

| Bản               | Dung lượng |
| ----------------- | ---------- |
| 1 stage (bản đầu) | ... MB     |
| Multi-stage       | ... MB     |

Giải thích: phần dung lượng chênh lệch đó là những gì?

Image 1 stage giữ cả pip cache, compiler, source và build tools nên rất nặng. Multi-stage chỉ giữ runtime dependencies và code cần chạy, nên giảm được phần dư thừa như package manager, cache và toolchain.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

Khi sửa một dòng trong `app/main.py`, Docker chỉ phải rebuild layer copy source và layer chạy app; các layer cài dependency vẫn reuse cache. Nếu đặt `COPY . .` trước `RUN pip install`, cứ sửa code là layer cài thư viện bị invalid và build lại từ đầu.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

Nếu app Python bị khai thác, kẻ tấn công chỉ có quyền của user trong container. Nếu container chạy root, họ có thể thao tác với file hệ thống, mount hoặc cấu hình nội bộ dễ hơn và rủi ro lan sang host cao hơn. `USER appuser` giảm quyền của tiến trình ở điểm chạy app.

---

### Câu 6 — Bearer token (CP3)

Vì sao 401 phải kèm header `WWW-Authenticate: Bearer`? Và vì sao ta trả **cùng
một** thông báo lỗi cho cả ba trường hợp (thiếu header, sai scheme, sai token)
thay vì nói rõ sai ở đâu cho người dùng dễ sửa?

`WWW-Authenticate: Bearer` là tín hiệu chuẩn HTTP cho client biết kiểu xác thực cần dùng khi nhận 401. Mình trả chung một thông báo cho thiếu header, sai scheme và sai token để không tiết lộ token nào đúng hay sai, tránh trợ giúp cho người dò brute-force.

---

### Câu 7 — Token bucket (CP3)

Với `capacity=10`, `refill_per_minute=10`: một client im lặng 10 phút rồi gửi
liên tiếp. Nó gửi được bao nhiêu request trước khi bị 429? Nếu bỏ đoạn
`min(capacity, ...)` trong `available()` thì con số đó thành bao nhiêu, và tại sao?

Sau khi im lặng 10 phút, xô đầy lại tối đa 10 token nên client gửi được 10 request liên tiếp trước khi bị 429. Nếu bỏ `min(capacity, ...)`, token có thể tích vượt sức chứa trong thời gian dài rồi bắn ra hàng trăm request trong một đợt.

---

### Câu 8 — Ngân sách theo ngày (CP3)

So sánh hạn mức $30/tháng với hạn mức $1/ngày cho cùng một client. Giả sử có sự
cố khiến một client gọi liên tục từ 2h sáng. Với mỗi cách, thiệt hại tối đa là
bao nhiêu và service tự hồi phục khi nào?

Với 30 USD/tháng, một sự cố từ 2h sáng có thể đốt gần hết hạn mức của cả tháng trước khi bị chặn. Với 1 USD/ngày, thiệt hại tối đa chỉ quanh 1 USD trong ngày đó và sang ngày mới budget được reset tự nhiên.

---

### Câu 9 — /healthz khác /readyz (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

Nếu gộp hai endpoint và để nó phụ thuộc Redis, Redis mất 30 giây sẽ làm `/health` bị 503, load balancer tưởng container chết và restart liên tục. Như vậy các request đang chạy dở bị cắt, làm cả cụm 3 container mất ổn định thay vì chỉ ngắt traffic mới.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

Khi deploy local fallback, lỗi mình gặp là Compose/stack chưa có Redis hoặc app chưa đọc đúng biến môi trường, nên `/readyz` trả 503. Mình dò bằng `docker compose ps`, đọc log container và gọi thử `/readyz` để xác nhận dependency nào đang lỗi, rồi sửa `REDIS_URL` và khởi động lại stack.

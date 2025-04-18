# Shopee Price Tracker

Công cụ theo dõi giá sản phẩm trên Shopee, ghi lại biến động giá theo thời gian và tính toán phần trăm giảm giá so với giá trung bình.

## Tính năng chính

- Tự động trích xuất giá sản phẩm từ Shopee thông qua URL
- Hỗ trợ theo dõi sản phẩm có tối đa 2 phân loại (màu sắc, kích thước, v.v.)
- Lưu trữ giá theo ngày dưới dạng cột trong file Excel
- Tính toán phần trăm giảm giá so với giá trung bình và hiển thị trực quan (màu xanh cho giảm giá, đỏ cho tăng giá)
- Cung cấp cả giao diện web (cho người dùng thông thường) và giao diện dòng lệnh (cho người dùng nâng cao)

## Hướng dẫn cài đặt và sử dụng

### Yêu cầu

- Python 3.6+
- Các thư viện: pandas, openpyxl, requests, beautifulsoup4, flask, gunicorn, tqdm

### Cài đặt trên máy tính cá nhân

1. Sao chép mã nguồn
```bash
git clone https://github.com/yourusername/shopee-price-tracker.git
cd shopee-price-tracker
```

2. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng web
```bash
python main.py
# Hoặc sử dụng gunicorn
gunicorn --bind 0.0.0.0:5000 main:app
```

4. Chạy công cụ dòng lệnh
```bash
python shopee_tracker_cli.py -f path/to/excel_file.xlsx -t 4
```

### Tạo file Excel mẫu

```bash
python create_sample_excel.py
```

Lệnh này sẽ tạo ra một file `shopee_sample.xlsx` với cấu trúc chuẩn và dữ liệu mẫu.

### Cấu trúc file Excel

File Excel cần có cấu trúc sau:

1. **Dòng 1:** Chứa thông tin cấu hình dưới dạng `link_column=X;var1_column=Y;var2_column=Z;discount_column=W` trong ô A1
   - `link_column`: Cột chứa URL sản phẩm Shopee
   - `var1_column`: Cột chứa thông tin phân loại 1 (màu sắc, v.v.)
   - `var2_column`: Cột chứa thông tin phân loại 2 (dung lượng, kích thước, v.v.)
   - `discount_column`: Cột để lưu phần trăm giảm giá

2. **Dòng 2:** Tiêu đề cột
   - Cột URL sản phẩm (thường là cột A)
   - Cột phân loại 1 (thường là cột B)
   - Cột phân loại 2 (thường là cột C)
   - Cột phần trăm giảm giá (thường là cột D)
   - Các cột thể hiện ngày theo định dạng YYYY-MM-DD (cột E và tiếp theo)

3. **Dòng 3 trở đi:** Dữ liệu sản phẩm
   - URL sản phẩm Shopee
   - Thông tin phân loại 1 (nếu có)
   - Thông tin phân loại 2 (nếu có)
   - Cột phần trăm giảm giá (để trống, sẽ được tự động tính toán)
   - Giá theo ngày

## Triển khai trên Render

### Chuẩn bị

1. Tạo tài khoản trên [Render](https://render.com) nếu chưa có

2. Đảm bảo đã có file `requirements.txt` cho triển khai. Bạn có thể sử dụng file `requirements.txt.sample` làm mẫu:
```bash
# Đổi tên file mẫu thành requirements.txt
cp requirements.txt.sample requirements.txt
```

3. Tạo file `render.yaml` tại thư mục gốc của dự án với nội dung:
```yaml
services:
  - type: web
    name: shopee-price-tracker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn main:app
    autoDeploy: true
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

### Triển khai

1. Trong dashboard của Render, chọn "New" > "Blueprint"

2. Kết nối với repository GitHub/GitLab/Bitbucket của bạn

3. Chọn repository chứa mã nguồn Shopee Price Tracker

4. Render sẽ tự động phát hiện file `render.yaml` và thiết lập theo cấu hình trong đó

5. Xác nhận và bắt đầu quá trình triển khai

6. Sau khi triển khai hoàn tất, bạn có thể truy cập ứng dụng qua URL do Render cung cấp

## Tính năng nâng cao

- **Multi-threading:** Công cụ hỗ trợ đa luồng để tăng tốc quá trình thu thập giá. Mặc định sử dụng 4 luồng, có thể điều chỉnh thông qua tham số `-t` trong CLI hoặc form web.

- **Xử lý lỗi thông minh:** Nếu không thể lấy giá qua API, công cụ sẽ ghi nhận lỗi nhưng vẫn tiếp tục xử lý các sản phẩm khác.

- **Tự động tạo cột ngày:** Mỗi lần chạy, công cụ sẽ tự động tạo cột cho ngày hiện tại nếu chưa tồn tại.

## Khắc phục sự cố

**Lỗi 403 Forbidden:** Shopee có các biện pháp chống scraping. Nếu bạn gặp lỗi này, hãy thử các giải pháp sau:
- Sử dụng proxy
- Giảm số lượng luồng
- Thêm thời gian chờ giữa các yêu cầu

**Không tìm thấy sản phẩm:** Đảm bảo URL sản phẩm chứa các thông tin shop_id và item_id (thường có dạng `i.[shop_id].[item_id]` ở cuối URL).

## Tham khảo và liên hệ

Nếu bạn có câu hỏi hoặc gặp vấn đề, vui lòng tạo issue trên GitHub hoặc liên hệ qua email.
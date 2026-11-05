# Mạng Lưới Xã Hội Điện Ảnh & Sân Khấu Việt Nam (Vietnam Cinema SNA)
> **BÀI TẬP LỚN: XÂY DỰNG MẠNG XÃ HỘI DỰA TRÊN KỸ THUẬT PHÂN TÍCH XỬ LÝ NGÔN NGỮ TỰ NHIÊN (NLP)**
> 
> **Khai thác Infobox và Văn bản Wikipedia tiếng Việt để Trích xuất Mạng Tri thức Điện ảnh**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Graph%20DB-Neo4j%205.x-green.svg)](https://neo4j.com/)
[![Nodes](https://img.shields.io/badge/Nodes-3%2C037-orange.svg)]()
[![Edges](https://img.shields.io/badge/Edges-18%2C122-red.svg)]()
[![Precision](https://img.shields.io/badge/Precision-96.00%25-brightgreen.svg)]()
[![Report](https://img.shields.io/badge/Report-11%20Pages%20PDF-purple.svg)](./reports/BAO_CAO_BAI_TAP_LON_SNA.pdf)

---

## 1. Giới Thiệu Đề Tài

Dự án thực hiện thu thập, trích xuất thực thể và liên kết quan hệ tự động từ **2.253 bài viết Wikipedia tiếng Việt** thuộc chủ đề điện ảnh, sân khấu, diễn viên, đạo diễn và tác phẩm nghệ thuật Việt Nam.

Hệ thống kết hợp **Regex Template Engine** phân tích Infobox chuẩn hóa với mô hình **Open Information Extraction (Open IE)** đọc hiểu văn bản tự nhiên tại các mục *"Tiểu sử"*, *"Sự nghiệp điện ảnh"*, *"Sân khấu"*. Kết quả tạo nên một đồ thị mạng xã hội tri thức hoàn chỉnh, sẵn sàng nạp trực tiếp vào hệ quản trị cơ sở dữ liệu đồ thị **Neo4j**.

### 1.1. Phân Công Công Việc Trong Nhóm (2 Thành Viên)

| STT | Thành viên | Vai trò | Trách nhiệm chính | Tỷ lệ |
| :---: | :--- | :--- | :--- | :---: |
| 1 | **Thành viên 1** *(Trưởng nhóm)*<br>`[Họ và tên - MSSV]` | Data Engineer & Backend Neo4j | Thiết kế Ontology & Schema đồ thị 3.037 đỉnh, lập trình crawler bất đồng bộ (`crawl_vietnam_cinema.py`), mô hình hóa CSDL đồ thị Neo4j & xuất script Cypher 3.5 MB (`import_neo4j.cypher`). | 100% |
| 2 | **Thành viên 2**<br>`[Họ và tên - MSSV]` | NLP Specialist & SNA Data Analyst | Xây dựng bộ bóc tách Infobox & OpenIE (`cinema_extractor.py`), trích xuất 10 loại quan hệ đặc thù (thầy trò, đóng cặp, chỉ đạo...), phân tích tô-pô mạng xã hội & xuất báo cáo PDF 11 trang. | 100% |

---

## 2. Bảng Tổng Hợp Chỉ Số Đạt Được

| Tiêu chuẩn yêu cầu bài tập | Mức tối thiểu yêu cầu | Thực tế đạt được | Đánh giá |
| :--- | :---: | :---: | :---: |
| **Quy mô số đỉnh (Nodes)** | $\ge$ 2.000 nút (hoặc 1.000) | **3.037 Đỉnh** *(Person: 2.107, Artwork: 802, Organization: 128)* | **Vượt 151.8%** |
| **Quy mô số cạnh (Edges)** | $\ge$ 5.000 cạnh | **18.122 Cạnh có hướng** | **Vượt 362.4%** |
| **Số loại quan hệ ngữ nghĩa** | $\ge$ 10 loại quan hệ | **Đúng 10 loại quan hệ chi tiết** | **Đạt 10/10** |
| **Độ chính xác mạng lưới** | $\ge$ 90% | **96.00%** *(Thẩm định ngẫu nhiên 300 cạnh)* | **Vượt chỉ tiêu** |
| **Hệ quản trị CSDL Graph** | Neo4j / ArangoDB,... | **Neo4j 5.x** *(kèm script Cypher 3.5 MB)* | **Hoàn thành** |
| **Báo cáo học thuật** | $\ge$ 10 trang | **11 Trang PDF A4 màu** + file Markdown đầy đủ | **Vượt chỉ tiêu** |

---

## 3. Thống Kê 10 Loại Quan Hệ Chi Tiết (10 Edge Relationship Types)

Mạng lưới tuân thủ nghiêm ngặt ràng buộc bản thể học (Ontology Constraints):

| STT | Mã quan hệ (`rel_type`) | Đỉnh nguồn $\to$ Đích | Số lượng cạnh | Tỷ lệ | Định nghĩa & Ý nghĩa nghiệp vụ |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | `CO_STARRED` | Person $\leftrightarrow$ Person | **11.629** | 64.17% | Diễn viên đóng cặp / hợp tác trong cùng tác phẩm |
| **2** | `ACTED_IN` | Person $\to$ Artwork | **2.898** | 15.99% | Diễn viên tham gia diễn xuất trong phim / kịch |
| **3** | `DIRECTED_ACTOR` | Person $\to$ Person | **1.982** | 10.94% | Đạo diễn chỉ đạo diễn xuất diễn viên trong phim |
| **4** | `DIRECTED` | Person $\to$ Artwork | **621** | 3.43% | Đạo diễn chỉ đạo sản xuất tác phẩm nghệ thuật |
| **5** | `MARRIED_TO` | Person $\leftrightarrow$ Person | **440** | 2.43% | Quan hệ vợ chồng / gia đình nghệ sĩ |
| **6** | `PRODUCED_BY` | Artwork $\to$ Organization | **296** | 1.63% | Phim được sản xuất bởi hãng phim / đài TH |
| **7** | `PRODUCED` | Person $\to$ Artwork | **161** | 0.89% | Nhà sản xuất (Producer) đầu tư sản xuất phim |
| **8** | `MENTORED` | Person $\to$ Person | **52** | 0.29% | Thầy trò nghệ thuật, người nâng đỡ, phát hiện tài năng |
| **9** | `AFFILIATED_WITH` | Person $\to$ Organization | **24** | 0.13% | Nghệ sĩ công tác / biên chế tại Nhà hát, Đoàn kịch |
| **10**| `FOUNDED` | Person $\to$ Organization | **19** | 0.10% | Nghệ sĩ sáng lập sân khấu, hãng phim, nhóm kịch |
| **Tổng** | **10 Loại quan hệ** | — | **18.122** | **100%** | **Đầy đủ 10/10 quan hệ đặc thù** |

---

## 4. Cấu Trúc Thư Mục Dự Án

```
├── README.md                      # Tài liệu tổng quan & hướng dẫn dự án
├── .gitignore                     # Cấu hình loại trừ cache & file tạm
│
├── data/                          # Dữ liệu đồ thị và kịch bản Neo4j
│   ├── vietnam_cinema_nodes.csv   # Danh sách 3.037 đỉnh (Person, Artwork, Organization)
│   ├── vietnam_cinema_edges.csv   # Danh sách 18.122 cạnh có hướng & minh chứng văn bản
│   └── import_neo4j.cypher        # Kịch bản 3.44 MB nạp CSDL đồ thị Neo4j
│
├── src/                           # Toàn bộ mã nguồn thu thập, trích xuất & phân tích
│   ├── crawl_vietnam_cinema.py    # Pipeline thu thập dữ liệu Wikipedia & trích xuất đồ thị
│   ├── cinema_extractor.py        # Module NLP (Regex Infobox + Rule-based Open IE)
│   ├── cinema_models.py           # Mô hình dữ liệu Graph, Node, Edge & CSV/Cypher Exporter
│   ├── analyze_cinema_graph.py    # Script tính toán giải thuật SNA (PageRank, HITS, Communities)
│   └── generate_cinema_report_pdf.py # Script biên soạn & xuất báo cáo PDF 11 trang đồ họa cao
│
├── tests/                         # Bộ kiểm thử tự động (Unit Tests)
│   ├── test_cinema_models.py      # Unit test kiểm thử cấu trúc dữ liệu đồ thị
│   └── test_cinema_extractor.py   # Unit test kiểm thử bộ trích xuất NLP
│
└── reports/                       # Báo cáo học thuật hoàn chỉnh
    ├── BAO_CAO_BAI_TAP_LON_SNA.pdf # Báo cáo PDF 11 trang A4 màu chuẩn in ấn
    └── BAO_CAO_BAI_TAP_LON_SNA.md # Toàn văn báo cáo học thuật định dạng Markdown
```

---

## 5. Hướng Dẫn Cài Đặt & Tái Hiện (Quick Start)

### 5.1. Yêu cầu môi trường
- Python 3.10 trở lên
- Git
- Neo4j Desktop 5.x hoặc Neo4j Community Server (tùy chọn để trực quan hóa CSDL)

### 5.2. Cài đặt thư viện phụ thuộc
```bash
git clone https://github.com/DontAskMeWhy0507/vietnam-cinema-graph-nlp.git
cd vietnam-cinema-graph-nlp
pip install httpx beautifulsoup4 networkx matplotlib scipy numpy pytest
```

### 5.3. Chạy kiểm thử tự động (Unit Tests)
```bash
pytest tests/
# hoặc chạy trực tiếp từng test:
python tests/test_cinema_models.py
python tests/test_cinema_extractor.py
```

### 5.4. Thu thập & Trích xuất đồ thị
```bash
python src/crawl_vietnam_cinema.py
```
*Kết quả xuất tự động vào thư mục `data/`: `vietnam_cinema_nodes.csv`, `vietnam_cinema_edges.csv`, và `import_neo4j.cypher`.*

### 5.5. Phân tích mạng lưới xã hội (SNA Analysis)
```bash
python src/analyze_cinema_graph.py
```
*Tính toán: Degree Centrality, In/Out-degree, PageRank, HITS Authority/Hub, Louvain Communities, Reciprocity, SCC/WCC.*

### 5.6. Xuất báo cáo PDF 11 trang
```bash
python src/generate_cinema_report_pdf.py
```
*Tạo file `reports/BAO_CAO_BAI_TAP_LON_SNA.pdf` chuẩn đồ họa in ấn.*

---

## 6. Hướng Dẫn Nạp Dữ Liệu Vào Neo4j

### Cách 1: Nạp trực tiếp bằng file Cypher script
Mở **Neo4j Desktop** hoặc **Cypher-shell**:
```bash
cypher-shell -u neo4j -p <password> -f data/import_neo4j.cypher
```

### Cách 2: Truy vấn trực quan hóa các quan hệ đặc thù trên Neo4j Browser
```cypher
// 1. Xem mạng lưới Thầy trò nâng đỡ (MENTORED)
MATCH (mentor:Person)-[r:MENTORED]->(mentee:Person)
RETURN mentor.name AS NguoiNangDo, mentee.name AS HocTro, r.context AS BoCanh
LIMIT 25;

// 2. Xem quan hệ Đạo diễn chỉ đạo diễn viên (DIRECTED_ACTOR)
MATCH (d:Person)-[r:DIRECTED_ACTOR]->(a:Person)
RETURN d.name AS DaoDien, a.name AS DienVien, count(r) AS SoLanHopTac
ORDER BY SoLanHopTac DESC
LIMIT 15;

// 3. Xem cặp đôi diễn viên đóng cặp ăn ý nhất (CO_STARRED)
MATCH (a1:Person)-[r:CO_STARRED]->(a2:Person)
WHERE a1.name < a2.name
RETURN a1.name AS DienVien1, a2.name AS DienVien2, r.weight AS SoPhimChung
ORDER BY SoPhimChung DESC
LIMIT 15;
```

---

## 7. Báo Cáo Học Thuật Đầy Đủ

Vui lòng tham khảo file báo cáo chi tiết:
- **[BAO_CAO_BAI_TAP_LON_SNA.pdf](./reports/BAO_CAO_BAI_TAP_LON_SNA.pdf)** (Phiên bản PDF hoàn chỉnh 11 trang kèm đồ thị phân tích).
- **[BAO_CAO_BAI_TAP_LON_SNA.md](./reports/BAO_CAO_BAI_TAP_LON_SNA.md)** (Phiên bản Markdown toàn văn).
